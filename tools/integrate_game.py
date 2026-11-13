#!/usr/bin/env python3
from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools/vesper_enhanced.html'
DEST=ROOT/'app/src/main/assets/index.html'
manifest=json.loads((ROOT/'app/src/main/assets/assets/sprites.json').read_text(encoding='utf-8'))
s=SRC.read_text(encoding='utf-8')
s=s.replace('<title>VESPER', '<title>VESPER')
s=s.replace('VESPER · ABISMO · ANIMAÇÕES VIVAS', 'VESPER · ABISMO · EDIÇÃO PIXEL ART')
s=s.replace('MOVIMENTOS EXCLUSIVOS</span>', 'SPRITES PIXEL ART</span>')
s=s.replace('14 assassinos com movimentos, golpes e efeitos próprios; bots com animações de fuga, reparo, ferimentos e queda.', '4.584 quadros reais em pixel art; 14 moris exclusivos com 80 quadros cada, mais caminhada, corrida, golpe, habilidade, ferimento, reparo e resgate.')
s=s.replace('VESPER: ABISMO — ANIMAÇÕES VIVAS', 'VESPER: ABISMO — PIXEL ART')
s=s.replace('/* Sem feed de notificações: evita reanimação e pisca-pisca no celular. */', '/* Sem feed de notificações: evita reanimação e pisca-pisca no celular. */')
s=s.replace('</style>', '''\n/* Pixel sprites: recorte de quadro fixo, renderização nearest-neighbor e atlas sem suavização */
#game,#cinCanvas{image-rendering:pixelated}
.survCard .face{min-height:40px;background-size:768px auto;background-repeat:no-repeat;background-position:6px 0;image-rendering:pixelated}
.survCard .face .avatar{display:none}
.killerOpt .portrait.pixelPortrait{background-color:#0c0d16;image-rendering:pixelated;min-width:39px;min-height:46px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #58546d72;border-radius:4px}
</style>''',1)
# Minimal, inline manifest to keep file:// and WebView working with no HTTP/fetch.
manifest_text=json.dumps(manifest,ensure_ascii=False,separators=(',',':'))
s=s.replace('<script>\n(()=>',f'<script id="pixelManifest" type="application/json">{manifest_text}</script>\n<script>\n(()=>',1)
plugin=r'''
/* === VESPER PIXEL ART RUNTIME / REAL SPRITE ATLAS ===
   20 characters with unique anatomy + 14 staged 104-frame moris.
   Offline: PNG images + an embedded manifest; no external packages or network.
*/
const PIXEL = JSON.parse(document.getElementById('pixelManifest').textContent);
const pixelCharacters=Object.create(null),pixelMoris=Object.create(null);
const PIXEL_SURV=['lia','maya','noah','erik','iris','caio'];
let pixelLoaded=0;
function pixelLoad(id,mori=false){
 const dic=mori?pixelMoris:pixelCharacters;
 if(dic[id])return dic[id];
 const entry=mori?PIXEL.moris[id]:PIXEL.characters[id];if(!entry)return null;
 const im=new Image();im.decoding='async';dic[id]=im;
 im.onload=()=>{pixelLoaded++;};
 im.onerror=()=>{console.warn('VESPER PIXEL: sprite não carregado',entry.file);};
 im.src=entry.file;return im;
}
function pixelReady(id,mori=false){const img=pixelLoad(id,mori);return img&&img.complete&&img.naturalWidth>0}
function pixelDrawFrame(id,clip,phase,time,scale=1){
 if(!pixelReady(id))return false;
 const meta=PIXEL.characters[id],entry=meta.clips[clip]||meta.clips.idle;
 if(!entry)return false;
 const idx=phase>=0?Math.min(entry.frames-1,Math.floor(phase*entry.frames)):Math.floor(Math.max(0,time)*entry.fps)%entry.frames;
 const fi=entry.start+idx;const sx=fi%meta.columns*meta.width,sy=Math.floor(fi/meta.columns)*meta.height;
 const im=pixelCharacters[id];ctx.imageSmoothingEnabled=false;
 ctx.drawImage(im,sx,sy,meta.width,meta.height,-meta.width*.5*scale,-meta.height*.5*scale,meta.width*scale,meta.height*scale);
 return true;
}
function pixelDrawKiller(t){
 if(!player||!pixelReady(selectedKiller))return false;
 const m=player.anim||{};let clip='idle',phase=-1;
 const vel=Math.hypot(player.vx||0,player.vy||0);
 if(player.stun>0)clip='hurt';
 else if(m.attack>0&&m.attackMax>0){clip='attack';phase=1-m.attack/m.attackMax}
 else if(m.cast>0&&m.castMax>0){clip='ability';phase=1-m.cast/m.castMax}
 else if(player.dashing>0)clip='run';
 else if(vel>18)clip=player.carrying!==null?'carry':vel>killer().speed*.85?'run':'walk';
 ctx.save();ctx.translate(player.x,player.y);ctx.rotate(player.angle+Math.PI/2);
 if(player.stealth>0)ctx.globalAlpha=.58;
 const size=['brute','judge','automaton','weaver','hunter','raven'].includes(selectedKiller)?.89:.76;
 if(player.dashing>0){ctx.save();ctx.globalAlpha=.36;ctx.fillStyle=killer().color;ctx.fillRect(-26,11,52,4);ctx.restore()}
 pixelDrawFrame(selectedKiller,clip,phase,t,size);ctx.restore();
 if(player.stun>0){ctx.save();ctx.fillStyle='#fff0b7';ctx.font='bold 12px monospace';ctx.textAlign='center';ctx.fillText('ATORDOADO',player.x,player.y-55);ctx.restore()}
 return true;
}
function pixelDrawSurvivor(s,t){
 const id=PIXEL_SURV[s.id]||'lia';if(!pixelReady(id))return false;
 let clip='idle',phase=-1;
 const m=s.anim||{};const speed=m.speed||0;
 if(s.state==='hooked')clip='hook';
 else if(s.state==='down')clip='down';
 else if(s.state==='carried')clip='carry';
 else if(s.vaultFx>0){clip='vault';phase=Math.min(.99,Math.max(0,1-s.vaultFx/.5))}
 else if(m.impact>0){clip='hurt';phase=Math.max(0,Math.min(.99,1-m.impact/.5))}
 else if(s.healing>0||String(s.task).includes('CURANDO'))clip='heal';
 else if(s.repairFx>0||String(s.task).includes('REPAR'))clip='repair';
 else if(speed>.78||s.fear>0)clip='run';
 else if(speed>.07)clip='walk';
 ctx.save();ctx.translate(s.x,s.y);ctx.rotate((s.state==='carried'?player.angle:s.angle)+Math.PI/2);if(s.state==='down')ctx.rotate(-Math.PI/2);
 if(s.state==='carried')ctx.globalAlpha=.82;
 if(s.state==='injured')ctx.globalAlpha=.94;
 pixelDrawFrame(id,clip,phase,t,.70);ctx.restore();
 if(s.state==='injured'){ctx.save();ctx.strokeStyle='#f65069';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(s.x-14,s.y-12);ctx.lineTo(s.x+13,s.y+6);ctx.stroke();ctx.restore()}
 if(s.state==='hooked'&&s.hookTimer){ctx.save();ctx.fillStyle='#ff607e';ctx.fillRect(s.x-25,s.y-57,50*Math.max(0,s.hookTimer/(s.hookCount===1?27:24)),3);ctx.restore()}
 ctx.save();ctx.textAlign='center';ctx.font='900 10px monospace';ctx.fillStyle='#030409';ctx.fillText(s.name,s.x+1,s.y-44);ctx.fillStyle='#ffffff';ctx.fillText(s.name,s.x,s.y-45);ctx.restore();
 return true;
}
function pixelDrawMori(){
 if(!finisher||!pixelReady(selectedKiller,true))return false;
 const info=PIXEL.moris[selectedKiller];const img=pixelMoris[selectedKiller];
 const dpi=Math.min(devicePixelRatio||1,1.65),w=window.innerWidth,h=window.innerHeight;
 const bw=Math.round(w*dpi),bh=Math.round(h*dpi);
 if(mc.width!==bw||mc.height!==bh){mc.width=bw;mc.height=bh}
 const c=mctx;c.setTransform(dpi,0,0,dpi,0,0);c.imageSmoothingEnabled=false;
 c.fillStyle='#040510';c.fillRect(0,0,w,h);
 const idx=Math.min(info.frames-1,Math.floor(Math.max(0,finisher.t/finisher.total)*info.frames));
 const sx=idx%info.columns*info.width,sy=Math.floor(idx/info.columns)*info.height;
 // Letterboxing rather than stretching; handles phones and tablets gracefully.
 const scale=Math.min(w/info.width,h/info.height),dw=info.width*scale,dh=info.height*scale;
 c.drawImage(img,sx,sy,info.width,info.height,(w-dw)/2,(h-dh)/2,dw,dh);
 return true;
}
function pixelDecorateMenu(){
 for(const button of document.querySelectorAll('#killerSelect [data-killer]')){
  const id=button.dataset.killer;const face=button.querySelector('.portrait');if(!face)continue;
  face.classList.add('pixelPortrait');face.style.backgroundImage=`url(assets/characters/${id}.png)`;
  face.style.backgroundPosition='2px 3px';face.style.backgroundSize='768px auto';face.style.backgroundRepeat='no-repeat';face.style.color='transparent';
 }
}
const pixObserver=new MutationObserver(()=>pixelDecorateMenu());
pixObserver.observe(document.getElementById('killerSelect'),{childList:true});
for(const id of Object.keys(PIXEL.characters))pixelLoad(id);
'''
s=s.replace('let player,bots=[]',plugin+'\nlet player,bots=[]',1)
s=s.replace('function drawBot(s,t){if(s.state===\'dead\'||s.state===\'escaped\')return;',"function drawBot(s,t){if(s.state==='dead'||s.state==='escaped')return;if(pixelDrawSurvivor(s,t))return;",1)
s=s.replace('function drawPlayer(t){\n', 'function drawPlayer(t){\nif(pixelDrawKiller(t))return;\n',1)
s=s.replace('function renderMori(){\n','function renderMori(){\n if(pixelDrawMori())return;\n',1)
s=s.replace('function drawCombatWeaponTrail(t){\n','function drawCombatWeaponTrail(t){\n if(pixelReady(selectedKiller))return;\n',1)
s=s.replace('function previewMori(){if(mode', 'function previewMori(){pixelLoad(selectedKiller,true);if(mode',1)
s=s.replace('function executeTarget(){const s=', 'function executeTarget(){pixelLoad(selectedKiller,true);const s=',1)
s=s.replace('loadProfile();killerMenuUI();gameMapUI();','loadProfile();killerMenuUI();pixelDecorateMenu();gameMapUI();',1)
# absolute offline paths are forbidden; all sprites must remain relative to this file.
DEST.write_text(s,encoding='utf-8')
(ROOT/'JOGAR_NO_PC.html').write_text(s,encoding='utf-8')
shutil.copytree(ROOT/'app/src/main/assets/assets', ROOT/'assets',dirs_exist_ok=True)
print('Wrote',DEST,len(s),'chars; embedded manifest',len(manifest_text))