#!/usr/bin/env python3
"""Build a patched game source from pristine base without replacing mechanics."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/vesper_base.html').read_text(encoding='utf8')

def replace(needle,replacement):
 global s
 found=s.count(needle)
 if found<1:raise RuntimeError('Expected code not found: '+needle[:100])
 s=s.replace(needle,replacement)
 print(f'Patching {found}: {needle[:65]}')

helper=(R/'tools/pro_bot_ai.js').read_text(encoding='utf8')
replace('function init(){',helper+'\nfunction init(){')
replace('walls=cfg.layout.map(([x,y,w,h,type])=>({x:x*T,y:y*T,w:w*T,h:h*T,type}));\nlet seed=',
        'walls=cfg.layout.map(([x,y,w,h,type])=>({x:x*T,y:y*T,w:w*T,h:h*T,type}));buildProLoopClusters(cfg);\nlet seed=')
replace('bots.forEach(s=>s.brain=makeBrain(s));aiPings=[];',
        'bots.forEach((s,i)=>{s.brain=makeBrain(s);setupProBot(s,i)});aiPings=[];')
replace('occupant:null,inactive:false}', 'occupant:null,inactive:false,sabotagedUntil:0}')
replace('h.occupant===null&&!h.inactive', 'h.occupant===null&&!h.inactive&&!(h.sabotagedUntil>elapsed)')
replace("s.aiWait=Math.max(0,s.aiWait-dt);s.root=", "s.itemCooldown=Math.max(0,(s.itemCooldown||0)-dt);s.aiWait=Math.max(0,s.aiWait-dt);s.root=")
replace("const sensed=perceiveKiller(s,dt);\n if(s.root>0){", "const sensed=perceiveKiller(s,dt);\n if(s.root>0){")
replace("if(s.root>0){s.task='PRESO';s.genId=-1;s.target=null;return}\n // Danger override",
        "if(s.root>0){s.task='PRESO';s.genId=-1;s.target=null;return}\n if(tryCarrierSave(s,dt))return;\n if(medkitDecision(s,dt))return;\n // Danger override")
replace('drawLights(time);ctx.restore();','drawLights(time);ctx.restore();drawBotItems();')
replace("s.state+':'+s.hookCount","s.state+':'+s.hookCount+':'+(s.itemCharges||0)")
# Make HUD item charge clearly visible, without intrusive popups.
replace('<div class="who">${s.name}</div></div>`',
        '<div class="who">${s.name}<span class="equip"> ${s.item===\'flashlight\'?\'🔦\':s.item===\'medkit\'?\'✚\':\'⚒\'}${s.itemCharges||\'\'}</span></div></div>`')
# Extend mori timeline to 104 frames / 6 seconds; sprite runtime maps percentage.
replace('total:4.6', 'total:6.0')
replace('finisher.t>=2.2', 'finisher.t>=2.9')
# Fully mobile: keep the items HUD compact, and strengthen map cover contrast.
replace('</style>', '''\n.survCard .equip{font:900 8px monospace;color:#ffe1ab;letter-spacing:0}
@media(max-width:720px){.survCard .equip{font-size:7px}}
</style>''',1) if False else None
# Insert styles without relying on replace count parameter.
pos=s.index('</style>')
s=s[:pos]+'.survCard .equip{font:900 8px monospace;color:#ffe1ab;letter-spacing:0}\n@media(max-width:720px){.survCard .equip{font-size:7px}}\n'+s[pos:]
(R/'tools/vesper_enhanced.html').write_text(s,encoding='utf8')
print('Enhanced HTML source',len(s),'bytes')