//import<socket>
SOCKET_close(1);
//SOCKET_close(2);
//input socket
SOCKET_open(1,"127.0.0.1",9010);
//output socket
//SOCKET_open(2,"127.0.0.1",8002);
//maximum size of the temperature array
limsize=200
//time/temperature array
temp_tab=[]

//main loop
while 1==1
    //getting raw data
    raw = SOCKET_query(1,"")
    raw_size=size(raw,'r')
    if raw_size==0 then
        mprintf("no data")
    else
        //extract raw data
        [n,resist,time]=msscanf(raw_size,raw,"%f%d");
        
        //compute the temperature from the resistance
        R = 10000.0*((1023.0 ./resist)-1.0);
        tK = 3950.0 ./(log(R*120.6685));
        tC = tK - 273.15;
        
        //convert time/temp to string
        stroutp=msprintf("%d %f\n",time,tC)
        
        //send this output to the socket
        //nores = SOCKET_query(2,stroutp)
        
        //store the time/temp in the array
        output=[time tC]
        temp_tab=[temp_tab ; output];
        tts=size(temp_tab,'r');
        if tts>limsize then
            temp_tab = temp_tab(tts-limsize:tts)
        end
        
        //plot the array
        clf(0)
        plot(temp_tab(:,1),temp_tab(:,2))
        sleep(2000)
    end
end
//SOCKET_close(1)
