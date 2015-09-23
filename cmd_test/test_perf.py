#!/usr/bin/python2
# -*- coding: utf-8 -*-
from bindpyrame import *
import time

pt=init_ports_table("/opt/pyrame/ports.txt")
s=open_socket("localhost",get_port("TEST_PORT",pt))

nb=100000
t1=time.time()
for i in range(nb):
    execcmd(s,"void_test")
t2=time.time()
print("elapsed time : %f s/op"%((t2-t1)/nb))
s.close()
