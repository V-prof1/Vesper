#!/usr/bin/env python3
"""Distinct anatomical pixel-art silhouettes and staged finishers for VESPER.
Runs after build_sprites.py and is intended as the canonical art generator.
No third-party assets or online API needed. Requires Pillow.
"""
import importlib.util, math, random, json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('vesper_base_art', ROOT/'tools/build_sprites.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.FW=96;b.FH=104;b.MORI_FRAMES=104
FW,FH=b.FW,b.FH
TAU=math.tau

def poly(d,xy,c,edge='#0a0b12',width=2):
 xy=[tuple(map(int,q)) for q in xy];d.polygon(xy,fill=c)
 if edge:d.line(xy+[xy[0]],fill=edge,width=width,joint='curve')
def line(d,xy,c,width=3):d.line([tuple(map(int,p)) for p in xy],fill=c,width=width,joint='curve')
def oval(d,xy,c,edge=None,width=1):d.ellipse(tuple(map(int,xy)),fill=c,outline=edge,width=width)
def rect(d,xy,c,edge=None):d.rectangle(tuple(map(int,xy)),fill=c,outline=edge)
def point(d,x,y,c,r=2):oval(d,(x-r,y-r,x+r,y+r),c)

def sprite(id,action,i,count,small=False):
 if small:
  # Six distinct survivors retain human movement, with extra inventory and detail.
  legacy=b.character_base(id,action,i,count,True)
  im=legacy.resize((75,94),Image.Resampling.NEAREST)
  out=Image.new('RGBA',(FW,FH))
  out.alpha_composite(im,(11,5));d=ImageDraw.Draw(out)
  phase=i/count;bob=round(math.sin(phase*TAU)*3)
  cols={'lia':'#f5a964','maya':'#7dcbf7','noah':'#83e5b4','erik':'#c99dfc','iris':'#f792bd','caio':'#e9c377'}
  col=cols[id]
  # Reflect the class item at the character's belt; items animate with movement.
  if id in ('lia','erik','iris'):
   rect(d,(62,54+bob,70,61+bob),'#a8c8dd','#1b2432')
   rect(d,(64,52+bob,68,55+bob),'#fff2ae')
   if action=='ability':poly(d,[(66,48),(84,43),(84,61)],'#f9f3b360',None)
  elif id in ('maya','noah'):
   rect(d,(61,54+bob,72,63+bob),'#e4eff1','#3c4a50')
   rect(d,(65,51+bob,69,65+bob),'#e54665')
   rect(d,(61,56+bob,72,59+bob),'#e54665')
  else:
   rect(d,(62,50+bob,72,65+bob),'#c5b984','#373737')
   line(d,[(65,54+bob),(71,58+bob)],'#5c4737',2)
  return out
 name,accent,base,skin,hair,style=b.KILLERS[id]
 dcol=b.mul(base,.65); pale=b.mul(skin,1.05); bright=b.mul(accent,1.15)
 p=i/max(1,count);w=math.sin(p*TAU);w2=math.sin(p*TAU*2);step=5*w if action=='walk' else 9*w if action=='run' else 1.5*w
 burst=math.sin(min(1,max(0,(p-.12)/.78))*math.pi) if action in ('attack','ability') else 0
 idle=math.sin(p*TAU)*1.7
 im=Image.new('RGBA',(FW,FH));d=ImageDraw.Draw(im)
 oval(d,(17,86,79,96),(2,4,12,80))
 # No universal humanoid puppet: each branch owns its entire anatomy.
 if id=='weaver':
  # Real arachnid: 8 articulated legs, abdomen, cephalothorax, 8 eyes and mandibles.
  for side in (-1,1):
   for j in range(4):
    phase=p*TAU+j*1.3+(0 if side==1 else math.pi)
    hip=(48+side*(12+j*2),49+(j-1.5)*8)
    knee=(48+side*(26+j*3),23+j*13+math.sin(phase)*(5 if action in ('walk','run') else 1))
    tip=(48+side*(42+j*1),14+j*21+math.cos(phase)*abs(step)*.8)
    line(d,[hip,knee,tip],b.mul(base,.36),8)
    line(d,[hip,knee,tip],b.mul(accent,.65),4)
    point(d,*knee,bright,2)
   # Rear spinneret branches
  oval(d,(23,42+idle,76,86+idle),b.mul(base,.45),'#140d20',3)
  for j in range(7):line(d,[(35+j*4,62+idle),(34+j*4,77+idle)],b.mul(accent,.42),2)
  oval(d,(30,23+idle,70,61+idle),b.mul(base,.75),b.mul(accent,.52),3)
  for row in range(2):
   for k in range(4):point(d,38+k*7,33+row*7+idle,bright,2 if row==0 else 3)
  for side in (-1,1):poly(d,[(48+side*9,53),(48+side*17,69+burst*9),(48+side*4,61)],pale)
  for k in range(5):point(d,32+k*8,58,accent,1)
 elif id=='hunter':
  # Full wolf monster on all fours, no human legs or torso.
  motion=step
  poly(d,[(12,53),(26,35-idle),(62,31-idle),(78,42),(73,64),(23,71)],b.mul(base,.68))
  for side in (0,1):
   for j in range(2):
    x=27+j*39; yy=58+side*4
    xx=x+(motion if j%2 else -motion)*(.8 if side else 1)
    line(d,[(x,yy),(xx+5,80-abs(step)*.35),(xx+2,87-abs(step)*.35)],b.mul(base,.38),9)
    rect(d,(xx-5,84-abs(step)*.35,xx+9,89-abs(step)*.35),pale)
  poly(d,[(56,35),(73,18),(89,22),(94,37),(88,57),(65,57)],b.mul(base,.52))
  poly(d,[(64,27),(67,10),(78,20)],pale)
  poly(d,[(80,22),(89,10),(90,28)],pale)
  poly(d,[(86,44),(95,48),(82,57),(70,55)],b.mul(skin,.77))
  point(d,76,32,bright,3);point(d,91,46,'#080a11',2)
  line(d,[(16,50),(5,33-2*w),(1,21-4*w)],b.mul(base,.58),10)
  if burst:poly(d,[(76,53),(90,54+burst*6),(87,64),(70,59)],'#b99e90')
 elif id=='raven':
  # Gigantic avian anatomy with beat-driven wings and talons.
  spread=math.sin(p*TAU*(2 if action in ('walk','run','ability') else 1))
  for side in (-1,1):
   wing=[(48+side*8,48),(48+side*(28+burst*6),34-spread*9),(48+side*43,10-spread*12),(48+side*41,51+spread*4),(48+side*32,70),(48+side*15,59)]
   poly(d,wing,b.mul(base,.46),b.mul(accent,.35))
   for j in range(6):
    line(d,[(48+side*(17+j*3),43),(48+side*(30+j*2),57+j*4+spread*2)],b.mul(accent,.42),2)
  oval(d,(31,28+idle,68,75+idle),b.mul(base,.60),'#090a13',3)
  oval(d,(35,14+idle,66,47+idle),b.mul(base,.83))
  poly(d,[(61,31),(88,38),(61,45)],b.mul(skin,.94))
  point(d,55,29+idle,bright,3)
  for j in (-1,1):line(d,[(48+j*9,72),(48+j*13+step,88),(48+j*22+step,91)],pale,4)
  for j in range(5):poly(d,[(37+j*5,67),(29+j*7,86),(43+j*5,82)],dcol,None)
 elif id=='specter':
  # Hovering smoky wraith; feet do not exist.
  for j in range(8):
   y=29+j*7;aa=math.sin(p*TAU+j*.8)
   poly(d,[(48-17+aa*4,y),(48+17-aa*4,y),(48+24+aa*6,y+10),(48+aa*6,y+13),(48-22+aa*5,y+10)],b.mul(base,.26+j*.045),None)
  poly(d,[(34,25),(47,11+idle),(63,27),(70,54),(78,83+2*w),(56,72),(45,92),(30,77),(19,86),(26,46)],b.mul(base,.62))
  oval(d,(35,19+idle,64,49+idle),b.mul(base,.32))
  for side in (-1,1):point(d,48+side*8,35+idle,bright,4)
  for j in range(9):point(d,12+(j*19)%75,46+((j*11)%30)+3*w,b.mul(accent,.7),1+j%2)
 elif id=='shadow':
  # Tall split silhouette made of shifting ribbons, no regular arms.
  for side in (-1,1):
   for j in range(4):
    xx=48+side*(6+j*6);dx=side*(14+math.sin(p*TAU+j)*10)
    poly(d,[(xx,27),(xx+dx,49+j*9),(xx+dx-side*8,90)],b.mul(base,.35+j*.07),None)
  poly(d,[(34,18),(47,8+idle),(63,19),(70,50),(61,78),(49,73),(33,89),(25,52)],b.mul(base,.58))
  oval(d,(36,16+idle,62,49+idle),'#080b19',b.mul(accent,.65),2)
  line(d,[(38,34),(57,33)],bright,3)
  for j in range(6):line(d,[(29+j*7,48),(27+j*5+w*8,82)],b.mul(accent,.44),2)
 elif id=='siren':
  # Aquatic leviathan with a serpentine coiled tail and fins.
  tail=[(56,45),(67,55),(68+6*w,71),(58,83),(34,88),(20,75),(7,79),(26,91),(46,94),(75,81),(86,59),(74,42)]
  poly(d,tail,b.mul(base,.58),b.mul(accent,.46))
  for j in range(6):line(d,[(35+j*6,76),(26+j*7,88)],b.mul(accent,.68),2)
  poly(d,[(39,41),(34,24),(48,15),(63,25),(60,45)],b.mul(base,.74))
  for side in (-1,1):
   poly(d,[(48+side*17,32),(48+side*29,13),(48+side*25,49)],b.mul(accent,.7))
   line(d,[(48+side*9,40),(48+side*25,58+step*.2)],pale,5)
  oval(d,(37,15,59,37),b.mul(skin,.85))
  point(d,53,26,bright,3)
 elif id=='automaton':
  # Tracked machine: chassis, treads, central reactor, tool arms, pistons.
  rect(d,(22,63,75,85),'#262a30','#b4a9a0')
  for j in range(7):oval(d,(23+j*7,74,32+j*7,84),b.mul(skin,.65),'#101218')
  poly(d,[(25,29),(38,18),(64,18),(76,29),(78,69),(20,69)],'#45535b')
  for j in range(5):line(d,[(29+j*9,28),(29+j*9,66)],b.mul(skin,.55),2)
  oval(d,(34,30,62,58),'#202630',pale,3);point(d,48,44,accent,8)
  rect(d,(36,13,61,29),'#62717b','#131823');line(d,[(37,21),(62,21)],bright,5)
  for side in (-1,1):
   line(d,[(48+side*21,38),(48+side*36,51+step*.4),(48+side*43,39+burst*8)],'#89909c',8)
   oval(d,(48+side*44-6,36+burst*8,48+side*44+6,48+burst*8),accent)
 elif id=='brute':
  # Thick ogre with offset shoulder and hand-sized hammer.
  for side in (-1,1):
   x=48+side*17
   line(d,[(x,57),(x+side*(6+step*.38),80),(x+side*(8+step*.5),91)],'#343137',15)
  poly(d,[(13,35),(29,16),(69,17),(90,38),(80,76),(16,77)],b.mul(base,.63))
  poly(d,[(13,33),(21,19),(38,27),(30,53),(5,55)],b.mul(skin,.6))
  poly(d,[(71,26),(86,18),(95,37),(93,59),(70,56)],b.mul(skin,.55))
  oval(d,(34,12,63,40),b.mul(skin,.75),'#15131a',3)
  line(d,[(40,28),(58,28)],bright,4)
  for j in range(4):line(d,[(23+j*15,44),(28+j*14,55)],b.mul(skin,.8),3)
  line(d,[(86,49),(89+burst*5,75)],'#57443a',9)
  rect(d,(69,72+burst*4,96,91+burst*4),'#82838e','#15131a')
 elif id=='judge':
  # Floating stone tribunal with scales, not a standard human.
  for side in (-1,1):
   poly(d,[(48+side*22,36),(48+side*34,50),(48+side*26,75),(48+side*12,60)],'#66535b')
   line(d,[(48+side*27,46),(48+side*43,57)],'#b49a81',4)
  poly(d,[(27,22),(48,3+idle),(69,22),(76,55),(58,82),(38,82),(20,55)],'#514148')
  poly(d,[(31,25),(48,13),(65,25),(61,46),(35,46)],b.mul(skin,.58))
  line(d,[(35,34),(61,34)],bright,4)
  for j in range(7):line(d,[(28+j*7,53),(26+j*7,73)],b.mul(accent,.54),2)
  for side in (-1,1):
   x=48+side*33
   line(d,[(x,36),(x,63)],pale,2)
   line(d,[(x-12,63),(x+12,63)],pale,3)
   poly(d,[(x-12,63),(x-7,75),(x+7,75),(x+12,63)],accent)
 elif id=='puppet':
  # Suspended wooden doll, joint balls and external strings.
  yy=idle*2
  line(d,[(48,0),(48,25+yy)],'#bcb4bd',2)
  for side in (-1,1):line(d,[(48+side*18,5),(48+side*21,57+step*.5)],'#cbd0e2',2)
  rect(d,(18,1,78,5),'#807787');rect(d,(45,4,51,21),'#afa9b7')
  for side in (-1,1):
   line(d,[(48+side*12,43),(48+side*(17+step*.4),71)],'#8a5269',7)
   oval(d,(48+side*16-5,66,48+side*16+5,77),pale,'#392a35')
   line(d,[(48+side*16,71),(48+side*20+step,89)],'#ad8a85',6)
   line(d,[(48+side*15,39),(48+side*28,58+step)],'#a47a81',5)
   point(d,48+side*16,50,accent,3)
  poly(d,[(35,33),(60,33),(66,67),(31,67)],'#664758')
  oval(d,(36,14+yy,61,38+yy),'#d3b7ab','#43303c',3)
  for x in (42,54):point(d,x,26+yy,bright,2)
  line(d,[(43,34),(54,34)],'#7c3347',2)
 elif id=='pyre':
  # Living furnace with molten core, flaming arms, bottom smoke.
  for j in range(7):
   x=22+j*8;flame=12+abs(math.sin(p*TAU+j))*22+(burst*16)
   poly(d,[(x-7,57),(x,57-flame),(x+7,60)],b.mul(accent,.58+(j%3)*.2),None)
  poly(d,[(29,35),(39,17),(61,17),(72,35),(68,71),(28,71)],'#64342a')
  rect(d,(36,36,62,61),'#251c22',b.mul(skin,.67))
  poly(d,[(41,58),(48,31),(57,57)],bright,None)
  for side in (-1,1):
   line(d,[(48+side*20,41),(48+side*33,58+step*.3)],'#a3492b',10)
   poly(d,[(48+side*31,55),(48+side*41,44-burst*13),(48+side*42,66)],accent,None)
  for j in range(7):point(d,28+j*7,74+math.sin(p*TAU+j)*4,accent,2)
  oval(d,(39,14,59,35),'#302129');line(d,[(42,25),(56,25)],bright,4)
 elif id=='frost':
  # Crystal beast: spiked mountain limbs and snowflake heart.
  for side in (-1,1):
   for j in range(3):
    x=48+side*(8+j*10)
    poly(d,[(x,49),(x+side*13,17-j*5),(x+side*(14+j*2),68)],b.mul(accent,.5+j*.15))
  poly(d,[(48,5+idle),(65,28),(72,61),(62,77),(50,91),(31,68),(26,27)],b.mul(base,.56))
  for j in range(4):poly(d,[(29+j*11,45),(34+j*11,24),(41+j*10,53)],pale,None)
  point(d,48,45,bright,7);line(d,[(36,28),(60,28)],'#e3f9fa',3)
  for j in range(10):point(d,10+(j*13)%80,27+(j*17)%65,pale,1)
 elif id=='huntress':
  # Long-legged avian ranger with antlered mask, cloak, separated bow.
  poly(d,[(28,26),(50,9+idle),(64,27),(72,77),(54,91),(23,74)],dcol)
  for side in (-1,1):
   line(d,[(48+side*10,55),(48+side*14+step,90)],b.mul(skin,.5),6)
   line(d,[(48+side*10,31),(48+side*22,56)],pale,5)
   poly(d,[(48+side*5,24),(48+side*17,5),(48+side*20,29)],accent,None)
  oval(d,(35,13,63,42),'#c5d4bc','#162226',3)
  point(d,41,31,bright,3);point(d,56,31,bright,3)
  line(d,[(78,20),(88,47),(76,79)],pale,4)
  line(d,[(78,20),(76,79)],'#f6eee2',2)
  if action in ('attack','ability'):line(d,[(48,44),(90,44-burst*4)],accent,3)
 elif id=='reaper':
  # Skeletal scythe-bearing thing with vertebrae, hollow rib cage and ragged hood.
  for side in (-1,1):
   poly(d,[(48+side*12,45),(48+side*25,59),(48+side*37,92),(48+side*8,85)],dcol)
   line(d,[(48+side*7,67),(48+side*20+step*.5,91)],pale,5)
  poly(d,[(25,30),(35,12+idle),(59,12+idle),(72,31),(78,79),(58,92),(48,78),(28,92),(18,78)],b.mul(base,.5))
  oval(d,(32,19,64,50),'#0c101a','#888c9d',3)
  for side in (-1,1):point(d,48+side*9,34,bright,4)
  for j in range(4):line(d,[(32,50+j*6),(64,50+j*6)],b.mul(skin,.53),2)
  line(d,[(80,80),(79-burst*9,8)],'#998e94',5)
  poly(d,[(79-burst*9,8),(56-burst*10,17),(48-burst*12,32),(62-burst*8,8),(73-burst*5,2)],pale)
 # Face / attack highlights differentiating from idle; never morph silhouettes into human base.
 if action in ('attack','ability'):
  for j in range(5):
   a=(j*1.3+p*TAU);xx=48+math.cos(a)*(24+burst*21);yy=49+math.sin(a)*(18+burst*25)
   point(d,xx,yy,bright,1+j%2)
 if action=='hurt':
  for j in range(5):line(d,[(38+j*5,16),(32+j*4,24)],'#ff7c9b',2)
 # Material detail pass: weathered metal, chitin, fur, icy facets, rags, bones.
 # Random spatial positions remain fixed for each body, not independently flashing.
 palette=im.load();seed=random.Random(sum(ord(c)*(j+1) for j,c in enumerate(id))+37)
 for k in range(240):
  xx=seed.randrange(6,90);yy=seed.randrange(9,89)
  col=palette[xx,yy]
  if col[3]<230 or max(col[:3])<49:continue
  fac=.75 if (xx+yy)%5 else 1.33
  if id in ('weaver','automaton','frost','judge'):fac=1.3 if (xx+yy)%3==0 else .76
  if id in ('hunter','raven','reaper','specter'):fac=.78 if (xx+yy)%4 else 1.24
  rr,gg,bb=tuple(max(0,min(255,int(v*fac))) for v in col[:3]);
  if xx>53 and yy>36: rr,gg,bb=int(rr*.88),int(gg*.88),int(bb*.9)
  rect(d,(xx,yy,xx+seed.randint(1,2),yy+seed.randint(1,2)),(rr,gg,bb,255),None)
 # Extra high-contrast pixel highlights follow the main anatomical features.
 if id=='weaver':
  for side in (-1,1):
   for j in range(3):line(d,[(48+side*(12+j*4),57),(48+side*(19+j*5),61)],b.mul(accent,.95),1)
 elif id=='hunter':
  for j in range(7):line(d,[(20+j*7,40),(24+j*7,45)],b.mul(accent,.7),2)
 elif id=='automaton':
  for xx in range(28,76,9):point(d,xx,32,bright,1)
 elif id=='pyre':
  for j in range(8):point(d,28+j*5,67+math.sin(p*TAU+j)*4,bright,1)
 elif id=='brute':
  for j in range(8):line(d,[(17+j*8,52),(19+j*8,58)],b.mul(skin,.75),2)
 return im

b.character_base=b.character
b.character=sprite

# Cinematic moris are performed by each anatomy, not a universal stick-figure.
# Distinct poses across 104 frames: approach -> seize -> strike -> consequence -> abyss.
def finisher(id,i):
 t=i/max(1,b.MORI_FRAMES-1)
 acc=b.KILLERS[id][1];base=b.KILLERS[id][2]
 im=Image.new('RGBA',(b.MW,b.MH),(8,9,16,255));d=ImageDraw.Draw(im)
 for j in range(7):
  x=18+j*40;rect(d,(x,17,x+12,110),b.mul(base,.30));rect(d,(x+3,20,x+6,105),b.mul(base,.45))
 rect(d,(0,107,255,143),(24,24,32))
 for j in range(11):line(d,[(128,105),(j*27,142)],(41,36,48),1)
 # Atmosphere, spotlight and cinematic letterbox.
 for j in range(20):
  xx=(j*37+i*2)%256;yy=(j*19+i%5)%104
  point(d,xx,yy,b.rgb(acc,95),1+j%2)
 a=max(0,min(1,(t-.05)/.36)); kx=32+78*a
 attack=t>.40 and t<.70
 # The victim actively struggles / falls. Different behavior in the aftermath.
 vx=187-(t>.57)*min(20,(t-.57)*90)
 if id in ('weaver','specter','puppet','siren'):
  vy=0 if t<.38 else -min(27,(t-.38)*54)
 elif id=='brute':vy=min(32,max(0,(t-.48)*130))
 else:vy=0
 sc=1.12 if id in ('brute','weaver','hunter','raven') else .97
 kclip='run' if t<.32 else 'ability' if t<.49 else 'attack' if t<.72 else 'idle'
 k=b.character(id,kclip,int(t*50)%24,24,False).resize((round(FW*sc),round(FH*sc)),Image.Resampling.NEAREST)
 im.alpha_composite(k,(int(kx-FW*sc*.5),int(20+(1-sc)*10)))
 sclip='run' if t<.38 else 'hurt' if t<.73 else 'down'
 surv=b.character('lia',sclip,int(t*52)%24,24,True)
 if t>.84:
  surv.putalpha(surv.getchannel('A').point(lambda v:round(v*max(0,1-(t-.84)/.15))))
 if t>.68 and id not in ('specter','weaver','puppet','siren'):
  surv=surv.rotate(-min(75,(t-.68)*350),Image.Resampling.NEAREST,expand=False)
 im.alpha_composite(surv,(int(vx-42),int(24+vy)))
 d=ImageDraw.Draw(im)
 intensity=max(0,min(1,(t-.39)/.22))
 if id=='weaver':
  # Eight legs envelop the victim -> cocoon pulls upward into the web.
  for j in range(11):
   off=j*12;line(d,[(128+off%44,0),(vx-25+(j*7)%58,43+vy+intensity*45)],b.mul(acc,.55+j%3*.16),2)
  if t>.55:
   for rr in (11,22,31):oval(d,(vx-rr,56+vy-rr,vx+rr,56+vy+rr),None,b.mul(acc,.85),2)
   for j in range(8):
    ang=j*TAU/8;line(d,[(vx,56+vy),(vx+math.cos(ang)*36,56+vy+math.sin(ang)*35)],b.mul(acc,.70),2)
 elif id=='hunter':
  # Quadruped leap onto the victim, then retreat after the takedown.
  if t>.38:
   poly(d,[(132,48),(vx-14,49),(vx+5,63),(130,64)],b.mul(acc,.62),None)
  if t>.58:
   for j in range(3):line(d,[(vx-31+j*7,43),(vx-14+j*7,74)],acc,3)
 elif id=='brute':
  # Heavy monster raises a massive hammer and slams the ground by the victim.
  if t>.4:
   hh=14 if t<.56 else 72
   rect(d,(vx-30,hh,vx+25,hh+16),'#a69b9a','#13141c')
   rect(d,(vx-5,hh+13,vx+1,102),'#564842')
  if t>.61:
   for j in range(9):line(d,[(vx,105),(vx+(j-4)*21,103+(j%3)*12)],b.mul(acc,.65),3)
 elif id=='reaper':
  # Sweeping execution arc, then a visible collapsing silhouette.
  if t>.42:
   r=15+70*intensity;d.arc((vx-r,65-r,vx+r,65+r),175,345,fill=acc,width=5)
   line(d,[(110,87),(vx+28,43)],b.mul(acc,.78),3)
 elif id=='shadow':
  # Three copies cross the victim; each produces a discrete slash.
  if t>.40:
   for j in range(3):
    xx=vx-38+j*24;yy=37+j*12
    poly(d,[(xx,yy),(xx+15,yy-15),(xx+18,yy+23)],b.mul(base,.7),None)
    line(d,[(xx-5,yy+22),(xx+20,yy-17)],acc,3)
 elif id=='specter':
  # Wraith draws out a soul-shaped light; body sinks into blackness.
  if t>.48:
   for j in range(7):
    q=(t-.48)*150
    oval(d,(vx-22+j*6,57-q-j*2,vx-12+j*6,70-q-j*2),b.rgb(acc,160))
 elif id=='judge':
  # Chains hold the victim, a hanging scale passes judgement.
  for j in (-1,1):
   line(d,[(vx+j*16,3),(vx+j*19,45+vy)],b.mul(acc,.77),3)
  if t>.55:rect(d,(vx-29,65,vx+29,77),b.mul(acc,.83))
 elif id=='huntress':
  # Archer draws, three magical arrows converge before the finale.
  if t>.44:
   for j in range(3):
    y=43+j*17;start=135+int((t-.44)*145)
    line(d,[(start,y),(vx+6,y)],acc,3)
    poly(d,[(vx+6,y),(vx-5,y-4),(vx-5,y+4)],b.mul(acc,.8),None)
 elif id=='pyre':
  # Flames ignite at the floor and consume a shadow, leaving embers.
  if t>.46:
   for j in range(11):
    xx=vx-33+j*7;h=max(0,54*intensity)+math.sin(j+t*32)*8
    poly(d,[(xx-6,112),(xx,112-h),(xx+7,112)],b.mul(acc,.52+j%3*.18),None)
 elif id=='frost':
  # Crystals grow around the victim, cage closes and fractures into shards.
  if t>.45:
   for j in range(9):
    xx=vx-39+j*10;hh=24+58*intensity*(1 if j%2 else .7)
    poly(d,[(xx-6,113),(xx,113-hh),(xx+6,113)],b.mul(acc,.52+j%3*.15),None)
   if t>.7:
    for j in range(12):
     ang=j*TAU/12;line(d,[(vx,65),(vx+math.cos(ang)*74,vx*.1+50+math.sin(ang)*45)],acc,2)
 elif id=='puppet':
  # Control strings lift arms and legs against the victim's will.
  for j in range(6):
   sx=vx-24+j*10;line(d,[(sx,0),(sx+math.sin(t*16+j)*9,59+vy)],b.mul(acc,.8),2)
  if t>.62:rect(d,(vx-24,18,vx+25,25),'#5c475b')
 elif id=='raven':
  # Swarm of distinct bird sprites forms a moving eclipse around target.
  if t>.38:
   for j in range(22):
    angle=t*14+j*2.6;rad=8+j*2*intensity;xx=vx+math.cos(angle)*rad;yy=66+math.sin(angle)*rad*.6
    poly(d,[(xx,yy),(xx-10,yy-4),(xx-7,yy+6),(xx+6,yy+5)],b.mul(acc,.55+j%4*.12),None)
 elif id=='automaton':
  # A mechanical claw grips; an industrial beam completes the kill.
  if t>.43:
   line(d,[(122,38),(vx,48)],'#b2bbc1',10)
   oval(d,(vx-17,36,vx+17,69),'#67747d',b.mul(acc,.92),4)
  if t>.60:rect(d,(vx-5,8,vx+7,113),b.rgb(acc,200))
 elif id=='siren':
  # Musical pressure waves spiral and drag the victim into abyss.
  if t>.45:
   for j in range(9):
    rr=(17+j*9)*intensity;oval(d,(vx-rr,72-rr*.7,vx+rr,72+rr*.7),None,b.mul(acc,.5+j%3*.15),2)
   for j in range(5):
    poly(d,[(vx+j*8-24,99),(vx+j*7-30,66-intensity*21),(vx+j*7-20,102)],b.mul(base,.9),None)
 if t>.73:
  # Common established game mechanic: defeated characters are swallowed by darkness.
  aa=(t-.73)/.27
  oval(d,(vx-30*aa,109-21*aa,vx+30*aa,113+7*aa),'#05040c',acc,2)
  for j in range(12):
   a=j*TAU/12+t*6;rr=27*aa;point(d,vx+math.cos(a)*rr,102+math.sin(a)*rr*.45,acc,1+j%2)
 if .54<t<.61:
  k=round(80*math.sin((t-.54)/.07*math.pi));rect(d,(0,0,255,143),(b.HEX(acc)[0],b.HEX(acc)[1],b.HEX(acc)[2],k))
 rect(d,(0,0,255,6),'#050510');rect(d,(0,138,255,143),'#050510')
 if t>.96:rect(d,(0,0,255,143),(2,3,9,round(255*(t-.96)/.04)))
 return im

b.mori_frame=finisher

def build():
 data={'version':2,'pixelArt':True,'size':[b.FW,b.FH],'characters':{},'moris':{},'metadata':{'killer_count':len(b.KILLERS),'survivor_count':len(b.SURVIVORS),'mori_frames':b.MORI_FRAMES,'anatomy':'14 distinct bodies, 104 animated finisher frames each'}}
 for id in b.KILLERS:
  data['characters'][id]=b.make_sheet(id)
  print('KILLER',id,data['characters'][id]['frames'],flush=True)
 for id in b.SURVIVORS:
  data['characters'][id]=b.make_sheet(id,True)
  print('SURV',id,data['characters'][id]['frames'],flush=True)
 for id in b.KILLERS:
  data['moris'][id]=b.make_mori(id)
  print('MORI',id,b.MORI_FRAMES,flush=True)
 (b.ASSETS/'sprites.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 b.contact_sheet()
 print('COMPLETE:',sum(v['frames'] for v in data['characters'].values())+sum(v['frames'] for v in data['moris'].values()),'frames')
if __name__=='__main__':build()