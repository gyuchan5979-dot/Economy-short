import asyncio
from playwright.async_api import async_playwright

NAVY, RED, CREAM, YEL = "#14254a", "#d63a2f", "#faf6ee", "#ffd23f"

opts = {
"A_sheet": f"""<svg viewBox='0 0 1080 1080' width='1080' height='1080'>
<rect width='1080' height='1080' fill='{NAVY}'/>
<g transform='rotate(-6 540 540)'>
 <path d='M310 230 h360 l100 100 v520 h-460z' fill='{CREAM}'/>
 <path d='M670 230 v100 h100z' fill='#d9d1bf'/>
 <rect x='370' y='620' width='80' height='150' rx='12' fill='#9fb0d3'/>
 <rect x='490' y='520' width='80' height='250' rx='12' fill='{NAVY}'/>
 <rect x='610' y='420' width='80' height='350' rx='12' fill='{RED}'/>
 <path d='M360 560 L470 470 L560 500 L700 330' stroke='{YEL}' stroke-width='30' fill='none' stroke-linecap='round' stroke-linejoin='round'/>
 <path d='M640 320 L712 316 L706 388' stroke='{YEL}' stroke-width='30' fill='none' stroke-linecap='round' stroke-linejoin='round'/>
 <rect x='370' y='300' width='190' height='26' rx='13' fill='{NAVY}' opacity='.85'/>
 <rect x='370' y='350' width='120' height='20' rx='10' fill='{NAVY}' opacity='.35'/>
</g></svg>""",

"B_text": f"""<svg viewBox='0 0 1080 1080' width='1080' height='1080'>
<rect width='1080' height='1080' fill='{CREAM}'/>
<text x='540' y='500' text-anchor='middle' font-family='Noto Sans CJK KR' font-weight='900' font-size='300' letter-spacing='-20' fill='{NAVY}'>경제</text>
<text x='540' y='800' text-anchor='middle' font-family='Noto Sans CJK KR' font-weight='900' font-size='300' letter-spacing='-20' fill='{RED}'>한장</text>
<rect x='300' y='840' width='480' height='34' rx='17' fill='{YEL}'/>
</svg>""",

"C_one": f"""<svg viewBox='0 0 1080 1080' width='1080' height='1080'>
<rect width='1080' height='1080' fill='{RED}'/>
<circle cx='540' cy='540' r='380' fill='{CREAM}'/>
<text x='540' y='720' text-anchor='middle' font-family='Noto Sans CJK KR' font-weight='900' font-size='520' fill='{NAVY}'>1</text>
<text x='540' y='860' text-anchor='middle' font-family='Noto Sans CJK KR' font-weight='900' font-size='92' letter-spacing='-4' fill='{RED}'>경제한장</text>
<path d='M690 300 l60 -60 M720 330 l70 -10' stroke='{YEL}' stroke-width='26' stroke-linecap='round'/>
</svg>""",
}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1080,"height":1080})
        for k, svg in opts.items():
            await pg.set_content(f"<html><body style='margin:0'>{svg}</body></html>")
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"assets/profile/{k}.png")
        await b.close()
asyncio.run(main())

from PIL import Image, ImageDraw
sheet = Image.new("RGB", (3*360+80, 460), "#ffffff")
d = ImageDraw.Draw(sheet)
for i, k in enumerate(opts):
    im = Image.open(f"assets/profile/{k}.png").resize((320, 320))
    m = Image.new("L", (320, 320), 0); ImageDraw.Draw(m).ellipse((0, 0, 320, 320), fill=255)
    sheet.paste(im, (40 + i*360, 20), m)
    sm = im.resize((110, 110)); ms = m.resize((110, 110))
    sheet.paste(sm, (145 + i*360, 340), ms)
sheet.save("assets/profile/preview.png")
