%online treatment for pyrame
%take care : the sockets packet has to be installed with the command
%pkg -forge install sockets
pkg load sockets

%data out socket
output=socket(AF_INET,SOCK_STREAM,0);
out_server.addr="127.0.0.1";
out_server.port=8002;
status=connect(output,out_server)

%data in socket
input=socket(AF_INET,SOCK_STREAM,0);
in_server.addr="10.220.0.97";
in_server.port=8001;
status=connect(input,in_server)
send(input,"\n",0);


d=[];
while (1==1)
  %get a char from input
  recv(input,1,0);
  if ans==10
    %treating data
    data=str2num(char(d));
    res=abs(data);
    %send result to output
    send(output,num2str(res),0);
    send(output,"\n",0);
    d=[];
    else
    %aggregating data char by char
    d=[d ans];
  endif
endwhile
      
