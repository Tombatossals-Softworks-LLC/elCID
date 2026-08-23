10 graphic3,1:color0,1
20 slow
30 bload"cvbm",b0,p8192
40 bload"cvsc",b0,p7168
50 bload"cvco",b0,p4864
60 fast:fori=0to999:poke55296+i,peek(4864+i):next:slow
70 geta$:ifa$<>""then100
80 if(peek(56320)and16)=0then100
90 goto70
100 graphic clr:dload"elcid128"
