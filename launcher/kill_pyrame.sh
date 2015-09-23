#!/bin/bash
kill `ps -eo pid,cmd | grep autolauncher | grep python2 | awk '{ print $1 }'`
killall cmdmod
killall acq_server
killall raweth_server
