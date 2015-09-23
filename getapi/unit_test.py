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

import apipools
import sys

test=apipools.api_pool()
test.add_api_from_file("cmd_ps","/opt/pyrame/cmd_ps.api")
api=test.get_api("cmd_ps","get_voltage_ps")
pattern="{'function': 'get_voltage_ps', 'model': 'cmd_ps', 'args': ['ps_id', 'channel'], 'id': 10}"
if str(api)==pattern:
    sys.exit(0)
else:
    print("%s\n    not equal to \n%s"%(str(api),pattern))
    sys.exit(1)
