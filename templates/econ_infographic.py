"""경제 요약 인포그래픽 렌더러 (사건·정책형)

사용법:
    python templates/econ_infographic.py content/2026-10-30-binance.json
    → output/2026-10-30-binance.png, output/2026-10-30-binance.txt (캡션)

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


def build_caption(d: dict, cfg: dict) -> str:
    c = d.get("caption", {})
    lines = [f"🚨 {plain(c.get('title', d['headline']))}", ""]
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
    lines += [f"매일 경제 이슈 한 장 정리 👉 {cfg['handle']}", ""]
    lines.append(" ".join("#" + t.lstrip("#") for t in c.get("hashtags", [])))
    return "\n".join(lines).strip() + "\n"


async def render(html_str: str, out: Path):
    async with async_playwright() as p:
        # Claude 클라우드 환경에는 크로미움이 /opt/pw-browsers/chromium 에 미리 설치돼 있다
        exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None)
        b = await p.chromium.launch(executable_path=exe)
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        await pg.set_content(html_str)
        await pg.wait_for_timeout(400)
        # 넘침 검사: 마지막 섹션이 하단 배너를 침범하면 경고
        overlap = await pg.evaluate("""() => {
            const secs=[...document.querySelectorAll('.sec')]; const ban=document.querySelector('.ban');
            return secs.length ? secs[secs.length-1].getBoundingClientRect().bottom - ban.getBoundingClientRect().top : 0 }""")
        await pg.screenshot(path=str(out))
        await b.close()
    return overlap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content", help="content/*.json")
    ap.add_argument("-o", "--outdir", default=str(ROOT / "output"))
    a = ap.parse_args()

    src = Path(a.content)
    d = json.loads(src.read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)

    png, txt = outdir / f"{src.stem}.png", outdir / f"{src.stem}.txt"
    overlap = asyncio.run(render(build_html(d, cfg), png))
    txt.write_text(build_caption(d, cfg), encoding="utf-8")
    print(f"이미지: {png}\n캡션: {txt}")
    if overlap > 0:
        print(f"⚠️ 내용이 하단 배너와 {overlap:.0f}px 겹칩니다. 문구를 줄이세요.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
