import asyncio, random
from playwright.async_api import async_playwright
random.seed(7)

# quilted black padding texture
baffles = ""
for i in range(9):
    y = i * 150
    baffles += f"<rect x='0' y='{y}' width='1080' height='150' fill='url(#puff)'/>"
    baffles += f"<line x1='0' y1='{y}' x2='1080' y2='{y}' stroke='#050608' stroke-width='6'/>"
    for x in range(0, 1080, 18):
        baffles += f"<line x1='{x}' y1='{y+1}' x2='{x+6}' y2='{y+5}' stroke='#2a2f3a' stroke-width='2'/>"

# slash: polygon gash with stuffing puffs
gash = "M 170 300 C 330 420, 560 560, 900 820 C 880 860, 850 870, 820 860 C 560 650, 330 500, 150 340 Z"
puffs = ""
for _ in range(70):
    t = random.random()
    x = 170 + t * 720 + random.uniform(-40, 40)
    y = 310 + t * 520 + random.uniform(-40, 50)
    r = random.uniform(16, 44)
    puffs += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='url(#down)'/>"
for _ in range(14):  # escaped feathers
    x = random.uniform(80, 1000); y = random.uniform(150, 1000)
    a = random.uniform(-60, 60)
    puffs += f"<g transform='translate({x:.0f},{y:.0f}) rotate({a:.0f})'><ellipse rx='26' ry='8' fill='#f1efe8' opacity='.85'/><line x1='-30' y1='0' x2='30' y2='0' stroke='#cfcac0' stroke-width='2'/></g>"

svg = f"""<svg width='1080' height='1350' viewBox='0 0 1080 1350' xmlns='http://www.w3.org/2000/svg'>
<defs>
<linearGradient id='puff' x1='0' y1='0' x2='0' y2='1'>
 <stop offset='0' stop-color='#0b0d12'/><stop offset='.45' stop-color='#262b36'/><stop offset='.6' stop-color='#1b1f28'/><stop offset='1' stop-color='#07080b'/></linearGradient>
<radialGradient id='down'><stop offset='0' stop-color='#ffffff'/><stop offset='.7' stop-color='#ece9e1'/><stop offset='1' stop-color='#bdb8ad'/></radialGradient>
<linearGradient id='fade' x1='0' y1='0' x2='0' y2='1'><stop offset='.45' stop-color='#000' stop-opacity='0'/><stop offset='.78' stop-color='#000' stop-opacity='.92'/><stop offset='1' stop-color='#000'/></linearGradient>
</defs>
{baffles}
<path d='{gash}' fill='#e9e5dc' stroke='#000' stroke-width='10'/>
{puffs}
<rect width='1080' height='1350' fill='url(#fade)'/>
</svg>"""

html = f"""<html><head><meta charset='utf-8'><style>
*{{margin:0;padding:0}} body{{width:1080px;height:1350px;position:relative;font-family:'Noto Sans CJK KR';word-break:keep-all;background:#000}}
.t{{position:absolute;left:70px;right:70px;bottom:120px;color:#fff;font-weight:900;font-size:96px;line-height:1.16;letter-spacing:-5px;text-shadow:0 0 18px #000,0 6px 0 #000}}
.y{{color:#ffd23f}}
.tag{{position:absolute;left:70px;top:70px;background:#e8262b;color:#fff;font-weight:900;font-size:40px;padding:12px 26px;border-radius:10px;letter-spacing:-1px}}
.s{{position:absolute;left:70px;bottom:62px;color:#a9adb8;font-size:30px;font-weight:700}}
.il{{position:absolute;right:30px;top:80px;color:#ffffff99;font-size:22px}}
</style></head><body>{svg}
<div class='tag'>🚨 출근길 공포</div><div class='il'>일러스트</div>
<div class='t'>"누가 칼로<br>긋고 갔다"<br><span class='y'>5호선 출근길<br>패딩 찢김 ㄷㄷ</span></div>
<div class='s'>@your_account · 원인은 아직 미확인</div>
</body></html>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1080,"height":1350})
        await pg.set_content(html); await pg.wait_for_timeout(300)
        await pg.screenshot(path="output/thumbnail.png"); await b.close()
asyncio.run(main())
