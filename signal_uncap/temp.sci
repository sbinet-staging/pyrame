//import<socket>
SOCKET_close(1);
SOCKET_close(2);
SOCKET_open(1,"127.0.0.1",9010);
SOCKET_open(2,"127.0.0.1",8002);
limsize=200
gy=[]
while 1==1
    t=0;
    t = SOCKET_query(1,"")
    s=size(t,'r');
    if s==0 then
        mprintf("no data")
    else
        y=msscanf(s,t,"%f");
        gy=[gy ; y];
        sgy=size(gy,'r');
        if sgy>limsize then
            gy = gy(sgy-limsize:sgy)
        end
        R = 10000.0*((1023.0 ./y)-1.0);
        tK = 3950.0 ./(log(R*120.6685));
        tC = tK - 273.15;
        strtC=msprintf("%f\n",tC)
        nores = SOCKET_query(2,strtC)
        
        gR = 10000.0*((1023.0 ./gy)-1.0);
        gtK = 3950.0 ./(log(gR*120.6685));
        gtC = gtK - 273.15;
        clf(0)
        plot(gtC)
        sleep(2000)
    end
end
//SOCKET_close(1)
