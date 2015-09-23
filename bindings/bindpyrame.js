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

function bindpyrame (ws_host, ws_port) {
  this.host = ws_host;
  this.port = ws_port;

  this.sendcmd = function (receive_handler, data, port, command) {
    if (!("WebSocket" in window)) {
      alert("WebSocket NOT supported by your Browser!");
      return;
    }
    var i;
    var smsg = {};
    smsg["port"] = port.toString();
    smsg["command"] = command;
    params_start = 4;
    for (i=0; i<arguments.length-params_start;i++)
      smsg["param"+(i+1)] = arguments[i+params_start];
    var ws = new WebSocket("ws://"+this.host+":"+this.port+"/pyrame");
    ws.onopen = function() {
      ws.send(JSON.stringify(smsg));
    };
    ws.onmessage = function (evt) {
      var rmsg = JSON.parse(evt.data);
      rmsg.res = (rmsg.res || "").replace(/&/g,'&amp;').replace(/</g,'&lt;');
      receive_handler(rmsg.retcode,rmsg.res,data);
    };
    ws.onclose = function() {
    };
  };
}

