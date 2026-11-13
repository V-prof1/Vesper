from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
AS=ROOT/'app/src/main/assets';m=json.loads((AS/'assets/sprites.json').read_text())
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(f,15);big=ImageFont.truetype(bold,24)
sets=[('reaper','walk'),('weaver','run'),('huntress','attack'),('pyre','ability'),('lia','run'),('maya','repair'),('noah','heal')]
w=1130;cellw=129;cellh=125;image=Image.new('RGB',(w,75+len(sets)*cellh),(11,12,22));d=ImageDraw.Draw(image)
d.text((26,17),'VESPER: ABISMO — SEQUÊNCIAS DE SPRITES REAIS',font=big,fill='#f9b9c6')
for row,(id,action) in enumerate(sets):
 meta=m['characters'][id];clip=meta['clips'][action];at=Image.open(AS/meta['file']).convert('RGBA')
 yy=65+row*cellh
 d.text((16,yy+25),id.upper(),font=font,fill='#ffb0a6')
 d.text((16,yy+49),action.upper(),font=font,fill='#b2bacc')
 for i in range(8):
  fi=clip['start']+round(i*(clip['frames']-1)/7)
  x=fi%meta['columns']*meta['width'];y=fi//meta['columns']*meta['height']
  fr=at.crop((x,y,x+meta['width'],y+meta['height'])).resize((72,90),Image.Resampling.NEAREST)
  xx=135+i*123
  image.paste(fr,(xx,yy+4),fr)
  d.text((xx+23,yy+96),f'{i+1:02}',font=font,fill='#808fa7')
image.save(ROOT/'PREVIA_QUADROS_ANIMACAO.png')
rows=['reaper','brute','weaver','frost','raven','siren']; p=Image.new('RGB',(1140,60+len(rows)*115),(9,10,19));d=ImageDraw.Draw(p)
d.text((25,15),'VESPER — 14 MORIS • 80 QUADROS CADA • STORYBOARD EM PIXEL ART',font=big,fill='#ffd4da')
for row,id in enumerate(rows):
 meta=m['moris'][id];at=Image.open(AS/meta['file']).convert('RGBA');y=60+row*115
 d.text((10,y+45),id.upper(),font=font,fill='#ebaabc')
 for col in range(8):
  fi=col*10;ww,hh=meta['width'],meta['height'];x=fi%meta['columns']*ww;yy=fi//meta['columns']*hh
  fr=at.crop((x,yy,x+ww,yy+hh)).resize((124,70),Image.Resampling.NEAREST)
  p.paste(fr,(129+col*126,y))
  d.text((155+col*126,y+75),f'{fi+1:02}',font=font,fill='#8d9ab2')
p.save(ROOT/'PREVIA_QUADROS_MORI.png')
