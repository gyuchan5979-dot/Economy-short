"""인스타그램 게시 도구 (Instagram Graph API, 표준 라이브러리 + Pillow)

하위 명령
  enqueue  output/이름.png  → queue/ 로 복사 + 검사 (게시 대기열에 올리기)
  validate queue/이름.png   → 이미지 크기·캡션 규칙 검사만
  check                    → 토큰·계정 확인 (게시하지 않음)
  jpeg     입력.png 출력.jpg → 인스타용 JPEG 변환 (인스타 API는 JPEG만 받음)
  publish  --image-url URL --caption-file 파일 [--out 결과.json]

환경변수 (GitHub Secrets에서 주입. 코드·JSON에 절대 넣지 않는다)
  IG_ACCESS_TOKEN, IG_USER_ID, IG_GRAPH_VERSION(선택, 기본 v26.0)
"""
import argparse
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue"
CAPTION_MAX = 2200
HASHTAG_MAX = 30


def die(msg: str, code: int = 1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


# ---------- 검사 ----------
def validate(png: Path) -> list[str]:
    errs = []
    txt = png.with_suffix(".txt")
    if not png.exists():
        return [f"이미지 없음: {png}"]
    if not txt.exists():
        errs.append(f"캡션 파일 없음: {txt}")
    try:
        from PIL import Image
        with Image.open(png) as im:
            if im.size != (1080, 1350):
                errs.append(f"이미지 크기 {im.size} (1080×1350이어야 함)")
    except ImportError:
        print("⚠️ Pillow 없음: 이미지 크기 검사 생략", file=sys.stderr)
    if txt.exists():
        cap = txt.read_text(encoding="utf-8")
        if len(cap) > CAPTION_MAX:
            errs.append(f"캡션 {len(cap)}자 (최대 {CAPTION_MAX})")
        if sum(w.startswith("#") for w in cap.split()) > HASHTAG_MAX:
            errs.append(f"해시태그 {HASHTAG_MAX}개 초과")
        for bad in ("**", "##", "__"):
            if bad in cap:
                errs.append(f"캡션에 마크다운 기호 '{bad}' 포함")
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        if cap.count(cfg["handle"]) > 1:
            errs.append(f"자기 계정 멘션 {cfg['handle']} 이 여러 번 들어감")
        if "@your_account" in cap:
            errs.append("캡션에 @your_account 자리표시자가 남아 있음")
    return errs


def cmd_validate(a):
    errs = validate(Path(a.png))
    for e in errs:
        print(f"❌ {e}", file=sys.stderr)
    if errs:
        sys.exit(1)
    print(f"✅ 검사 통과: {a.png}")


def cmd_enqueue(a):
    src = Path(a.png)
    errs = validate(src)
    if errs:
        for e in errs:
            print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    QUEUE.mkdir(exist_ok=True)
    if (ROOT / "published" / src.stem).exists():
        die(f"이미 게시된 이름입니다: published/{src.stem}")
    for f in (src, src.with_suffix(".txt")):
        shutil.copy2(f, QUEUE / f.name)
    print(f"✅ 대기열에 올림: queue/{src.stem}.png, queue/{src.stem}.txt")


def cmd_jpeg(a):
    from PIL import Image
    with Image.open(a.src) as im:
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[3])
        Path(a.dst).parent.mkdir(parents=True, exist_ok=True)
        bg.save(a.dst, "JPEG", quality=95, optimize=True)
    print(f"JPEG: {a.dst}")


# ---------- Graph API ----------
def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        die(f"환경변수 {name} 가 비어 있습니다. GitHub Secrets에 등록했는지 확인하세요.")
    return v


def api(method: str, path: str, params: dict | None = None) -> dict:
    ver = os.environ.get("IG_GRAPH_VERSION", "").strip() or "v26.0"
    url = f"https://graph.facebook.com/{ver}/{path}"
    params = dict(params or {}, access_token=env("IG_ACCESS_TOKEN"))
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read()).get("error", {})
        except Exception:
            err = {}
        msg = err.get("error_user_msg") or err.get("message") or str(e)
        die(f"Graph API 오류 ({method} {path.split('?')[0]}): {msg} [code {err.get('code')}, sub {err.get('error_subcode')}]")


def cmd_check(_a):
    ig = env("IG_USER_ID")
    me = api("GET", ig, {"fields": "id,username,name,followers_count,media_count"})
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    want = cfg["handle"].lstrip("@")
    print(f"계정: @{me.get('username')} ({me.get('name')}) · 팔로워 {me.get('followers_count')} · 게시물 {me.get('media_count')}")
    if me.get("username") != want:
        die(f"토큰의 계정(@{me.get('username')})이 config.json의 @{want} 와 다릅니다.")
    lim = api("GET", f"{ig}/content_publishing_limit", {"fields": "quota_usage,config"})
    d = (lim.get("data") or [{}])[0]
    print(f"24시간 게시량: {d.get('quota_usage')}/{(d.get('config') or {}).get('quota_total')}")
    print("✅ 토큰·계정 확인 완료")


def check_url(url: str):
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
                ct = r.headers.get("Content-Type", "")
                if r.status == 200 and ct.startswith("image/"):
                    return
                print(f"이미지 URL 응답 {r.status} {ct}", file=sys.stderr)
        except urllib.error.URLError as e:
            print(f"이미지 URL 확인 실패({i + 1}/6): {e}", file=sys.stderr)
        time.sleep(5)
    die(f"이미지 공개 URL에 접근할 수 없습니다: {url}")


def cmd_publish(a):
    ig = env("IG_USER_ID")
    caption = Path(a.caption_file).read_text(encoding="utf-8").strip()
    check_url(a.image_url)

    c = api("POST", f"{ig}/media", {"image_url": a.image_url, "caption": caption})
    cid = c["id"]
    print(f"컨테이너 생성: {cid}")
    for _ in range(30):
        st = api("GET", cid, {"fields": "status_code,status"})
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            die(f"컨테이너 처리 실패: {st}")
        time.sleep(4)
    else:
        die("컨테이너 처리 시간 초과")

    pub = api("POST", f"{ig}/media_publish", {"creation_id": cid})
    mid = pub["id"]
    info = api("GET", mid, {"fields": "permalink,timestamp"})
    result = {"media_id": mid, "permalink": info.get("permalink"), "timestamp": info.get("timestamp"),
              "image_url": a.image_url}
    print(f"✅ 게시 완료: {result['permalink']}")
    if a.out:
        Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("enqueue"); p.add_argument("png"); p.set_defaults(f=cmd_enqueue)
    p = sp.add_parser("validate"); p.add_argument("png"); p.set_defaults(f=cmd_validate)
    p = sp.add_parser("check"); p.set_defaults(f=cmd_check)
    p = sp.add_parser("jpeg"); p.add_argument("src"); p.add_argument("dst"); p.set_defaults(f=cmd_jpeg)
    p = sp.add_parser("publish")
    p.add_argument("--image-url", required=True); p.add_argument("--caption-file", required=True)
    p.add_argument("--out"); p.set_defaults(f=cmd_publish)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
