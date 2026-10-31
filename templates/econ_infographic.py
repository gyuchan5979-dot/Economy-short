import asyncio
from playwright.async_api import async_playwright

HTML = """<html><head><meta charset='utf-8'><style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#14254a;--red:#d63a2f;--cream:#faf6ee;--card:#fff;--line:#e6dfd0;--mute:#6b6f7c;--blue:#e9eef8;--peach:#fbeee3}
body{width:1080px;height:1350px;background:var(--cream);font-family:'Noto Sans CJK KR';word-break:keep-all;color:#1d2230;position:relative;overflow:hidden}
.top{position:relative;height:412px;padding:44px 56px 0 56px}
.brand{display:flex;align-items:center;gap:10px;font-weight:900;color:var(--navy);font-size:24px;letter-spacing:-.5px}
.brand small{display:block;font-size:13px;letter-spacing:1px;font-weight:700;color:#5c6680}
.kicker{display:inline-block;margin-top:22px;background:var(--red);color:#fff;font-weight:900;font-size:24px;padding:6px 16px;border-radius:6px}
h1{font-size:74px;font-weight:900;line-height:1.08;letter-spacing:-4px;color:var(--navy);margin-top:14px}
h1 .r{color:var(--red)}
.subline{margin-top:16px;display:inline-block;background:#fff;border:2px solid var(--line);border-radius:40px;padding:8px 22px;font-size:22px;font-weight:700;color:#3b4152}
.hero{position:absolute;right:40px;top:40px;width:330px;height:270px}
.row{display:flex;gap:18px;padding:0 40px}
.panel{flex:1;border-radius:18px;padding:22px 26px}
.panel h3{font-size:30px;font-weight:900;letter-spacing:-1px;margin-bottom:12px}
.panel .lab{font-size:18px;font-weight:700;color:var(--mute)}
.p1{background:var(--blue)} .p1 h3{color:var(--navy)}
.p2{background:var(--peach)} .p2 h3{color:var(--red)}
.flow{display:flex;align-items:center;gap:8px;margin-top:6px}
.fs{background:#fff;border-radius:10px;padding:10px 8px;text-align:center;font-size:19px;font-weight:700;flex:1;line-height:1.3}
.fs .e{font-size:30px;display:block}
.arr{color:var(--navy);font-weight:900;font-size:24px}
.bars{margin-top:4px}
.bar{display:flex;align-items:center;gap:10px;margin:10px 0;font-size:19px;font-weight:700}
.bar span.n{width:78px}
.bar .b{height:34px;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:10px;color:#fff;font-weight:900;font-size:20px}
.note{font-size:17px;color:var(--mute);margin-top:4px}
.sec{margin:26px 40px 0;border:2px solid var(--line);border-radius:18px;background:#fff;padding:30px 22px 16px;position:relative}
.sec .t{position:absolute;top:-20px;left:50%;transform:translateX(-50%);background:var(--navy);color:#fff;font-weight:900;font-size:22px;padding:6px 26px;border-radius:8px;white-space:nowrap}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 14px}
.it{display:flex;gap:12px;align-items:center;background:#fbfaf7;border-radius:12px;padding:10px 12px}
.it .no{font-weight:900;color:var(--navy);font-size:20px;width:26px}
.it .ic{font-size:34px;width:44px;text-align:center}
.it b{display:block;font-size:21px;letter-spacing:-.8px;color:#151a26}
.it p{font-size:16px;color:#5f6472;line-height:1.35}
.me{display:flex;gap:14px}
.mc{flex:1;border-radius:12px;padding:12px 16px}
.mc .h{display:inline-block;font-size:17px;font-weight:900;color:#fff;border-radius:6px;padding:3px 12px;margin-bottom:6px}
.mc p{font-size:18px;line-height:1.45;color:#2a2f3c}
.ban{position:absolute;left:40px;right:40px;bottom:46px;background:var(--navy);border-radius:16px;padding:16px 30px;display:flex;align-items:center;gap:20px}
.ban .q{color:#fff;font-weight:900;font-size:30px;line-height:1.3;letter-spacing:-1px;flex:1;text-align:center}
.ban .q em{color:#ffd23f;font-style:normal}
.ban .e{font-size:48px}
.src{position:absolute;left:0;right:0;bottom:18px;text-align:center;font-size:14px;color:#8a8e99}
</style></head><body>
<div class='top'>
  <div class='brand'>🏛️ <div>경제한장<small>ECONOMY IN ONE</small></div></div>
  <div class='kicker'>역대 최대 코인 해킹</div>
  <h1>바이낸스<br><span class='r'>9조 원</span> 털렸다</h1>
  <div class='subline'>세계 최대 거래소 · 피해 약 63억 달러 · 10월 29일(현지)</div>
  <svg class='hero' viewBox='0 0 330 270'>
    <circle cx='190' cy='130' r='120' fill='#e9eef8'/>
    <rect x='70' y='70' width='200' height='130' rx='12' fill='#14254a'/>
    <rect x='84' y='84' width='172' height='102' rx='6' fill='#1f3a70'/>
    <path d='M50 205 h240 l-18 18 h-204z' fill='#2b3d66'/>
    <circle cx='170' cy='128' r='30' fill='#d63a2f'/>
    <rect x='164' y='108' width='12' height='26' rx='4' fill='#fff'/><circle cx='170' cy='144' r='6' fill='#fff'/>
    <g font-family='Noto Sans CJK KR' font-weight='900' font-size='26' fill='#14254a'>
      <circle cx='272' cy='60' r='30' fill='#f2b632'/><text x='259' y='70' fill='#fff'>₿</text>
      <circle cx='300' cy='120' r='22' fill='#f2b632' opacity='.85'/>
      <circle cx='40' cy='80' r='22' fill='#f2b632' opacity='.7'/>
    </g>
    <path d='M268 160 l40 40 M262 178 l30 30' stroke='#d63a2f' stroke-width='6' stroke-linecap='round'/>
  </svg>
</div>

<div class='row'>
  <div class='panel p1'>
    <div class='lab'>어떻게 뚫렸나</div><h3>노트북 한 대에서 시작</h3>
    <div class='flow'>
      <div class='fs'><span class='e'>💻</span>직원 노트북<br>감염</div><span class='arr'>›</span>
      <div class='fs'><span class='e'>🗄️</span>내부 서버<br>침투</div><span class='arr'>›</span>
      <div class='fs'><span class='e'>💸</span>무단 출금<br>실행</div>
    </div>
  </div>
  <div class='panel p2'>
    <div class='lab'>얼마나 큰가</div><h3>기존 최대의 4배</h3>
    <div class='bars'>
      <div class='bar'><span class='n'>바이비트<br><small style='font-weight:500;color:#888'>2025.2</small></span><div class='b' style='width:70px;background:#c9a98f'>15억$</div></div>
      <div class='bar'><span class='n'>바이낸스<br><small style='font-weight:500;color:#888'>2026.10</small></span><div class='b' style='width:300px;background:var(--red)'>63억$</div></div>
    </div>
  </div>
</div>

<div class='sec'><div class='t'>핵심 정리</div>
  <div class='grid'>
    <div class='it'><span class='no'>01</span><span class='ic'>⛓️</span><div><b>10개 체인 지갑 털림</b><p>비트코인·이더리움·솔라나 등</p></div></div>
    <div class='it'><span class='no'>02</span><span class='ic'>🧊</span><div><b>약 30억$ 동결</b><p>테더·서클 등 협조 (회수와는 다름)</p></div></div>
    <div class='it'><span class='no'>03</span><span class='ic'>⏸️</span><div><b>입출금 일시 중단</b><p>조사·복구 진행 중</p></div></div>
    <div class='it'><span class='no'>04</span><span class='ic'>🛡️</span><div><b>"손실 전액 보전"</b><p>보험기금+회사 자금 63.4억$ 확보</p></div></div>
    <div class='it'><span class='no'>05</span><span class='ic'>🕵️</span><div><b>북한 조직 배후 지목</b><p>'트레이더트레이터' 추정, 확정 아님</p></div></div>
    <div class='it'><span class='no'>06</span><span class='ic'>📉</span><div><b>코인 시장 출렁</b><p>비트코인 3~4%, BNB 5%가량 하락</p></div></div>
  </div>
</div>

<div class='sec' style='padding-top:28px'><div class='t'>내 돈에 영향은?</div>
  <div class='me'>
    <div class='mc' style='background:var(--blue)'><span class='h' style='background:var(--navy)'>바이낸스 이용자</span><p>회사가 전액 보전을 약속한 상태. 입출금 재개는 <b>공식 공지</b>로만 확인하세요</p></div>
    <div class='mc' style='background:var(--peach)'><span class='h' style='background:var(--red)'>국내 거래소 이용자</span><p>직접 피해는 없지만 시세 변동성 주의. 사고를 틈탄 <b>"보상 신청" 피싱</b> 문자 조심</p></div>
  </div>
</div>

<div class='ban'><span class='e'>💡</span><div class='q'>"세계 1위 거래소도 뚫린다면,<br><em>내 코인은 어디에 두는 게 맞을까요?</em>"</div><span class='e'>💬</span></div>
<div class='src'>출처: 바이낸스 공지·뉴스1·한국경제·주간경향 (2026.10.30) · 투자 권유가 아닌 정보 요약입니다 · 일러스트</div>
</body></html>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1080,"height":1350})
        await pg.set_content(HTML); await pg.wait_for_timeout(400)
        await pg.screenshot(path="output/econ_infographic.png"); await b.close()
asyncio.run(main())
