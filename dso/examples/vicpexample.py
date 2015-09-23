import vicp
import sys
x = vicp.device()
x.deviceAddress = "10.220.0.140"
x.connect()
x.send("*CLS ; INE 1 ; *SRE 1",True,False,False)
count = 0
while x.serialPoll():
    x.send("C1:WF?",True,False,False)
    bytesRead,replyBuf = x.read(False)
    count += bytesRead
    i = 0
    for i in range(bytesRead):
        if not (i % 16): print("{0: >6d} -> {1: >6d}:  ".format(i,i+16)),
        if ord(replyBuf[i])<32 or ord(replyBuf[i])>127:
            print("{0:2x}".format(ord(replyBuf[i]))),
        else:
            print("{0: >2s}".format(replyBuf[i])),
        i += 1
        if not (i % 16): print(" ")
    print(" ")
    x.send("*CLS ; INE 1 ; *SRE 1",True,False,False)

x.disconnect()

