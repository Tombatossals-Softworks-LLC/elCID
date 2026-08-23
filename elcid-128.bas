4 j=0:a$="":cx=0:sc=0:ka=0:ic=0:kc=0:co=0:sb=0:cb=0:dn$="":rt$="":bl$="":cl$="":s$="":dx=0:dy=0:w$="":fc=0:sp=0:c$="":i=0:op=0
5 tt$="":dl=0:dz=0:p1=0:mg$="":rx=0:hd=0:va=0:ob=0:dv=0:dr=0:sq=0:w1$="":w2$="":w3$="":rm=0:nx=0:rn$="":rd$="":io$="":xt$="":kf=0:o=0:x=0:y=0:r=0:d=0:v=0:z$="":s=0:hs=0:t9=0:tk=0:en=0:ev=0:ew=0:em$=""
6 poke53280,0:poke53281,0:printchr$(147);chr$(154);
7 dn$="":for j=1 to 24:dn$=dn$+chr$(17):next:bl$=""
8 rt$="":for j=1 to 39:rt$=rt$+chr$(29):next:for j=1 to 40:bl$=bl$+" ":next
9 cl$=chr$(144)+chr$(5)+chr$(28)+chr$(159)+chr$(156)+chr$(30)+chr$(31)+chr$(158)+chr$(129)+chr$(149)+chr$(150)+chr$(151)+chr$(152)+chr$(153)+chr$(154)+chr$(155)
10 restore:read nr,ni,nu
11 dimvb$(126),vk%(126),vs%(90),no$(130),nk%(130),ns%(90),ru%(nu,12),rs%(nr),ex%(nr,6),il%(ni),it%(ni),fl%(31),in$(ni),nn$(nr),dd$(nr),ms$(ni+nu)
12 for j=1 to nr:read nn$(j),dd$(j):next:for j=1 to ni+nu:read ms$(j):next
13 for j=1 to ni:read in$(j):next
14 for j=1 to nr:for d=1 to 6:read ex%(j,d):next d:next j
15 for j=1 to ni:read il%(j),it%(j):next
16 for j=0 to nu-1:for d=0 to 12:read ru%(j,d):next d:next j
17 for j=1 to nr:read rs%(j):next
18 print"un momento, campeador...":fast
19 sb=1024:cb=55296:gw=0:l9=9:ic=sb+920:kc=cb+920:cx=2:poke54296,15:poke54277,9:poke54278,0:poke54273,50
20 for j=0 to 490:read v:poke 4864+j,v:next
21 poke65530,161:poke65531,19
30 nv=0
31 read z$:if z$="*" then 34
32 read cd:nv=nv+1:vb$(nv)=z$:vk%(nv)=cd:goto 31
34 nw=0
35 read z$:if z$="*" then 37
36 read cd:nw=nw+1:no$(nw)=z$:nk%(nw)=cd:goto 35
37 for j=1 to nv:kf=asc(vb$(j)):if vs%(kf)=0 then vs%(kf)=j
38 next:for j=1 to nw:kf=asc(no$(j)):if ns%(kf)=0 then ns%(kf)=j
39 next
40 slow:gosub 995:gosub 970:rm=1
50 gosub 100
51 gosub 500
52 if gw=0 then 51
53 slow:dx=0:dy=23:co=7:s$=left$("    *  pulsa una tecla  *               ",39):gosub 200
54 get a$:if a$="" then 54
55 printchr$(147)
56 if gw=2 then gosub 84
57 if gw=1 then gosub 61
58 dx=12:dy=24:co=3:s$="pulsa una tecla":gosub 200
59 get a$:if a$="" then 59
60 goto 88
61 ho=-(fl%(24)=1)-(fl%(26)=1)-(fl%(27)=1)-(il%(29)=-1)-(fl%(28)=1)-(fl%(29)=1)-(fl%(30)=1)
68 rm=32:gosub 240
69 gosub 874:dx=15:dy=11:co=7:s$="victoria!":gosub 200
70 dx=7:dy=12:co=1:s$="valencia es del campeador":gosub 200
71 if ho>=6 then 77
72 dx=4:dy=15:co=3:s$="honra del cid: "+chr$(48+ho)+" de 7":gosub 200
73 dx=3:dy=17:co=12:s$="(restan secretos y gestas por hallar)":gosub 200
74 return
77 dx=6:dy=14:co=13:s$="la leyenda del campeador":gosub 200
78 dx=2:dy=16:co=15:s$="hallaste los tesoros de los godos y":gosub 200
79 dx=2:dy=17:co=15:s$="amparaste a moros y a cristianos.":gosub 200
80 dx=2:dy=19:co=7:s$="tus hijas, reinas; de su sangre, dice":gosub 200
81 dx=2:dy=20:co=7:s$="el cantar, naceran reyes de espanna:":gosub 200
82 dx=7:dy=22:co=13:s$="oy los reyes de espanna":gosub 200
83 dx=9:dy=23:co=13:s$="sos parientes son.":gosub 200:return
84 gosub 872:dx=9:dy=10:co=2:s$="has caido, campeador.":gosub 200
85 dx=2:dy=12:co=15:s$="mas tu leyenda no muere con tu cuerpo.":gosub 200
86 dx=4:dy=14:co=7:s$="el que en buen hora cinxo espada.":gosub 200:return
87 run
88 trap 87:if gw=2 then dload"cd"
89 if ho>=5 then dload"cl"
90 dload"cv"
100 printchr$(147);
101 gosub 240:gosub 870
102 gosub 950
103 gosub 106:gosub 210:gosub 280:return
106 dx=1:dy=10:co=7:ho=fl%(24)+fl%(26)+fl%(27)+fl%(28)+fl%(29)+fl%(30)-(il%(29)=-1):s$=left$(rn$+bl$,38)
107 if ho>0 then s$=left$(s$,28)+" honra "+chr$(48+ho)+"/7"
108 gosub 200:hp=ho:return
200 print chr$(19);left$(dn$,dy);left$(rt$,dx);mid$(cl$,co+1,1);s$;:return
210 tt$=rd$:dl=12:dz=20:co=15:gosub 320:return
240 poke251,rm:sys4864:return
280 gosub 920:dx=1:dy=21:co=3:s$=left$("salidas: "+xt$+"                       ",38):gosub 200
281 gosub 930:dx=1:dy=22:co=13:s$=left$(io$+"                                     ",38):gosub 200:return
300 ho=fl%(24)+fl%(26)+fl%(27)+fl%(28)+fl%(29)+fl%(30)-(il%(29)=-1):he=(ho>hp)
301 tt$=mg$:dl=12:dz=20:gosub 315:dl=12:co=7:gosub 320:gosub 280
302 if he then gosub 866:gosub 106
303 return
315 print chr$(19);left$(dn$,dl);:z9=dl+l9-1:if z9>dz then z9=dz
316 for r=dl to z9:print bl$;:next:return
320 p1=1:l8=dl
321 sp=0:for j=p1 to len(tt$):if mid$(tt$,j,1)="/" then sp=j:j=len(tt$)
322 next
323 if sp=0 then s$=mid$(tt$,p1)
324 if sp>0 then s$=mid$(tt$,p1,sp-p1)
325 dx=1:dy=dl:gosub 200:dl=dl+1
326 if sp=0 then l9=dl-l8:return
327 if dl>dz then l9=dl-l8:return
328 p1=sp+1:goto 321
398 if ti<t9 then return
399 t9=ti+12:tk=1-tk:poke ic+cx,32+128*tk:poke kc+cx,co:poke251,rm:poke252,tk:sys5026:return
400 slow:co=14:ic=sb+920:kc=cb+920:print chr$(19);left$(dn$,23);mid$(cl$,co+1,1);">";left$(bl$,38);:cx=2
402 get a$:if a$="" then gosub 398:goto 402
403 if a$=chr$(13) then 410
404 if a$=chr$(20) and cx>2 then cx=cx-1:poke ic+cx,32
405 if a$=chr$(20) then 402
406 if asc(a$)<32 or asc(a$)>95 or cx>35 then 402
407 ka=asc(a$):sc=ka:if ka>63 then sc=ka-64
408 poke ic+cx,sc:poke kc+cx,co:cx=cx+1:poke54276,17:poke54276,16:goto 402
410 c$="":if cx<3 then return
411 for j=2 to cx-1:sc=peek(ic+j):ka=sc:if sc<32 then ka=sc+64
412 c$=c$+chr$(ka):next:return
500 gosub 400:if c$="" then return
501 fast:sp=0:for j=1 to len(c$):if mid$(c$,j,1)=" " and sp=0 then sp=j
502 next
503 if sp=0 then w1$=c$:w2$=""
504 if sp>0 then w1$=left$(c$,sp-1):w3$=mid$(c$,sp+1)
505 if sp=0 then 508
506 sq=0:for j=1 to len(w3$):if mid$(w3$,j,1)=" " and sq=0 then sq=j
507 next:w2$=w3$:if sq>0 then w2$=left$(w3$,sq-1)
508 w$=w1$:gosub 910:va=fc
509 w$=w2$:gosub 915:ob=fc
510 dv=0:w$=w1$:gosub 900:dv=dr
511 if va=5 then w$=w2$:gosub 900:dv=dr
512 gosub 700:if hd=1 then return
513 if dv>0 then dr=dv:gosub 680:return
514 if va=1 then gosub 600:return
515 if va=2 then gosub 620:return
516 if va=3 then gosub 640:return
517 if va=4 then gosub 660:return
518 if va=12 then mg$=ha$+hb$:gosub 300:return
519 if va=0 then mg$="ese verbo no lo conozco. di ayuda.":gosub 300:return
520 if va=46 then gosub 850:return
521 if va=47 then gosub 860:return
522 if va=48 then mg$="eso funcionaba en otra cueva, forastero. aqui se reza.":gosub 300:return
523 if va=49 then mg$="de los sos ojos tan fuertemientre llorando... el juglar, maravillado, te cede la palabra.":gosub 300:gosub 874:return
524 if va=50 then mg$="bailas una estampida castellana. babieca marca el compas con el casco.":gosub 300:return
525 if va=51 then mg$="salve, campeador! toda castilla responde al saludo.":gosub 300:return
526 mg$="eso no puedes hacerlo aqui, cid.":gosub 300:return
600 if ob=0 then gosub 100:return
601 if ob>=1 and ob<=ni then 605
602 mg$="nada de particular hay en ello.":gosub 300:return
605 if il%(ob)=rm or il%(ob)=-1 then rx=ob:gosub 960:gosub 300:return
606 mg$="eso no lo ves por aqui.":gosub 300:return
620 if ob<1 or ob>ni then mg$="coger, que cosa?":gosub 300:return
621 if il%(ob)=-1 then mg$="ya lo llevas contigo.":gosub 300:return
622 if il%(ob)<>rm then mg$="eso no lo ves por aqui.":gosub 300:return
623 if it%(ob)=0 then mg$="eso no has de llevarlo.":gosub 300:return
624 il%(ob)=-1:mg$="tomas "+in$(ob)+".":gosub 300:return
640 if ob<1 or ob>ni then mg$="dejar, que cosa?":gosub 300:return
641 if il%(ob)<>-1 then mg$="eso no lo llevas.":gosub 300:return
642 il%(ob)=rm:mg$="dejas "+in$(ob)+".":gosub 300:return
660 iv$="":for j=1 to ni:if il%(j)=-1 then iv$=iv$+in$(j)+" "
661 next
662 if iv$="" then mg$="nada llevas contigo, campeador.":gosub 300:return
663 mg$="llevas: "+iv$:gosub 300:return
680 if rm=11 and dr=3 then if fl%(5)=0 or il%(5)<>-1 then mg$=gd$:gosub 300:gw=2:return
681 if rm=17 and dr=3 then if fl%(10)=0 then mg$=gl$:gosub 300:return
682 nx=ex%(rm,dr):if nx=0 then mg$="por ahi no hay camino, cid.":gosub 300:return
683 rm=nx:gosub 100:return
700 hd=0:for ri=rs%(rm) to nu-1
701 if ru%(ri,0)<>rm then 716
702 if ru%(ri,1)<>va then 720
703 if ru%(ri,2)<>0 and ru%(ri,2)<>ob then 720
704 t=ru%(ri,3):if t>0 then if fl%(t)=0 then 720
705 t=ru%(ri,4):if t>0 then if fl%(t)=0 then 720
706 t=ru%(ri,5):if t>0 then if fl%(t)=0 then 720
707 t=ru%(ri,6):if t>0 then if fl%(t)=1 then 720
708 t=ru%(ri,11):if t>0 then if il%(t)<>-1 then 720
709 t=ru%(ri,7):if t>0 then fl%(t)=1
710 t=ru%(ri,8):if t>0 then il%(t)=-1
711 t=ru%(ri,9):if t>0 then il%(t)=-1
712 t=ru%(ri,10):if t>0 then il%(t)=0
713 rx=200+ri:gosub 960:gosub 300:hd=1
714 if ru%(ri,12)=1 then gw=2
715 if ru%(ri,12)=2 then gw=1
716 ri=nu
720 next ri:return
850 open15,8,15:open2,8,2,"@0:partida,s,w"
851 print#2,rm:for j=0 to 31:print#2,fl%(j):next:for j=1 to ni:print#2,il%(j):next
852 close2:input#15,en,em$,ev,ew:close15:mg$="partida grabada en disco."
853 if en>19 then mg$="no pude grabar. hay disco?"
854 gosub 300:return
860 open15,8,15:open2,8,2,"partida,s,r":input#15,en,em$,ev,ew
861 if en>19 then close2:close15:mg$="no hay partida grabada.":gosub 300:return
862 input#2,rm:for j=0 to 31:input#2,fl%(j):next:for j=1 to ni:input#2,il%(j):next
863 close2:close15:gosub 100:mg$="partida recuperada. adelante, campeador.":gosub 300:return
866 poke53280,7:for j=1 to 6:poke54273,28+j*11:poke54276,17:for x=1 to 22:next:poke54276,16:next:poke53280,0:return
870 poke54273,4+(rm and 7):poke54276,33:poke54276,32:return
872 for j=30 to 4 step-2:poke53280,2:poke54273,j:poke54276,33:for x=1 to 15:next:poke53280,0:for x=1 to 15:next:next:poke54276,32:return
874 for j=1 to 6:poke53280,7:poke54273,asc(mid$("aeiror",j,1))-48:poke54280,7:poke54276,17:poke54283,33:for x=1 to 55:next:poke53280,0:poke54276,16:poke54283,32:next:return
878 if ti<t8 then return
879 t8=ti+10:mu=mu+1:if mu>24 then mu=1:gosub 883
880 poke54273,asc(mid$(tm$,mu,1))-48:poke54276,16:poke54276,17
881 if (mu and 3)=1 then poke54283,32:poke54283,33
882 return
883 a9=a9+1:if a9>7 then a9=0
884 rm=asc(mid$("148;?dlp",a9+1,1))-48:gosub 240:gosub 978:return
900 dr=0
901 if w$="n" or w$="norte" then dr=1
902 if w$="s" or w$="sur" then dr=2
903 if w$="e" or w$="este" then dr=3
904 if w$="o" or w$="oeste" then dr=4
905 if w$="sube" or w$="arriba" then dr=5
906 if w$="baja" or w$="abajo" then dr=6
907 return
910 fc=0:if w$="" then return
911 kf=asc(w$):j=vs%(kf):if j=0 then return
912 if w$=vb$(j) then fc=vk%(j):return
913 j=j+1:if j<=nv then if asc(vb$(j))=kf then 912
914 return
915 fc=0:if w$="" then return
916 kf=asc(w$):j=ns%(kf):if j=0 then return
917 if w$=no$(j) then fc=nk%(j):return
918 j=j+1:if j<=nw then if asc(no$(j))=kf then 917
919 return
920 xt$=""
921 if ex%(rm,1)>0 then xt$=xt$+"norte "
922 if ex%(rm,2)>0 then xt$=xt$+"sur "
923 if ex%(rm,3)>0 then xt$=xt$+"este "
924 if ex%(rm,4)>0 then xt$=xt$+"oeste "
925 if ex%(rm,5)>0 then xt$=xt$+"arriba "
926 if ex%(rm,6)>0 then xt$=xt$+"abajo "
927 if xt$="" then xt$="ninguna"
928 return
930 io$="":for j=1 to ni:if il%(j)=rm then io$=io$+in$(j)+" "
931 next
932 if io$="" then io$=""
933 if io$<>"" then io$="ves: "+io$
934 return
950 rn$=nn$(rm):rd$=dd$(rm):return
960 if rx>=200 then mg$=ms$(ni+1+rx-200):return
961 mg$=ms$(rx):return
970 gosub 980:return
978 dx=11:dy=1:co=7:s$="e l   c i d":gosub 200:dx=9:dy=2:co=7:s$="c a m p e a d o r":gosub 200:return
980 rm=1:gosub 240
981 gosub 978
982 dx=4:dy=11:co=1:s$="de los sos ojos tan fuertemientre":gosub 200
983 dx=4:dy=12:co=1:s$="llorando, tornava la cabeza e":gosub 200
984 dx=4:dy=13:co=1:s$="estabalos catando. dios, que buen":gosub 200
985 dx=4:dy=14:co=1:s$="vassallo, si oviesse buen sennor!":gosub 200
986 dx=3:dy=16:co=15:s$="rodrigo diaz, desterrado, ha de ganar":gosub 200
987 dx=3:dy=17:co=15:s$="valencia, casar sus hijas y vengar su":gosub 200
988 dx=3:dy=18:co=15:s$="honra. ordenes de dos palabras:":gosub 200
989 dx=3:dy=19:co=15:s$="coge espada, ve norte. (ayuda=verbos)":gosub 200
990 dx=6:dy=21:co=3:s$="(c) 2026 tombatossals softworks":gosub 200
991 dx=6:dy=23:co=7:s$="* pulsa una tecla, campeador *":gosub 200
992 mu=0:t8=0:a9=0:poke54280,5:poke54284,9:poke54285,0
993 get a$:if a$="" then gosub 398:gosub 878:goto 993
994 poke54276,16:poke54283,16:return
995 ha$="verbos: mira coge deja da ve habla/abre monta llena echa reza cava/asoma cine finge sella empena/convida envia socorre ata exige/muestra reta acepta casa vence lidia/doma."
996 hb$="/graba/recupera: partida. n s e o arriba/abajo. i inv."
997 tm$="eefhmhfehhmquqmhmuqmhfee":gd$="cruzas el duero sin guia ni montura./la hueste se dispersa por los/caminos y mueres olvidado en el/yermo. fin."
998 gl$="aun no es tiempo de ir a levante./despacha antes las parias al rey por/mano de minaya.":return
10000 data 32,30,76
10010 data "vivar, solar del cid"
10011 data "tu casa, vacia, el hogar frio./una corneja: mal aguero. partes."
10012 data "camino de burgos"
10013 data "camino a burgos. las gentes lloran:/dios, que buen vassallo!"
10014 data "establos de vivar"
10015 data "cuadra umbria. en el pesebre,/babieca, tu bayo de mil batallas."
10016 data "puerta de burgos"
10017 data "burgos cerrada so pena de los ojos./tu ensena ondea. sale una nina."
10018 data "plaza de burgos"
10019 data "la plaza, hostil. solo antolinez/se acerca con pan y un ardid."
10020 data "casa de raquel e vidas"
10021 data "raquel e vidas cuentan oro./dos arcas de roble, vacias, esperan."
10022 data "glera del arlanzon"
10023 data "el arenal del arlanzon. arena fina/en monton: buen lugar de ardid."
10024 data "san pedro de cardena"
10025 data "san pedro de cardena. el abad./aqui dejas a jimena y a tus hijas."
10026 data "capilla de cardena"
10027 data "capilla en penumbra. jimena ora/ante un cristo de marfil. cirios."
10028 data "bodega de cardena"
10029 data "bodega bajo el monasterio. tinajas,/grano y herramientas. frescor."
10030 data "vado del duero"
10031 data "el ancho duero, raya del reino./mas alla, tierra de moros. cruza."
10032 data "tierras de frontera"
10033 data "paramo de frontera. atalayas moras/en los cerros. caminos al sol."
10034 data "castejon de henares"
10035 data "castejon duerme al alba. sus puertas/se abriran al mercado. minaya/espera."
10036 data "botin de castejon"
10037 data "castejon es tuya. oro, panos, armas./en el corral piafan corceles moros."
10038 data "alcocer, ribera del jalon"
10039 data "alcocer, fuerte villa amurallada./el asalto frontal seria locura."
10040 data "campo de fariz y galve"
10041 data "campo abierto. fariz y galve forman./tres mil contra tus seiscientos."
10042 data "pinar de tevar"
10043 data "el pinar de tevar. el conde/berenguer/te cerca, soberbio. habra lid."
10044 data "senda a levante"
10045 data "senda a levante. huele a azahar/y a mar. valencia te aguarda."
10046 data "huerta de valencia"
10047 data "la huerta, vergel de palmas. un pozo/de marmol. dicen que el agua es/mala."
10048 data "murallas de valencia"
10049 data "las murallas de valencia, altas/y blancas. un cerco las rinde."
10050 data "real del cid"
10051 data "el real del cid, mar de tiendas./minaya vuelve con nuevas del rey."
10052 data "alcazar de valencia"
10053 data "el alcazar, ya tuyo. del mirador se/ve/la mar. un leon dormita en su jaula."
10054 data "playa de valencia"
10055 data "la playa. velas en el horizonte:/la flota de bucar viene a vengarse."
10056 data "camara de las hijas"
10057 data "camara de elvira y sol. arcas y/un manto de bodas de oro. risas."
10058 data "tesoro del alcazar"
10059 data "el tesoro del alcazar. arcas, un/atril, y en la pared: tizona!"
10060 data "batalla contra bucar"
10061 data "playa erizada de tiendas moras./bucar te reta. jeronimo pide lid."
10062 data "vega del tajo y bodas"
10063 data "la vega del tajo. el rey alfonso/te perdona y pide a tus hijas."
10064 data "robledo de corpes"
10065 data "el robledo de corpes, oscuro./afrentaron a tus hijas, jirones."
10066 data "cortes de toledo"
10067 data "las cortes de toledo. el rey/preside./alli, palidos, los infantes."
10068 data "fuente de corpes"
10069 data "una fuente en lo hondo del robledo./alli yacen elvira y sol, sin/sentido."
10070 data "palenque de los duelos"
10071 data "el palenque de carrion. tus/campeones/contra los traidores. lidia por tu/honra."
10072 data "triunfo del campeador"
10073 data "valencia engalanada. tus hijas casan/con navarra y aragon. triunfo del/cid!"
10074 data "tu manto de pieles, raido por los/caminos del destierro."
10075 data "el bando del rey: destierro en nueve/dias. la injusticia quema."
10076 data "babieca, tu bayo de ojos de fuego./ni el rey tuvo tal caballo."
10077 data "silla de guerra, de cuero y hierro./sin ella no hay jinete."
10078 data "tu ensena verde, la que jamas fue/vencida en campo."
10079 data "la hogaza que te fio antolinez/cuando burgos te cerro la puerta."
10080 data "un odre del buen vino de castilla,/para el largo camino."
10081 data "dos arcas de roble, herradas y/vacias. el ardid las llenara."
10082 data "arena fina y humeda de la glera del/arlanzon."
10083 data "tu tienda de campana, que ha visto/cien fronteras."
10084 data "reliquia de san pedro, santa y/secreta. purifica las aguas danadas."
10085 data "vianda y grano para la hueste, que/ha de comer antes del cerco."
10086 data "recia cuerda de canamo. buena para/escalar un muro."
10087 data "seiscientos marcos en un cofre,/prestados sobre las arcas."
10088 data "rico botin de castejon: oro, panos y/armas moras."
10089 data "las parias para el rey alfonso,/presente que ablanda su ira."
10090 data "colada, ganada al conde de barcelona/en el pinar de tevar."
10091 data "el salvoconducto del rey para traer/a los tuyos a valencia."
10092 data "una cidra amarga. su zumo purga el/agua emponzonada."
10093 data "el manto de bodas, todo de oro, para/elvira y sol."
10094 data "tizona, que vale mas que mil marcos/de oro. su hoja arroja lumbre."
10095 data "rico alfanje, despojo de fariz en el/campo de alcocer."
10096 data "la cimitarra del rey bucar, don/digno de un rey."
10097 data "el pabellon de bucar, de oro y seda,/tomado en la playa."
10098 data "el manto roto en corpes: prueba de/la afrenta de los infantes."
10099 data "las cinchas con que azotaron a tus/hijas. la afrenta clama."
10100 data "agua de la fuente del robledo, para/volver en si a tus hijas."
10101 data "corona de navarra: tus hijas seran/reinas."
10102 data "moneda de oro visigoda, hallada en/la arena. guino a los godos."
10103 data "corona votiva visigoda, de oro y/esmeraldas. tesoro secreto."
10104 data "lees el bando: destierro en nueve/dias. la injusticia te quema, mas/partes con honra."
10105 data "la corneja grazna a tu diestra al/salir, a la siniestra al entrar en/burgos. mal aguero, dicen los/viejos."
10106 data "te santiguas ante el aguero de la/corneja. buen viento y buena/ventura, campeador."
10107 data "ensillas y montas a babieca. el bayo/relincha de gozo. ahora eres el cid/a caballo, y nada te ataja."
10108 data "a pelo no vas a la guerra. coge/antes la silla de montar, aqui en la/cuadra."
10109 data "vender a babieca? jamas. ni tras tu/muerte volvera nadie a montarlo. asi/lo jura el campeador."
10110 data "besas el testuz de babieca. el bayo/resopla, digno, y te perdona la/confianza."
10111 data "la nina de nueve anos te habla: cid,/el rey nos veda acogerte so pena de/los ojos. id, y dios os valga./lloras y partes."
10112 data "forzar la puerta? danar a esta/villa? un campeador no hace tal. tus/propios caballeros volverian la/cara. sin honra no hay cid. fin."
10113 data "antolinez te ensena el ardid: llena/dos arcas de arena, sellalas como/oro y empenalas a raquel e vidas por/marcos."
10114 data "llenas las dos arcas de arena hasta/los bordes. pesan como si fueran de/oro macizo."
10115 data "sellas y clavas las arcas. nadie/diria que no guardan un tesoro. el/ardid esta listo."
10116 data "raquel e vidas prestan seiscientos/marcos sobre las arcas, y aun un/manto. juran no abrirlas en un anno./tienes oro!"
10117 data "abres las arcas ante los/prestamistas y descubren la arena./corre la voz de tu engano y nadie te/fia ya. el destierro te ahoga. fin."
10118 data "cavas en la arena y bajo el sauce/hallas una moneda de oro visigoda./guino secreto al heredero de los/godos!"
10119 data "la arena fina y humeda se amontona/en la glera. justo lo que pide el/ardid de antolinez."
10120 data "das los marcos al abad don sancho/para dotar el monasterio. jimena y/tus hijas quedan a salvo. dios te lo/pague."
10121 data "jimena llora y reza: merced, cid, en/buen hora cinxiestes espada! te/abraza como la una de la carne."
10122 data "tras el altar hallas una reliquia de/san pedro, santa y secreta. su/virtud purifica las aguas mas/danadas."
10123 data "rezas de hinojos. una paz honda te/arma el corazon para lo que viene."
10124 data "duermes y se te aparece el arcangel/gabriel: cabalga, cid, que todo te/ira bien. despiertas con el alma en/vilo."
10125 data "envias las parias al rey alfonso por/mano de minaya. el favor del rey/empieza a tornar hacia ti."
10126 data "esperas al alba, agazapado. las/puertas de castejon se abren al/mercado, incautas..."
10127 data "con la cuerda escalas el muro/mientras minaya corre la tierra./castejon cae sin perder un hombre./al botin!"
10128 data "sin una cuerda no puedes escalar el/muro de castejon."
10129 data "finges la huida y levantas el campo./los de alcocer, codiciosos, salen/tras de ti dejando abierta la/villa..."
10130 data "vuelves grupas de golpe y asaltas/alcocer por sorpresa. la villa es/tuya. fariz y galve acuden/iracundos."
10131 data "das la ensena a pero bermudez:/tenedla, mas no la metais en lid sin/mi mandado. el la clava en las haces/moras."
10132 data "montado en babieca y con tu ensena/al frente, cargas. fariz y galve/huyen vencidos! gran botin, y parias/para el rey."
10133 data "cargar a pie contra tres mil moros?/te cercan y caes. murio el cid sin/caballo, no torno a castilla. fin."
10134 data "vences al conde berenguer mas lo/sueltas con cortesia y le devuelves/sus tierras. agradecido, te cede/colada!"
10135 data "derrotas al soberbio conde de/barcelona y, magnanimo, lo liberas./te deja su espada colada. asi la/gano el cid en tevar."
10136 data "labradores moros huyen de tu hueste./el cid los ampara: quedad en paz,/que conmigo nada perdereis. moros y/cristianos te bendicen."
10137 data "bebes del pozo emponzonado y las/calenturas te abrasan antes de la/boda. fin."
10138 data "echas la reliquia de san pedro al/pozo y el agua se aclara, dulce y/sana. el cerco tendra de beber."
10139 data "echas la reliquia de san pedro al/pozo y el agua se aclara, dulce y/sana. el cerco tendra de beber."
10140 data "exprimes la cidra amarga en el pozo./su zumo purga el agua danada. el/cerco tendra agua limpia."
10141 data "exprimes la cidra amarga en el pozo./su zumo purga el agua danada. el/cerco tendra agua limpia."
10142 data "un pozo de marmol en la huerta./dicen que su agua esta danada:/guardate de beber de el."
10143 data "asedias valencia mes tras mes hasta/que el hambre la rinde. pero/bermudez clava tu ensena en la/torre. valencia es tuya, cid!"
10144 data "sin agua sana, el cerco enferma y se/deshace. purga antes el pozo de la/huerta."
10145 data "minaya vuelve de castilla: el rey,/ablandado por las parias, concede/salvoconducto para traer a tu/familia a valencia."
10146 data "repartes la vianda entre la hueste./comen y bendicen al cid: en buen/hora nascio! te siguen al cerco con/nuevo brio."
10147 data "desde el mirador ves llegar a jimena/y a tus hijas. a vos, mugier/ondrada, valencia por morada! lloras/de gozo."
10148 data "la fiera duerme ya en su jaula. toda/valencia recuerda como la tomaste/por la melena, sin armas."
10149 data "el leon ya esta manso en su jaula."
10150 data "el leon se ha soltado! fernando se/esconde bajo el escanno diego, tras/la viga del lagar. la corte contiene/el aliento. la fiera te mira."
10151 data "te alzas sin armas, tomas al leon/por la melena y lo llevas manso a la/jaula. la corte se maravilla. los/infantes, blancos de verguenza, no/lo olvidaran."
10152 data "un leon del emir, tomado en la/conquista, dormita en su jaula de/hierro."
10153 data "el leon duerme en su jaula. no hay/fiera que domar... por ahora."
10154 data "alzar tizona contra la fiera? la/corte murmura. el cid no mata/leones: los doma. (prueba doma leon)"
10155 data "la fiera duerme. dejala, que/bastante verguenza cargan ya los/infantes."
10156 data "las velas de bucar cubren la mar:/cincuenta mil vienen a cobrar/valencia. el cid no tiembla aprieta/el puno sobre tizona."
10157 data "mueves el atril y tras el hallas una/corona votiva visigoda, de oro y/esmeraldas. tesoro secreto!"
10158 data "un atril de hierro junto al muro./firme parece... mas quiza algo/guarde tras de si."
10159 data "el obispo don jeronimo te pide la/primera herida: esta lid yo la/quiero por mi alma! y bendice a la/hueste."
10160 data "cines tizona al cinto. su hoja/arroja lumbre. ahora si: que venga/bucar."
10161 data "con tizona en mano y babieca al/galope, alcanzas a bucar en la/huida: tornate, bucar! lo derribas./su cimitarra es tuya, don para el/rey."
10162 data "enfrentas a bucar sin cenir tizona y/el moro te derriba. valencia cae en/manos almoravides. fin."
10163 data "presentas al rey la cimitarra de/bucar. alfonso, contento, te otorga/su perdon entero. eres su vassallo y/su amigo."
10164 data "besas la mano del rey en senal de/vassallaje. el te alza y te perdona/ante toda la corte."
10165 data "casas a elvira y a sol con los/infantes de carrion, como pide el/rey, y das el manto de bodas. ojala/no lo lamentes..."
10166 data "los infantes huyeron tras azotar y/abandonar a tus hijas. recoge la/prueba: el manto roto y las cinchas."
10167 data "mesar barbas en las cortes? la tuya/esta atada por si acaso... y la del/cid nadie oso mesarla jamas."
10168 data "atas tu barba con un cordon. por/aquesta barba que nadie no messo!/asi entras a las cortes, intocado y/firme."
10169 data "exiges en justicia tizona y colada,/que diste a los infantes. el rey/manda que te las devuelvan. recobras/tus espadas!"
10170 data "muestras a las cortes el manto roto/y las cinchas. un murmullo de horror/recorre la sala. la afrenta queda/probada."
10171 data "retas a riepto a los infantes de/carrion. pero bermudez, antolinez y/muno gustioz seran tus campeones. al/palenque!"
10172 data "retar sin haber recobrado las/espadas ni mostrado la prueba? los/jueces te tienen por loco. pierdes/el pleito y tu honra. fin."
10173 data "socorres a tiempo a tus hijas y con/el agua de la fuente vuelven en si./felez munoz las pone a salvo./viviran, y veran justicia."
10174 data "das agua de la fuente a tus hijas/desmayadas. abren los ojos. las/salvas de una muerte segura en el/monte."
10175 data "das tizona a pero bermudez. con ella/derribara a fernando, que clamara/vencido."
10176 data "das colada a martin antolinez. con/ella derribara a diego gonzalez en/el palenque."
10177 data "tus tres campeones vencen: pero a/fernando, antolinez a diego, muno a/asur. los de carrion quedan por/traidores. tu honra resplandece!"
10178 data "al palenque sin las espadas/recobradas, tus campeones flaquean./recobralas antes en las cortes."
10179 data "aceptas las nuevas bodas: tus hijas,/antes afrentadas, casan con navarra/y aragon, y seran reinas. victoria,/campeador!"
10180 data "manto"
10181 data "carta"
10182 data "babieca"
10183 data "silla"
10184 data "ensena"
10185 data "pan"
10186 data "vino"
10187 data "arcas"
10188 data "arena"
10189 data "tienda"
10190 data "reliquia"
10191 data "vianda"
10192 data "cuerda"
10193 data "oro"
10194 data "botin"
10195 data "parias"
10196 data "colada"
10197 data "aval"
10198 data "cidra"
10199 data "gala"
10200 data "tizona"
10201 data "alfanje"
10202 data "cimitarra"
10203 data "pabellon"
10204 data "jirones"
10205 data "cinchas"
10206 data "agua"
10207 data "corona"
10208 data "moneda"
10209 data "joya"
10210 data 0,0,2,0,0,3,0,0,4,1,0,0,0,0,0,0,1,0,0,6,5,2,0,0,0,7,0,4,0,0,4,0,7
10211 data 0,0,0,5,0,8,6,0,0,0,11,9,7,0,10,0,0,0,8,0,0,0,0,0,0,8,0,8,0,12,0
10212 data 0,0,13,17,15,11,0,0,0,12,14,0,0,0,0,0,0,13,0,0,0,0,16,12,0,0,0,0
10213 data 0,15,0,0,12,0,18,0,0,0,0,0,19,17,0,0,21,0,20,18,0,0,0,0,22,19,0,0
10214 data 0,19,0,0,0,0,24,0,23,20,0,25,0,0,26,22,0,0,0,22,0,0,0,0,0,0,0,0
10215 data 22,0,0,0,27,23,0,0,0,0,28,26,0,0,0,0,29,27,0,30,0,0,0,28,31,0,0,0
10216 data 0,0,28,0,0,0,32,0,0,29,0,0,0,31,0,0
10217 data 1,1,1,1,3,0,3,1,4,1,5,1,5,1,6,0,7,1,7,0,0,1,10,1,10,1,0,1,14,1,0
10218 data 1,0,1,0,1,19,1,24,1,25,1,0,1,0,1,0,1,28,1,28,1,30,1,0,1,0,1,0,1
10219 data 1,20,2,0,0,0,0,0,0,0,0,0,0,1,1,101,0,0,0,0,0,0,0,0,0,0,1,25,0,0,0
10220 data 0,0,0,0,0,0,0,0,3,21,3,0,0,0,5,5,0,0,0,4,0,3,21,3,0,0,0,5,0,0,0,0
10221 data 0,0,3,8,3,0,0,0,0,0,0,0,0,0,0,3,42,3,0,0,0,0,0,0,0,0,0,0,4,1,102
10222 data 0,0,0,0,0,0,0,0,0,0,4,41,119,0,0,0,0,0,0,0,0,0,1,5,1,103,0,0,0,0
10223 data 1,0,0,0,0,0,6,22,8,1,0,0,2,2,0,0,9,9,0,6,23,8,2,0,0,3,3,0,0,0,0,0
10224 data 6,24,8,3,0,0,25,25,14,0,0,0,0,6,6,8,0,0,0,0,0,0,0,0,0,1,7,44,0,0
10225 data 0,0,0,0,29,0,0,0,0,7,1,104,0,0,0,0,0,0,0,0,0,0,8,8,14,0,0,0,4,4,0
10226 data 0,14,14,0,8,1,106,0,0,0,0,0,0,0,0,0,0,9,1,105,0,0,0,26,26,11,0,0
10227 data 0,0,9,25,0,0,0,0,0,0,0,0,0,0,0,11,25,0,0,0,0,24,24,0,0,0,0,0,12
10228 data 40,16,8,0,0,10,10,0,0,15,15,0,13,39,0,0,0,0,6,0,0,0,0,0,0,13,26,0
10229 data 0,0,0,6,6,0,0,0,13,0,13,26,0,0,0,0,6,0,0,0,0,0,0,15,27,0,0,0,0,7
10230 data 0,0,0,0,0,0,15,26,0,0,0,0,7,7,0,0,0,0,0,16,8,5,0,0,0,23,23,0,0,0
10231 data 5,0,16,26,0,5,23,0,8,8,22,0,0,0,0,16,26,0,0,0,0,5,0,0,0,0,0,1,17
10232 data 28,0,0,0,0,9,9,17,0,0,0,0,17,26,0,0,0,0,9,9,17,0,0,0,0,18,28,121
10233 data 0,0,0,29,29,0,0,0,0,0,19,45,109,0,0,0,11,0,0,0,0,0,1,19,29,11,0,0
10234 data 0,11,11,0,0,11,11,0,19,29,109,0,0,0,11,11,0,0,11,11,0,19,29,19,0
10235 data 0,0,11,11,0,0,19,19,0,19,29,109,0,0,0,11,11,0,0,19,19,0,19,1,109
10236 data 0,0,0,0,0,0,0,0,0,0,20,26,0,11,0,0,12,12,0,0,0,0,0,20,26,0,0,0,0
10237 data 12,0,0,0,0,0,0,21,1,116,10,0,0,13,13,18,0,0,0,0,21,8,12,0,0,0,28
10238 data 28,0,0,12,12,0,22,30,108,12,13,0,14,14,0,0,0,0,0,22,1,120,30,0,0
10239 data 0,0,0,0,0,0,0,22,45,120,30,0,0,0,0,0,0,0,0,0,22,1,120,17,0,0,30,0
10240 data 0,0,0,0,0,22,45,120,17,0,0,30,30,0,0,0,0,0,22,1,120,0,0,0,17,0,0
10241 data 0,0,0,0,22,45,120,0,0,0,17,0,0,0,0,0,0,22,26,120,17,0,0,30,0,0,0
10242 data 0,0,0,22,26,120,30,0,0,0,0,0,0,0,0,0,23,1,122,0,0,0,0,0,0,0,0,0,0
10243 data 25,43,111,0,0,0,27,27,30,0,0,0,0,25,1,111,0,0,0,0,0,0,0,0,0,0,26
10244 data 1,112,0,0,0,0,0,0,0,0,0,0,26,31,21,0,0,0,0,0,0,0,0,21,0,26,26,0,5
10245 data 0,0,15,15,23,0,0,21,0,26,26,0,0,0,0,15,0,0,0,0,0,1,27,8,23,15,0,0
10246 data 16,16,0,0,23,23,0,27,42,115,15,0,0,16,16,0,0,0,0,0,27,32,0,16,0,0
10247 data 17,17,0,0,20,20,0,28,1,114,17,0,0,0,0,0,0,0,0,0,29,52,113,0,0,0,0
10248 data 0,0,0,0,0,0,29,34,113,0,0,0,21,21,0,0,0,0,0,29,35,0,18,0,0,19,19
10249 data 21,17,0,0,0,29,36,25,19,0,0,0,0,0,0,0,25,0,29,37,114,18,19,0,0,0
10250 data 0,0,0,0,0,29,37,114,0,0,0,19,0,0,0,0,0,1,30,33,0,17,0,0,18,18,0,0
10251 data 0,27,0,30,8,27,17,0,0,18,18,0,0,27,27,0,31,8,21,19,0,0,0,0,0,0,0
10252 data 21,0,31,8,17,19,0,0,0,0,0,0,0,17,0,31,26,0,19,0,0,20,20,0,0,0,0,0
10253 data 31,26,0,0,0,0,19,0,0,0,0,0,0,32,38,0,12,14,20,0,0,28,0,0,0,2
10254 data 0,3,3,7,9,10,14,16,18,20,20,21,22,25,25,27,30,32,33,39,41,43,52
10255 data 53,53,55,59,62,63,69,71,75
10256 data 120,169,62,141,0,255,165,251,56,233,1,10,168,185,0,160,133,247
10257 data 200,185,0,160,133,248,169,0,133,253,169,4,133,254,169,144,133,249
10258 data 169,1,133,250,32,120,19,165,246,160,0,145,253,32,154,19,198,245
10259 data 208,243,165,249,5,250,208,234,169,0,133,253,169,216,133,254,169
10260 data 200,133,249,169,0,133,250,32,120,19,165,246,74,74,74,74,160,0,145
10261 data 253,32,154,19,165,246,41,15,160,0,145,253,32,154,19,198,245,208
10262 data 228,165,249,208,221,169,0,141,0,255,88,96,160,0,177,247,133,245
10263 data 200,177,247,133,246,165,247,24,105,2,133,247,144,2,230,248,165
10264 data 249,56,229,245,133,249,176,2,198,250,96,230,253,208,2,230,254,96
10265 data 64,165,251,56,233,1,133,250,10,10,24,101,250,170,189,75,20,133
10266 data 250,232,189,75,20,232,32,247,19,189,75,20,133,250,232,189,75,20
10267 data 232,32,247,19,189,75,20,133,250,201,255,240,36,169,0,32,26,20,165
10268 data 252,133,249,160,0,165,249,41,1,208,4,169,64,208,2,169,32,145,253
10269 data 230,249,152,24,105,4,168,192,40,144,231,96,72,165,250,201,255,208
10270 data 2,104,96,104,32,26,20,160,0,177,253,201,78,208,5,169,77,145,253
10271 data 96,201,77,208,4,169,78,145,253,96,72,165,250,10,10,10,133,253,169
10272 data 0,133,254,6,253,38,254,6,253,38,254,165,250,10,10,10,24,101,253
10273 data 133,253,165,254,105,0,133,254,104,24,101,253,133,253,165,254,105
10274 data 4,133,254,96,255,255,255,255,255,2,26,255,255,255,255,255,255,255
10275 data 255,0,6,255,255,255,255,255,255,255,255,255,255,255,255,255,3,9
10276 data 255,255,3,255,255,255,255,255,255,255,255,255,255,255,255,255,255
10277 data 255,255,255,255,255,6,255,255,255,255,255,2,24,255,255,255,1,37
10278 data 255,255,255,0,16,255,255,9,1,33,1,39,255,255,255,255,255,255,255
10279 data 255,255,255,255,255,255,255,255,255,255,255,255,255,9,2,21,255
10280 data 255,255,255,255,255,255,7,255,255,255,255,6,255,255,255,255,255
10281 data 255,255,255,255,255,2,19,2,29,255,4,8,4,36,255,255,255,255,255
10282 data 255,255,255,255,255,255,255,255,255,255,255,3,4,3,38,255,255,255
10283 data 255,255,9
10284 data "abracadabra",48,"abre",6,"abrir",6,"acepta",38,"aceptar",38
10285 data "aguarda",39,"alza",30,"asoma",30,"aparta",43,"ardes",31
10286 data "arroja",29,"asalta",26,"ataca",26,"ata",34,"atar",34,"ayuda",12
10287 data "bebe",45,"beber",45,"baila",50,"bailar",50,"besa",42,"besar",42
10288 data "consiente",38,"coge",2,"copa",2,"cina",31,"cine",31,"canta",49
10289 data "cantar",49,"casa",32,"casar",32,"cava",44,"cavar",44,"cierra",23
10290 data "clava",23,"convida",28,"destapa",6,"doma",45,"danza",50
10291 data "desposa",32,"da",8,"dar",8,"deja",3,"dejar",3,"duerme",25
10292 data "espera",39,"esperar",39,"echa",29,"ensilla",21,"excava",44
10293 data "exige",35,"exigir",35,"envia",40,"enviar",40,"empena",24
10294 data "emplea",9,"esgrime",36,"ex",1,"forzar",41,"fuerza",41,"fia",24
10295 data "finge",27,"fingir",27,"graba",46,"grabar",46,"guarda",46,"help",12
10296 data "hola",51,"ir",5,"i",4,"inv",4,"inventario",4,"invita",28
10297 data "lidia",26,"libera",28,"lee",20,"leer",20,"llena",22,"llenar",22
10298 data "mover",43,"mueve",43,"monta",21,"montar",21,"manda",40
10299 data "mostrar",36,"muestra",36,"mira",1,"mete",11,"meter",11,"mesa",52
10300 data "mesar",52,"otea",30,"ora",25,"plugh",48,"purga",29,"paga",8
10301 data "pide",35,"prenda",24,"pon",11,"recita",49,"rompe",41,"reta",37
10302 data "retar",37,"riepta",37,"reza",25,"retira",27,"rellena",22
10303 data "recupera",47,"recuperar",47,"restaura",47,"sal",5,"salva",33
10304 data "salvar",33,"socorre",33,"sella",23,"saluda",51,"salve",51,"toma",2
10305 data "traba",34,"tira",3,"usa",9,"usar",9,"ve",5,"vence",26,"ver",1
10306 data "xyzzy",48
10307 data "*"
10308 data "arnes",4,"arcas",8,"arena",9,"aval",18,"alfanje",22,"alfanje2",23
10309 data "agua",27,"atril2",30,"ave",101,"antolinez",103,"arenal",104
10310 data "altar",105,"abad",107,"agua2",109,"atril",111,"alfonso",115
10311 data "alvar",116,"aldea",121,"bando",2,"babieca",3,"bayo",3,"botin",15
10312 data "bodas",20,"botin2",22,"burgales",103,"barba",113,"bermudez",117
10313 data "bermuez",117,"berenguer",118,"capa",1,"carta",2,"corcel",3
10314 data "cofres",8,"cajas",8,"comida",12,"cuerda",13,"cofre",14,"colada",17
10315 data "carta2",18,"cidra",19,"cinchas",26,"correas",26,"corona",28
10316 data "coronag",30,"corneja",101,"cristo",105,"carrion",114,"conde",118
10317 data "cautivos",121,"despojos",15,"dones",23,"dona",106,"diego",114
10318 data "edicto",2,"ensena",5,"espada",21,"espadab",22,"espbucar",23
10319 data "esposa",106,"fruta",19,"fuente2",109,"facistol",111,"fanez",116
10320 data "fiera",120,"flota",122,"gala",20,"glera",104,"hogaza",6,"hueso",11
10321 data "infantes",114,"jaima",10,"jirones",25,"joya",30,"jimena",106
10322 data "jeronimo",112,"jaula",120,"limon",19,"leon",120,"manto",1
10323 data "montura",4,"maroma",13,"marcos",14,"manto2",20,"manto3",25
10324 data "mantor",25,"moneda",29,"martin",103,"monje",107,"mirador",108
10325 data "mar",110,"minaya",116,"moros",121,"nina",102,"ninna",102
10326 data "ninia",102,"naves",122,"odre",7,"oro",14,"olas",110,"obispo",112
10327 data "pendon",5,"pan",6,"provision",12,"parias",16,"pabellon",24
10328 data "pajaro",101,"pozo",109,"playa",110,"pero",117,"puerta",119
10329 data "puertas",119,"reliquia",11,"rey",115,"silla",4,"sena",5,"soga",13
10330 data "salvo",18,"sauce",104,"sancho",107,"tierra",9,"tienda",10
10331 data "tributo",16,"tizona",21,"tienda2",24,"tiendab",24,"torre",108
10332 data "vino",7,"vianda",12,"ventana",108,"velas",122
10333 data "*"
