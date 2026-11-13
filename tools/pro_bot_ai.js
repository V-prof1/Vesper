/* VESPER PRO BOT UPDATE — 6 independent survivor inventory builds and team coordination.
   Runs inside the existing game closure. Items are finite, save attempts respect line-of-sight.
*/
const PRO_ITEMS = ['flashlight','medkit','medkit','flashlight','flashlight','toolbox'];
const PRO_ITEM_LABELS={flashlight:'LANTERNA',medkit:'KIT MÉDICO',toolbox:'CAIXA DE FERRAMENTAS'};
function setupProBot(s,i){
 s.profile={...s.profile,reaction:Math.min(s.profile.reaction,.14),loopSkill:Math.max(s.profile.loopSkill,.89),caution:Math.max(s.profile.caution,.76)};
 s.item=PRO_ITEMS[i]||'medkit';s.itemCharges=s.item==='flashlight'?2:1;
 s.itemCooldown=0;s.flashHold=0;s.medkitProgress=0;s.bullyTime=0;s.rescueAttempts=0;
 s.skillTalent=Math.max(s.skillTalent,.88);
}
function releaseCarried(saviour,method){
 if(player.carrying===null)return false;
 const captive=bots[player.carrying];
 if(!captive||captive.state!=='carried')return false;
 captive.state='down';captive.bleed=Math.max(80,captive.bleed);captive.x=player.x+Math.cos(player.angle+Math.PI/2)*40;
 captive.y=player.y+Math.sin(player.angle+Math.PI/2)*40;
 captive.stunImmune=3.2; captive.fear=0;captiveFix(captive);
 player.carrying=null;player.stun=hasPerk('brutal')?1.7:2.8;player.dashing=0;
 saviour.itemCooldown=Math.max(saviour.itemCooldown,18);saviour.rescueAttempts++;
 shake=Math.max(shake,16);flash=.27;score=Math.max(0,score-120);
 burst(player.x,player.y,method==='pallet'?'#ebae71':'#f9e8a8',34,180);
 sound(520,'sawtooth',.25,.13,-360);
 for(const bot of bots)if(bot.brain&&survivorLive(bot)){bot.brain.orderUntil=0;bot.brain.think=0;}
 return true;
}
function captiveFix(captive){
 captive.brain.orderUntil=0;captive.brain.order='';captive.brain.think=0;
 captive.pathTo='';captive.target=null;
}
function bestCarryHook(){return hooks.filter(h=>h.occupant===null&&!h.inactive&&!(h.sabotagedUntil>elapsed))
 .sort((a,b)=>dist(player,a)-dist(player,b))[0]||null;}
function tryCarrierSave(s,dt){
 if(player.carrying===null||!survivorLive(s)||s.root>0||s.itemCooldown>0)return false;
 const captive=bots[player.carrying];if(!captive||captive.id===s.id)return false;
 const candidates=bots.filter(b=>survivorLive(b)&&b.itemCooldown<=0&&b.id!==captive.id).map(b=>{
  const dis=dist(b,player),pallet=pallets.filter(p=>!p.destroyed&&!p.dropped&&dist(p,player)<260);
  const ability=(b.item==='flashlight'&&b.itemCharges>0?340:0)+(b.item==='toolbox'&&b.itemCharges>0?220:0)+(pallet.length?130:0);
  return {b,score:ability+((b.state==='healthy')?140:0)+b.profile.courage*80-dis*.48};
 }).sort((a,b)=>b.score-a.score);
 // Two rescuers max. Other teammates stay on objectives.
 if(!candidates.slice(0,2).some(v=>v.b===s))return false;
 const d=dist(s,player),hook=bestCarryHook();
 if(s.item==='toolbox'&&s.itemCharges>0&&hook&&dist(player,hook)<340){
  s.task='SABOTANDO GANCHO';s.genId=-1;
  if(dist(s,hook)>60)navigate(s,hook,dt,214*s.profile.speed,'sabo'+hook.id);
  else if(dist(player,hook)<300&&hook.occupant===null){
   hook.sabotagedUntil=elapsed+65; s.itemCharges=0;s.itemCooldown=90;
   burst(hook.x,hook.y,'#eac47e',20,125);sound(310,'square',.22,.08,-150);
   s.task='GANCHO DESARMADO';return true;
  }
  return true;
 }
 // A real pallet-save: drop a usable pallet while the carrier is within collision range.
 const savePallet=pallets.filter(p=>!p.dropped&&!p.destroyed&&dist(p,player)<178)
  .sort((a,b)=>(dist(a,s)+dist(a,player)*.8)-(dist(b,s)+dist(b,player)*.8))[0];
 if(savePallet&&dist(s,savePallet)<88&&dist(player,savePallet)<111){
  savePallet.dropped=true;savePallet.droppedAt=elapsed;s.palletCD=18;
  if(releaseCarried(s,'pallet')){s.task='PALLET SAVE';return true}
 }
 if(s.item==='flashlight'&&s.itemCharges>0){
  const facing=(s.x-player.x)*Math.cos(player.angle)+(s.y-player.y)*Math.sin(player.angle);
  const frontal=facing>20; // only frontal beams work: killer can turn away
  if(d<238&&frontal&&lineClear(s,player,7)){
   s.task='FLASHLIGHT SAVE';s.genId=-1;s.flashHold+=dt*(difficulty==='hard'?1.30:1);
   if(s.flashHold>=.86){s.itemCharges--;s.flashHold=0;
    if(releaseCarried(s,'flashlight'))return true;
   }
   return true;
  }
  s.flashHold=Math.max(0,s.flashHold-dt*2);
 }
 if(d<630&&((s.item==='flashlight'&&s.itemCharges>0)||savePallet)){
  s.task='PREPARANDO SAVE';s.genId=-1;
  let dest=savePallet||{x:player.x+Math.cos(player.angle)*160,y:player.y+Math.sin(player.angle)*160};
  if(collision(dest.x,dest.y,25))dest=bestSpotForBot(s,Math.atan2(player.y-s.y,player.x-s.x),120);
  if(dist(s,dest)>66)navigate(s,dest,dt,218*s.profile.speed,'carrySave'+captive.id);
  return true;
 }
 return false;
}
function medkitDecision(s,dt){
 if(s.item!=='medkit'||s.itemCharges<=0||s.state!=='injured'||s.root>0)return false;
 if(dist(player,s)<390||s.brain.knownTimer>0){s.medkitProgress=Math.max(0,s.medkitProgress-dt*.14);return false}
 const safe=chooseHideSpot(s);if(dist(s,safe)>140&&tacticalRisk(s,s,'task')>2){
  s.task='BUSCANDO ABRIGO';navigate(s,safe,dt,135*s.profile.speed,'medicCover'+s.id);return true;
 }
 s.task='USANDO KIT MÉDICO';s.genId=-1;s.medkitProgress+=dt*(s.id===2?1.18:1);
 if(s.medkitProgress>=12){s.state='healthy';s.itemCharges--;s.itemCooldown=45;s.medkitProgress=0;
  burst(s.x,s.y,'#9ef2cf',15,95);sound(420,'triangle',.19,.06,120);s.brain.orderUntil=0;}
 return true;
}
function drawBotItems(){
 for(const s of bots){if(!survivorLive(s))continue;
  const x=s.x-cam.x,y=s.y-cam.y;if(x<-50||y<-50||x>W+50||y>H+50)continue;
  ctx.save();ctx.textAlign='center';ctx.font='bold 10px monospace';
  const name=s.item==='flashlight'?'▰':s.item==='medkit'?'✚':'⚒';
  ctx.fillStyle=s.itemCharges>0?'#d5f5e4':'#4d5761';ctx.fillText(name,x+20,y-19);
  if(s.flashHold>0&&s.itemCharges>0&&player.carrying!==null){
   ctx.strokeStyle='#fff0ad';ctx.lineWidth=4;ctx.globalAlpha=.5+Math.sin(elapsed*23)*.2;
   ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(player.x-cam.x,player.y-cam.y);ctx.stroke();
  }
  if(s.medkitProgress>0){ctx.fillStyle='#6fc9a0';ctx.fillRect(x-14,y-41,28*Math.min(1,s.medkitProgress/12),3)}
  ctx.restore();
 }
 for(const h of hooks)if(h.sabotagedUntil>elapsed){
  const x=h.x-cam.x,y=h.y-cam.y;ctx.save();ctx.fillStyle='#f4d79d';ctx.font='bold 12px monospace';
  ctx.textAlign='center';ctx.fillText('✕ '+Math.ceil(h.sabotagedUntil-elapsed)+'s',x,y-55);ctx.restore();
 }
}
function buildProLoopClusters(cfg){
 // Real U/L-shaped loop tiles: create protective corners on opposite sides
 // of selected pallets, keeping generators, windows and spawns accessible.
 let placed=0;
 const reserved=[...cfg.gen,...cfg.hooks,...cfg.spawns,...cfg.windows].map(([x,y])=>P(x,y));
 for(let i=0;i<cfg.pallet.length;i++){
  const [tx,ty]=cfg.pallet[i],anchor=P(tx,ty);
  const axis=i%2===0?1:0;
  const offsets=axis?[[95,68],[130,-74],[-90,-75]]:[[72,95],[-80,130],[-75,-95]];
  let local=0;
  for(const [ox,oy] of offsets){
   const x=anchor.x+ox,y=anchor.y+oy,w=48,h=65;
   if(x<100||y<95||x+w>MW-100||y+h>MH-95)continue;
   const c={x:x-w/2,y:y-h/2,w,h,type:'cover'};
   const overlaps=walls.some(b=>c.x<b.x+b.w+12&&c.x+c.w+12>b.x&&c.y<b.y+b.h+12&&c.y+c.h+12>b.y);
   const nearCritical=reserved.some(a=>a.x>c.x-79&&a.x<c.x+c.w+79&&a.y>c.y-79&&a.y<c.y+c.h+79);
   if(overlaps||nearCritical)continue;
   walls.push(c);placed++;local++;if(local>=2)break;
  }
 }
 cfg.loopCoversPlaced=placed;
}