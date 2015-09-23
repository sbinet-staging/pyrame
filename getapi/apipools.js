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

function api_pool () {
  this.pool = [];

  this.add_api_from_string = function (module_name,str_api) {
    api_list = (str_api || "").replace(/^(\n;)+|(\n;)+$/g,"").split(";")
    for (var i=0;i<api_list.length;i++) {
      var f = api_list[i].split(":");
      if (!f[1]) f[1] = [];
      else f[1] = f[1].split(",")
      this.pool.push({model:module_name,func:f[0],args:f[1]});
    }
  }
      
  this.get_api = function (module_name,func_name) {
    for (var i=0;i<this.pool.length;i++) {
      var api = this.pool[i];
      if ((api.model==module_name) && (api.func==func_name))
        return api;
    }
    return -1;
  }

  this.is_present = function (module_name) {
    for (var i=0;i<this.pool.length;i++) {
      var api = this.pool[i];
      if (api.model==module_name) {
        console.log(module_name + " present");
        return true;
      }
    }
    console.log(module_name + " not present");
    return false;
  }
}
