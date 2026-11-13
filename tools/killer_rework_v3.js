/* VESPER: ABISMO 3.0 — 42 killer powers, six additional handcrafted arenas,
   discrete stealth perception and carry-drop. Runs inside the engine closure. */
const V3_ABILITIES={
 reaper:[['COLHEITA CIRCULAR',9,'reap'],['SINO DOS MORTOS',16,'deathbell'],['RUNAS DA FOICE',14,'deathrune']],
 shadow:[['PASSO DA SOMBRA',8,'shadowstep'],['INVISIBILIDADE',20,'darkveil'],['DUPLICATA',13,'shadowclone']],
 brute:[['MARTELO TITÂNICO',10,'hammer'],['RUGIDO DE GUERRA',16,'warroar'],['TERREMOTO',19,'quakev3']],
 weaver:[['SALTO ARACNÍDEO',10,'spiderleap'],['OLHOS DA TEIA',14,'websight'],['CASULO ADESIVO',12,'cocoon']],
 hunter:[['CORRIDA PREDADORA',8,'predatorrun'],['FARO DO SANGUE',14,'bloodscent'],['UIVO DA MATILHA',18,'wolfhowl']],
 specter:[['PORTAL ESPECTRAL',13,'hauntport'],['CORPO ETÉREO',23,'specterveil'],['ECOS DO ALÉM',14,'ghostecho']],
 judge:[['MARCA DA SENTENÇA',9,'sentence'],['CORRENTES DE CULPA',16,'chains'],['VEREDITO PROFANO',19,'verdict']],
 huntress:[['FLECHA PRECISA',7,'precisearrow'],['OLHO DE ÁGUIA',15,'eaglesight'],['CHUVA DE FLECHAS',17,'arrowrain']],
 pyre:[['PAREDE DE CHAMAS',14,'firewall'],['COMBUSTÃO VIVA',14,'combustion'],['METEORO INFERNAL',11,'meteor']],
 frost:[['ESPINHOS DE GELO',12,'icespikes'],['NEVASCA PERPÉTUA',16,'snowstorm'],['ESTILHAÇOS',9,'frostshards']],
 puppet:[['FIOS CORTANTES',9,'cutthreads'],['TROCA DE CORPOS',14,'puppetswap'],['FALSA VÍTIMA',12,'falsevictim']],
 raven:[['VOO RASANTE',7,'ravenflight'],['OLHOS DOS CORVOS',13,'ravenscout'],['BANDO ASSASSINO',12,'ravenmurder']],
 automaton:[['PULSO ELETROMAGNÉTICO',14,'emp'],['RADAR DE ALVOS',15,'radar'],['SENTINELA',19,'sentry']],
 siren:[['SUSSURRO HIPNÓTICO',13,'whisper'],['CANTO ATORDOANTE',16,'song'],['ONDA ABISSAL',11,'tidalwave']]
};
let v3Fx=[],v3Zones=[];
const v3Colors={reap:'#fa526a',deathbell:'#ea7395',deathrune:'#ea415f',shadowstep:'#947dff',darkveil:'#6e65cb',shadowclone:'#aa83ff',hammer:'#ffb57c',warroar:'#faab54',quakev3:'#fb8558',spiderleap:'#d8a6ff',websight:'#f1d0ff',cocoon:'#ba70ff',predatorrun:'#ff9f66',bloodscent:'#ff5e79',wolfhowl:'#e9ab79',hauntport:'#9ab7ff',specterveil:'#a7b3ff',ghostecho:'#7787ff',sentence:'#ffbc7f',chains:'#cc9de9',verdict:'#fcce7b',precisearrow:'#adfbe6',eaglesight:'#89e9c7',arrowrain:'#9ce5c2',firewall:'#ff763d',combustion:'#ffb14d',meteor:'#ff5b36',icespikes:'#83dffc',snowstorm:'#b7eeff',frostshards:'#b0dbff',cutthreads:'#e5aad8',puppetswap:'#c6b0ff',falsevictim:'#c58be2',ravenflight:'#a99afe',ravenscout:'#9995ed',ravenmurder:'#bc97ff',emp:'#ffe689',radar:'#c7ed93',sentry:'#fbe39c',whisper:'#6dd6d7',song:'#9aeef0',tidalwave:'#53cbd6'};
function v3Reset(){v3Fx=[];v3Zones=[];}
function v3Pulse(type,x,y,r=170,duration=.75,dir=0){v3Fx.push({type,x,y,r,dir,t:duration,max:duration,color:v3Colors[type]||killer().color});if(v3Fx.length>90)v3Fx.shift();}
function v3Zone(type,x,y,r,duration,extra={}){v3Zones.push({type,x,y,r,t:duration,max:duration,hit:new Map(),...extra});if(v3Zones.length>25)v3Zones.shift();v3Pulse(type,x,y,r,.65);}
function v3VisibleBots(maxDistance=700){return bots.filter(s=>survivorLive(s)&&dist(s,player)<maxDistance&&lineClear(s,player,12));}
function v3ArcHit(radius,angle,arc,root=0,doDamage=true){let hit=0;for(const s of bots)if(survivorLive(s)&&dist(s,player)<radius&&lineClear(s,player,10)){
 const a=Math.atan2(s.y-player.y,s.x-player.x),d=Math.atan2(Math.sin(a-angle),Math.cos(a-angle));
 if(Math.abs(d)<=arc){if(doDamage)hitBot(s,true);s.root=Math.max(s.root,root);s.fear=Math.max(s.fear,2);hit++;}}
 return hit;
}
function v3Reveal(duration,predicate=()=>true){enemySense=Math.max(enemySense,duration);for(const s of bots)if(survivorLive(s)&&predicate(s))s.mark=Math.max(s.mark||0,duration);}
function v3StartStealth(seconds){player.stealth=Math.max(player.stealth,seconds);player.dashing=0;aiPings=[];
 for(const s of bots)if(s.brain&&survivorLive(s)){
  const b=s.brain;b.knownTimer=0;b.knownAge=99;b.knownX=-10000;b.knownY=-10000;b.knownVX=0;b.knownVY=0;
  b.alert=0;b.sawPlayer=false;b.sawUntil=0;b.react=0;b.orderUntil=0;b.order='';b.panic=0;s.fear=0;
  s.target=null;s.pathTo='';s.loopTimer=0;
 }
}
function v3MakeDash(mob,time,speedBoost=0){player.dashing=time;player.dashKind=mob;player.dashHit=false;player.lastSafe={x:player.x,y:player.y};player.stealth=0;if(speedBoost)player.speedBoost=Math.max(player.speedBoost,speedBoost);}
function v3SafeTeleport(x,y,maxRange){let vx=x-player.x,vy=y-player.y,d=Math.hypot(vx,vy)||1;
 if(d>maxRange){x=player.x+vx/d*maxRange;y=player.y+vy/d*maxRange;}
 for(let i=0;i<16;i++){let a=i*TAU/16,rr=i?Math.ceil(i/4)*31:0,tx=clamp(x+Math.cos(a)*rr,36,MW-36),ty=clamp(y+Math.sin(a)*rr,36,MH-36);
 if(!killerCollision(tx,ty,25)){const ox=player.x,oy=player.y;player.x=tx;player.y=ty;v3Pulse('hauntport',ox,oy,90,.6);v3Pulse('hauntport',tx,ty,140,.7);return true;}}
 return false;
}
function v3CastEffect(type){const k=killer(),a=player.angle,front=(r)=>({x:player.x+Math.cos(a)*r,y:player.y+Math.sin(a)*r});
 switch(type){
 case 'reap':v3ArcHit(205,a,1.25,0,true);v3Pulse(type,player.x,player.y,210,.60,a);break;
 case 'deathbell':v3Reveal(6,s=>s.state==='injured'||dist(s,player)<590);for(const s of bots)if(survivorLive(s)&&dist(s,player)<460){s.fear=Math.max(s.fear,3);s.slow=Math.max(s.slow,2)}v3Pulse(type,player.x,player.y,530,1.25);break;
 case 'deathrune':{let p=front(160);v3Zone(type,p.x,p.y,105,24,{trigger:'root',strength:2.8});break;}
 case 'shadowstep':v3MakeDash('phase',.43);v3Pulse(type,player.x,player.y,115,.5,a);break;
 case 'darkveil':v3StartStealth(13);v3Pulse(type,player.x,player.y,170,.9);break;
 case 'shadowclone':{let p=front(130);traps.push({x:p.x,y:p.y,life:24,r:295,armed:0,type:'decoy'});v3Pulse(type,p.x,p.y,120,1);break;}
 case 'hammer':v3ArcHit(175,a,.78,1.25,true);for(const p of pallets)if(p.dropped&&!p.destroyed&&dist(p,player)<200){p.destroyed=true;p.dropped=false;}v3Pulse(type,front(85).x,front(85).y,190,.6,a);shake=Math.max(shake,9);break;
 case 'warroar':for(const s of bots)if(survivorLive(s)&&dist(s,player)<505){s.slow=Math.max(s.slow,5);s.fear=Math.max(s.fear,5)}v3Pulse(type,player.x,player.y,510,1.0);break;
 case 'quakev3':for(const s of bots)if(survivorLive(s)&&dist(s,player)<270){s.root=Math.max(s.root,2.1);s.slow=5}for(const g of generators)if(!g.complete&&dist(g,player)<300){g.jam=Math.max(g.jam,6);g.progress=Math.max(0,g.progress-.04)}v3Pulse(type,player.x,player.y,315,1);shake=14;break;
 case 'spiderleap':{const p=front(345);v3SafeTeleport(p.x,p.y,350);v3ArcHit(95,a,Math.PI,1.5,false);v3Pulse(type,player.x,player.y,180,.68);break;}
 case 'websight':v3Reveal(7,s=>dist(s,player)<730||traps.some(t=>t.type==='web'&&dist(s,t)<320));v3Pulse(type,player.x,player.y,690,1.0);break;
 case 'cocoon':{const p=front(220);v3Zone(type,p.x,p.y,107,31,{trigger:'root',strength:4});traps.push({x:p.x,y:p.y,life:31,r:89,armed:.55,type:'web'});break;}
 case 'predatorrun':v3MakeDash('charge',.60,2.5);v3Pulse(type,player.x,player.y,130,.5,a);break;
 case 'bloodscent':v3Reveal(9,s=>s.state==='injured'||s.state==='down'||s.bleed<110);v3Pulse(type,player.x,player.y,600,1);break;
 case 'wolfhowl':player.speedBoost=Math.max(player.speedBoost,8);for(const s of bots)if(survivorLive(s)&&dist(s,player)<455)s.fear=6;v3Pulse(type,player.x,player.y,450,1.1);break;
 case 'hauntport':{const near=[...generators.filter(g=>!g.complete),...hooks.filter(h=>!h.inactive)];const p=near.filter(p=>dist(p,player)<860&&dist(p,player)>195).sort((a,b)=>{
  let da=Math.abs(Math.atan2(Math.sin(Math.atan2(a.y-player.y,a.x-player.x)-player.angle),Math.cos(Math.atan2(a.y-player.y,a.x-player.x)-player.angle)));
  let db=Math.abs(Math.atan2(Math.sin(Math.atan2(b.y-player.y,b.x-player.x)-player.angle),Math.cos(Math.atan2(b.y-player.y,b.x-player.x)-player.angle)));
  return da-db;})[0]; if(p)v3SafeTeleport(p.x+65,p.y+30,770);else v3SafeTeleport(front(330).x,front(330).y,330);break;}
 case 'specterveil':v3StartStealth(16);v3Pulse(type,player.x,player.y,220,1);break;
 case 'ghostecho':{const p=front(190);v3Zone(type,p.x,p.y,175,9,{trigger:'fear',strength:4});traps.push({x:p.x,y:p.y,life:18,r:260,armed:0,type:'decoy'});break;}
 case 'sentence':{const target=v3VisibleBots(405).sort((x,y)=>dist(x,player)-dist(y,player))[0];if(target){target.mark=Math.max(target.mark,13);target.slow=Math.max(target.slow,3);v3Pulse(type,target.x,target.y,75,.85);}else v3Pulse(type,front(220).x,front(220).y,140,.85);break;}
 case 'chains':for(const s of bots)if(survivorLive(s)&&dist(s,player)<275){s.root=Math.max(s.root,2.3);s.fear=4;}v3Pulse(type,player.x,player.y,270,1.15);break;
 case 'verdict':for(const g of generators)if(!g.complete&&dist(g,player)<650){g.jam=Math.max(g.jam,6);g.progress=Math.max(0,g.progress-.025);v3Pulse(type,g.x,g.y,120,1)}v3Pulse(type,player.x,player.y,670,1.2);break;
 case 'precisearrow':launchProjectile('arrow',a);v3Pulse(type,front(100).x,front(100).y,68,.45,a);break;
 case 'eaglesight':v3Reveal(6,s=>dist(s,player)<880&&lineClear(s,player,6));v3Pulse(type,player.x,player.y,870,1);break;
 case 'arrowrain':for(const off of [-.36,-.18,0,.18,.36])launchProjectile('arrow',a+off);v3Pulse(type,front(220).x,front(220).y,240,.65,a);break;
 case 'firewall':{let p=front(240);for(const shift of [-100,-50,0,50,100])v3Zone(type,p.x-Math.sin(a)*shift,p.y+Math.cos(a)*shift,53,11,{trigger:'fire',strength:1.1});break;}
 case 'combustion':v3Zone(type,player.x,player.y,180,8,{trigger:'fire',strength:1});break;
 case 'meteor':launchProjectile('fire',a);v3Pulse(type,front(140).x,front(140).y,110,.55);break;
 case 'icespikes':for(const d of [85,165,245,325]){let p=front(d);v3Zone(type,p.x,p.y,63,9,{trigger:'root',strength:2.6})}break;
 case 'snowstorm':v3Zone(type,front(160).x,front(160).y,265,12,{trigger:'slow',strength:6});break;
 case 'frostshards':for(const off of [-.24,0,.24])launchProjectile('ice',a+off);v3Pulse(type,front(90).x,front(90).y,150,.75);break;
 case 'cutthreads':v3ArcHit(240,a,.52,2.2,false);v3Pulse(type,front(115).x,front(115).y,240,.8,a);break;
 case 'puppetswap':{const t=traps.filter(t=>t.type==='decoy').sort((a,b)=>dist(a,player)-dist(b,player))[0];if(t&&dist(t,player)<850){v3SafeTeleport(t.x,t.y,850);t.life=0}else{const p=front(205);v3SafeTeleport(p.x,p.y,205)}v3Pulse(type,player.x,player.y,140,.65);break;}
 case 'falsevictim':{let near=generators.filter(g=>!g.complete).sort((a,b)=>dist(a,player)-dist(b,player))[0],p=near&&dist(near,player)<550?near:front(200);traps.push({x:p.x,y:p.y,life:37,r:305,armed:0,type:'decoy'});v3Pulse(type,p.x,p.y,135,.8);break;}
 case 'ravenflight':v3MakeDash('leap',.50);v3Pulse(type,player.x,player.y,155,.66,a);break;
 case 'ravenscout':v3Reveal(6,s=>dist(s,player)<760||s.noise>0);v3Pulse(type,player.x,player.y,770,1.1);break;
 case 'ravenmurder':for(const off of [-.48,-.24,0,.24,.48])launchProjectile('ravens',a+off);v3Pulse(type,front(140).x,front(140).y,225,1);break;
 case 'emp':for(const g of generators)if(!g.complete&&dist(g,player)<600){g.jam=Math.max(g.jam,8);g.progress=Math.max(0,g.progress-.027)}for(const s of bots)if(survivorLive(s)&&dist(s,player)<260){s.root=Math.max(s.root,1.5)}v3Pulse(type,player.x,player.y,650,1);break;
 case 'radar':v3Reveal(7,s=>dist(s,player)<860);v3Pulse(type,player.x,player.y,870,1.15);break;
 case 'sentry':{const p=front(95);if(!collision(p.x,p.y,35)){turrets.push({x:p.x,y:p.y,t:0,life:96,r:340});if(turrets.length>3)turrets.shift();v3Pulse(type,p.x,p.y,170,1)}break;}
 case 'whisper':{const p=front(320);v3Zone(type,p.x,p.y,245,8,{trigger:'lure',strength:4});break;}
 case 'song':for(const s of bots)if(survivorLive(s)&&dist(s,player)<460&&lineClear(s,player,12)){s.slow=Math.max(s.slow,7);s.root=Math.max(s.root,1.3)}v3Pulse(type,player.x,player.y,470,1.4);break;
 case 'tidalwave':launchProjectile('wave',a);v3Pulse(type,front(130).x,front(130).y,230,1);break;
 }
}
function castKillerPower(slot){
 if(mode!=='playing'||player.stun>0||player.carrying!==null)return false;
 const index=slot==='q'?0:slot==='e'?1:2,cdKey=['dash','sense','trap'][index];
 if(player[cdKey]>.04)return false;
 const config=V3_ABILITIES[selectedKiller][index],skillId=config[2];
 if(index===0)aimAssist();
 const perkMult=index===0&&hasPerk('dash')?.83:index===1&&hasPerk('sense')?.82:1;
 player[cdKey]=config[1]*perkMult;animationAbility(index===0?'dash':index===1?'sense':'trap');
 if(skillId!=='darkveil'&&skillId!=='specterveil')player.stealth=0;
 v3CastEffect(skillId);sound(100+index*95,'sawtooth',.20,.075,170);
 burst(player.x,player.y,v3Colors[skillId]||killer().color,11,100);
 return true;
}
function v3Tick(dt){
 for(let i=v3Fx.length-1;i>=0;i--){v3Fx[i].t-=dt;if(v3Fx[i].t<=0)v3Fx.splice(i,1)}
 for(let i=v3Zones.length-1;i>=0;i--){const z=v3Zones[i];z.t-=dt;if(z.t<=0){v3Zones.splice(i,1);continue}
  for(const s of bots)if(survivorLive(s)&&dist(s,z)<z.r+16){
   if(z.trigger==='slow'){s.slow=Math.max(s.slow,1.8);s.fear=Math.max(s.fear,1.7)}
   if(z.trigger==='lure'){s.slow=Math.max(s.slow,2.4);s.fear=Math.max(s.fear,2.4);}
   const last=z.hit.get(s.id)||-999;
   if(elapsed-last>3.2){if(z.trigger==='root')s.root=Math.max(s.root,z.strength||2.4);
    if(z.trigger==='fire'){s.slow=Math.max(s.slow,3.3);hitBot(s,true)}
    if(z.trigger==='fear')s.fear=Math.max(s.fear,5);
    z.hit.set(s.id,elapsed);
   }
  }
 }
}
function v3DrawFX(time){
 ctx.save();
 for(const z of v3Zones){const p=Math.max(0,z.t/z.max);const col=v3Colors[z.type]||killer().color;
  ctx.save();ctx.globalAlpha=.12+.20*p;ctx.strokeStyle=col;ctx.fillStyle=col;ctx.lineWidth=3;
  ctx.setLineDash(z.trigger==='root'?[5,9]:[]);ctx.beginPath();ctx.arc(z.x,z.y,z.r,0,TAU);ctx.stroke();ctx.setLineDash([]);
  for(let q=0;q<6;q++){let a=TAU*q/6+time*(z.trigger==='fire'?.5:-.4),rr=z.r*(.35+.3*Math.sin(time+q));
   ctx.beginPath();ctx.arc(z.x+Math.cos(a)*rr,z.y+Math.sin(a)*rr,5+(q%3)*3,0,TAU);ctx.fill()}
  ctx.restore();
 }
 for(const f of v3Fx){let p=1-f.t/f.max;ctx.save();ctx.translate(f.x,f.y);ctx.globalAlpha=(1-p)*.8;ctx.strokeStyle=f.color;ctx.shadowColor=f.color;ctx.shadowBlur=15;ctx.lineWidth=2+3*(1-p);
  if(['reap','hammer','cutthreads','arrowrain'].includes(f.type)){ctx.rotate(f.dir);ctx.beginPath();ctx.arc(0,0,f.r*(.5+p*.55),-.93,.93);ctx.stroke();}
  else if(['cocoon','spiderleap','websight','deathrune'].includes(f.type)){for(let j=0;j<8;j++){let a=j*TAU/8+p*.3;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(a)*f.r*(.3+.7*p),Math.sin(a)*f.r*(.3+.7*p));ctx.stroke()}for(let r=1;r<=3;r++){ctx.beginPath();ctx.arc(0,0,f.r*(r/3)*p,0,TAU);ctx.stroke()}}
  else{ctx.beginPath();ctx.arc(0,0,f.r*p,0,TAU);ctx.stroke();ctx.beginPath();ctx.arc(0,0,f.r*Math.max(0,p-.16),0,TAU);ctx.stroke()}
  ctx.restore();}
 ctx.restore();
}
function dropCarried(){if(mode!=='playing'||player.carrying===null)return false;
 const s=bots[player.carrying];if(!s||s.state!=='carried'){player.carrying=null;return false;}
 let best=null;for(const da of [Math.PI,.72,-.72,Math.PI/2,-Math.PI/2,0]){
  const a=player.angle+da,p={x:player.x+Math.cos(a)*53,y:player.y+Math.sin(a)*53};
  if(!collision(p.x,p.y,20)&&!palletBlocked(p.x,p.y,19)){best=p;break;}}
 best=best||{x:player.x,y:player.y};s.x=best.x;s.y=best.y;s.state='down';s.bleed=Math.max(75,s.bleed||75);s.stunImmune=2.2;
 s.brain.orderUntil=0;s.brain.order='';s.brain.think=0;s.target=null;s.pathTo='';
 player.carrying=null;player.atk=Math.max(player.atk,.45);v3Pulse('sentence',s.x,s.y,65,.55);return true;
}
// New maps have specific structures, palette, safe spawns, 9-10 pallets and 5 windows each.
const V3_NEW_MAPS={
 laboratorio:{name:'LABORATÓRIO DE VIDRO',desc:'Salas de contenção, corredores em L e máquinas',color:'#101e28',accent:'#73d7df',layout:[
  [4,3,12,1,'stone'],[4,3,1,9,'stone'],[15,3,1,4,'stone'],[15,9,1,3,'stone'],[4,11,4,1,'stone'],[11,11,5,1,'stone'],
  [28,3,12,1,'stone'],[28,3,1,5,'stone'],[28,10,1,2,'stone'],[39,3,1,9,'stone'],[28,11,5,1,'stone'],[36,11,4,1,'stone'],
  [18,6,8,1,'stone'],[18,6,1,8,'stone'],[25,6,1,8,'stone'],[18,13,2,1,'stone'],[23,13,3,1,'stone'],
  [4,17,11,1,'shed'],[4,17,1,9,'shed'],[14,17,1,9,'shed'],[4,25,4,1,'shed'],[11,25,4,1,'shed'],
  [29,17,11,1,'shed'],[29,17,1,9,'shed'],[39,17,1,9,'shed'],[29,25,4,1,'shed'],[36,25,4,1,'shed'],
  [17,20,3,1,'crate'],[25,20,3,1,'crate'],[18,25,2,1,'crate'],[24,25,2,1,'crate']],
  spawns:[[7,6],[36,6],[7,22],[36,22],[20,4],[23,27]],gen:[[8,6],[36,6],[8,21],[36,21],[20,10],[23,23],[5,14],[39,14]],hooks:[[13,7],[31,7],[17,16],[27,16],[12,27],[32,27],[21,4],[22,27],[3,15],[40,15]],pallet:[[11,9],[31,9],[16,14],[27,14],[12,21],[31,21],[21,19],[9,26],[36,26]],windows:[[8,11],[35,11],[21,13],[8,25],[36,25]],loops:[[4,3,15,11],[28,3,39,11],[18,6,25,13],[4,17,14,25],[29,17,39,25]]},
 mansao:{name:'MANSÃO DAS MÁSCARAS',desc:'Salões, biblioteca e corredores cruzados',color:'#251c26',accent:'#c99ac9',layout:[
  [5,3,34,1,'stone'],[5,3,1,7,'stone'],[38,3,1,7,'stone'],[5,9,5,1,'stone'],[12,9,8,1,'stone'],[24,9,8,1,'stone'],[35,9,4,1,'stone'],
  [19,3,1,6,'stone'],[24,3,1,6,'stone'],[4,14,12,1,'shed'],[4,14,1,9,'shed'],[15,14,1,9,'shed'],[4,22,4,1,'shed'],[11,22,5,1,'shed'],
  [28,14,12,1,'shed'],[28,14,1,9,'shed'],[39,14,1,9,'shed'],[28,22,5,1,'shed'],[36,22,4,1,'shed'],
  [18,14,8,1,'stone'],[18,22,8,1,'stone'],[18,14,1,4,'stone'],[18,20,1,3,'stone'],[25,14,1,4,'stone'],[25,20,1,3,'stone'],
  [7,25,4,2,'crate'],[33,25,4,2,'crate'],[20,26,4,1,'crate']],
  spawns:[[7,6],[36,6],[7,19],[36,19],[19,6],[24,25]],gen:[[9,6],[35,6],[8,19],[35,19],[21,17],[21,26],[4,26],[40,26]],hooks:[[16,6],[27,6],[17,12],[27,12],[12,24],[33,24],[21,10],[21,23],[4,11],[40,11]],pallet:[[11,11],[32,11],[16,18],[27,18],[9,24],[35,24],[22,12],[21,27],[12,6]],windows:[[10,9],[34,9],[21,14],[9,22],[35,22]],loops:[[5,3,19,9],[24,3,38,9],[4,14,15,22],[28,14,39,22],[18,14,25,22]]},
 bosque:{name:'BOSQUE DOS SUSSURROS',desc:'Trilhas sinuosas, grutas e bosques cerrados',color:'#10241c',accent:'#80aa83',layout:[
  [5,4,5,2,'crate'],[14,3,2,5,'crate'],[21,5,3,2,'crate'],[29,3,2,6,'crate'],[35,6,5,2,'crate'],
  [4,13,2,4,'crate'],[10,11,6,2,'crate'],[18,11,2,5,'crate'],[24,12,5,2,'crate'],[35,12,4,2,'crate'],
  [5,20,5,2,'crate'],[13,19,2,6,'crate'],[18,23,6,1,'shed'],[26,20,2,5,'crate'],[33,19,5,2,'crate'],
  [5,26,6,1,'crate'],[17,27,4,1,'crate'],[31,26,4,1,'crate'],[39,23,2,4,'crate']],
  spawns:[[8,8],[36,8],[8,22],[36,22],[20,3],[24,27]],gen:[[7,7],[37,7],[8,18],[36,18],[21,9],[22,24],[6,25],[38,25]],hooks:[[13,7],[32,7],[19,17],[28,17],[12,25],[31,25],[21,3],[22,27],[3,13],[40,14]],pallet:[[11,9],[33,9],[16,17],[29,17],[11,24],[32,24],[22,19],[17,7],[27,7]],windows:[[10,13],[34,13],[22,11],[9,22],[36,22]],loops:[[4,4,16,8],[29,3,40,9],[10,11,20,16],[24,12,39,16],[13,19,28,25]]},
 subterraneo:{name:'TÚNEIS DO SUBSOLO',desc:'Galerias estreitas, câmaras e passagens laterais',color:'#17212a',accent:'#89acd4',layout:[
  [4,4,36,1,'stone'],[4,4,1,7,'stone'],[39,4,1,7,'stone'],[4,10,8,1,'stone'],[15,10,14,1,'stone'],[32,10,8,1,'stone'],
  [7,14,1,10,'stone'],[15,14,1,10,'stone'],[28,14,1,10,'stone'],[36,14,1,10,'stone'],
  [4,14,4,1,'stone'],[11,14,5,1,'stone'],[28,14,4,1,'stone'],[35,14,5,1,'stone'],
  [4,23,7,1,'stone'],[14,23,5,1,'stone'],[24,23,8,1,'stone'],[35,23,5,1,'stone'],
  [18,16,8,1,'shed'],[18,16,1,5,'shed'],[25,16,1,5,'shed'],[18,20,3,1,'shed'],[23,20,3,1,'shed'],
  [19,26,6,1,'crate'],[3,27,4,1,'crate'],[37,27,4,1,'crate']],
  spawns:[[8,7],[36,7],[9,19],[34,19],[19,12],[24,27]],gen:[[8,7],[35,7],[10,19],[34,19],[21,18],[21,27],[5,25],[39,25]],hooks:[[13,7],[31,7],[19,12],[25,12],[13,25],[31,25],[5,15],[39,15],[22,4],[22,28]],pallet:[[13,11],[31,11],[12,17],[33,17],[13,24],[31,24],[21,15],[21,23],[7,12]],windows:[[11,10],[33,10],[21,16],[12,23],[33,23]],loops:[[4,4,39,10],[7,14,15,23],[28,14,36,23],[18,16,25,20],[4,23,19,27]]},
 docas:{name:'DOCAS DO FIM',desc:'Contêineres, armazéns e corredores industriais',color:'#152530',accent:'#dfb078',layout:[
  [3,5,10,2,'crate'],[16,4,3,7,'crate'],[23,4,11,2,'crate'],[37,5,4,6,'crate'],
  [4,12,7,2,'crate'],[13,13,7,1,'crate'],[24,11,3,6,'crate'],[30,13,10,2,'crate'],
  [4,20,11,2,'crate'],[18,20,4,6,'crate'],[25,22,12,2,'crate'],[38,20,3,7,'crate'],
  [4,26,10,1,'shed'],[26,27,9,1,'shed'],[12,3,2,1,'shed']],
  spawns:[[7,8],[34,7],[8,18],[35,19],[21,4],[22,27]],gen:[[7,9],[34,9],[8,17],[34,18],[21,13],[22,27],[4,25],[39,25]],hooks:[[14,7],[29,8],[11,15],[31,16],[14,25],[31,25],[21,6],[22,23],[4,16],[41,17]],pallet:[[13,9],[29,9],[13,17],[30,19],[15,24],[27,25],[21,16],[8,24],[35,25]],windows:[[11,11],[31,11],[21,20],[10,21],[34,22]],loops:[[3,5,19,11],[23,4,41,11],[4,12,20,21],[24,11,40,17],[18,20,38,27]]},
 observatorio:{name:'OBSERVATÓRIO PARTIDO',desc:'Cúpulas, laboratórios de luz e anéis concêntricos',color:'#121b2d',accent:'#c8c1ff',layout:[
  [16,3,12,1,'stone'],[16,3,1,7,'stone'],[27,3,1,7,'stone'],[16,9,4,1,'stone'],[24,9,4,1,'stone'],
  [5,7,7,1,'stone'],[5,7,1,7,'stone'],[11,7,1,7,'stone'],[5,13,2,1,'stone'],[9,13,3,1,'stone'],
  [32,7,7,1,'stone'],[32,7,1,7,'stone'],[38,7,1,7,'stone'],[32,13,3,1,'stone'],[37,13,2,1,'stone'],
  [16,16,12,1,'stone'],[16,16,1,7,'stone'],[27,16,1,7,'stone'],[16,22,4,1,'stone'],[24,22,4,1,'stone'],
  [5,20,7,1,'shed'],[5,20,1,7,'shed'],[11,20,1,7,'shed'],[5,26,3,1,'shed'],[10,26,2,1,'shed'],
  [32,20,7,1,'shed'],[32,20,1,7,'shed'],[38,20,1,7,'shed'],[32,26,3,1,'shed'],[37,26,2,1,'shed'],
  [20,11,4,2,'crate'],[3,16,2,2,'crate'],[39,16,2,2,'crate']],
  spawns:[[8,9],[35,9],[8,23],[35,23],[20,6],[24,27]],gen:[[8,9],[35,9],[8,23],[35,23],[21,6],[22,19],[5,17],[39,17]],hooks:[[14,8],[30,8],[15,15],[29,15],[14,25],[30,25],[21,3],[22,27],[3,13],[40,13]],pallet:[[14,11],[29,11],[13,18],[30,18],[14,24],[29,24],[21,14],[21,25],[8,16]],windows:[[8,13],[35,13],[21,9],[8,26],[35,26]],loops:[[16,3,27,9],[5,7,11,13],[32,7,38,13],[16,16,27,22],[5,20,11,26],[32,20,38,26]]}
};
Object.assign(MAPS,V3_NEW_MAPS);
for(const [id,abilities]of Object.entries(V3_ABILITIES)){
 const k=KILLERS[id];k.q=abilities[0][0];k.e=abilities[1][0];k.r=abilities[2][0];
 k.qcd=abilities[0][1];k.ecd=abilities[1][1];k.rcd=abilities[2][1];
 k.description='Poderes exclusivos: '+abilities.map(a=>a[0]).join(' · ')+'.';
}
