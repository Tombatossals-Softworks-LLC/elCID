#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EL CID CAMPEADOR - single source of truth.
Rooms/items/vocab/rules -> (a) Python reference engine + critical-path autotest
(proves winnability & lose conditions), (b) C64 BASIC v2 DATA (build_bas.py).
Flags are integer indices 1..63. Items 1..NI. Scenery nouns = 100+."""

# ----- verb codes (synonyms share a code) -----
VERB = {}
def vset(code, *ws):
    for w in ws: VERB[w] = code
vset(1,"mira","habla","hablar","examina","ex","observa","ver","mirar","registra","inspecciona")
vset(2,"coge","toma","tomar","agarra","recoge","coger")
vset(3,"deja","suelta","soltar","tira","dejar")
vset(4,"inventario","inv","i","objetos","bolsa")
vset(5,"ve","ir","anda","camina","cabalga","vete","cruza","cruzar","entra","sal")
vset(6,"abre","abrir","destapa")
vset(8,"da","entrega","ofrece","dar","paga")
vset(9,"usa","usar","emplea")
vset(11,"mete","meter","pon","poner","introduce")
vset(12,"ayuda","help")
# specials
vset(20,"lee","leer")
vset(21,"monta","cabalgar","ensilla","montar")
vset(22,"llena","llenar","rellena")
vset(23,"sella","sellar","cierra","clava")
vset(24,"empena","empenna","empenia","fia","prenda")
vset(25,"reza","rezar","ora","duerme","duermes","suena")
vset(26,"ataca","asalta","asedia","cerca","sitia","lidia","vence","conquista","lucha","combate","carga","atacar")
vset(27,"finge","fingir","simula","retira")
vset(28,"convida","invita","libera","perdona")  # courtesy to Berenguer
vset(29,"echa","purga","purgar","vierte","arroja")
vset(30,"asoma","otea","alza")  # subir al mirador (asoma to avoid dir clash)
vset(31,"cine","cinne","cina","cennir")  # cenir tizona
vset(32,"casa","casar","desposa")
vset(33,"rescata","auxilia")  # socorrer (socorre maps below too)
vset(33,"socorre","socorrer","salva","salvar")
vset(34,"ata","atar","traba")  # atar barba
vset(35,"exige","exigir","reclama","pide","demanda")
vset(36,"muestra","mostrar","presenta","esgrime")
vset(37,"reta","retar","riepta","desafia")
vset(38,"acepta","aceptar","consiente")
vset(39,"espera","esperar","aguarda")
vset(40,"envia","enviar","manda","despacha")
vset(41,"fuerza","forzar","derriba","rompe")
vset(42,"besa","besar")
vset(43,"mueve","mover","aparta","empuja")
vset(44,"cava","cavar","escarba","excava")
vset(45,"doma","domar","amansa","sujeta")   # el leon del alcazar
vset(46,"graba","grabar","guarda")          # save game (BASIC file I/O special)
vset(47,"recupera","recuperar","restaura")  # load game (BASIC file I/O special)
# --- easter-egg verbs (state-neutral; global jokes live in the BASIC dispatch,
#     contextual ones in the rule table below) ---
vset(48,"xyzzy","plugh","abracadabra")
vset(49,"canta","cantar","recita")
vset(50,"baila","bailar","danza")
vset(51,"saluda","hola","salve")
vset(52,"mesa","mesar")
vset(53,"bebe","beber","sorbe")   # beber (era codigo 45: chocaba con doma)

# ----- items: id: (name, [syn], start_room, takeable, exam) -----
ITEMS = {
 1:("manto",["capa"],1,1,"tu manto de pieles, raido por los caminos del destierro."),
 2:("carta",["bando","pergamino","edicto"],1,1,"el bando del rey: destierro en nueve dias. la injusticia quema."),
 3:("babieca",["caballo","corcel","bayo"],3,0,"babieca, tu bayo de ojos de fuego. ni el rey tuvo tal caballo."),
 4:("silla",["montura","arnes"],3,1,"silla de guerra, de cuero y hierro. sin ella no hay jinete."),
 5:("ensena",["pendon","bandera","sena"],4,1,"tu ensena verde, la que jamas fue vencida en campo."),
 6:("pan",["hogaza"],5,1,"la hogaza que te fio antolinez cuando burgos te cerro la puerta."),
 7:("vino",["odre"],5,1,"un odre del buen vino de castilla, para el largo camino."),
 8:("arcas",["arcas","cofres","cajas"],6,0,"dos arcas de roble, herradas y vacias. el ardid las llenara."),
 9:("arena",["arena","tierra"],7,1,"arena fina y humeda de la glera del arlanzon."),
 10:("tienda",["tienda","jaima"],7,0,"tu tienda de campanna, que ha visto cien fronteras."),
 11:("reliquia",["reliquia","hueso"],0,1,"reliquia de san pedro, santa y secreta. purifica las aguas danadas."),
 12:("vianda",["comida","provision"],10,1,"vianda y grano para la hueste, que ha de comer antes del cerco."),
 13:("cuerda",["soga","maroma"],10,1,"recia cuerda de cannamo. buena para escalar un muro."),
 14:("oro",["cofre","marcos","dinero","seiscientos"],0,1,"seiscientos marcos en un cofre, prestados sobre las arcas."),
 15:("botin",["botin","despojos"],14,1,"rico botin de castejon: oro, panos y armas moras."),
 16:("parias",["parias","tributo"],0,1,"las parias para el rey alfonso, presente que ablanda su ira."),
 17:("colada",["colada"],0,1,"colada, ganada al conde de barcelona en el pinar de tevar."),
 18:("aval",["salvoconducto","salvo"],0,1,"el salvoconducto del rey para traer a los tuyos a valencia."),
 19:("cidra",["cidra","fruta","limon"],19,1,"una cidra amarga. su zumo purga el agua emponzonada."),
 20:("gala",["bodas","boda"],24,1,"el manto de bodas, todo de oro, para elvira y sol."),
 21:("tizona",["tizona","espada"],25,1,"tizona, que vale mas que mil marcos de oro. su hoja arroja lumbre."),
 22:("alfanje",["cimitarra2","despojo"],0,1,"rico alfanje, despojo de fariz en el campo de alcocer."),
 23:("cimitarra",["dones","presente"],0,1,"la cimitarra del rey bucar, don digno de un rey."),
 24:("pabellon",["seda"],0,1,"el pabellon de bucar, de oro y seda, tomado en la playa."),
 25:("jirones",["jiron","roto"],28,1,"el manto roto en corpes: prueba de la afrenta de los infantes."),
 26:("cinchas",["cinchas","correas"],28,1,"las cinchas con que azotaron a tus hijas. la afrenta clama."),
 27:("agua",["agua"],30,1,"agua de la fuente del robledo, para volver en si a tus hijas."),
 28:("corona",["corona"],0,1,"corona de navarra: tus hijas seran reinas."),
 29:("moneda",["moneda"],0,1,"moneda de oro visigoda, hallada en la arena. guino a los godos."),
 30:("joya",["votiva"],0,1,"corona votiva visigoda, de oro y esmeraldas. tesoro secreto."),
}
NI = max(ITEMS)
INAME = {i: ITEMS[i][0] for i in ITEMS}

# scenery nouns (code 100+) -> just examinable / rule targets
SCEN = {}
def sset(code,*ws):
    for w in ws: SCEN[w]=code
sset(101,"corneja","ave","pajaro")
sset(102,"nina","ninna")
sset(103,"antolinez","martin","burgales")
sset(104,"sauce","arenal","glera")
sset(105,"altar","cristo")
sset(106,"jimena","esposa","dona")
sset(107,"abad","sancho","monje")
sset(108,"mirador","torre","ventana")
sset(109,"pozo","brocal")
sset(110,"mar","playa","olas")
sset(111,"atril","facistol")
sset(112,"jeronimo","obispo")
sset(113,"barba")
sset(114,"infantes","carrion","fernando","diego")
sset(115,"rey","alfonso")
sset(116,"minaya","fanez","alvar")
sset(117,"pero","bermudez","bermuez")
sset(118,"berenguer","conde")
sset(119,"puerta","puertas")
sset(120,"leon","fiera","melena","jaula")
sset(121,"moros","cautivos","labradores","aldea")  # senda a levante (r18)
sset(122,"flota","velas","naves","armada")          # playa, flota de bucar (r23)

# ----- room descriptions (tight, '/'-separated lines, no accents) -----
# (name, desc, exits dict, start items list, scene-key)
import json, os
_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "canon.json")) as _f:
    RM = json.load(_f)["rooms"]
DESC = {}
def setdesc(rid, d): DESC[rid]=d
# terse 2-line descriptions
setdesc(1,"tu casa, vacia, el hogar frio./una corneja: mal aguero. partes.")
setdesc(2,"camino a burgos. las gentes lloran:/dios, que buen vassallo!")
setdesc(3,"cuadra umbria. en el pesebre,/babieca, tu bayo de mil batallas.")
setdesc(4,"burgos cerrada so pena de los ojos./tu ensena ondea. sale una nina./quien la fuerce pierde la honra.")
setdesc(5,"la plaza, hostil. solo antolinez/se acerca con pan y un ardid.")
setdesc(6,"raquel e vidas cuentan oro./dos arcas de roble, vacias, esperan.")
setdesc(7,"el arenal del arlanzon. arena fina/en monton: buen lugar de ardid.")
setdesc(8,"san pedro de cardena. el abad./aqui dejas a jimena y a tus hijas.")
setdesc(9,"capilla en penumbra. jimena ora/ante un cristo de marfil. cirios.")
setdesc(10,"bodega bajo el monasterio. tinajas,/grano y herramientas. frescor.")
setdesc(11,"el ancho duero, raya del reino./mas alla, tierra de moros./sin bayo ni ensena no pases al este.")
setdesc(12,"paramo de frontera. atalayas moras/en los cerros. caminos al sol.")
setdesc(13,"castejon duerme al alba. sus puertas/se abriran al mercado. minaya espera.")
setdesc(14,"castejon es tuya. oro, panos, armas./en el corral piafan corceles moros.")
setdesc(15,"alcocer, fuerte villa amurallada./el asalto frontal seria locura.")
setdesc(16,"campo abierto. fariz y galve forman./tres mil contra tus seiscientos.")
setdesc(17,"el pinar de tevar. el conde berenguer/te cerca, soberbio. habra lid.")
setdesc(18,"senda a levante. huele a azahar/y a mar. labradores moros huyen./valencia te aguarda.")
setdesc(19,"la huerta, vergel de palmas. un pozo/de marmol. dicen que el agua es mala.")
setdesc(20,"las murallas de valencia, altas/y blancas. un cerco las rinde.")
setdesc(21,"el real del cid, mar de tiendas./minaya vuelve con nuevas del rey./la hueste aguarda vianda.")
setdesc(22,"el alcazar, ya tuyo./del mirador se ve la mar./un leon dormita en su jaula.")
setdesc(23,"la playa. velas en el horizonte:/la flota de bucar viene a vengarse.")
setdesc(24,"camara de elvira y sol. arcas y/un manto de bodas de oro. risas.")
setdesc(25,"el tesoro del alcazar. arcas, un/atril, y en la pared: tizona!")
setdesc(26,"playa erizada de tiendas moras./bucar te reta. jeronimo pide lid./sin espada cennida no hay victoria.")
setdesc(27,"la vega del tajo. el rey alfonso/te perdona y pide a tus hijas.")
setdesc(28,"el robledo de corpes, oscuro./afrentaron a tus hijas, jirones.")
setdesc(29,"cortes de toledo. el rey preside./alli, palidos, los infantes de carrion.")
setdesc(30,"una fuente en lo hondo del robledo./alli yacen elvira y sol, sin sentido.")
setdesc(31,"el palenque de carrion./tus campeones contra los traidores./lidia por tu honra.")
setdesc(32,"valencia engalanada. tus hijas casan/con navarra y aragon. triunfo, cid!")

SCENE = {r["id"]: r.get("scene","") for r in RM}
EXITS = {r["id"]: r.get("exits",{}) for r in RM}
ROOMITEMS = {i: [] for i in range(1,33)}
for i in ITEMS:
    s=ITEMS[i][2]
    if isinstance(s,int) and s>0: ROOMITEMS[s].append(i)
NR=32

# ----- RULES (data-driven; same logic runs in Python ref-engine and C64 BASIC) -----
# flags: 1 antolinez 2 arcas_llenas 3 arcas_selladas 4 familia_segura 5 babieca 6 castejon
# 7 alcocer 8 fariz 9 colada 10 parias 11 pozo 12 valencia 13 salvo 14 familia_val 15 bucar
# 16 perdon 17 bodas 18 hijas_salvadas 19 espadas 20 honra 21 barba 24 angel 25 oro 26 reliq 27 corona
# --- honra (deeds counted at the victory screen; legendary ending at 5+ of 6) ---
# 24 sueno del angel  26 reliquia hallada  27 corona goda hallada  (item 29 moneda visigoda en bolsa)
# 28 provisiones a la hueste (da vianda)   29 clemencia con los moros de la senda
# 30 el leon del alcazar domado (7a gesta; leyenda a 6+ de 7)
R=[]
def rule(room,v,o,need=(),forbid=(),setf=(),give=0,give2=0,take=0,msg="",kind=0,needi=0):
    R.append(dict(room=room,v=v,o=o,need=list(need),forbid=list(forbid),setf=list(setf),
                  give=give,give2=give2,take=take,msg=msg,kind=kind,needi=needi))
# movement gates: (room,dir) -> dict(needf, needi, lose, msg)
GATE={
 (11,"e"):dict(needf=[5],needi=5,lose=True,
   msg="cruzas el duero sin guia ni montura. la mesnada se dispersa por los caminos y mueres olvidado en el yermo. fin."),
 (17,"e"):dict(needf=[10],needi=0,lose=False,
   msg="aun no es tiempo de marchar a levante. despacha antes las parias al rey por mano de minaya."),
}
# --- cantar 1: destierro ---
rule(1,20,2,msg="lees el bando: destierro en nueve dias. la injusticia te quema, mas partes con honra.")
rule(1,1,101,msg="la corneja grazna a tu diestra al salir, a la siniestra al entrar en burgos. mal aguero, dicen los viejos.")
rule(3,21,3,forbid=[5],setf=[5],needi=4,msg="ensillas y montas a babieca. el bayo relincha de gozo. ahora eres el cid a caballo, y nada te ataja.")
rule(3,21,3,forbid=[5],msg="a pelo no vas a la guerra. coge antes la silla de montar, aqui en la cuadra.")
rule(3,8,3,msg="vender a babieca? jamas. ni tras tu muerte volvera nadie a montarlo. asi lo jura el campeador.")
rule(4,1,102,msg="la nina de nueve anos te habla: cid, el rey nos veda acogerte so pena de los ojos. id, y dios os valga. lloras y partes.")
rule(4,41,119,kind=1,msg="forzar la puerta? danar a esta villa? un campeador no hace tal. tus propios caballeros volverian la cara. sin honra no hay cid. fin.")
rule(5,1,103,setf=[1],msg="antolinez te ensena el ardid: llena dos arcas de arena, sellalas como oro y empenalas a raquel e vidas por marcos.")
rule(7,44,0,give=29,msg="cavas en la arena y bajo el sauce hallas una moneda de oro visigoda. guino secreto al heredero de los godos!")
rule(7,1,104,msg="arena fina y humeda se amontona en la glera bajo el sauce. tierra suelta: buen lugar para cavar.")
rule(6,22,8,need=[1],forbid=[2],setf=[2],take=9,needi=9,msg="llenas las dos arcas de arena hasta los bordes. pesan como si fueran de oro macizo.")
rule(6,23,8,need=[2],forbid=[3],setf=[3],msg="sellas y clavas las arcas. nadie diria que no guardan un tesoro. el ardid esta listo.")
rule(6,24,8,need=[3],forbid=[25],setf=[25],give=14,msg="raquel e vidas prestan seiscientos marcos sobre las arcas, y aun un manto. juran no abrirlas en un anno. tienes oro!")
rule(6,6,8,forbid=[3],msg="las arcas estan vacias aun. antolinez te dira que hacer con ellas.")
rule(6,6,8,kind=1,msg="abres las arcas ante los prestamistas y descubren la arena. corre la voz de tu engano y nadie te fia ya. el destierro te ahoga. fin.")
rule(8,8,14,forbid=[4],setf=[4],take=14,needi=14,msg="das los marcos al abad don sancho para dotar el monasterio. jimena y tus hijas quedan a salvo. dios te lo pague.")
rule(8,1,106,msg="jimena llora y reza: merced, cid, en buen hora cinxiestes espada! te abraza como la una de la carne.")
rule(9,1,105,forbid=[26],setf=[26],give=11,msg="tras el altar hallas una reliquia de san pedro, santa y secreta. su virtud purifica las aguas mas danadas.")
rule(9,25,0,msg="rezas de hinojos. una paz honda te arma el corazon para lo que viene.")
rule(11,25,0,forbid=[24],setf=[24],msg="duermes y se te aparece el arcangel gabriel: cabalga, cid, que todo te ira bien. despiertas con el alma en vilo.")
rule(13,39,0,forbid=[6],msg="esperas al alba, agazapado. las puertas de castejon se abren al mercado, incautas...")
rule(13,26,0,need=[],forbid=[6],setf=[6],needi=13,msg="con la cuerda escalas el muro mientras minaya corre la tierra. castejon cae sin perder un hombre. al botin!")
rule(13,26,0,forbid=[6],msg="sin una cuerda no puedes escalar el muro de castejon.")
rule(15,27,0,forbid=[7],msg="finges la huida y levantas el campo. los de alcocer, codiciosos, salen tras de ti dejando abierta la villa...")
rule(15,26,0,forbid=[7],setf=[7],msg="vuelves grupas de golpe y asaltas alcocer por sorpresa. la villa es tuya. fariz y galve acuden iracundos.")
rule(16,8,5,forbid=[23],setf=[23],needi=5,msg="das la ensena a pero bermudez: tenedla, mas no la metais en lid sin mi mandado. el la clava en las haces moras.")
rule(16,26,0,need=[5,23],forbid=[8],setf=[8],give=22,msg="montado en babieca y con tu ensena al frente, cargas. fariz y galve huyen vencidos! gran botin, y parias para el rey.")
rule(16,26,0,forbid=[23],msg="cargar sin ensena delantera? da antes tu pendon a pero bermudez, que el la clave en las haces moras.")
rule(17,28,0,forbid=[9],setf=[9],give=17,msg="vences al conde berenguer mas lo sueltas con cortesia y le devuelves sus tierras. agradecido, te cede colada!")
rule(17,26,0,forbid=[9],setf=[9],give=17,msg="derrotas al soberbio conde de barcelona y, magnanimo, lo liberas. te deja su espada colada. asi la gano el cid en tevar.")
rule(12,40,16,need=[8],forbid=[10],setf=[10],take=15,needi=15,msg="envias las parias al rey alfonso por mano de minaya. el favor del rey empieza a tornar hacia ti.")
# --- cantar 2: valencia ---
# senda a levante: clemencia con los moros (honra; el cid amparaba moros y cristianos)
rule(18,28,121,forbid=[29],setf=[29],msg="labradores moros huyen de tu hueste. el cid los ampara: quedad en paz, que conmigo nada perdereis. moros y cristianos te bendicen.")
rule(21,1,116,need=[10],forbid=[13],setf=[13],give=18,msg="minaya vuelve de castilla: el rey, ablandado por las parias, concede salvoconducto para traer a tu familia a valencia.")
# real del cid: repartir vianda a la mesnada (honra; el cid provee a los suyos para el cerco)
rule(21,8,12,forbid=[28],setf=[28],take=12,needi=12,msg="repartes la vianda entre la hueste. comen y bendicen al cid: en buen hora nascio! te siguen al cerco con nuevo brio.")
rule(19,53,109,forbid=[11],kind=1,msg="bebes del pozo emponzonado y las calenturas te abrasan antes de la boda. fin.")
rule(19,29,0,forbid=[11],setf=[11],take=11,needi=11,msg="echas la reliquia de san pedro al pozo y el agua se aclara, dulce y sana. el cerco tendra de beber.")
rule(19,29,0,forbid=[11],setf=[11],take=19,needi=19,msg="exprimes la cidra amarga en el pozo. su zumo purga el agua danada. el cerco tendra agua limpia.")
rule(20,26,0,need=[11],forbid=[12],setf=[12],msg="asedias valencia mes tras mes hasta que el hambre la rinde. pero bermudez clava tu ensena en la torre. valencia es tuya, cid!")
rule(20,26,0,forbid=[12],msg="sin agua sana, el cerco enferma y se deshace. purga antes el pozo de la huerta.")
rule(22,1,108,msg="un mirador sobre la mar y el camino de castilla. asomate y otea quien viene.")
rule(22,30,108,forbid=[13],msg="sin salvoconducto del rey no vendran los tuyos. minaya lo trae al real del cid.")
rule(22,30,108,need=[12,13],forbid=[14],setf=[14],msg="desde el mirador ves llegar a jimena y a tus hijas. a vos, mugier ondrada, valencia por morada! lloras de gozo.")
# --- el leon del alcazar (episodio del cantar; 7a gesta de honra) ---
rule(22,1,120,need=[30],msg="la fiera duerme ya en su jaula. toda valencia recuerda como la tomaste por la melena, sin armas.")
rule(22,45,120,need=[30],msg="el leon ya esta manso en su jaula.")
rule(22,1,120,need=[17],forbid=[30],msg="el leon se ha soltado! fernando se esconde bajo el escanno; diego, tras la viga del lagar. la corte contiene el aliento. la fiera te mira.")
rule(22,45,120,need=[17],forbid=[30],setf=[30],msg="te alzas sin armas, tomas al leon por la melena y lo llevas manso a la jaula. la corte se maravilla. los infantes, blancos de verguenza, no lo olvidaran.")
rule(22,1,120,forbid=[17],msg="un leon del emir, tomado en la conquista, dormita en su jaula de hierro.")
rule(22,45,120,forbid=[17],msg="el leon duerme en su jaula. no hay fiera que domar... por ahora.")
# --- humour / easter-egg rules (all state-neutral) ---
rule(22,26,120,need=[17],forbid=[30],msg="alzar tizona contra la fiera? la corte murmura. el cid no mata leones: los doma. (prueba DOMA LEON)")
rule(22,26,120,need=[30],msg="la fiera duerme. dejala, que bastante verguenza cargan ya los infantes.")
rule(3,42,3,msg="besas el testuz de babieca. el bayo resopla, digno, y te perdona la confianza.")
rule(29,52,113,msg="mesar barbas en las cortes? la tuya esta atada por si acaso... y la del cid nadie oso mesarla jamas.")
rule(1,25,0,msg="te santiguas ante el aguero de la corneja. buen viento y buena ventura, campeador.")
rule(25,43,111,forbid=[27],setf=[27],give=30,msg="mueves el atril y tras el hallas una corona votiva visigoda, de oro y esmeraldas. tesoro secreto!")
# playa de valencia: otear la flota de bucar (densidad; tension antes de la lid)
rule(23,1,122,msg="las velas de bucar cubren la mar: cincuenta mil vienen a cobrar valencia. el cid no tiembla; aprieta el puno sobre tizona.")
rule(26,1,112,msg="el obispo don jeronimo te pide la primera herida: esta lid yo la quiero por mi alma! y bendice a la hueste.")
rule(26,31,21,needi=21,msg="cines tizona al cinto. su hoja arroja lumbre. ahora si: que venga bucar.")
rule(26,26,0,need=[5],forbid=[15],setf=[15],give=23,give2=24,needi=21,msg="con tizona en mano y babieca al galope: tornate, bucar! lo derribas y le ganas tizon, y su pabellon de oro y seda. la cimitarra sera don para el rey.")
rule(26,26,0,forbid=[15],kind=1,msg="enfrentas a bucar sin cenir tizona y el moro te derriba. valencia cae en manos almoravides. fin.")
rule(27,8,23,need=[15],forbid=[16],setf=[16],take=23,needi=23,msg="presentas al rey la cimitarra de bucar. alfonso, contento, te otorga su perdon entero. eres su vassallo y su amigo.")
rule(27,42,115,need=[15],forbid=[16],setf=[16],msg="besas la mano del rey en senal de vassallaje. el te alza y te perdona ante toda la corte.")
rule(27,8,3,msg="ofreces babieca al rey. alfonso lo rehusa: si tal fiziesse, el cavallo non serie tan bien colodrado. quedese con vos, cid.")
rule(27,32,0,forbid=[16],msg="el rey no te ha perdonado aun. vence a bucar y traele su cimitarra en don.")
rule(27,32,0,need=[16],forbid=[17],setf=[17],take=20,needi=20,msg="casas a elvira y a sol con los infantes, y das el manto de bodas. corre nueva: el leon del alcazar anda suelto! ojala no lo lamentes...")
# --- cantar 3: corpes y cortes ---
rule(28,1,114,need=[17],msg="los infantes huyeron tras azotar y abandonar a tus hijas. recoge la prueba: el manto roto y las cinchas.")
rule(30,33,0,need=[17],forbid=[18],setf=[18],needi=27,msg="socorres a tiempo a tus hijas y con el agua de la fuente vuelven en si. felez munoz las pone a salvo. viviran, y veran justicia.")
rule(30,8,27,need=[17],forbid=[18],setf=[18],take=27,needi=27,msg="das agua de la fuente a tus hijas desmayadas. abren los ojos. las salvas de una muerte segura en el monte.")
rule(29,1,113,msg="tu barba, crecida en el destierro, jamas fue mesada de nadie. es tu honra hecha carne.")
rule(29,34,113,forbid=[21],setf=[21],msg="atas tu barba con un cordon. por aquesta barba que nadie no messo! asi entras a las cortes, intocado y firme.")
rule(29,35,0,need=[18],forbid=[19],setf=[19],give=21,give2=17,msg="exiges en justicia tizona y colada, que diste a los infantes. el rey manda que te las devuelvan. recobras tus espadas!")
rule(29,36,25,need=[19],needi=25,msg="muestras a las cortes el manto roto y las cinchas. un murmullo de horror recorre la sala. la afrenta queda probada.")
rule(29,37,114,need=[18,19],msg="retas a riepto a los infantes de carrion. pero bermudez, antolinez y muno gustioz seran tus campeones. al palenque!")
rule(29,37,114,forbid=[18],msg="tus hijas aun yacen en corpes. baja al robledo y socorrelas antes.")
rule(29,37,114,need=[18],forbid=[19],kind=1,msg="retar sin haber recobrado las espadas ni mostrado la prueba? los jueces te tienen por loco. pierdes el pleito y tu honra. fin.")
rule(31,8,21,need=[19],needi=21,msg="das tizona a pero bermudez. con ella derribara a fernando, que clamara vencido.")
rule(31,8,17,need=[19],needi=17,msg="das colada a martin antolinez. con ella derribara a diego gonzalez en el palenque.")
rule(31,26,0,need=[19],forbid=[20],setf=[20],msg="tus tres campeones vencen: pero a fernando, antolinez a diego, muno a asur. los de carrion quedan por traidores. tu honra resplandece!")
rule(31,26,0,forbid=[19],msg="al palenque sin las espadas recobradas, tus campeones flaquean. recobralas antes en las cortes.")
rule(32,38,0,need=[12,14,20],give=28,kind=2,msg="aceptas las nuevas bodas: tus hijas, antes afrentadas, casan con navarra y aragon, y seran reinas. victoria, campeador!")
rule(32,38,0,msg="aun no, campeador: falta ganar valencia, traer a los tuyos y vencer en el palenque.")

# --- contextual MIRA on scenery: two gameplay hints only.  The C64 build is
#     at its BASIC-RAM edge (~1.1 KB free); each rule costs ~150 bytes of the
#     free heap the game needs to defer the C64's O(n^2) GC, so this is kept to
#     the two examines that carry real hints and no more. ---
rule(19,1,109,msg="un pozo de marmol en la huerta. dicen que su agua esta danada: guardate de beber de el.")
rule(25,1,111,msg="un atril de hierro junto al muro. firme parece... mas quiza algo guarde tras de si.")

print("spec loaded: rooms=%d items=%d verbs=%d rules=%d gates=%d"%(NR,NI,len(set(VERB.values())),len(R),len(GATE)))
