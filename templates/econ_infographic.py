"""경제 요약 인포그래픽 렌더러 (사건·정책형)

사용법:
    python templates/econ_infographic.py content/2026-10-30-binance.json
    → output/이름.cover.png (1장: 후킹 표지)
      output/이름.png       (2장: 인포그래픽 본문)
      output/이름.detail.png (3장: 내 돈에 영향은? 확대 + 저장 유도)
      output/이름.txt       (캡션)
    세 장은 인스타에 여러 장(캐러셀) 게시물로 올라간다.

내용은 JSON에서, 채널 정보는 config.json에서 읽는다.
텍스트 안의 간단한 표기:
    [[글자]]  → 강조색(레드/노랑)
    {{글자}}  → 굵게
    |         → 줄바꿈
"""
import argparse, asyncio, html, json, os, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent

HEROES = {
    # 상단 우측 일러스트. 새 이슈 유형이 생기면 여기에 추가한다.
    "hack": """<circle cx='190' cy='130' r='120' fill='#e9eef8'/>
<rect x='70' y='70' width='200' height='130' rx='12' fill='#14254a'/>
<rect x='84' y='84' width='172' height='102' rx='6' fill='#1f3a70'/>
<path d='M50 205 h240 l-18 18 h-204z' fill='#2b3d66'/>
<circle cx='170' cy='128' r='30' fill='#d63a2f'/>
<rect x='164' y='108' width='12' height='26' rx='4' fill='#fff'/><circle cx='170' cy='144' r='6' fill='#fff'/>
<circle cx='272' cy='60' r='30' fill='#f2b632'/><text x='259' y='70' fill='#fff' font-family='Noto Sans CJK KR' font-weight='900' font-size='26'>₿</text>
<circle cx='300' cy='120' r='22' fill='#f2b632' opacity='.85'/><circle cx='40' cy='80' r='22' fill='#f2b632' opacity='.7'/>
<path d='M268 160 l40 40 M262 178 l30 30' stroke='#d63a2f' stroke-width='6' stroke-linecap='round'/>""",
    "chart_up": """<circle cx='180' cy='135' r='120' fill='#e9eef8'/>
<rect x='70' y='160' width='40' height='60' rx='6' fill='#9fb0d3'/>
<rect x='125' y='125' width='40' height='95' rx='6' fill='#6d84b8'/>
<rect x='180' y='90' width='40' height='130' rx='6' fill='#14254a'/>
<rect x='235' y='55' width='40' height='165' rx='6' fill='#d63a2f'/>
<path d='M60 150 L130 110 L190 120 L280 40' stroke='#f2b632' stroke-width='8' fill='none' stroke-linecap='round'/>
<path d='M262 36 L290 34 L284 62' stroke='#f2b632' stroke-width='8' fill='none' stroke-linecap='round'/>
<rect x='50' y='220' width='260' height='8' rx='4' fill='#14254a'/>""",
    "chart_down": """<circle cx='180' cy='135' r='120' fill='#fbeee3'/>
<rect x='70' y='55' width='40' height='165' rx='6' fill='#d63a2f'/>
<rect x='125' y='90' width='40' height='130' rx='6' fill='#14254a'/>
<rect x='180' y='125' width='40' height='95' rx='6' fill='#6d84b8'/>
<rect x='235' y='160' width='40' height='60' rx='6' fill='#9fb0d3'/>
<path d='M60 40 L140 90 L200 80 L285 150' stroke='#d63a2f' stroke-width='8' fill='none' stroke-linecap='round'/>
<path d='M262 152 L290 154 L282 126' stroke='#d63a2f' stroke-width='8' fill='none' stroke-linecap='round'/>
<rect x='50' y='220' width='260' height='8' rx='4' fill='#14254a'/>""",
    "policy": """<circle cx='180' cy='135' r='120' fill='#e9eef8'/>
<path d='M60 100 L180 40 L300 100 Z' fill='#14254a'/>
<rect x='70' y='100' width='220' height='14' fill='#2b3d66'/>
<g fill='#ffffff' stroke='#14254a' stroke-width='4'>
<rect x='85' y='118' width='26' height='86'/><rect x='135' y='118' width='26' height='86'/>
<rect x='199' y='118' width='26' height='86'/><rect x='249' y='118' width='26' height='86'/></g>
<rect x='55' y='204' width='250' height='18' fill='#14254a'/>
<circle cx='180' cy='78' r='12' fill='#f2b632'/>""",
    "calendar": """<circle cx='180' cy='135' r='120' fill='#e9eef8'/>
<rect x='70' y='50' width='220' height='180' rx='16' fill='#ffffff' stroke='#14254a' stroke-width='6'/>
<rect x='70' y='50' width='220' height='50' rx='16' fill='#14254a'/><rect x='70' y='84' width='220' height='16' fill='#14254a'/>
<rect x='110' y='34' width='12' height='36' rx='6' fill='#d63a2f'/><rect x='238' y='34' width='12' height='36' rx='6' fill='#d63a2f'/>
<g fill='#c9d3e8'><rect x='92' y='118' width='34' height='26' rx='5'/><rect x='136' y='118' width='34' height='26' rx='5'/>
<rect x='224' y='118' width='34' height='26' rx='5'/><rect x='92' y='158' width='34' height='26' rx='5'/>
<rect x='136' y='158' width='34' height='26' rx='5'/><rect x='180' y='158' width='34' height='26' rx='5'/></g>
<rect x='180' y='118' width='34' height='26' rx='5' fill='#d63a2f'/><rect x='224' y='158' width='34' height='26' rx='5' fill='#f2b632'/>
<circle cx='292' cy='206' r='34' fill='#f2b632'/><path d='M292 186 v22 l14 8' stroke='#14254a' stroke-width='6' fill='none' stroke-linecap='round'/>""",
}

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#14254a;--red:#d63a2f;--cream:#faf6ee;--line:#e6dfd0;--mute:#6b6f7c;--blue:#e9eef8;--peach:#fbeee3}
body{width:1080px;height:1350px;background:var(--cream);font-family:'Noto Sans CJK KR';word-break:keep-all;color:#1d2230;position:relative;overflow:hidden}
.top{position:relative;height:412px;padding:44px 56px 0 56px}
.brand{display:flex;align-items:center;gap:10px;font-weight:900;color:var(--navy);font-size:24px;letter-spacing:-.5px}
.brand small{display:block;font-size:13px;letter-spacing:1px;font-weight:700;color:#5c6680}
.kicker{display:inline-block;margin-top:22px;background:var(--red);color:#fff;font-weight:900;font-size:24px;padding:6px 16px;border-radius:6px}
h1{font-size:74px;font-weight:900;line-height:1.08;letter-spacing:-4px;color:var(--navy);margin-top:14px;max-width:660px}
h1 .hl{color:var(--red)}
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
.bar{display:flex;align-items:center;gap:10px;margin:10px 0;font-size:19px;font-weight:700}
.bar .n{width:96px;line-height:1.2}
.bar .n small{display:block;font-weight:500;color:#888;font-size:16px}
.bar .b{height:34px;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:10px;color:#fff;font-weight:900;font-size:20px;white-space:nowrap}
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
.ban .q .hl{color:#ffd23f}
.ban .e{font-size:48px}
.src{position:absolute;left:0;right:0;bottom:18px;text-align:center;font-size:14px;color:#8a8e99}
"""


def fmt(s: str) -> str:
    """이스케이프 후 간단 표기를 HTML로 변환"""
    s = html.escape(str(s), quote=False)
    s = re.sub(r"\[\[(.+?)\]\]", r"<span class='hl'>\1</span>", s)
    s = re.sub(r"\{\{(.+?)\}\}", r"<b>\1</b>", s)
    return s.replace("|", "<br>")


def plain(s: str) -> str:
    """캡션용: 표기 기호와 마크다운 제거"""
    s = re.sub(r"\[\[(.+?)\]\]|\{\{(.+?)\}\}", lambda m: m.group(1) or m.group(2), str(s))
    s = s.replace("|", " ")
    return re.sub(r"[*#`_]{1,3}", "", s).strip()


def build_html(d: dict, cfg: dict) -> str:
    hero = HEROES.get(d.get("hero", "chart_up"), HEROES["chart_up"])

    left, right = d["panel_left"], d["panel_right"]
    steps = "<span class='arr'>›</span>".join(
        f"<div class='fs'><span class='e'>{s['icon']}</span>{fmt(s['text'])}</div>" for s in left["steps"]
    )
    vmax = max(b["value"] for b in right["bars"]) or 1
    bars = "".join(
        f"<div class='bar'><span class='n'>{fmt(b['label'])}<small>{fmt(b.get('sub',''))}</small></span>"
        f"<div class='b' style='width:{max(70, int(300 * b['value'] / vmax))}px;"
        f"background:{'var(--red)' if b.get('highlight') else '#c9a98f'}'>{fmt(b['text'])}</div></div>"
        for b in right["bars"]
    )
    points = "".join(
        f"<div class='it'><span class='no'>{i:02d}</span><span class='ic'>{p['icon']}</span>"
        f"<div><b>{fmt(p['title'])}</b><p>{fmt(p['desc'])}</p></div></div>"
        for i, p in enumerate(d["points"][:6], 1)
    )
    colors = [("var(--blue)", "var(--navy)"), ("var(--peach)", "var(--red)")]
    impact = "".join(
        f"<div class='mc' style='background:{colors[i % 2][0]}'><span class='h' style='background:{colors[i % 2][1]}'>"
        f"{fmt(m['who'])}</span><p>{fmt(m['text'])}</p></div>"
        for i, m in enumerate(d["impact"][:2])
    )
    notes = [f"출처: {d['sources']}"]
    if d.get("investment"):
        notes.append("투자 권유가 아닌 정보 요약입니다")
    notes.append("일러스트")

    return f"""<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>
<div class='top'>
  <div class='brand'>{cfg['brand_icon']} <div>{html.escape(cfg['brand_name'])}<small>{html.escape(cfg['brand_sub'])}</small></div></div>
  <div class='kicker'>{fmt(d['kicker'])}</div>
  <h1>{fmt(d['headline'])}</h1>
  <div class='subline'>{fmt(d['subline'])}</div>
  <svg class='hero' viewBox='0 0 330 270'>{hero}</svg>
</div>
<div class='row'>
  <div class='panel p1'><div class='lab'>{fmt(left['label'])}</div><h3>{fmt(left['title'])}</h3><div class='flow'>{steps}</div></div>
  <div class='panel p2'><div class='lab'>{fmt(right['label'])}</div><h3>{fmt(right['title'])}</h3><div>{bars}</div></div>
</div>
<div class='sec'><div class='t'>핵심 정리</div><div class='grid'>{points}</div></div>
<div class='sec' style='padding-top:28px'><div class='t'>{fmt(d.get('impact_title', '내 돈에 영향은?'))}</div><div class='me'>{impact}</div></div>
<div class='ban'><span class='e'>💡</span><div class='q'>{fmt(d['question'])}</div><span class='e'>💬</span></div>
<div class='src'>{' · '.join(html.escape(n) for n in notes)}</div>
</body></html>"""


COVER_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#14254a;--red:#d63a2f;--cream:#faf6ee;--yellow:#ffd23f}
body{width:1080px;height:1350px;background:var(--cream);font-family:'Noto Sans CJK KR';word-break:keep-all;color:var(--navy);position:relative;overflow:hidden}
.brand{position:absolute;left:64px;top:56px;display:flex;align-items:center;gap:10px;font-weight:900;font-size:26px}
.brand small{display:block;font-size:14px;letter-spacing:1px;font-weight:700;color:#5c6680}
.page{position:absolute;right:64px;top:62px;font-size:24px;font-weight:900;color:#fff;background:var(--navy);border-radius:30px;padding:6px 18px}
.hero{position:absolute;right:30px;top:150px;width:470px;height:385px;opacity:.95}
.main{position:absolute;left:64px;right:64px;top:300px}
.kicker{display:inline-block;background:var(--red);color:#fff;font-weight:900;font-size:34px;padding:8px 22px;border-radius:8px}
.big{font-size:250px;font-weight:900;letter-spacing:-12px;line-height:1;color:var(--red);margin-top:30px}
.title{font-size:92px;font-weight:900;letter-spacing:-5px;line-height:1.12;margin-top:34px}
.title .hl{color:var(--red)}
.hook{position:absolute;left:64px;right:64px;bottom:150px;background:var(--navy);border-radius:22px;padding:30px 40px;color:#fff;font-size:44px;font-weight:900;line-height:1.35;letter-spacing:-1.5px}
.hook .hl{color:var(--yellow)}
.swipe{position:absolute;left:0;right:0;bottom:64px;text-align:center;font-size:30px;font-weight:900;color:var(--navy)}
.swipe span{color:var(--red)}
.src{position:absolute;left:0;right:0;bottom:22px;text-align:center;font-size:15px;color:#8a8e99}
"""

DETAIL_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#14254a;--red:#d63a2f;--cream:#faf6ee;--blue:#e9eef8;--peach:#fbeee3;--yellow:#ffd23f}
body{width:1080px;height:1350px;background:var(--cream);font-family:'Noto Sans CJK KR';word-break:keep-all;color:#1d2230;position:relative;overflow:hidden}
.brand{position:absolute;left:64px;top:56px;display:flex;align-items:center;gap:10px;font-weight:900;font-size:26px;color:var(--navy)}
.brand small{display:block;font-size:14px;letter-spacing:1px;font-weight:700;color:#5c6680}
.page{position:absolute;right:64px;top:62px;font-size:24px;font-weight:900;color:#fff;background:var(--navy);border-radius:30px;padding:6px 18px}
h2{position:absolute;left:64px;top:170px;font-size:76px;font-weight:900;letter-spacing:-4px;color:var(--navy)}
.cards{position:absolute;left:64px;right:64px;top:300px;bottom:400px;display:flex;flex-direction:column;justify-content:center;gap:28px}
.card{border-radius:24px;padding:34px 40px}
.card .h{display:inline-block;font-size:30px;font-weight:900;color:#fff;border-radius:8px;padding:6px 18px;margin-bottom:16px}
.card p{font-size:40px;line-height:1.45;letter-spacing:-1px;color:#1d2230;font-weight:500}
.card p b{font-weight:900;color:var(--navy)}
.card .more{font-size:30px;line-height:1.5;color:#4a5060;margin-top:12px}
.q{position:absolute;left:64px;right:64px;bottom:250px;text-align:center;font-size:40px;font-weight:900;line-height:1.35;letter-spacing:-1.5px;color:var(--navy)}
.q .hl{color:var(--red)}
.save{position:absolute;left:64px;right:64px;bottom:80px;background:var(--navy);border-radius:22px;padding:26px 30px;display:flex;justify-content:space-around;color:#fff;font-size:34px;font-weight:900}
.save span{color:var(--yellow)}
.src{position:absolute;left:0;right:0;bottom:24px;text-align:center;font-size:15px;color:#8a8e99}
"""


def cover_fields(d: dict) -> dict:
    """cover가 없으면 헤드라인에서 만든다: [[강조]] → 큰 숫자, 나머지 → 제목"""
    c = dict(d.get("cover") or {})
    m = re.search(r"\[\[(.+?)\]\]", d["headline"])
    c.setdefault("big", m.group(1) if m else "")
    c.setdefault("title", re.sub(r"\s*\[\[.+?\]\]\s*", " ", d["headline"]).strip(" |") if m else d["headline"])
    c.setdefault("hook", d["panel_left"]["title"])
    return c


def brand_html(cfg: dict) -> str:
    return (f"<div class='brand'>{cfg['brand_icon']} <div>{html.escape(cfg['brand_name'])}"
            f"<small>{html.escape(cfg['brand_sub'])}</small></div></div>")


def build_cover_html(d: dict, cfg: dict) -> str:
    c = cover_fields(d)
    hero = HEROES.get(d.get("hero", "chart_up"), HEROES["chart_up"])
    # 큰 숫자가 길면 글자를 줄여 오른쪽 일러스트와 겹치지 않게 한다
    n = len(c["big"])
    size = 250 if n <= 4 else 200 if n <= 5 else 165 if n <= 7 else 130
    big = f"<div class='big' style='font-size:{size}px'>{fmt(c['big'])}</div>" if c["big"] else ""
    return f"""<html><head><meta charset='utf-8'><style>{COVER_CSS}</style></head><body>
{brand_html(cfg)}<div class='page'>1 / 3</div>
<svg class='hero' viewBox='0 0 330 270'>{hero}</svg>
<div class='main'><div class='kicker'>{fmt(d['kicker'])}</div>{big}<div class='title'>{fmt(c['title'])}</div></div>
<div class='hook'>{fmt(c['hook'])}</div>
<div class='swipe'>넘겨서 한 장으로 정리 보기 <span>→</span></div>
<div class='src'>{html.escape(d['sources'])} · 일러스트</div>
</body></html>"""


def build_detail_html(d: dict, cfg: dict) -> str:
    colors = [("var(--blue)", "var(--navy)"), ("var(--peach)", "var(--red)")]
    cards = "".join(
        f"<div class='card' style='background:{colors[i % 2][0]}'><span class='h' style='background:{colors[i % 2][1]}'>"
        f"{fmt(m['who'])}</span><p>{fmt(m['text'])}</p>"
        + (f"<div class='more'>{fmt(m['more'])}</div>" if m.get("more") else "") + "</div>"
        for i, m in enumerate(d["impact"][:2])
    )
    notes = [html.escape(d["sources"])]
    if d.get("investment"):
        notes.append("투자 권유가 아닌 정보 요약입니다")
    return f"""<html><head><meta charset='utf-8'><style>{DETAIL_CSS}</style></head><body>
{brand_html(cfg)}<div class='page'>3 / 3</div>
<h2>{fmt(d.get('impact_title', '내 돈에 영향은?'))}</h2>
<div class='cards'>{cards}</div>
<div class='q'>{fmt(d['question'])}</div>
<div class='save'><div>📌 <span>저장</span>해두고 다시 보기</div><div>🔁 필요한 사람에게 <span>공유</span></div></div>
<div class='src'>{' · '.join(notes)}</div>
</body></html>"""


def build_caption(d: dict, cfg: dict) -> str:
    c = d.get("caption", {})
    lines = [f"🚨 {plain(c.get('title', d['headline']))}"]
    if c.get("keywords"):  # 인스타 검색용: 사람들이 실제로 검색할 단어를 자연스럽게 한 줄로
        lines.append(plain(c["keywords"]))
    lines.append("")
    for sec in c.get("sections", []):
        lines.append(f"📌 {plain(sec['title'])}")
        lines += [plain(x) for x in sec["lines"]]
        lines.append("")
    if c.get("ask"):
        lines += [plain(c["ask"]), ""]
    if d.get("affiliate"):
        lines += ["이 게시물은 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다.", ""]
    if d.get("investment"):
        lines += ["※ 투자 권유가 아닌 정보 요약입니다.", ""]
    lines += [f"📌 저장해두고 다시 보기 · 매일 경제 한 장 👉 {cfg['handle']}", ""]
    lines.append(" ".join("#" + t.lstrip("#") for t in c.get("hashtags", [])))
    return "\n".join(lines).strip() + "\n"


OVERFLOW_JS = """() => {
    const r = s => document.querySelector(s)?.getBoundingClientRect();
    const ban = r('.ban');
    if (ban) { const secs=[...document.querySelectorAll('.sec')];
        return secs.length ? secs[secs.length-1].getBoundingClientRect().bottom - ban.top : 0 }
    const cards = document.querySelector('.cards'), q = r('.q');   // 3장: 카드 내용이 영역을 넘거나 질문과 겹치는지
    if (cards && q) return Math.max(cards.scrollHeight - cards.clientHeight,
        [...cards.children].pop().getBoundingClientRect().bottom + 20 - q.top);
    const main = r('.main'), hook = r('.hook');       // 1장: 제목이 후킹 박스와 겹치는지
    if (main && hook) return main.bottom + 20 - hook.top;
    return 0 }"""


async def render(pages: list[tuple[str, Path]]) -> dict:
    """[(html, 출력경로)] 를 렌더하고 {경로: 넘침px} 를 돌려준다"""
    res = {}
    async with async_playwright() as p:
        # Claude 클라우드 환경에는 크로미움이 /opt/pw-browsers/chromium 에 미리 설치돼 있다
        exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None)
        b = await p.chromium.launch(executable_path=exe)
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for html_str, out in pages:
            await pg.set_content(html_str)
            await pg.wait_for_timeout(400)
            res[out] = await pg.evaluate(OVERFLOW_JS)
            await pg.screenshot(path=str(out))
        await b.close()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content", help="content/*.json")
    ap.add_argument("-o", "--outdir", default=str(ROOT / "output"))
    a = ap.parse_args()

    src = Path(a.content)
    d = json.loads(src.read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)

    stem = src.stem
    pages = [(build_cover_html(d, cfg), outdir / f"{stem}.cover.png"),
             (build_html(d, cfg), outdir / f"{stem}.png"),
             (build_detail_html(d, cfg), outdir / f"{stem}.detail.png")]
    txt = outdir / f"{stem}.txt"
    res = asyncio.run(render(pages))
    txt.write_text(build_caption(d, cfg), encoding="utf-8")
    for _, out in pages:
        print(f"이미지: {out}")
    print(f"캡션: {txt}")
    bad = [(o, v) for o, v in res.items() if v > 0]
    for o, v in bad:
        print(f"⚠️ {o.name}: 내용이 {v:.0f}px 겹칩니다. 문구를 줄이세요.", file=sys.stderr)
    if bad:
        sys.exit(2)

if __name__ == "__main__":
    main()
