=========================
The VICP Python binding
=========================

Python class vicp.device providing binding to libvicp library.

API
===

.. py:class:: vicp.device

  .. py:method:: connect()

    Connect to VICP device on deviceAddress.

    Return True on success

  .. py:method:: disconnect()

    Disconnect from connected VICP device.

    Return True on success

  .. py:method:: read([bFlush=False])
  
    Read device responses. *bFlush* is a boolean parameter asking to flush the socket buffer up to the next VICP header.

    Returns a tuple of 1,response in case of success or 0,error_message in case of failure

  .. py:method:: write(message[, eoiTermination=True, deviceClear=False, serialPoll=False])

    Send *message* to device. The rest of the parameters are boolean and control the respective bits on the VICP packet header. Usually *eoiTermination* will be True and the others False.

    Returns 1 on successful operation, 0 on error.

  .. py:method:: wrnrd(message)

    Send *message* to device and read response.

    Returns a tuple of 1,response in case of success or 0,error_message in case of failure

  .. py:method:: serialPoll()

    Do a serial poll on the device. Usually done after the command "\*CLS; INE 1; \*SRE 1" that instructs the DSO to send SRQ packets whenever the next triggering event is produced. If serialPoll returns '1' (1 as a character), data can be recovered from the DSO.

  .. py:attribute:: deviceAddress

    Compulsory attribute. Needed for connect()

  .. py:attribute:: ErrorFlag

    True if error has been observed. Read-only attribute.

  .. py:attribute:: iberr

    Emulation of GPIB counterpart. See libvicp for documentation. Read-only attribute.

  .. py:attribute:: ibsta

    Emulation of GPIB counterpart. See libvicp for documentation. Read-only attribute.

  .. py:attribute:: ibcntl

    Emulation of GPIB counterpart. See libvicp for documentation. Read-only attribute.

  .. py:attribute:: RemoteMode

    True if device is in remote mode. Read-only attribute.

  .. py:attribute:: LocalLockout

    True if device is in local lockout mode. Read-only attribute.

  .. py:attribute:: LastErrorMsg

    Last error message
