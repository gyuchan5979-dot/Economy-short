# 경제 요약 인스타그램 계정 — 프로젝트 안내

이 저장소는 경제 이슈를 한 장짜리 인포그래픽으로 정리해 인스타그램에 자동 게시하는 프로젝트다.
운영자: 조규찬 (드리움 커튼&블라인드 운영 중, 부업으로 진행). 채널: 인스타그램 @econ.oneshot (브랜드명 "경제한장 / ECONOMY IN ONE").

## 목표
- 매일 화제가 되는 경제 이슈를 찾아 사실 위주로 요약하고 인포그래픽 + 캡션을 만든다.
- 팔로워를 모은 뒤 제휴 링크(재테크 도서, 가계부 앱, 증권사 이벤트 등)로 수익을 낸다.
- 최종적으로는 사람 손을 최소화한 자동 게시. Make는 쓰지 않는다 (아래 "게시 구조" 참고).

## 게시 구조 (2026-10-31 확정)
1. 매일 정해진 시간에 Claude 예약 작업이 실행된다: 오늘의 경제 이슈 검색 → `content/YYYY-MM-DD-주제.json` 작성 → 렌더 → 이미지 직접 확인 → GitHub에 커밋·푸시.
2. GitHub Actions가 새 게시물을 감지해 Instagram Graph API(공식 콘텐츠 게시 API)로 올린다.
   - 이유: Claude 클라우드 작업 환경은 인스타·페이스북 서버에 직접 접속할 수 없다 (GitHub은 가능).
   - 토큰·계정 ID는 GitHub Secrets에만 저장한다. 코드나 JSON에 절대 넣지 않는다.
   - Graph API는 이미지 공개 URL이 필요하다. 저장소가 비공개라면 Actions에서 임시 공개 URL을 만드는 방법을 정해야 한다.
3. 처음 1~2주는 바로 게시하지 않고 "게시 대기" 상태로 둔다. 운영자가 휴대폰에서 확인 후 승인(예: GitHub Actions 수동 실행 또는 승인 라벨)하면 게시. 품질이 안정되면 완전 자동으로 전환.
4. 구현 (2026-10-31): `.github/workflows/instagram-publish.yml` + `scripts/publish_queue.sh` + `scripts/instagram.py`
   - 게시 대기열은 `queue/이름.png` + `queue/이름.txt`. main의 `queue/`가 바뀌면 워크플로가 게시하고 `published/이름/`(image.png, caption.txt, result.json)으로 옮긴다. `published/`에 같은 이름이 있으면 건너뛴다 (중복 방지).
   - 승인 방식: 예약 작업은 `post/이름` 브랜치에 커밋하고 PR(제목 `📮 게시 대기: …`)을 연다. 운영자가 Merge = 승인. 완전 자동 전환 시 main에 바로 푸시.
   - 대기열에 올리기: `python scripts/instagram.py enqueue output/이름.png` (크기·캡션 규칙 검사 포함)
   - 이미지는 JPEG로 변환해 공개 저장소의 `media` 브랜치에 올리고 raw URL을 Graph API에 넘긴다. 기본은 이 저장소. 비공개 전환 시 변수 `MEDIA_REPO` + 시크릿 `MEDIA_TOKEN` 필요.
   - Secrets: `IG_ACCESS_TOKEN`(만료 없는 페이지 토큰), `IG_USER_ID`. 수동 실행 mode `check`로 토큰만 점검 가능.
   - 운영자 세팅 절차: `docs/instagram-setup.md` (1~8단계)
- 인스타 계정: 비즈니스 계정으로 전환함. 페이스북 페이지 연결과 Meta 개발자 토큰 발급은 운영자가 직접 해야 하며, Claude가 화면별로 안내한다.

## 지금까지 정한 것
- 1번 컨셉: 경제 이슈 요약 인포그래픽 (참고 계정: @economy.notes)
- 연예·정치 가십형(@lime.now 스타일)은 하지 않기로 함. 명예훼손·초상권 위험이 크고 제휴 수익과 맞지 않음.
- 템플릿 두 가지를 번갈아 사용
  1. 사건·정책형: `templates/econ_infographic.py` (헤드라인 → 어떻게/얼마나 → 핵심 정리 6개 → 내 돈에 영향은? → 질문 배너)
  2. 수치 비교형: 꺾은선 차트 + 변동폭 표 (아직 미제작, @economy.notes 비자 거절률 게시물 참고)
- 후킹용 첫 장 이미지는 필수. 이미지는 직접 그린 일러스트, 무료 상업용 사진(Pexels 등), AI 생성 이미지만 사용.

## 반드시 지킬 규칙
- 실존 인물 사진, 기사·SNS 원본 사진은 쓰지 않는다. 인물 이슈는 아이콘·상징 이미지로 대체.
- 발언은 맥락을 자르거나 해석을 덧붙여 왜곡하지 않는다. 확인된 것과 미확인인 것을 구분해 표기.
- 이미지 하단에 출처(언론사·날짜)를 표기한다. AI·일러스트 이미지는 "일러스트" 또는 "AI 이미지"로 표기.
- 투자 관련 내용에는 "투자 권유가 아닌 정보 요약" 문구를 넣는다.
- 제휴 링크가 들어가면 "파트너스 활동으로 수수료를 받을 수 있음" 같은 광고 표기를 꼭 넣는다.
- 캡션에는 마크다운 기호(`**`, `##` 등)를 넣지 않는다. 인스타는 굵은 글씨를 지원하지 않는다.
- 캡션 끝 CTA는 한 줄, 자기 계정 멘션은 한 번만.

## 디자인 규칙
- 크기 1080×1350 (인스타 세로형)
- 폰트: Noto Sans CJK KR, 줄바꿈은 `word-break: keep-all`
- 경제 템플릿 색: 네이비 #14254a, 레드 #d63a2f, 크림 배경 #faf6ee, 강조 노랑 #ffd23f
- 채널명이 정해지면 `config.json`의 "경제한장"과 `@your_account`를 교체한다.

## 실행 방법
```
pip install playwright && playwright install chromium
python templates/econ_infographic.py content/2026-10-30-binance.json
```
→ `output/2026-10-30-binance.png` (이미지)와 `.txt` (캡션)가 생긴다.

## 새 게시물 만드는 법
1. `content/` 에 `YYYY-MM-DD-주제.json` 파일을 만든다. 형식은 `content/2026-10-30-binance.json`을 그대로 따른다.
2. 텍스트 표기: `[[글자]]` 강조색, `{{글자}}` 굵게, `|` 줄바꿈. 마크다운(`**`)은 쓰지 않는다.
3. `hero`는 상단 일러스트: `hack`, `chart_up`, `chart_down`, `policy` 중 선택. 새로 필요하면 `templates/econ_infographic.py`의 `HEROES`에 추가.
4. `points`는 정확히 6개, `impact`는 2개. 문구가 길어 하단 배너와 겹치면 스크립트가 경고하고 종료코드 2를 낸다 → 문구를 줄인다.
5. `investment: true`면 투자 권유 아님 문구, `affiliate: true`면 파트너스 광고 문구가 자동으로 들어간다.
6. 렌더한 이미지를 직접 열어 확인한 뒤 게시한다.

채널명·아이디는 `config.json`에서 바꾼다.

## 남은 할 일
- [x] 채널명 확정: @econ.oneshot (색은 기존 네이비·레드·크림 유지)
- [x] 인스타 계정 개설 (@econ.oneshot), 프로필 사진 A_sheet 적용, 비즈니스 계정 전환
- [x] 페이스북 페이지 "경제한장" 만들어 인스타 연결 (2026-10-31)
- [x] Meta 개발자 앱(econ-oneshot-publisher, 개발 모드) 생성, 만료 없는 페이지 토큰·인스타 계정 ID → GitHub Secrets 등록 (2026-10-31)
- [x] GitHub Actions 게시 워크플로 작성 (승인 후 게시 방식으로 시작). 토큰·계정 확인 성공 (2026-10-31), 실제 게시는 첫 게시물로 확인 예정
- [ ] 매일 이슈를 만드는 Claude 예약 작업 설정
- [ ] 저장소 비공개 전환 (운영자)
- [x] 사건·정책형 템플릿을 JSON 입력 방식으로 리팩터링 (`issue_cards.py`, `thumbnail.py`는 아직 하드코딩)
- [ ] 수치 비교형 템플릿 제작
- [ ] 첫 게시물: 오늘 이슈로 하나 만들어 수동 게시 (바이낸스 샘플은 이슈가 지나서 쓰지 않음)
- 프로필 소개글: "경제한장 | ECONOMY IN ONE / 📊 오늘의 경제 이슈, 한 장으로 끝 / 💡 뉴스 요약 · 내 돈에 미치는 영향까지", 이름 칸 추천: "경제한장 | 경제뉴스 요약"
- [ ] 제휴 프로그램 가입 (쿠팡 파트너스 등)
