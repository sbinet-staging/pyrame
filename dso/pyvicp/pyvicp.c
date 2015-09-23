/*
Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
This file is part of Pyrame.

Pyrame is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pyrame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Pyrame.  If not, see <http://www.gnu.org/licenses/>
*/

#include <Python.h>
#include "structmember.h"
#include "../libvicp/vicp.h"
#include <stdbool.h>
#include <inttypes.h>

#define PYVICP_BUFFER_SIZE 65536

typedef struct {
  PyObject_HEAD
  PyObject * ws;
} py_ws;

static void py_ws_dealloc(py_ws* self) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  deinitvicpdevice(ws);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject * py_ws_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
  py_ws * self;
  self = (py_ws*) type->tp_alloc(type,0);
  self->ws = (PyObject*) initvicpdevice();
  return (PyObject*) self;
}

//////////////////////////////////////////
// MEMBERS
//////////////////////////////////////////

static PyMemberDef py_ws_members[] = {
  {NULL}
};

//////////////////////////////////////////
// GETTERS AND SETTERS
//////////////////////////////////////////

static PyObject * py_ws_getdeviceAddress(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  if (ws->m_deviceAddress != NULL) 
    return PyString_FromString(ws->m_deviceAddress);
  else return NULL;
}

static int py_ws_setdeviceAddress(py_ws *self, PyObject *value, void *closure) {
  struct vicpdevice * ws;
  if (value == NULL) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete the first attribute");
    return -1;
  }
  if (!PyString_Check(value)) {
    PyErr_SetString(PyExc_TypeError, "The deviceAddress attribute value must be a string");
    return -1;
  }
  ws = (struct vicpdevice *) self->ws;
  strncpy(ws->m_deviceAddress, PyString_AsString(value), MAX_DEVICE_ADDR_LEN);
  return 0;
}

static PyObject * py_ws_getErrorFlag(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyBool_FromLong((long) ws->m_bErrorFlag);
}

static PyObject * py_ws_getiberr(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyInt_FromLong((long) ws->m_iberr);
}

static PyObject * py_ws_getibsta(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyInt_FromLong((long) ws->m_ibsta);
}

static PyObject * py_ws_getibcntl(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyInt_FromLong((long) ws->m_ibcntl);
}

static PyObject * py_ws_getRemoteMode(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyBool_FromLong((long) ws->m_remoteMode);
}

static PyObject * py_ws_getLocalLockout(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyBool_FromLong((long) ws->m_localLockout);
}

static PyObject * py_ws_getLastErrorMsg(py_ws *self, void *closure) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  return PyString_FromString((char*)&ws->m_lastErrorMsg);
}

static PyGetSetDef py_ws_getseters[] = {
  {"deviceAddress",(getter)py_ws_getdeviceAddress,(setter)py_ws_setdeviceAddress,"VICP device address",NULL},
  {"ErrorFlag",(getter)py_ws_getErrorFlag,NULL,"if true, error has been observed",NULL},
  {"iberr",(getter)py_ws_getiberr,NULL,"emulation of GPIB counterpart",NULL},
  {"ibsta",(getter)py_ws_getibsta,NULL,"emulation of GPIB counterpart",NULL},
  {"ibcntl",(getter)py_ws_getibcntl,NULL,"emulation of GPIB counterpart",NULL},
  {"RemoteMode",(getter)py_ws_getRemoteMode,NULL,"if true, device is in remote mode",NULL},
  {"LocalLockout",(getter)py_ws_getLocalLockout,NULL,"if true, device is in local lockout mode",NULL},
  {"LastErrorMsg",(getter)py_ws_getLastErrorMsg,NULL,"Last error message",NULL},
  {NULL}
};

//////////////////////////////////////////
// METHODS
//////////////////////////////////////////

static PyObject * py_ws_connect(py_ws *self, PyObject *args) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  if (ws->m_deviceAddress[0] == 0) {
    PyErr_SetString(PyExc_TypeError, "Set the attribute deviceAddress to the IP or network name of the device before calling connect()");
    return NULL;
  }
  bool res = connectToDevice(ws);
  return PyBool_FromLong((long) res);
}

static PyObject * py_ws_disconnect(py_ws *self, PyObject *args) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  bool res = disconnectFromDevice(ws);
  return PyBool_FromLong((long) res);
}

static PyObject * py_ws_read(py_ws *self, PyObject *args) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  PyObject * bFlush = NULL;
  char * finalResponse = malloc(PYVICP_BUFFER_SIZE+1);
  if (finalResponse == NULL) return NULL;
  memset(finalResponse, 0, PYVICP_BUFFER_SIZE+1);
  char replyBuf [PYVICP_BUFFER_SIZE];
  uint32_t count = 0;
  if (!PyArg_ParseTuple(args, "|O", &bFlush))
    return NULL;
  if (bFlush == NULL) bFlush = PyInt_FromLong((long)false);
  while (1) {
    memset(replyBuf, 0, sizeof(replyBuf));
    uint32_t bytesRead = readDataFromDevice(ws, replyBuf, PYVICP_BUFFER_SIZE, (bool) PyObject_IsTrue(bFlush));
    memcpy(finalResponse+count,replyBuf,bytesRead);
    count += bytesRead;
    if (ws->m_readState != NetWaitingForData) break;
    else finalResponse = realloc(finalResponse,count+PYVICP_BUFFER_SIZE+1);
  }
  if ((ws->m_ibsta >> 14) % 2 || (ws->m_ibsta >> 15) % 2) {
    char result[MAX_ERROR_MSG_LEN+26+1];
    memset(result,0,sizeof(result));
    strcpy(result,"Error reading or timeout: ");
    strncat(result,ws->m_lastErrorMsg,MAX_ERROR_MSG_LEN);
    return Py_BuildValue("is#", 0, result, strlen(result));
  } else return Py_BuildValue("is#", 1, finalResponse, count);
}

static PyObject * py_ws_write(py_ws *self, PyObject *args, PyObject *keywds) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  char * message;
  PyObject * eoiTermination = NULL;
  PyObject * deviceClear = NULL;
  static char *kwlist[] = {"message", "eoiTermination", "deviceClear", NULL};
  if (!PyArg_ParseTupleAndKeywords(args,keywds,"s|OO",kwlist,&message,&eoiTermination,&deviceClear))
    return NULL;
  if (message == NULL)
    return NULL;
  if (eoiTermination == NULL) eoiTermination = PyInt_FromLong((long)true);
  if (deviceClear    == NULL) deviceClear    = PyInt_FromLong((long)false);
  bool res = sendDataToDevice(ws, message, (uint32_t) strlen(message), (bool) PyObject_IsTrue(eoiTermination), (bool) PyObject_IsTrue(deviceClear), false);
  return PyInt_FromLong((long) res);
}

static PyObject * py_ws_wrnrd(py_ws *self, PyObject *args, PyObject *keywds) {
  PyObject * result;
  result = py_ws_write(self, args, keywds);
  if (PyObject_IsTrue(result)) {
    result = py_ws_read(self, PyTuple_Pack(1,PyInt_FromLong((long)0)));
    return result;
  } else return Py_BuildValue("is#", 0, "", 0);
}

static PyObject * py_ws_serialPoll(py_ws *self, PyObject *args) {
  struct vicpdevice * ws = (struct vicpdevice *) self->ws;
  int res = serialPoll(ws);
  int retcode = 0 ? ws->m_bErrorFlag : 1;
  return PyTuple_Pack(2,PyInt_FromLong((long)retcode), PyString_FromString((char*) &res));
}

static PyMethodDef py_ws_methods[] = {
  {"connect", (PyCFunction)py_ws_connect, METH_NOARGS, "Connect to VICP device on deviceAddress."},
  {"disconnect", (PyCFunction)py_ws_disconnect, METH_NOARGS, "Disconnect from connected VICP device."},
  {"read", (PyCFunction)py_ws_read, METH_VARARGS, "Read device responses."},
  {"write", (PyCFunction)py_ws_write, METH_VARARGS | METH_KEYWORDS, "Send command to device."},
  {"wrnrd", (PyCFunction)py_ws_wrnrd, METH_VARARGS | METH_KEYWORDS, "Send command to device and read response."},
  {"serialPoll", (PyCFunction)py_ws_serialPoll, METH_NOARGS, "Do a serial poll on the device."},
  {NULL}
};

//////////////////////////////////////////
// TYPE
//////////////////////////////////////////

static PyTypeObject py_wstype = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "vicp.device",             /*tp_name*/
  sizeof(py_ws),        /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)py_ws_dealloc, /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
  "VICP device",             /* tp_doc */
  0,                         /* tp_traverse */
  0,                         /* tp_clear */
  0,                         /* tp_richcompare */
  0,                         /* tp_weaklistoffset */
  0,                         /* tp_iter */
  0,                         /* tp_iternext */
  py_ws_methods,        /* tp_methods */
  py_ws_members,        /* tp_members */
  py_ws_getseters,      /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  0,                         /* tp_init */
  0,                         /* tp_alloc */
  py_ws_new             /* tp_new */
};

//////////////////////////////////////////
// MODULE
//////////////////////////////////////////

static PyMethodDef vicp_methods[] = {
  {NULL}
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC initvicp(void) {
  PyObject * m;
  if (PyType_Ready(&py_wstype) < 0 )
    return;
  m = Py_InitModule3("vicp",vicp_methods,"Python binding to libvicp");
  if (m == NULL)
    return;
  Py_INCREF(&py_wstype);
  PyModule_AddObject(m, "device", (PyObject*)&py_wstype);
}
