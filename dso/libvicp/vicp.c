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

#include "vicp.h"

#define DEBUG 0

struct vicpdevice * initvicpdevice()
{
  struct vicpdevice * ws = malloc(sizeof(struct vicpdevice));
  // no connection (yet)
  memset(ws->m_deviceAddress,0,sizeof(ws->m_deviceAddress));
  memset(ws->m_lastErrorMsg,0,sizeof(ws->m_lastErrorMsg));
  ws->m_socketFd = -1;
  ws->m_readState = NetWaitingForHeader;
  ws->m_connectedToScope = false;
  ws->m_remoteMode = false;
  ws->m_localLockout = false;
  ws->m_iberr = ws->m_ibsta = ws->m_ibcntl = 0;
  ws->m_bErrorFlag = false;
  ws->m_nextSequenceNumber = 1;
  ws->m_lastSequenceNumber = 1;
  ws->m_bFlushUnreadResponses = true;
  ws->m_bVICPVersion1aSupported = false;

  // TODO: determine the max. block size
  ws->m_maxBlockSize = 512;    // TODO: safe value for now

  ws->m_currentTimeout = 10;
  return ws;
}

void deinitvicpdevice(struct vicpdevice * ws)
{
  free(ws);
}

//------------------------------------------------------------------------------------------
// Lookup the IP address of a DNS name
uint32_t GetIPFromDNS(struct vicpdevice * ws)
{
  struct in_addr addr;
  int  ret, *intp;
  char  **p;
  struct hostent *hp = gethostbyname(ws->m_deviceAddress);
  if (hp != NULL)
  {
    // We assume that if there is more than 1 address, there might be
    // a server conflict.
    p = hp->h_addr_list;
    intp = (int *) *p;
    ret = *intp;
    addr.s_addr = ret;
    return addr.s_addr;
  }

  return 0;
}

uint32_t GetDeviceIPAddress(struct vicpdevice * ws)
{
  // loop through the address string and try to identify whether it's a dotted static IP
  // address, or a DNS address
  bool bOnlyDigitsAndDots = true;
  int dotCount = 0;
  uint32_t i;
  for(i = 0; i < strlen(ws->m_deviceAddress); ++i)
  {
    // count the dots
    if(ws->m_deviceAddress[i] == '.')
      ++dotCount;

    // if the character is not a digit and not a dot then assume a DNS name
    if(!isdigit(ws->m_deviceAddress[i]) && !(ws->m_deviceAddress[i] == '.'))
      bOnlyDigitsAndDots = false;
  }

  // if only digits and dots were found then assume that it's a static IP address
  if(bOnlyDigitsAndDots && dotCount == 3)
  {
    struct in_addr ipAddr;
    inet_aton(ws->m_deviceAddress,&ipAddr);
    return ipAddr.s_addr;
  }

  // assume that it's DNS name
  return GetIPFromDNS(ws);
}

//------------------------------------------------------------------------------------------
// initialize the socket (doesn't require remote device to be connected or responding)
bool openSocket(struct vicpdevice * ws)
{
  if (DEBUG) fprintf(stdout,"Opening Socket:\n");

  // create client's socket
  ws->m_socketFd = socket(AF_INET, SOCK_STREAM, 0);
  if (ws->m_socketFd < 0)
  {
    int errsv = errno;
    sprintf(ws->m_lastErrorMsg, "socket() failed, error code = %d; ", errsv);
    ws->m_bErrorFlag = true;
    return(false);
  }

  // disable the TCP/IP 'NAGLE' algorithm that buffers a bunch of
  // packets before sending them.
  const int just_say_no = 1;
  if (0 != setsockopt(ws->m_socketFd, IPPROTO_TCP, TCP_NODELAY, (char*)&just_say_no, sizeof(just_say_no)))
  {
    fprintf(stderr,"Could not set socket option 'TCP_NODELAY'");
    return(false);
  }

  // enable SO_LINGER to allow hard closure of sockets (LINGER enabled, but with timeout of zero)
  struct linger lingerStruct = { 1, 0 };
  if (0 != setsockopt(ws->m_socketFd, SOL_SOCKET, SO_LINGER, (char *) &lingerStruct, sizeof(lingerStruct)))
  {
    fprintf(stderr,"Could not set socket option 'SO_LINGER'");
    return(false);
  }

  return(true);
}

//------------------------------------------------------------------------------------------
// disconnect from a network device
bool disconnectFromDevice(struct vicpdevice * ws)
{
  if (DEBUG) fprintf(stdout,"Disconnecting:\n");

  if(ws->m_connectedToScope)
  {
    ws->m_readState = NetWaitingForHeader;    // reset any partial read operation
    if(close(ws->m_socketFd) != 0)
    {
      int errsv = errno;
      sprintf(ws->m_lastErrorMsg, "close() failed, error code = %d; ", errsv);
      ws->m_bErrorFlag = true;
    }
    ws->m_socketFd = -1;
    ws->m_connectedToScope = false;
    ws->m_bVICPVersion1aSupported = false;
  }

  return(true);
}

//------------------------------------------------------------------------------------------
// connect to a network device
// address is extracted from ws->m_deviceAddress (specified during construction of base class)
bool connectToDevice(struct vicpdevice * ws)
{
  // if not yet connected to scope...
  if(!ws->m_connectedToScope)
  {
    if (DEBUG) fprintf(stdout,"Connecting:\n");

    // lookup the IP address of the device
    uint32_t addr = GetDeviceIPAddress(ws);

    // initialize the socket
    openSocket(ws);

    // ensure that the connect command will not block
    fcntl(ws->m_socketFd, F_SETFL, fcntl(ws->m_socketFd, F_GETFL, 0) | O_NONBLOCK);

    // try to connect to server (scope)
    int sockAddrSize = sizeof (struct sockaddr); // size of socket address structures

    // build server socket address
    ws->m_serverAddr.sin_family = AF_INET;
    ws->m_serverAddr.sin_port = htons (SERVER_PORT_NUM);
    if ((ws->m_serverAddr.sin_addr.s_addr = addr) == -1)
    {
      sprintf(ws->m_lastErrorMsg, "Bad server address; ");
      ws->m_bErrorFlag = true;
      ws->m_ibsta = ERR;
      ws->m_iberr = EARG;    // Invalid argument to function call
      ws->m_ibcntl = 0;
      return(false);
    }

    connect(ws->m_socketFd, (struct sockaddr *) &ws->m_serverAddr, sockAddrSize);

    // after a connect in non-blocking mode a 'select' is require to
    // determine the outcome of the connect attempt
    fd_set writeSet;
    FD_ZERO(&writeSet);
    FD_SET(ws->m_socketFd,&writeSet);
    struct timeval timeout = { CONNECT_TIMEOUT_SECS, 0L };
    int numReady = select(ws->m_socketFd+1, NULL, &writeSet, NULL, &timeout);

    // restore blocking behaviour
    fcntl(ws->m_socketFd, F_SETFL, fcntl(ws->m_socketFd, F_GETFL, 0) & ~O_NONBLOCK);

    // see if the connection succeeded
    if(numReady == 1)
    {
      if (DEBUG) fprintf(stdout,"Connect Succeeded\n");
      ws->m_connectedToScope = true;
    }
    else
    {
      int errsv = errno;
      sprintf(ws->m_lastErrorMsg, "socket() failed, error code = %d; ", errsv);
      ws->m_bErrorFlag = true;
      disconnectFromDevice(ws);
      ws->m_ibsta = ERR;
      ws->m_iberr = EABO;    // I/O operation aborted
      ws->m_ibcntl = 0;
      return(false);
    }
  }

  return(true);
}

//------------------------------------------------------------------------------------------
// Return the next sequence number in the range 1..255 (Note that zero is omitted intentionally)
// used to synchronize write/read operations, attempting to emulate the 488.2 'discard unread response'
// behaviour
unsigned char GetNextSequenceNumber(struct vicpdevice * ws, unsigned char flags)
{
  // we'll return the current sequence number
  ws->m_lastSequenceNumber = ws->m_nextSequenceNumber;

  // which then gets incremented if this block is EOI terminated
  if(flags & OPERATION_EOI)
  {
    ++ws->m_nextSequenceNumber;
    if(ws->m_nextSequenceNumber >= 256)
      ws->m_nextSequenceNumber = 1;
  }

  return ws->m_lastSequenceNumber;
}

//------------------------------------------------------------------------------------------
// send a 'small' block of data to a network device
// returns true on error status
bool sendSmallDataToDevice(struct vicpdevice * ws, const char *message, uint32_t bytesToSend, bool eoiTermination, bool deviceClear, bool serialPoll)
{
  static unsigned char smallDataBuffer[SMALL_DATA_BUFSIZE + IO_NET_HEADER_SIZE + 2];
  uint32_t bytesSent;
  uint32_t bytesToSendWithHeader = bytesToSend + IO_NET_HEADER_SIZE;

  // copy message into data buffer
  memcpy(&smallDataBuffer[IO_NET_HEADER_SIZE], message, bytesToSend);

  // clear status words
  ws->m_bErrorFlag = false;
  ws->m_ibsta &= (RQS);  // preserve SRQ
  ws->m_ibcntl = 0;
  ws->m_iberr = 0;

  // send header + data
  smallDataBuffer[0] = OPERATION_DATA;
  if(eoiTermination)
    smallDataBuffer[0] |= OPERATION_EOI;
  if(ws->m_remoteMode)
    smallDataBuffer[0] |= OPERATION_REMOTE;
  if(deviceClear)
    smallDataBuffer[0] |= OPERATION_CLEAR;
  if(serialPoll)
    smallDataBuffer[0] |= OPERATION_REQSERIALPOLL;
  smallDataBuffer[1] = HEADER_VERSION1;
  smallDataBuffer[2] = GetNextSequenceNumber(ws, smallDataBuffer[0]);    // sequence number
  smallDataBuffer[3] = 0x00;                      // unused
  *((uint32_t *) &smallDataBuffer[4]) = htonl(bytesToSend);    // message size

  if (DEBUG) fprintf(stdout,"sendSmallDataToDevice: seq=%d eoi=%d ", smallDataBuffer[2], eoiTermination);

  bytesSent = send(ws->m_socketFd, (char *) smallDataBuffer, bytesToSendWithHeader, 0);
  if (bytesSent != bytesToSendWithHeader)
  {
    sprintf(ws->m_lastErrorMsg, "Could not send small data block (Header + Data); ");
    ws->m_bErrorFlag = true;
    ws->m_ibsta |= ERR;
    if (DEBUG) fprintf(stdout," bytesSent=%d [%.20s] ERROR\n", bytesSent, message);
    return(false);
  }
  else
  {
    if (DEBUG) fprintf(stdout," bytesSent=%d [%.20s]\n", bytesSent, message);
    ws->m_ibsta = CMPL | CIC | TACS;
    ws->m_ibcntl = bytesToSend;
    return(true);
  }
}

//------------------------------------------------------------------------------------------
// return the last-used sequence number without incrementing it
unsigned char GetLastSequenceNumber(struct vicpdevice * ws)
{
  return ws->m_lastSequenceNumber;
}

//------------------------------------------------------------------------------------------
// dump data until the next header is found
// TODO: Handle timeout cases
void dumpData(struct vicpdevice * ws, int numBytes)
{
  sprintf(ws->m_lastErrorMsg, "dumpData: Unread Response, dumping %d bytes; ", numBytes);
  if (DEBUG) fprintf(stdout,"%s\n",ws->m_lastErrorMsg);

  uint32_t bytesToGo = numBytes;
  char *dumpBuf = (char *) malloc(ws->m_maxBlockSize);
  if(dumpBuf != NULL)
  {
    while(bytesToGo > 0)
    {
      int dumpBytesReceived = (uint32_t)recv(ws->m_socketFd, dumpBuf, min(bytesToGo, (uint32_t)ws->m_maxBlockSize), 0);
      bytesToGo -= dumpBytesReceived;
    }
    free(dumpBuf);
  }
}

//------------------------------------------------------------------------------------------
// read header a network device
bool readHeaderFromDevice(struct vicpdevice * ws, uint32_t *blockSize, bool *eoiTerminated, bool *srqStateChanged, int *seqNum)
{
  static unsigned char headerBuf[IO_NET_HEADER_SIZE];
  fd_set readSet;
  FD_ZERO(&readSet);
  FD_SET(ws->m_socketFd,&readSet);
  struct timeval timeout = { (long) ws->m_currentTimeout, ((long) (ws->m_currentTimeout * 1000000L)) % 1000000L};

  // if there is no sign of a header, get out quick (timeout)
  int numReady = select(ws->m_socketFd+1, &readSet, NULL, NULL, &timeout);
  if(numReady != 1)
    return(false);

  // wait until 8 bytes are available (the entire header)
  int headerBytesRead = 0, bytesThisTime;
  while(headerBytesRead < 8)
  {
    // ensure that the recv command will not block
    int numReady = select(ws->m_socketFd+1, &readSet, NULL, NULL, &timeout);
    if(numReady != 1)
      break;

    // try to read the remainder of the header
    bytesThisTime = recv(ws->m_socketFd, (char *) headerBuf + headerBytesRead, IO_NET_HEADER_SIZE - headerBytesRead, 0);
    if(bytesThisTime > 0)
      headerBytesRead += bytesThisTime;

    // if we get this far without reading any part of the header, get out
    if(headerBytesRead == 0)
      break;
  }

  // receive the scope's response, header first
  if(headerBytesRead == 8)
  {
    // extract the number of bytes contained in this packet
    *blockSize = ntohl(*((unsigned long *) &headerBuf[4]));

    // check the integrity of the header
    if(!((headerBuf[0] & OPERATION_DATA) && (headerBuf[1] == HEADER_VERSION1)))
    {
      sprintf(ws->m_lastErrorMsg, "Invalid Header!; ");
      ws->m_bErrorFlag = true;

      // error state, cannot recognise header. since we are
      // out of sync, need to close & reopen the socket
      disconnectFromDevice(ws);
      connectToDevice(ws);
      return(false);
    }

    // inform the caller of the EOI and SRQ state
    if(headerBuf[0] & OPERATION_EOI)
      *eoiTerminated = true;
    else
      *eoiTerminated = false;

    if(headerBuf[0] & OPERATION_SRQ)
      *srqStateChanged = true;
    else
      *srqStateChanged = false;

    // inform the caller of the received sequence number
    *seqNum = headerBuf[2];

    if (DEBUG) fprintf(stdout,"readHeaderFromDevice: seq=%d\n", headerBuf[2]);
  }
  else
  {
    // error state, cannot read header. since we are out of sync,
    // need to close & reopen the socket
    disconnectFromDevice(ws);
    connectToDevice(ws);
    return(false);
  }

  return(true);
}

//------------------------------------------------------------------------------------------
// read block of data from a network device
// if bFlush is requested then ignore replyBuf and userBufferSizeBytes and read all remaining data
// from the current block (i.e. up to the start of the next header)
uint32_t readDataFromDevice(struct vicpdevice * ws, char *replyBuf, int userBufferSizeBytes, bool bFlush)
{
  static uint32_t srcBlockSizeBytes = 0, srcBlockBytesRead = 0;
  static bool srcBlockEOITerminated = false, srcBlockSRQStateChanged = false;
  int userBufferBytesRead = 0;          // # bytes placed in user buffer
  uint32_t bytesReceived = 0;
  char *bufCopy = replyBuf;

  // clear status words
  ws->m_bErrorFlag = false;
  ws->m_ibsta &= (RQS);  // preserve SRQ
  ws->m_ibcntl = 0;
  ws->m_iberr = 0;

  // ensure that the reply buffer is empty (if supplied)
  if(replyBuf != NULL)
    *replyBuf = '\0';

  while(1)
  {
    if(ws->m_readState == NetWaitingForHeader)
    {
      int seqNum = -1;
      if(readHeaderFromDevice(ws, &srcBlockSizeBytes, &srcBlockEOITerminated, &srcBlockSRQStateChanged, &seqNum))
      {
        // header was successfully read
        if (DEBUG) fprintf(stdout,"readDataFromDevice: Read Header: blockSize=%d, EOI=%d, userBufferSizeBytes=%d\n", srcBlockSizeBytes, srcBlockEOITerminated, userBufferSizeBytes);
        ws->m_readState = NetWaitingForData;
        srcBlockBytesRead = 0;

        // if we're flushing unread responses, and this header contains an unexpected sequence number (older than
        // the current one), then dump this block and go around again.
        // note that the 'seqNum != 0' test checks for the case where we're talking to a scope running pre-June 2003
        // code that didn't support sequence numbering, and therefore we don't know when to dump data.
        if(ws->m_bFlushUnreadResponses && seqNum != 0 && (GetLastSequenceNumber(ws) > seqNum) && !srcBlockSRQStateChanged)
        {
          printf("dumping data with seqNum: %d. LastSeqNum: %d\n",seqNum,GetLastSequenceNumber(ws));
          dumpData(ws, srcBlockSizeBytes);
          ws->m_readState = NetWaitingForHeader;
        }

        // if a non-zero sequence number was seen then assume that version '1a' of the
        // VICP protocol is in use, supporting, in addition to sequence numbering,
        // the use of Out-of-band signalling.
        if(seqNum != 0)
          ws->m_bVICPVersion1aSupported = true;
        else
          ws->m_bVICPVersion1aSupported = false;    // seq. numbers should never be zero in V1a of the protocol
      }
      else
      {
        // header was not successfully read, probably indicates a timeout
        if (DEBUG) fprintf(stdout,"readDataFromDevice Timeout reading header\n");

        // let the caller know that a timeout occured
        ws->m_ibsta |= ERR;
        ws->m_ibsta |= TIMO;
        break;
      }
    }

    if(ws->m_readState == NetWaitingForData)
    {
      // dump any unread partial buffer if requested
      if(bFlush)
      {
        dumpData(ws, srcBlockSizeBytes - srcBlockBytesRead);
        ws->m_readState = NetWaitingForHeader;
        break;
      }

      // fill the user-supplied buffer
      uint32_t bytesToGo = min((uint32_t)userBufferSizeBytes - userBufferBytesRead,  // space free in user Buffer
                srcBlockSizeBytes - srcBlockBytesRead);         // src bytes available
      while(bytesToGo > 0)
      {
        bytesReceived = (uint32_t)recv(ws->m_socketFd, replyBuf, min(bytesToGo, (uint32_t)ws->m_maxBlockSize), 0);

        if(bytesReceived <= 0)
        {
          sprintf(ws->m_lastErrorMsg, "error on recv; ");
          ws->m_bErrorFlag = true;
          ws->m_readState = NetErrorState;

          // let the caller know that a timeout occured
          ws->m_ibsta |= ERR;
          ws->m_ibsta |= TIMO;
          break;
        }

        if(bytesReceived > 0)
        {
          userBufferBytesRead += bytesReceived;
          bytesToGo -= bytesReceived;
          replyBuf += bytesReceived;
          srcBlockBytesRead += bytesReceived;
        }
      }

      // if we have finished reading the contents of this header-prefixed block,
      // then go back to the state where we can watch for the next block
      if(srcBlockBytesRead >= srcBlockSizeBytes)
      {
        ws->m_readState = NetWaitingForHeader;

        if (srcBlockSRQStateChanged)  // update SRQ status bits, discard SRQ packet
        {
          if (bufCopy[0] == '1')    // 1 = SRQ asserted, 0 = SRQ deasserted
            ws->m_ibsta |= RQS;
          else {
            ws->m_ibsta &= ~(RQS);    // clear SRQ

            // discard SRQ data in buffer
            userBufferBytesRead -= bytesReceived;
            replyBuf -= bytesReceived;
            srcBlockBytesRead -= bytesReceived;

            if (DEBUG) fprintf(stdout,"SRQ Packet Discarded  '%c'\n", bufCopy[0]);
            continue;          // go around the loop again (discard SRQ packet)
          }
        }

        // go around the loop again unless the last block was EOI terminated
        if(srcBlockEOITerminated)
        {
          ws->m_ibsta |= END;
          break;
        }
      }

      // if there is space left in the user's buffer, go around again
      if(userBufferBytesRead >= userBufferSizeBytes)
        break;
    }

    if(ws->m_readState == NetErrorState)
    {
      // when we come back in here, enter the 'waiting for header' state
      ws->m_readState = NetWaitingForHeader;
      break;
    }

  }

  // keep track of size of last transfer
  ws->m_ibcntl = userBufferBytesRead;

  if (DEBUG) fprintf(stdout,"readDataFromDevice: returning %d bytes\n", userBufferBytesRead);

  return(ws->m_ibcntl);
}

//------------------------------------------------------------------------------------------
// send a block of data to a network device
// returns false on error status
bool sendDataToDevice(struct vicpdevice * ws, const char *message, int bytesToSend, bool eoiTermination, bool deviceClear, bool serialPoll)
{
  static unsigned char headerBuf[IO_NET_HEADER_SIZE];
  int bytesSent;

  // handle cases where the user didn't read all data from a previous query
  if(ws->m_bFlushUnreadResponses && (ws->m_readState != NetWaitingForHeader))
    readDataFromDevice(ws, NULL, -1, true);    // flush

  // if the block is relatively small, send header + data with one 'send' command (faster)
  if(bytesToSend < SMALL_DATA_BUFSIZE)
    return(sendSmallDataToDevice(ws, message, bytesToSend, eoiTermination, deviceClear, serialPoll));

  // clear status words
  ws->m_bErrorFlag = false;
  ws->m_ibsta &= (RQS);  // preserve SRQ
  ws->m_ibcntl = 0;
  ws->m_iberr = 0;

  // send header
  headerBuf[0] = OPERATION_DATA;
  if(eoiTermination)
    headerBuf[0] |= OPERATION_EOI;
  if(ws->m_remoteMode)
    headerBuf[0] |= OPERATION_REMOTE;
  if(deviceClear)
    headerBuf[0] |= OPERATION_CLEAR;
  if(serialPoll)
    headerBuf[0] |= OPERATION_REQSERIALPOLL;
  headerBuf[1] = HEADER_VERSION1;
  headerBuf[2] = GetNextSequenceNumber(ws, headerBuf[0]);      // sequence number
  headerBuf[3] = 0x00;                    // unused
  *((unsigned long *) &headerBuf[4]) = htonl(bytesToSend);  // message size

  if (DEBUG) fprintf(stdout,"sendDataToDevice: seq=%d eoi=%d ", headerBuf[2], eoiTermination);

  bytesSent = send(ws->m_socketFd, (char *) headerBuf, IO_NET_HEADER_SIZE, 0);
  if (bytesSent != IO_NET_HEADER_SIZE)
  {
    sprintf(ws->m_lastErrorMsg, "Could not send Net Header; ");
    ws->m_bErrorFlag = true;
    ws->m_ibsta |= ERR;
    if (DEBUG) fprintf(stdout," bytesSent=%d [%.20s] ERROR sending header\n", bytesSent, message);
    return(false);
  }

  // send contents of message
  bytesSent = send(ws->m_socketFd, message, bytesToSend, 0);
  if(bytesSent < 0 || bytesSent != bytesToSend)
  {
    sprintf(ws->m_lastErrorMsg, "Send error; ");
    ws->m_bErrorFlag = true;
    ws->m_ibsta |= ERR;
    if (DEBUG) fprintf(stdout," bytesSent=%d [%.20s] ERROR sending data\n", bytesSent, message);
    return(false);
  }
  else
  {
    if (DEBUG) fprintf(stdout," bytesSent=%d [%.20s]\n", bytesSent, message);
    ws->m_ibsta = CMPL | CIC | TACS;
    ws->m_ibcntl = bytesSent;
  }

  return(true);
}

//------------------------------------------------------------------------------------------
// clear the device
void deviceClear(struct vicpdevice * ws)
{
  sendDataToDevice(ws, "", 0, 0, true /* device clear */, false);
  sleep(100);            // TODO: remove when 'RebootScope' bug is fixed
  disconnectFromDevice(ws);
  connectToDevice(ws);
}

//------------------------------------------------------------------------------------------
// out-of band data request, used for serial polling and possibly other features in the future
bool oobDataRequest(struct vicpdevice * ws, char requestType, unsigned char *response)
{
  char oobDataTest[1] = { requestType };
  send(ws->m_socketFd, (char *) oobDataTest, 1, MSG_OOB);

  struct timeval timeout = { (long) ws->m_currentTimeout, ((long) (ws->m_currentTimeout * 1000000L)) % 1000000L};

  // Note that we don't look for in-band data, only OOB data (which appears in the exception record)
  fd_set exceptSet;
  FD_ZERO(&exceptSet);
  FD_SET(ws->m_socketFd,&exceptSet);
  select(ws->m_socketFd+1, NULL, NULL, &exceptSet, &timeout);
  char buf[1] = { 0x00 };
  if(FD_ISSET(ws->m_socketFd, &exceptSet))
  {
    recv(ws->m_socketFd, (char *) buf, 1, MSG_OOB);
    *response = buf[0];
    return true;
  }
  else
  {
    return false;
  }
}

//------------------------------------------------------------------------------------------
// return the serial poll byte. Uses the new Out-Of-Band signalling technique if
// supported, else use the original 'in-band' technique.
int serialPoll(struct vicpdevice * ws)
{
  // clear status words
  ws->m_bErrorFlag = false;
  ws->m_ibsta &= (RQS);  // preserve SRQ
  ws->m_ibcntl = 0;
  ws->m_iberr = 0;

/* Commenting OOB serialPoll because it does not work as desired
  if(ws->m_bVICPVersion1aSupported)
  {
    unsigned char oobResponse = 0x00;
    if(oobDataRequest(ws, 'S', &oobResponse))    // 'S' == Serial Poll
    {
      return oobResponse;
    }
    else
    {
      ws->m_ibsta = ERR;
      ws->m_iberr = EABO;        // The serial poll response could not be read within the serial poll timeout period.
      sprintf(ws->m_lastErrorMsg, "serialPoll failed to receive OOB response from DSO; ");
      ws->m_bErrorFlag = true;
      return oobResponse;
    }
  }
  else
  {*/
    // request the serial poll using an in-band technique
//    sendDataToDevice(ws, "", 0, false /* EOI */, false /* device clear */, true /* request serial poll */);

    // read the single serial-poll byte
    #define SPOLLBUFSIZE   2
    char buf[SPOLLBUFSIZE+1];
    int bytesRead = -1;
    bytesRead = readDataFromDevice(ws, buf, SPOLLBUFSIZE, false);
    if(bytesRead >= 1)
    {
      ws->m_ibsta = CMPL;
      return buf[0];
    }
    else
    {
      ws->m_ibsta = ERR;
      ws->m_iberr = EABO;      // The serial poll response could not be read within the serial poll timeout period.
      sprintf(ws->m_lastErrorMsg, "serialPoll failed to receive SRQ response from DSO; ");
      ws->m_bErrorFlag = true;
      return 0;
    }
//  }
}

