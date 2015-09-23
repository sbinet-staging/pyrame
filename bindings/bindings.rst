========
Bindings
========

This document describes how to create a program interracting with Pyrame modules.

The Pyrame binding API
======================

In order to make Pyrame easilly interracting with other programs, we provide binding for numerous languages. These bindings are very 5 simple functions that implements the Pyrame protocol :

- open_socket(host,port)
- init_ports_table(filename)
- get_port(name,table)
- execcmd(sock,name,*args)
- sendcmd(host,port,name,*args)

open_socket
-----------

The *open_socket* just open a TCP socket that is usable with Pyrame. 
It takes two arguments :

- the host : the IP address or the DNS name of the machine where the module you need is running.
- the port : the TCP port on which the module is listening

It returns the socket

init_ports_table
----------------

The *init_ports_table* loads a table of port in memory.
It takes the file name as an argument.
It return the table.

get_port
--------

The *get_port* search a port number in a port table.
It takes two arguments : 

- the name of the port as a string
- the ports table (as returned by *init_ports_table*)

it returns the number of the port

execcmd
-------

The *execcmd* execute a Pyrame command on a module through a given socket.
It takes a variable number of arguments : 

- a socket (as returned by the *open_socket* function)
- the name of the function we want to execute on the module
- a variable number of arguments depending on the function

it returns the boolean return value and the return string value of the command

sendcmd
-------

The *sendcmd* function is very similar to the *execcmd* function. The difference is that it opens the socket itself.
It takes a variable number of arguments : 

- the host : the IP address or the DNS name of the machine where the module you need is running.
- the port : the TCP port on which the module is listening
- the name of the function we want to execute on the module
- a variable number of arguments depending on the function

it returns the boolean return value and the return string value of the command

The advantage of *execcmd* is the conservation of the socket wich reduce the system time necessary to open it at every command. 


An example in Python
====================

In this example, we open a port table, get the port of our module and send it a helloworld_test command.

Here is the code ::

  #!/usr/bin/env python2   
  import bindpyrame
  import socket
  import sys

  #open a port table and find the test port
  try:
    table = bindpyrame.init_ports_table("/opt/pyrame/ports.txt")
    port = bindpyrame.get_port("TEST_PORT",table)
  except Exception as e:
    print e
    sys.exit(1)
  
  #open a socket and send the command
  try:
    sockid = bindpyrame.open_socket("localhost",port)
    retcode,res=bindpyrame.execcmd(sockid,"helloworld_test","")
  except Exception as e:
    print e
    sys.exit(1)

  #print the result
  print("execcmd: retcode=%d res=%s"%(retcode,res))

The execcmd section can be replaced by its sendcmd equivalent ::

  try:
    retcode,res=bindpyrame.sendcmd("localhost",port,"helloworld_test","")
  except Exception as e:
    print e
    sys.exit(1)

The example in C
----------------

Here is the equivalent code in C::

  #include <bindpyrame.h>
  int main() {
    struct cmd_result result;
    struct ports_table table;
    int port;

    //open a port table and find the test port
    table = init_ports_table("/opt/pyrame/ports.txt");
    port = get_port("TEST_PORT",table);
    free_ports_table(table);

    //open a socket and send the command
    result = sendcmd("localhost",port,"helloworld_test","","end");

    //print the result
    printf("sendcmd: retcode=%d res=%s\n",result.retcode,result.str);
    free(result.str);

Take care to the "end" parameter in sendcmd and execcmd that mark the end of the variable number of parameters. Its lacks can produce segmentation faults.
To be compact, this code has been written without any check but they should be implemented in a real application.

The example in C++
------------------

Here is the equivalent code in C++::

  #include <bindpyrame++.hpp>
  int main() {
    bindpyrame pyrame;
    bindpyrame::cmd_result result;
    int port;

    //open a port table and find the test port
    try {
      bindpyrame::ports_table table("/opt/pyrame/ports.txt");
      port = table.get_port("TEST_PORT");
    } catch (exception& e) {
      cout << e.what() << endl;
      exit(1);
    }

    //open a socket and send the command
    try {
      result = pyrame.sendcmd("localhost",port,"helloworld_test","","end");
    } catch (exception& e) {
      cout << e.what() << endl;
      exit(1);
    }

    //print the result
    cout << "sendcmd: retcode=" << result.retcode << " res=" << result.str << endl;

