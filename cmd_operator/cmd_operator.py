#!/usr/bin/python2

import time,sys,os
import base64
import notify2

if __name__=='__main__':
    import gtk
    notify2.init("Pyrame_operator","glib")

entry=0
win=0
answer=""

def on_button_clicked(widget):
    global entry,answer,win
    answer = entry.get_text()
    win.hide()
    gtk.main_quit()

def on_ok_button_clicked(widget):
    global entry,win
    win.hide()
    gtk.main_quit()

def callback(notification=None,action=None,data=None):
    global entry,answer,win
    
    #main window
    win = gtk.Window()
    win.set_title("Pyrame Operator Request")

    #box
    box = gtk.VBox(False,0)
    win.add(box)

    #label
    label = gtk.Label()
    label.set_label(data[1])
    box.pack_start(label,True,True,0)

    if data[2]!="noimage":
        print("printing the image %s"%(data[2]))
        img=gtk.Image()
        img.set_from_file(data[2])
        box.pack_start(img,True,True,0)

    if data[0]=="question":
        #entrytext
        entry=gtk.Entry(max=0)
        box.pack_start(entry,True,True,0)
        entry.connect("activate",on_button_clicked)

        #button
        button = gtk.Button(label="Send Answer")
        button.connect("clicked",on_button_clicked)
        box.pack_start(button,True,True,0)
    else:
        #button
        button = gtk.Button(label="OK")
        button.connect("clicked",on_ok_button_clicked)
        box.pack_start(button,True,True,0)

    #show all the widgets
    win.show_all()

def notify_operator(message):
    notice = notify2.Notification("Pyrame Operator Information",message)
    notice.set_timeout(notify2.EXPIRES_NEVER)
    notice.show()
    submod.setres(1,"ok")

def notify_ok_operator(message):
    notice = notify2.Notification("Pyrame Operator Information","","dialog-warning")
    notice.set_urgency(notify2.URGENCY_CRITICAL)
    notice.set_timeout(notify2.EXPIRES_NEVER)
    notice.add_action ("actions","Please click here!",callback,["OK",message,"noimage"])
    notice.show()
    gtk.main()
    submod.setres(1,"ok")

def ask_operator(message):
    notice = notify2.Notification("Pyrame Operator Request","","dialog-warning")
    notice.set_urgency(notify2.URGENCY_CRITICAL)
    notice.set_timeout(notify2.EXPIRES_NEVER)
    notice.add_action ("actions","Please click here!",callback,["question",message,"noimage"])
    notice.show()
    gtk.main()
    submod.setres(1,answer)

def ask_wimg_operator(message,image):
    notice = notify2.Notification("Pyrame Operator Request","","dialog-warning")
    notice.set_urgency(notify2.URGENCY_CRITICAL)
    notice.set_timeout(notify2.EXPIRES_NEVER)
    notice.add_action ("actions","Please click here!",callback,["question",message,image])
    notice.show()
    gtk.main()
    submod.setres(1,answer)
