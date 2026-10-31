import asyncio
from playwright.async_api import async_playwright

OUT = "output"
HANDLE = "@your_account"

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{word-break:keep-all;width:1080px;height:1350px;font-family:'Noto Sans CJK KR',sans-serif;background:#0f1424;color:#f4f1ea;position:relative;overflow:hidden}
.wrap{position:absolute;inset:0;padding:110px 96px}
.tag{display:inline-block;background:#ffd23f;color:#0f1424;font-weight:900;font-size:34px;padding:10px 24px;border-radius:8px;letter-spacing:-1px}
.num{font-size:30px;color:#8b93ad;font-weight:700;letter-spacing:2px}
h1{font-size:112px;font-weight:900;line-height:1.12;letter-spacing:-5px;margin-top:48px}
h2{font-size:76px;font-weight:900;line-height:1.2;letter-spacing:-3px;margin:28px 0 44px}
.hl{color:#ffd23f}
p{font-size:44px;line-height:1.6;letter-spacing:-1.5px;color:#d9dbe4;margin-bottom:34px}
p b{color:#fff;font-weight:900}
.sub{font-size:46px;color:#c3c8d8;margin-top:56px;line-height:1.5;letter-spacing:-1.5px}
.box{border:3px solid #2c3552;border-radius:20px;padding:30px 40px;margin-bottom:24px;background:#151c31}
.box .k{font-size:32px;font-weight:900;color:#ffd23f;margin-bottom:14px}
.box .v{font-size:40px;line-height:1.5;color:#e8e9ef;letter-spacing:-1px}
.foot{position:absolute;left:96px;right:96px;bottom:80px;display:flex;justify-content:space-between;font-size:28px;color:#6f7795;font-weight:700}
.bar{position:absolute;left:0;top:0;width:18px;height:100%;background:#ffd23f}
.slash{position:absolute;right:-120px;top:280px;width:520px;height:30px;background:#ffd23f;transform:rotate(-38deg);opacity:.9}
.slash2{position:absolute;right:-60px;top:400px;width:420px;height:14px;background:#ffd23f;transform:rotate(-38deg);opacity:.5}
"""

def page(body, n, total=6):
    return f"""<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='bar'></div>
<div class='wrap'>{body}</div>
<div class='foot'><span>{HANDLE}</span><span>{n} / {total}</span></div></body></html>"""

cards = [
page("""<div class='slash'></div><div class='slash2'></div>
<span class='tag'>지금 화제</span>
<h1 style='margin-top:120px'>출근길<br>5호선에서<br><span class='hl'>패딩이<br>찢겼다</span></h1>
<div class='sub'>누가 그은 걸까, 어디 걸린 걸까<br>지금까지 알려진 것만 정리했어요</div>""", 1),

page("""<div class='num'>WHAT HAPPENED</div>
<h2>무슨 일이<br><span class='hl'>있었나</span></h2>
<p>10월 29일, 한 승객이 SNS 스레드에 <b>출근길 5호선</b>에서 옷이 훼손됐다는 글을 올렸어요.</p>
<p>검은 패딩 겉감이 크게 갈라져 <b>충전재가 쏟아졌고</b>, 안에 입은 니트와 들고 있던 캔버스 가방에도 구멍이 났다고 해요.</p>
<p>작성자는 <b>경찰에 신고</b>했다고 밝혔어요.</p>""", 2),

page("""<div class='num'>REACTIONS</div>
<h2>"나도 당했다"<br><span class='hl'>경험담 속출</span></h2>
<div class='box'><div class='k'>비슷한 피해 주장</div><div class='v'>수선집에서 커터칼 자국처럼 네모 반듯하다는 말을 들었다, 코트 등판에 긴 줄이 그어져 있었다 등</div></div>
<div class='box'><div class='k'>반대 사례도</div><div class='v'>범행인 줄 알고 CCTV까지 봤는데, 알고 보니 계단 손잡이 파손 부위에 걸려 찢어졌다는 경험담도 나왔어요</div></div>""", 3),

page("""<div class='num'>FACT CHECK</div>
<h2>확인된 것<br><span class='hl'>vs 아닌 것</span></h2>
<div class='box'><div class='k'>✔ 확인</div><div class='v'>옷과 가방이 훼손된 사진이 공개됐고, 피해자가 신고했다고 밝힘</div></div>
<div class='box'><div class='k'>✖ 미확인</div><div class='v'>누군가 고의로 그었는지, 다른 물체에 걸린 건지는 아직 밝혀지지 않음</div></div>
<div class='box'><div class='k'>참고</div><div class='v'>2019년 비슷한 신고 때는 혼잡한 인파 탓에 장소·시점 특정이 어려웠던 것으로 알려짐</div></div>""", 4),

page("""<div class='num'>TIP</div>
<h2>혹시 나도<br><span class='hl'>겪는다면</span></h2>
<p>① 발견 즉시 <b>탑승 역·시간·칸 위치</b>를 메모해 두세요</p>
<p>② 역무실이나 <b>112</b>에 바로 알리세요. 시간이 지날수록 CCTV 확인이 어려워져요</p>
<p>③ 훼손된 옷은 <b>수선 전에 사진</b>을 찍고 그대로 보관하세요</p>
<p>④ 혼잡한 칸에선 백팩·가방을 <b>앞으로</b> 메는 것도 방법</p>""", 5),

page("""<span class='tag'>정리</span>
<h1 style='font-size:92px;margin-top:80px'>원인은<br><span class='hl'>아직 모른다</span></h1>
<div class='sub'>고의든 사고든, 출근길 안전은<br>모두의 문제예요.<br><br>여러분은 비슷한 경험 있으신가요?<br>댓글로 알려주세요 👇</div>
<div style='position:absolute;left:96px;bottom:150px;font-size:26px;color:#6f7795;line-height:1.6'>출처: 뉴시스·매일신문·파이낸셜뉴스·머니투데이 (2026.10.30)<br>본 게시물은 보도 내용을 요약한 것으로, 사건 원인은 확인되지 않았습니다.</div>""", 6),
]

async def main():
    import os; os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1080,"height":1350})
        for i, html in enumerate(cards, 1):
            await pg.set_content(html)
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"{OUT}/card_{i}.png")
        await b.close()
asyncio.run(main())
