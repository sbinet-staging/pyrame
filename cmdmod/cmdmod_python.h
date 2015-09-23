/*
Copyright 2012-2014 Frédéric Magniette, Miguel Rubio-Roy
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
#include "cmdmod.h"

#ifndef CMDMOD_PYTHON_H
#define CMDMOD_PYTHON_H

struct python_ws {
  int id;
  PyObject *pModule;
};


static PyObject* submod_exec_python(PyObject *self,  PyObject *args);
static PyObject* submod_setres_python(PyObject *self,  PyObject *args);

static  PyMethodDef  submodmethods[]  =  {
    {"execcmd",submod_exec_python,METH_VARARGS,"Sub-module execution"},
    {"setres",submod_setres_python,METH_VARARGS,"Script result setting"},
    {NULL,  NULL,  0,  NULL}
};
#endif
