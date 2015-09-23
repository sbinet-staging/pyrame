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

#include "cmdmod.h"
#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#ifndef CMDMOD_LUA_H
#define CMDMOD_LUA_H


struct lua_ws {
  lua_State *L;
};

static int submod_exec_lua(lua_State *L);
static int submod_setres_lua(lua_State *L);

#endif
