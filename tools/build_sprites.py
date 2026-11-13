#!/usr/bin/env python3
"""VESPER pixel-art sprite compiler. All frames are real, indexed, transparent PNG sprites.
This file is included so animations can be regenerated and modified offline.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, json, random, hashlib

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'app/src/main/assets/assets'
CHARS=ASSETS/'characters'; MORIS=ASSETS/'moris'
CHARS.mkdir(parents=True,exist_ok=True); MORIS.mkdir(parents=True,exist_ok=True)
FW,FH=64,80; MW,MH=256,144; COLS=16
KILLERS={
 'reaper':('Ceifador','#e94b65','#303040','#b7c4cd','#a2b0bd','scythe'),
 'shadow':('Sombra','#8791f9','#24223a','#c3c8d9','#8990bd','dagger'),
 'brute':('Colosso','#ffae6c','#65473f','#b5aaa3','#e0c8a4','hammer'),
 'weaver':('Tecelã','#cd9af9','#362541','#b7a1dc','#c3a0e6','spider'),
 'hunter':('Rastreador','#f8a164','#5d3a2e','#9c7d69','#efb695','claws'),
 'specter':('Espectro','#91b9ff','#25374e','#b5d6f5','#90b3d9','ghost'),
 'judge':('Juiz','#e7c397','#504047','#d1b7a3','#bd929a','gavel'),
 'huntress':('Vigia','#8cddbf','#40554a','#c8d9b4','#c7a688','bow'),
 'pyre':('Incendiário','#ff6d39','#662d2c','#e7ad65','#e09358','fire'),
 'frost':('Gélida','#93e1fb','#405768','#e0eff9','#c6e5f2','ice'),
 'puppet':('Marionetista','#eab0d9','#514058','#e0d0df','#f0d0cd','strings'),
 'raven':('Corvo','#ac95ff','#272135','#bdafd0','#8b82ae','raven'),
 'automaton':('Autômato','#ebdf75','#596264','#9aa5a8','#b9c5ba','saw'),
 'siren':('Sereia','#7bded5','#2d646e','#c0e5e0','#8ed5cc','trident'),
}
SURVIVORS={
 'lia':('Lia','#f2b968','#b65d40','#efc3a1','#a7402b','athlete'),
 'maya':('Maya','#78bfe6','#4b7399','#e7bca9','#212637','tech'),
 'noah':('Noah','#82bea0','#4c806c','#a87659','#332825','medic'),
 'erik':('Erik','#bfa0f1','#69578d','#ce9976','#d2bb80','trickster'),
 'iris':('Íris','#e98b99','#86465a','#b47c62','#24192b','scout'),
 'caio':('Caio','#b5c765','#697c3e','#e4c5a0','#46362a','engineer')
}
CLIPS_K={'idle':16,'walk':24,'run':24,'attack':28,'ability':28,'hurt':16,'carry':24}
CLIPS_S={'idle':16,'walk':24,'run':24,'hurt':16,'repair':24,'down':20,'hook':20,'vault':20,'carry':20,'heal':20}
HEX=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
def mul(col,f):
 c=HEX(col) if isinstance(col,str) else col
 return tuple(max(0,min(255,round(x*f))) for x in c)
def rgb(c,a=255): return (*HEX(c),a) if isinstance(c,str) else (*c[:3],a)
def mix(a,b,v):
 x=HEX(a) if isinstance(a,str) else a; y=HEX(b) if isinstance(b,str) else b
 return tuple(int(x[i]*(1-v)+y[i]*v) for i in range(3))
def P(d,pts,color,stroke='#0a0d16',w=2):
 pts=[(round(x),round(y)) for x,y in pts];d.polygon(pts,fill=color)
 if stroke:d.line(pts+[pts[0]],fill=stroke,width=w,joint='curve')
def line(d,pts,color,width=2):d.line([(round(x),round(y)) for x,y in pts],fill=color,width=width,joint='curve')
def ellipse(d,box,c,outline=None,width=1):d.ellipse(tuple(round(t) for t in box),fill=c,outline=outline,width=width)
def rect(d,box,c,outline=None,width=1):d.rectangle(tuple(round(t) for t in box),fill=c,outline=outline,width=width)
def sparkle(d,x,y,c,sz=2):
 x=int(x);y=int(y);rect(d,(x-1,y-sz,x+1,y+sz),c);rect(d,(x-sz,y-1,x+sz,y+1),c)
def seed_for(s):return int(hashlib.md5(s.encode()).hexdigest()[:8],16)

def character(id,action,idx,frames=24,small=False):
 key=(SURVIVORS if small else KILLERS)[id];_,accent,base,skin,hair,style=key
 im=Image.new('RGBA',(FW,FH));d=ImageDraw.Draw(im)
 p=idx/max(1,frames);cyc=math.sin(p*math.tau);bounce=math.cos(p*math.tau*2)
 motion=action in ('walk','run','carry','vault','down')
 amp={'idle':.5,'walk':4.2,'run':7.0,'attack':1.2,'ability':2.,'hurt':2.,'carry':3.2,'repair':1.1,'down':1.4,'hook':1.0,'vault':5.,'heal':1.2}.get(action,2)
 stride=cyc*amp; bob=(math.sin(p*math.tau*2)+1)*(2 if action=='run' else 1 if action=='walk' else .6)
 if action=='hurt':bob=4*math.sin(p*math.pi)
 dy=int(-bob) if motion else 0
 if action=='down':dy=12
 if action=='vault':dy=-int(9*math.sin(p*math.pi))
 if action=='hook':dy=-round(2*math.cos(p*math.tau))
 is_atk=action=='attack'; att=math.sin(min(1,max(0,(p-.12)/.62))*math.pi) if is_atk else 0
 cast=math.sin(p*math.pi) if action=='ability' else 0
 tilt=round(4*math.sin(p*math.tau)) if action=='hurt' else 0
 x=tilt; Y=lambda y:y+dy
 # grounded contact shadow
 ellipse(d,(13,66,52,74),(2,3,10,72))
 if style in ('ghost','dagger') or id in ('shadow','specter'):
  P(d,[(16+x,Y(32)),(13+x,Y(47)),(17+x,Y(65)),(10+x,Y(73)),(24+x,Y(67)),(33+x,Y(75)),(42+x,Y(65)),(53+x,Y(72)),(48+x,Y(41))],mul(base,.55),None)
 if style in ('spider','raven','trident','strings'):
  for side in (-1,1):
   for n in range(3):
    sx=32+side*(13+n*3); yy=Y(34+n*6)
    offset=math.sin(p*math.tau+n*2+side)*3
    line(d,[(sx,yy),(sx+side*(12+n*2),yy-10+offset),(sx+side*(17+n*3),yy+5+offset)],mul(base,.65),3)
    line(d,[(sx+side*(14+n*2),yy),(sx+side*(17+n*3),yy+5+offset)],accent,1)
 if style=='raven':
  for side in (-1,1):
   wing=6+math.sin(p*math.tau*2)*8
   P(d,[(32+side*6,Y(30)),(32+side*(26+wing),Y(10)),(32+side*(22+wing),Y(31)),(32+side*(32+wing),Y(42)),(32+side*11,Y(43))],mul(base,.58),None)
   for f in range(4):line(d,[(32+side*19,Y(26)),(32+side*(28+f*2),Y(29+f*3))],accent,1)
 if style=='claws':
  for side in (-1,1):P(d,[(32+side*7,Y(16)),(32+side*14,Y(5)),(32+side*19,Y(24))],mul(base,.72))
 if style=='ice':
  for side in (-1,1):
   P(d,[(32+side*14,Y(24)),(32+side*23,Y(4)),(32+side*25,Y(37)),(32+side*17,Y(42))],mul(accent,.72))
 if style=='fire':
  for j in range(4):
   fx=18+j*9+math.sin(p*math.tau+j)*2
   flameH=9+round(6*math.sin(p*math.tau+j*1.9))
   P(d,[(fx-4,Y(38)),(fx,Y(22-flameH)),(fx+5,Y(37))],mul(accent,.6+j*.12),None)
 # back scarf, cloak / skirt
 if not small:
  cloakBottom=71+math.sin(p*math.tau)*2
  if style in ('scythe','dagger','ghost','gavel','strings','raven','trident','ice'):
   P(d,[(17+x,Y(34)),(47+x,Y(35)),(51+x+cyc*2,Y(cloakBottom)),(40+x,Y(64)),(32+x,Y(73)),(22+x,Y(64)),(11+x+cyc*2,Y(cloakBottom))],mul(base,.62))
 if small and id in ('lia','iris'):
  P(d,[(21+x,Y(40)),(24+x-2*cyc,Y(57)),(27+x,Y(62)),(31+x,Y(39))],accent,None)
 # left foot & thigh drawn independently for gait; down state sprawls
 for side in (-1,1):
  l=32+side*8+x; step=(stride*side)
  if action=='down':
   line(d,[(l,Y(52)),(l+side*12,Y(59)),(l+side*16,Y(64))],mul(base,.65),7)
   ellipse(d,(l+side*16-4,Y(61),l+side*16+5,Y(66)),mul(base,.45),'#0e1019')
  else:
   line(d,[(l,Y(50)),(l+side*2+step*.6,Y(60)),(l+step,Y(67)-abs(step)*.38)],mul(base,.64),8)
   line(d,[(l+step-4,Y(65)-abs(step)*.38),(l+step+5,Y(69)-abs(step)*.38)],mul(base,.42),5)
   rect(d,(round(l-4+step),round(Y(66)-abs(step)*.38),round(l+4+step),round(Y(68)-abs(step)*.38)),mul(accent,.45))
 # torso: outline, highlights, jacket seams
 torso=13 if not small else 11
 if style in ('hammer','gavel','saw'):torso=17
 if style=='claws':torso=14
 P(d,[(32-torso+x,Y(30)),(32+torso+x,Y(30)),(34+torso+x,Y(50)),(31+x,Y(55)),(30-torso+x,Y(50))],base)
 rect(d,(32-torso+x+3,Y(35),32-torso+x+6,Y(48)),mul(accent,.65))
 rect(d,(32+torso+x-6,Y(36),32+torso+x-4,Y(49)),mul(accent,.55))
 line(d,[(32+x,Y(33)),(32+x,Y(50))],mul(accent,.65),2)
 rect(d,(23+x,Y(49),41+x,Y(52)),mul(base,.55))
 if style in ('saw','gavel','hammer'):
  for side in (-1,1):
   P(d,[(32+side*13+x,Y(31)),(32+side*21+x,Y(28)),(32+side*20+x,Y(39)),(32+side*11+x,Y(41))],mul(skin,.67))
  for v in (37,44):line(d,[(24+x,Y(v)),(40+x,Y(v))],mul(skin,.88),2)
 elif style in ('fire','ice','spider','trident','strings'):
  for h in (39,46):
   sparkle(d,32+x,Y(h),mul(accent,.85),2)
 elif small:
  rect(d,(31+x,Y(35),33+x,Y(48)),mul(skin,.72))
  for v in (41,46):rect(d,(30+x,Y(v),31+x,Y(v+1)),mul(accent,.8))
 # attack arm slash motion
 for side in (-1,1):
  shoulder=32+side*(torso-1)+x
  swing=(stride*.8 if motion else (math.sin(p*math.tau*2)*9 if action in ('repair','heal','hook') else math.sin(p*math.tau)*2.4))
  weaponSide=side==1
  # right arm follows attack / casting arc
  armx=shoulder+side*(7+(att*11 if weaponSide else 0))
  army=Y((26 if action=='hook' else 45)+swing*side -(10*att if weaponSide else 0) - 8*cast)
  line(d,[(shoulder,Y(35)),(armx,army)],mul(base,.74),8 if not small else 6)
  line(d,[(shoulder+side*2,Y(36)),(armx,army)],mul(accent,.67),3)
  ellipse(d,(armx-3,army-3,armx+3,army+3),skin,'#111019')
 # hair/head/helmet: different designs
 hx=32+x;hy=Y(22)
 if style=='saw':
  P(d,[(hx-11,hy-13),(hx+11,hy-13),(hx+13,hy+7),(hx-13,hy+7)],mul(skin,.73))
  rect(d,(hx-12,hy-7,hx+12,hy-2),mul(base,.5))
  rect(d,(hx-9,hy-5,hx+9,hy-2),accent)
 elif style in ('ghost','dagger'):
  P(d,[(hx-14,hy+8),(hx-13,hy-7),(hx,hy-19),(hx+15,hy-6),(hx+14,hy+12),(hx+8,hy+16),(hx-9,hy+15)],mul(base,.46))
  ellipse(d,(hx-8,hy-8,hx+8,hy+10),mul(skin,.72),'#0d1220')
 else:
  ellipse(d,(hx-10,hy-12,hx+10,hy+11),skin,'#10131a',2)
  P(d,[(hx-11,hy-2),(hx-11,hy-13),(hx-5,hy-18),(hx+7,hy-17),(hx+12,hy-10),(hx+9,hy-6),(hx,hy-8)],hair,None)
  if id in ('weaver','frost','siren','puppet','iris','maya'):
   for side in (-1,1):line(d,[(hx+side*8,hy-9),(hx+side*12,hy+13)],hair,3)
  if id in ('brute','judge','hunter','pyre','huntress','caio'):
   rect(d,(hx-11,hy-13,hx+11,hy-9),mul(base,.6))
 # silhouette signature
 if style=='scythe':P(d,[(hx-13,hy-9),(hx-9,hy-20),(hx+7,hy-24),(hx+14,hy-8)],mul(base,.5))
 elif style=='spider':
  for side in (-1,1):P(d,[(hx+side*7,hy-9),(hx+side*16,hy-20),(hx+side*12,hy-5)],accent)
 elif style=='claws':
  for side in (-1,1):P(d,[(hx+side*4,hy-13),(hx+side*9,hy-27),(hx+side*13,hy-14)],mul(skin,.76))
 elif style=='gavel':P(d,[(hx-13,hy-13),(hx,hy-24),(hx+13,hy-12)],mul(accent,.56))
 elif style=='bow':P(d,[(hx-12,hy-10),(hx-7,hy-20),(hx+4,hy-21),(hx+13,hy-10)],mul(base,.57))
 elif style=='fire':
  for s in (-1,0,1):P(d,[(hx+s*7-5,hy-12),(hx+s*7,hy-25+math.sin(p*math.tau+s)*3),(hx+s*7+5,hy-13)],mul(accent,.6),None)
 elif style=='ice':
  for s in (-1,0,1):P(d,[(hx+s*7-5,hy-12),(hx+s*7,hy-27-abs(s)*4),(hx+s*7+5,hy-12)],mul(accent,.8))
 elif style=='strings':P(d,[(hx-12,hy-4),(hx+12,hy-4),(hx+8,hy+6),(hx-8,hy+6)],mul(skin,.5))
 elif style=='raven':P(d,[(hx-13,hy-10),(hx,hy-24),(hx+15,hy-11)],mul(base,.5))
 elif style=='trident':
  for side in (-1,1):P(d,[(hx+side*9,hy-12),(hx+side*18,hy-23),(hx+side*12,hy-3)],mul(accent,.78))
 elif style=='hammer':
  for side in (-1,1):P(d,[(hx+side*10,hy-13),(hx+side*15,hy-20),(hx+side*19,hy-4)],mul(skin,.64))
 elif small:
  if style=='tech':rect(d,(hx-11,hy-4,hx+11,hy),mul(base,.5))
  if style=='engineer':rect(d,(hx-12,hy-12,hx+12,hy-8),mul(accent,.7))
  if style=='medic':rect(d,(hx-3,hy-17,hx+3,hy-10),'#c3e5cb')
  if style=='trickster':rect(d,(hx+5,hy-7,hx+13,hy-2),mul(accent,.7))
  if style=='scout':rect(d,(hx-13,hy-8,hx+13,hy-6),mul(accent,.75))
 # eyes / visor / face
 if small:
  rect(d,(hx-5,hy-2,hx-3,hy),mul(base,.55))
  rect(d,(hx+3,hy-2,hx+5,hy),mul(base,.55))
  rect(d,(hx-2,hy+6,hx+1,hy+7),mul(skin,.68))
 else:
  rect(d,(hx-7,hy-3,hx-2,hy),accent)
  rect(d,(hx+3,hy-3,hx+8,hy),accent)
  rect(d,(hx-5,hy-3,hx-4,hy-2),(249,247,239))
  if style in ('scythe','gavel','raven','strings'):line(d,[(hx-7,hy+7),(hx+6,hy+7)],mul(accent,.6),2)
 if action=='hurt':
  line(d,[(hx-13,hy-3),(hx+12,hy+9)],'#fb4d69',3)
 if action=='hook':
  line(d,[(12,Y(0)),(20,Y(20)),(32,Y(10)),(44,Y(20)),(52,Y(0))],rgb(accent,155),2)
 if action=='repair':
  for j in range(3):sparkle(d,46+j*4+math.sin(p*math.tau*2+j)*4,Y(43-j*4+math.sin(p*math.tau*3+j)*5),accent,1)
 if action=='heal':
  sparkle(d,48+math.sin(p*math.tau)*6,Y(34+math.cos(p*math.tau*3)*10),accent,2)
 if action=='ability':
  # particles reflect unique magical ability, no neon smooth blur
  for j in range(5):
   ang=p*math.tau*2+j*math.tau/5
   px=32+27*math.cos(ang);py=34+28*math.sin(ang)
   sparkle(d,px,py,mul(accent,.7),2)
 if not small:
  # full weapon silhouette; unique weapon per killer
  wx=49+x;wy=Y(31)-round(12*att)
  angle=-1.1*att + .12*math.sin(p*math.tau)
  def wpt(dx,dy):return (wx+dx*math.cos(angle)-dy*math.sin(angle),wy+dx*math.sin(angle)+dy*math.cos(angle))
  if style=='scythe':
   line(d,[wpt(-2,20),wpt(4,-29)],mul(skin,.7),3)
   P(d,[wpt(4,-29),wpt(-20,-26),wpt(-27,-17),wpt(-20,-31),wpt(-7,-37)],mul(skin,1.2))
  elif style=='dagger':
   line(d,[wpt(-3,13),wpt(8,-19)],mul(skin,.55),4)
   P(d,[wpt(8,-19),wpt(1,-14),wpt(12,-31)],mul(skin,1.2))
  elif style in ('hammer','gavel'):
   line(d,[wpt(0,17),wpt(1,-29)],mul(skin,.6),4)
   P(d,[wpt(-13,-34),wpt(17,-33),wpt(17,-21),wpt(-13,-21)],mul(skin,.93))
   line(d,[wpt(-10,-31),wpt(12,-31)],mul(accent,.8),2)
  elif style=='spider':
   for k in range(3):line(d,[wpt(1,9),wpt(6+k*4,-16-k*3)],accent,3)
  elif style=='claws':
   for k in range(3):line(d,[wpt(1+k*3,10),wpt(8+k*3,-11)],mul(accent,.8),2)
  elif style=='ghost':
   P(d,[wpt(-8,8),wpt(9,-24),wpt(14,-17),wpt(5,8)],mul(accent,.75))
  elif style=='bow':
   line(d,[wpt(0,-25),wpt(12,-10),wpt(12,13),wpt(0,24)],mul(skin,.7),3)
   line(d,[wpt(0,-25),wpt(0,24)],'#e7eee3',1)
   P(d,[wpt(-10,-4),wpt(6,-7),wpt(-10,0)],mul(accent,.8),None)
  elif style=='fire':
   P(d,[wpt(-5,12),wpt(-5,-14),wpt(12,-14),wpt(14,12)],mul(base,.58))
   for k in range(3):P(d,[wpt(k*5-3,-11),wpt(k*5,-29-5*math.sin(p*math.tau+k)),wpt(k*5+3,-11)],accent,None)
  elif style=='ice':
   P(d,[wpt(-7,9),wpt(0,-38),wpt(11,3)],mul(accent,1.16))
  elif style=='strings':
   for k in range(4):line(d,[wpt(0,-14),wpt(7+k*3,10+k*4)],mul(accent,.9),1)
  elif style=='raven':
   for k in range(3):P(d,[wpt(-4,4),wpt(9+k*5,-18-k*3),wpt(14,7)],mul(accent,.65),None)
  elif style=='saw':
   P(d,[wpt(-7,18),wpt(12,16),wpt(10,-24),wpt(-5,-22)],mul(base,.64))
   for k in range(6):rect(d,(*wpt(-7+k*3,-26),*wpt(-5+k*3,-22)),mul(accent,.82))
  elif style=='trident':
   line(d,[wpt(0,18),wpt(0,-34)],mul(skin,.83),3)
   for k in [-1,0,1]:line(d,[wpt(k*5,-24),wpt(k*6,-40)],accent,2)
 if action in ('idle','down','hurt','carry'):
  # a few restrained shifting pixels on garment folds: breathing, not static frames
  for j in (0,1):
   mx=27+round(math.sin(p*math.tau*(j+1)+j*1.1)*4)+j*8
   my=39+round(math.cos(p*math.tau*(2+j)+j)*3)
   rect(d,(mx,Y(my),mx+1,Y(my+1)),mul(accent,.42+j*.18))
 if action=='down':
  # ground shadow + blood indicator; knocked-down body flattened with torn fabric
  line(d,[(20,Y(62)),(43,Y(58))],(162,44,69,130),2)
 return im

def make_sheet(id, small=False):
 clips=CLIPS_S if small else CLIPS_K
 total=sum(clips.values()); rows=math.ceil(total/COLS)
 atlas=Image.new('RGBA',(FW*COLS,FH*rows))
 index=0; meta={};
 for action,n in clips.items():
  meta[action]={'start':index,'frames':n,'fps':24 if action in ('run','attack','walk','vault') else 18}
  for i in range(n):
   frame=character(id,action,i,n,small)
   atlas.alpha_composite(frame,((index%COLS)*FW,(index//COLS)*FH));index+=1
 path=CHARS/f'{id}.png';atlas.save(path,optimize=True)
 return {'id':id,'group':'survivor' if small else 'killer','file':f'assets/characters/{id}.png','width':FW,'height':FH,'columns':COLS,'rows':rows,'clips':meta,'frames':total,'bytes':path.stat().st_size}

# 80 unique 256x144 pixel-art MORI movie frames per killer (17.4 fps over 4.6sec).
MORI_FRAMES=80; MORI_COLS=8

def mori_frame(id,i):
 t=i/(MORI_FRAMES-1); name,accent,base,skin,hair,style=KILLERS[id]
 im=Image.new('RGBA',(MW,MH),(9,10,19,255));d=ImageDraw.Draw(im)
 rand=random.Random(seed_for(id)+i*233)
 # pixel-cinema background with parallax and abyss ruins
 rect(d,(0,0,255,78),(12,14,26));
 for j in range(8):
  xx=(j*47+seed_for(id)%33)%285-20
  rect(d,(xx,9,xx+9,107),mul(base,.46))
  rect(d,(xx-5,2,xx+14,12),mul(base,.62))
  rect(d,(xx+2,13,xx+4,93),mul(base,.83))
 rect(d,(0,107,255,143),(21,21,28))
 for j in range(9):line(d,[(128,105),(j*34-20,143)],(33,31,40),1)
 for yy in [115,125,138]:line(d,[(0,yy),(255,yy)],(36,33,45),1)
 # accent portal and dancing motes
 for j in range(22):
  x=(j*37+math.sin(t*4+j)*5+seed_for(id)%11)%256
  y=(j*23+seed_for(id)%41)%105
  sparkle(d,x,y,rgb(accent,110),1)
 # storyboard movements: entrance, confrontation, signature hit, abyss consumption
 approach=min(1,max(0,(t-.07)/.36)); kx=42+65*approach
 victimX=181-11*min(1,max(0,(t-.5)/.12))
 # victim animation and body fall begin after impact
 victim=character('lia','run' if t<.29 else 'hurt' if t<.69 else 'down',int(t*26)%20,20,True)
 if t>.72:
  # victim fades to black as darkness takes over; still composited for atmospheric effect
  victim.putalpha(victim.getchannel('A').point(lambda v:int(v*max(0,1-(t-.72)/.25))))
 # position actors; cutscene uses deliberately chunky 2x pixels
 vf=victim.resize((96,120),Image.Resampling.NEAREST)
 im.alpha_composite(vf,(int(victimX-45),int(16+10*max(0,(t-.61)/.28))))
 action='walk' if t<.29 else 'ability' if t<.55 else 'attack' if t<.72 else 'idle'
 kidx=int(t*29)%24
 kr=character(id,action,kidx,28,False).resize((112,140),Image.Resampling.NEAREST)
 im.alpha_composite(kr,(int(kx-57),7))
 d=ImageDraw.Draw(im)
 # staging flashes and attacks, distinctive for each killer
 impact=max(0,min(1,(t-.42)/.13)); strength=math.sin(min(1,impact)*math.pi/2)
 if t>.38 and t<.94:
  cx,cy=170,73
  if id=='reaper':
   r=8+strength*62; d.arc((cx-r,cy-r,cx+r,cy+r),183,340,fill=accent,width=5)
   for j in range(4):line(d,[(cx-45+j*9,cy+23),(cx+33+j*4,cy-15)],rgb(accent,180),2)
  elif id=='shadow':
   for j in range(10):
    sx=int(cx+math.cos(j*3.9)*strength*45);sy=int(cy+math.sin(j*2.4)*strength*35)
    P(d,[(sx,sy),(sx+rand.randint(6,13),sy-7),(sx+rand.randint(3,7),sy+9)],mul(accent,.6+j*.07),None)
  elif id=='brute':
   for j in range(8):
    x=(j-4)*19+cx;y=110-abs(j-4)*5
    line(d,[(x,118),(x+(j-4)*strength*6,y-20*strength)],mul(accent,.63),3)
   ellipse(d,(cx-55*strength,106-9*strength,cx+55*strength,111+5*strength),rgb(accent,100),accent,3)
  elif id=='weaver':
   for j in range(11):
    a=j*math.tau/11+t*4;xx=cx+math.cos(a)*(65*strength);yy=cy+math.sin(a)*(48*strength)
    line(d,[(cx,cy),(xx,yy)],mul(accent,.8),1)
    for k in range(3):
     b=(j+k*.38)*math.tau/11
     ellipse(d,(xx+math.cos(b)*3,yy+math.sin(b)*3,xx+math.cos(b)*3+3,yy+math.sin(b)*3+3),accent)
  elif id=='hunter':
   for j in range(6):
    off=j*9;line(d,[(cx-25-off,cy-28),(cx+25-off,cy+31)],accent,2)
    line(d,[(cx-18-off,cy-26),(cx+31-off,cy+23)],mul(accent,.7),1)
  elif id=='specter':
   for j in range(3):
    r=(16+j*16)*strength;ellipse(d,(cx-r,cy-r,cx+r,cy+r),rgb(accent,30),accent,2)
    for k in range(6):sparkle(d,cx+math.cos(k)*r,cy+math.sin(k)*r,accent,2)
  elif id=='judge':
   P(d,[(cx-25,cy-30-strength*31),(cx+25,cy-30-strength*31),(cx+34,cy-16),(cx-34,cy-16)],mul(accent,.86))
   for j in range(9):line(d,[(cx+j*7-27,cy+30),(cx+j*12-46,cy+32+strength*20)],accent,2)
  elif id=='huntress':
   for j in range(7):
    yy=cy-41+j*14;xx=85+strength*100
    line(d,[(xx-30,yy),(xx+15,yy)],mul(accent,.86),2)
    P(d,[(xx+16,yy-4),(xx+25,yy),(xx+16,yy+4)],accent,None)
  elif id=='pyre':
   for j in range(13):
    x=cx-50+j*9;h=17+strength*53+math.sin(j+t*18)*10
    P(d,[(x-5,110),(x,110-h),(x+5,110)],mul(accent,.5+(j%4)*.17),None)
  elif id=='frost':
   for j in range(14):
    a=j*math.tau/14;r=20+strength*53
    x=cx+math.cos(a)*r;y=cy+math.sin(a)*r*.7
    P(d,[(x-5,y+9),(x,y-15-strength*17),(x+6,y+10)],mul(accent,.6+j%3*.18),None)
  elif id=='puppet':
   for j in range(12):
    x=cx-48+j*9;yy=cy+math.sin(j+t*15)*17
    line(d,[(x,0),(x+math.sin(t*7+j)*6,yy)],mul(accent,.8),2)
    sparkle(d,x+math.sin(t*7+j)*6,yy,accent,2)
  elif id=='raven':
   for j in range(20):
    a=j*1.9+t*12;r=12+j*3*strength;x=cx+math.cos(a)*r;y=cy+math.sin(a)*r*.6
    P(d,[(x,y),(x-8,y-4),(x-5,y+6),(x+7,y+3)],mul(accent,.43+j%4*.14),None)
  elif id=='automaton':
   for j in range(6):
    rr=14+j*13*strength;d.arc((cx-rr,cy-rr,cx+rr,cy+rr),0,360,fill=accent,width=2)
   line(d,[(70,cy),(cx+66,cy)],accent,3)
   line(d,[(cx,10),(cx,132)],mul(accent,.9),2)
  elif id=='siren':
   for j in range(8):
    rr=18+j*11*strength;d.arc((cx-rr,cy-rr,cx+rr,cy+rr),10,170,fill=accent,width=2)
    d.arc((cx-rr,cy-rr,cx+rr,cy+rr),190,350,fill=accent,width=2)
 if .52<t<.61:
  alpha=int(120*math.sin((t-.52)/.09*math.pi))
  rect(d,(0,0,255,143),(255,230,240,max(0,alpha)))
 # the darkness swallows the defeated character, pixels get pulled into portal
 if t>.65:
  a=min(1,(t-.65)/.34)
  ellipse(d,(victimX-38*a,93-26*a,victimX+38*a,105+12*a),(6,3,13,210),mul(accent,.6),2)
  for j in range(22):
   aa=j*math.tau/22+t*4; rr=(10+j%5*4)*a
   px=victimX+math.cos(aa)*rr;py=99+math.sin(aa)*rr*.45
   sparkle(d,px,py,rgb(accent,int(180*a)),1+j%3)
 # film matte
 rect(d,(0,0,255,5),(2,3,9))
 rect(d,(0,138,255,143),(2,3,9))
 if t>.93:
  rect(d,(0,0,255,143),(3,4,10,int(255*(t-.93)/.07)))
 return im

def make_mori(id):
 rows=math.ceil(MORI_FRAMES/MORI_COLS)
 sheet=Image.new('RGBA',(MW*MORI_COLS,MH*rows))
 for i in range(MORI_FRAMES):
  frame=mori_frame(id,i)
  sheet.alpha_composite(frame,((i%MORI_COLS)*MW,(i//MORI_COLS)*MH))
 path=MORIS/f'{id}.png';sheet.save(path,optimize=True)
 return {'file':f'assets/moris/{id}.png','width':MW,'height':MH,'columns':MORI_COLS,'frames':MORI_FRAMES,'duration':4.6,'bytes':path.stat().st_size}

def contact_sheet():
 img=Image.new('RGB',(1200,780),(13,14,24));d=ImageDraw.Draw(img)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
 heading=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',27)
 d.text((30,13),'VESPER: ABISMO  |  PIXEL ART - 20 PERSONAGENS',font=heading,fill='#ffb4bd')
 ids=list(KILLERS)+list(SURVIVORS)
 for n,id in enumerate(ids):
  col=n%5;row=n//5
  x=20+col*235;y=64+row*168
  small=id in SURVIVORS;name,acc,_,_,_,_= (SURVIVORS if small else KILLERS)[id]
  for k,ac in enumerate(['idle','run','attack' if not small else 'repair']):
   fr=character(id,ac,(8+k*5)%24,24,small).resize((85,108),Image.Resampling.NEAREST)
   img.paste(fr,(x+k*72,y+7),fr)
  d.text((x+7,y+118),name.upper(),font=font,fill=acc)
  d.text((x+7,y+140),'SOBREVIVENTE' if small else 'ASSASSINO',font=font,fill='#99a4b8')
 img.save(ROOT/'PREVIA_PERSONAGENS.png')
 # storyboard mori previews for 14 killers (middle action frame)
 preview=Image.new('RGB',(1024,622),(8,9,17));dr=ImageDraw.Draw(preview)
 dr.text((20,12),'VESPER  |  14 MORIS ANIMADOS EM PIXEL ART',font=heading,fill='#efb8bd')
 for n,id in enumerate(KILLERS):
  x=(n%4)*256;y=53+(n//4)*139
  frame=mori_frame(id,51)
  preview.paste(frame,(x,y))
  dr.text((x+7,y+116),KILLERS[id][0].upper(),font=font,fill=KILLERS[id][1])
 preview.save(ROOT/'PREVIA_MORIS.png')

if __name__=='__main__':
 data={'version':1,'pixelArt':True,'size':[FW,FH],'characters':{},'moris':{},'metadata':{'killer_count':len(KILLERS),'survivor_count':len(SURVIVORS),'mori_frames':MORI_FRAMES}}
 for id in KILLERS:
  data['characters'][id]=make_sheet(id)
  print('KILLER',id,data['characters'][id]['frames'],flush=True)
 for id in SURVIVORS:
  data['characters'][id]=make_sheet(id,True)
  print('SURV',id,data['characters'][id]['frames'],flush=True)
 for id in KILLERS:
  data['moris'][id]=make_mori(id)
  print('MORI',id,MORI_FRAMES,flush=True)
 (ASSETS/'sprites.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 contact_sheet()
 print('TOTAL FRAMES',sum(v['frames'] for v in data['characters'].values())+sum(v['frames'] for v in data['moris'].values()))
