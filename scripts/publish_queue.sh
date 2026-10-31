#!/usr/bin/env bash
# queue/ 의 게시물을 인스타에 올리고 published/ 로 옮긴다. (GitHub Actions 전용)
# 인자: 게시할 이름(확장자 없이). 없으면 queue/*.png 전부.
#
# 이미지 공개 URL: MEDIA_REPO(공개 저장소)의 media 브랜치에 JPEG를 올리고 raw URL을 쓴다.
#   - MEDIA_REPO 미설정 → 이 저장소 자체 (저장소가 공개일 때만 동작)
#   - 저장소를 비공개로 바꾸면: 공개 저장소 하나를 만들어 변수 MEDIA_REPO, 시크릿 MEDIA_TOKEN 등록
set -euo pipefail

MEDIA_REPO="${MEDIA_REPO:-$GITHUB_REPOSITORY}"
MEDIA_TOKEN="${MEDIA_TOKEN:-$GITHUB_TOKEN}"
WORK="$(mktemp -d)"

git config --global user.name "github-actions[bot]"
git config --global user.email "41898299+github-actions[bot]@users.noreply.github.com"

if [ $# -gt 0 ] && [ -n "$1" ]; then
  slugs=("$@")
else
  shopt -s nullglob
  slugs=()
  for f in queue/*.png; do slugs+=("$(basename "$f" .png)"); done
fi

if [ ${#slugs[@]} -eq 0 ]; then
  echo "게시 대기열이 비어 있습니다."
  exit 0
fi

# media 브랜치 준비
MEDIA_DIR="$WORK/media"
MEDIA_URL="https://x-access-token:${MEDIA_TOKEN}@github.com/${MEDIA_REPO}.git"
if ! git clone -q --depth 1 --branch media "$MEDIA_URL" "$MEDIA_DIR" 2>/dev/null; then
  echo "media 브랜치가 없어 새로 만듭니다 ($MEDIA_REPO)"
  git init -q "$MEDIA_DIR"
  git -C "$MEDIA_DIR" checkout -q --orphan media
  git -C "$MEDIA_DIR" remote add origin "$MEDIA_URL"
  echo "인스타 게시용 공개 이미지 (자동 생성)" > "$MEDIA_DIR/README.md"
fi

for slug in "${slugs[@]}"; do
  echo "::group::$slug"
  if [ -d "published/$slug" ]; then
    echo "이미 게시됨: published/$slug → 건너뜀"; echo "::endgroup::"; continue
  fi
  python scripts/instagram.py validate "queue/$slug.png"

  python scripts/instagram.py jpeg "queue/$slug.png" "$MEDIA_DIR/$slug.jpg"
  git -C "$MEDIA_DIR" add -A
  git -C "$MEDIA_DIR" commit -q -m "media: $slug"
  git -C "$MEDIA_DIR" push -q origin media
  sha="$(git -C "$MEDIA_DIR" rev-parse HEAD)"
  url="https://raw.githubusercontent.com/${MEDIA_REPO}/${sha}/${slug}.jpg"
  echo "이미지 URL: $url"

  python scripts/instagram.py publish --image-url "$url" \
    --caption-file "queue/$slug.txt" --out "$WORK/result.json"
  mkdir -p "published/$slug"
  mv "$WORK/result.json" "published/$slug/result.json"

  # 게시 직후 바로 기록 (재실행 시 중복 게시 방지)
  git mv "queue/$slug.png" "published/$slug/image.png"
  git mv "queue/$slug.txt" "published/$slug/caption.txt"
  git add "published/$slug/result.json"
  git commit -q -m "게시 완료: $slug"
  git pull -q --rebase origin main && git push -q origin HEAD:main
  permalink="$(python -c "import json;print(json.load(open('published/$slug/result.json'))['permalink'])")"
  echo "- ✅ $slug → $permalink" >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
  echo "::endgroup::"
done
