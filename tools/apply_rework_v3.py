from pathlib import Path
import re, shutil
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'app/src/main/assets/index.html'
PATCH=(ROOT/'tools/killer_rework_v3.js').read_text()
h=BASE.read_text()
assert 'V3_ABILITIES' not in h
# New semantic labels/icons and carry-drop control.
h=h.replace('<span class="ico">⚡</span><small id="qLabel">INVESTIDA</small>', '<span class="ico">✦</span><small id="qLabel">HABILIDADE 1</small>')
h=h.replace('<b>⚡</b><small id="mbQLabel">DASH</small>','<b>✦</b><small id="mbQLabel">PODER 1</small>')
h=h.replace('</div></div></div>\n<div id="mobile">','<button id="dropBtn" type="button">⇣ G · SOLTAR</button></div></div></div>\n<div id="mobile">',1)
h=h.replace('<button class="mBtn" id="mbDash">','<button class="mBtn" id="mbDrop" style="display:none"><b>⇣</b><small>SOLTAR</small></button><button class="mBtn" id="mbDash">',1)
css='''\n/* V3 - Carry safety action: independent of power cooldowns. */
#dropBtn{display:none;pointer-events:auto;align-self:center;background:#4e2538;border:1px solid #ff8ea1;color:#fff0ee;border-radius:9px;padding:10px;font-size:10px;font-weight:900;min-width:108px}
#dropBtn:active{transform:scale(.97)}
.mBtn#mbDrop{grid-column:1;grid-row:3;background:#642a3e;border-color:#ff9a99}
@media (hover:none),(pointer:coarse){#dropBtn{display:none!important}.mBtn#mbDrop{display:flex}}
'''
h=h.replace('</style>',css+'</style>',1)
# Data can be attached after KILLERS and existing type defaults.
needle="KILLERS.brute.mob='ram';KILLERS.brute.senseType='roar';KILLERS.brute.special='quake';KILLERS.brute.body='brute';"
assert needle in h
h=h.replace(needle,needle+'\n'+PATCH+'\n',1)
# Important: no generic universal dash. All three ability buttons use a unique cast book.
patterns=[(r'function dash\(\)\{.*?(?=function sense\(\))',"function dash(){return castKillerPower('q')}\n"),
(r'function sense\(\)\{.*?(?=function launchProjectile\()',"function sense(){return castKillerPower('e')}\n"),
(r'function trap\(\)\{.*?(?=function projectileUpdate\()',"function trap(){return castKillerPower('r')}\n")]
for pat,rep in patterns:
 h,n=re.subn(pat,rep,h,count=1,flags=re.S);assert n==1,(pat,n)
h=h.replace("🎲 MAPA ALEATÓRIO (4)","🎲 MAPA ALEATÓRIO (10)")
h=h.replace('consumptions=[];hookAlert=0;endDelay=0;', 'consumptions=[];hookAlert=0;endDelay=0;v3Reset();',1)
h=h.replace('player.roar=Math.max(0,player.roar-dt);','player.roar=Math.max(0,player.roar-dt);v3Tick(dt);',1)
h=h.replace('drawCombatWeaponTrail(time);for(const v of consumptions)','drawCombatWeaponTrail(time);v3DrawFX(time);for(const v of consumptions)',1)
# Stealth cannot be tracked by literal position; close physical collision is still perceptible.
h=h.replace('let viewRadius=stealth?(alerted?178:104):(difficulty', 'let viewRadius=stealth?0:(difficulty',1)
h=h.replace('if(blocked)viewRadius=stealth?76:165;', 'if(blocked)viewRadius=stealth?0:165;',1)
h=h.replace('let soundRadius=(stealth?82:205)+(scent?120:0)+(selectedKiller', 'let soundRadius=(stealth?0:205)+(stealth?0:scent*120)+(stealth?0:(selectedKiller',1)
h=h.replace("&&player.roar>0?230:0);", "&&player.roar>0?230:0));",1)
h=h.replace('let perceived=vision||hearing;', 'let perceived=!stealth&&(vision||hearing);',1)
h=h.replace('let vision=d<viewRadius&&!blocked;', 'let vision=!stealth&&d<viewRadius&&!blocked;',1)
h=h.replace('let hearing=d<soundRadius;', 'let hearing=!stealth&&d<soundRadius;',1)
h=h.replace('b.knownTimer=Math.max(0,b.knownTimer-dt);b.knownAge+=dt;', 'b.knownTimer=Math.max(0,b.knownTimer-dt*(stealth?9:1));b.knownAge+=dt;',1)
h=h.replace('const camp=dist(player,v)<260;', 'const camp=player.stealth<=0&&dist(player,v)<260;',1)
h=h.replace('s.id===3&&lineClear(g,player,9)===false', 's.id===3&&knownThreat(s)&&lineClear(g,knownThreat(s),9)===false',1)
h=h.replace('if(tacticalRisk(s,v)>4.7||dist(player,v)<320)', 'if(tacticalRisk(s,v)>4.7||(player.stealth<=0&&dist(player,v)<320))',1)
h=h.replace("const b=s.brain,th=knownThreat(s)||player;", "const b=s.brain,th=knownThreat(s)||{x:MW/2,y:MH/2};",1)
# All bots should repair without omniscient knowledge while hidden (legacy task selector).
h=h.replace("Math.max(0,610-dist(player,g))*(player.stealth>0?.25:.67)","(knownThreat(s)?Math.max(0,610-dist(knownThreat(s),g))*.67:0)",1)
h=h.replace("if(s.id===3&&findCover(g,player))d-=160;", "if(s.id===3&&knownThreat(s)&&findCover(g,knownThreat(s)))d-=160;",1)
h=h.replace("down.state='carried';player.carrying=down.id;", "down.state='carried';player.carrying=down.id;player.stealth=0;",1)
h=h.replace('if(dist(player,s)<390||s.brain.knownTimer>0)', 'if((player.stealth<=0&&dist(player,s)<390)||s.brain.knownTimer>0)',1)
# Carry-drop actions on PC/G and mobile.
h=h.replace("if(e.code==='KeyF')interact();", "if(e.code==='KeyF')interact();if(e.code==='KeyG')dropCarried();",1)
h=h.replace("[['mbAttack',attack],['mbDash',dash]", "[['mbDrop',dropCarried],['mbAttack',attack],['mbDash',dash]",1)
h=h.replace("$('pause').onclick=pause;", "$('dropBtn').onclick=dropCarried;$('pause').onclick=pause;",1)
h=h.replace("function contextPrompt(){\n if(player.carrying!==null){const h=hooks.find", "function contextPrompt(){\n if(player.carrying!==null){const h=hooks.find",1)
h=h.replace("return h?{txt:'[ F ] PENDURAR',target:h}:null}","return h?{txt:'[ F ] PENDURAR · [ G ] SOLTAR',target:h}:{txt:'[ G ] SOLTAR SOBREVIVENTE',target:player}}",1)
# HUD updates after each game clock refresh; keep drop button linked only during carry.
needle='function hudUpdate(){const pr=contextPrompt();'
assert needle in h
h=h.replace(needle,'''function hudUpdate(){const carrying=player.carrying!==null;
 $('mbDrop').style.display=carrying?'flex':'none';$('dropBtn').style.display=carrying?'block':'none';
 const pr=contextPrompt();''',1)
# prevent pressing skills while carrying (visual state). If HUD not visible on PC update still works.
h=h.replace("$(id).disabled=value>.05||player.stun>0}","$(id).disabled=value>.05||player.stun>0||player.carrying!==null}",1)
# Set distinct abilities from selection, while cooldown draws use existing q/e/r counters.
# preserve same source as HTML for desktop preview and GitHub Pages.
BASE.write_text(h)
(ROOT/'index.html').write_text(h)
(ROOT/'JOGAR_NO_PC.html').write_text(h)
print('V3 patched HTML size:',len(h),'bytes; maps added:',h.count("name:'"))
assert 'function dash(){return castKillerPower' in h
assert 'function dropCarried(){' in h
assert h.count('id="mbDrop"')==1
