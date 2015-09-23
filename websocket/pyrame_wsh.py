#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# 
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
# This file is part of Pyrame.
# 
# Pyrame is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pyrame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrame.  If not, see <http://www.gnu.org/licenses/>

import bindpyrame
import json

def web_socket_do_extra_handshake(request):
    # This example handler accepts any request. See origin_check_wsh.py for how
    # to reject access from untrusted scripts based on origin value.

    pass  # Always accept.

def web_socket_transfer_data(request):
    received_request = request.ws_stream.receive_message()
    if received_request is None:
        return
    received_request = json.loads(received_request)
    port_string = received_request.pop("port")
    command = received_request.pop("command")
    params = []
    i = 1
    for param in received_request:
        params.append(received_request["param%d"%i])
        i += 1
    try:
        table = bindpyrame.init_ports_table("/opt/pyrame/ports.txt")
        port = bindpyrame.get_port(port_string,table)
        retcode,res=bindpyrame.sendcmd("localhost",port,command,*params)
    except Exception as e:
        retcode = 0
        res = str(e)
    answer = json.dumps({"retcode": retcode, "res": res})
    request.ws_stream.send_message(answer, binary=False)

# vi:sts=4 sw=4 et
