//------------------------------------------------------------------------------------------
// Summary:    Lightweight VICP client implementation.
//
// Started by:  Anthony Cake
//
// Started:    June 2003
//        Published on SourceForge under LeCroyVICP project, Sept 2003
//------------------------------------------------------------------------------------------
//
// Ported to Linux by: M. Rubio-Roy (LLR,CNRS)
// Ported to Linux: May 2014
//
// Description:
//
//    This file contains a Client-side implementation of the VICP network communications
//    protocol used to control LeCroy Digital Oscilloscopes (DSOs).
//
//    This file is intended to be ultimately as platform independent as possible, but at
//    present has only been compiled & tested under Visual C++ 6.0 on a Windows platform.
//
// VICP Protocol Description/History:
//
//    The VICP Protocol has been around since 1997/98. It did not change in any way between it's
//    conception, and June 2003, when a previously reserved field in the header was assigned.
//    This field, found at byte #2, is now used to allow the client-end of a VICP communication
//    to detect 'out of sync' situations, and therefore allows the GPIB 488.2 'Unread Response'
//    mechanism to be emulated.
//
//    These extensions to the original protocol did not cause a version number change, and are
//    referred to as version 1a. It was decided not to bump the version number to reduce the
//    impact on clients, many of which are looking for a version number of 1.
//    Clients and servers detect protocol version 1a by examining the sequence number field,
//    it should be 0 for version 1 of the protocol (early clients), or non-zero for v1a.
//
//
// VICP Headers:
//
//     Byte Description
//     ------------------------------------------------
//     0    Operation
//     1    Version    1 = version 1
//     2    Sequence Number { 1..255 }, (was unused until June 2003)
//     3    Unused
//     4    Block size, MSB   (not including this header)
//     5    Block size
//     6    Block size
//     7    Block size, LSB
//
//  Operation bits:
//
//    Bit   Mnemonic   Purpose
//    -----------------------------------------------
//    D7    DATA       Data block (D0 indicates with/without EOI)
//    D6    REMOTE     Remote Mode
//    D5    LOCKOUT    Local Lockout (Lockout front panel)
//    D4    CLEAR      Device Clear (if sent with data, clear occurs before block is passed to parser)
//    D3    SRQ        SRQ (Device -> PC only)
//    D2    SERIALPOLL Request a serial poll
//    D1    Reserved   Reserved for future expansion
//    D0    EOI        Block terminated in EOI
//
// Known Limitations:
//
// Outstanding Issues
//
// Dependencies:
//
//------------------------------------------------------------------------------------------
//

#include <stdio.h>
//#include <malloc.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <ctype.h>

#define min(a,b) (((a) < (b)) ? (a) : (b))

// GPIB status bit vector :
//       global variable ibsta and wait mask

#define ERR     (1<<15) // Error detected           0x8000
#define TIMO    (1<<14) // Timeout                  0x4000
#define END     (1<<13) // EOI or EOS detected      0x2000
#define SRQI    (1<<12) // SRQ detected by CIC      0x1000
#define RQS     (1<<11) // Device needs service     0x0800
#define SPOLL   (1<<10) // Board has been serially polled 0x0400
#define CMPL    (1<<8)  // I/O completed            0x0100
#define REM     (1<<6)  // Remote state             0x0040
#define CIC     (1<<5)  // Controller-in-Charge     0x0020
#define ATN     (1<<4)  // Attention asserted       0x0010
#define TACS    (1<<3)  // Talker active            0x0008
#define LACS    (1<<2)  // Listener active          0x0004
#define DTAS    (1<<1)  // Device trigger state     0x0002
#define DCAS    (1<<0)  // Device clear state       0x0001

// GPIB error codes :
//    iberr

#define EDVR  0     // System error
#define ECIC  1     // Function requires GPIB board to be CIC
#define ENOL  2     // Write function detected no Listeners
#define EADR  3     // Interface board not addressed correctly
#define EARG  4     // Invalid argument to function call
#define ESAC  5     // Function requires GPIB board to be SAC
#define EABO  6     // I/O operation aborted
#define ENEB  7     // Non-existent interface board
#define EDMA  8     // Error performing DMA
#define EOIP  10    // I/O operation started before previous operation completed
#define ECAP  11    // No capability for intended operation
#define EFSO  12    // File system operation error
#define EBUS  14    // Command error during device call
#define ESTB  15    // Serial poll status byte lost
#define ESRQ  16    // SRQ remains asserted
#define ETAB  20    // The return buffer is full.
#define ELCK  21    // Address or board is locked.

#define SERVER_PORT_NUM         1861    // port # registered with IANA for lecroy-vicp
#define IO_NET_HEADER_SIZE      8       // size of network header
#define ERR                     (1<<15) // Error detected
#define SMALL_DATA_BUFSIZE      8192
#define CONNECT_TIMEOUT_SECS    2L
#define MAX_DEVICE_ADDR_LEN     255     // max. length of a device address string (dns address/dotted ip address)
#define MAX_ERROR_MSG_LEN       255     // max. length of a device address string (dns address/dotted ip address)

// VICP header 'Operation' bits
#define OPERATION_DATA          0x80
#define OPERATION_REMOTE        0x40
#define OPERATION_LOCKOUT       0x20
#define OPERATION_CLEAR         0x10
#define OPERATION_SRQ           0x08
#define OPERATION_REQSERIALPOLL 0x04
#define OPERATION_EOI           0x01

// Header Version
#define HEADER_VERSION1         0x01

enum READSTATE
{
  NetWaitingForHeader,
  NetWaitingForData,
  NetErrorState
};

struct vicpdevice
{
  char m_deviceAddress[MAX_DEVICE_ADDR_LEN];
  float m_currentTimeout;          // current timeout time (seconds)
  bool m_remoteMode;               // if true, device is in remote mode
  bool m_localLockout;             // if true, device is in local lockout mode
  bool m_connectedToScope;         // connected to scope?
  struct sockaddr_in m_serverAddr;        // server's socket address
  int m_socketFd;                  // socket file descriptor
  int m_iberr;                     // emulation of GPIB counterparts
  int m_ibsta;                     // emulation of GPIB counterparts
  long m_ibcntl;                   // emulation of GPIB counterparts
  int m_maxBlockSize;              // max # bytes that may be read in one go by recv
  enum READSTATE m_readState;           // current state of read 'state machine'
  bool m_bFlushUnreadResponses;    // if true, unread responses are flushed (emulate GPIB 488.2 behaviour)
  char m_lastErrorMsg[MAX_ERROR_MSG_LEN];  // last error message
  bool m_bErrorFlag;               // if true, error has been observed
  bool m_bVICPVersion1aSupported;  // version 1a of the VICP protocol supported (seq. numbers and OOB data)
  int m_lastSequenceNumber;        // last used sequence value
  int m_nextSequenceNumber;        // next sequence value
};

struct vicpdevice * initvicpdevice(void);
void deinitvicpdevice(struct vicpdevice * ws);
// Lookup the IP address of a DNS name
uint32_t GetIPFromDNS(struct vicpdevice * ws);
uint32_t GetDeviceIPAddress(struct vicpdevice * ws);
// initialize the socket (doesn't require remote device to be connected or responding)
bool openSocket(struct vicpdevice * ws);
// disconnect from a network device
bool disconnectFromDevice(struct vicpdevice * ws);
// connect to a network device
// address is extracted from ws->m_deviceAddress (specified during construction of base class)
bool connectToDevice(struct vicpdevice * ws);
// Return the next sequence number in the range 1..255 (Zero is omitted intentionally)
// used to synchronize r/w operations, attempting to emulate the
// 488.2 'discard unread response' behaviour
unsigned char GetNextSequenceNumber(struct vicpdevice * ws, unsigned char flags);
// send a 'small' block of data to a network device
// returns true on error status
bool sendSmallDataToDevice(struct vicpdevice * ws, const char *message, uint32_t bytesToSend, bool eoiTermination, bool deviceClear, bool serialPoll);
// return the last-used sequence number without incrementing it
unsigned char GetLastSequenceNumber(struct vicpdevice * ws);
// dump data until the next header is found
// TODO: Handle timeout cases
void dumpData(struct vicpdevice * ws, int numBytes);
// read header a network device
bool readHeaderFromDevice(struct vicpdevice * ws, uint32_t *blockSize, bool *eoiTerminated, bool *srqStateChanged, int *seqNum);
// read block of data from a network device
// if bFlush is requested then ignore replyBuf and userBufferSizeBytes and read
// all remaining data from the current block (i.e. up to the start of the next header)
uint32_t readDataFromDevice(struct vicpdevice * ws, char *replyBuf, int userBufferSizeBytes, bool bFlush);
// send a block of data to a network device
// returns false on error status
bool sendDataToDevice(struct vicpdevice * ws, const char *message, int bytesToSend, bool eoiTermination, bool deviceClear, bool serialPoll);
// clear the device
void deviceClear(struct vicpdevice * ws);
// out-of band data request, used for serial polling and possibly other features in the future
bool oobDataRequest(struct vicpdevice * ws, char requestType, unsigned char *response);
// return the serial poll byte. Uses the new Out-Of-Band signalling technique if
// supported, else use the original 'in-band' technique.
int serialPoll(struct vicpdevice * ws);

