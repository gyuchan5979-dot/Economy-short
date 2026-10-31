# 매일 게시 작업 절차 (Claude 예약 작업용)

예약 작업이 실행되면 이 문서를 처음부터 끝까지 따른다. CLAUDE.md의 "반드시 지킬 규칙"이 항상 우선이다.
운영자 결정(2026-10-31): 승인 없이 바로 게시한다. 대신 아래 품질 기준을 못 맞추면 **게시하지 않는다**.

## 게시 일정 (한국 시간)
| 회차 | 예약 실행 | 게시 목표 | 요일 | 다룰 내용 |
|---|---|---|---|---|
| 아침판 | 06:43 | 07:10~07:40 (출근길) | 화~토 | 밤사이 미국 증시·환율·글로벌 이슈 (한국 투자자 관점) |
| 저녁판 | 19:47 | 20:10~20:40 (퇴근 후 최다 접속) | 일~금 | 국내 이슈: 정책·부동산·물가·금리·기업·생활경제. 일요일은 "다음 주 경제 일정·관전 포인트" |

- 월요일 아침판이 없는 이유: 주말 동안 미국 장이 쉬어 새 시장 뉴스가 적다.
- 토요일 저녁판이 없는 이유: 토요일 저녁은 경제 콘텐츠 반응이 가장 낮은 시간대다. 일요일 저녁에 한 주를 여는 게시물로 대신한다.
- 하루 최대 2개. 품질이 우선이고 같은 날 비슷한 주제는 올리지 않는다.

## 1. 준비
```
fc-list | grep -qi "Noto Sans CJK" || (apt-get update -q && apt-get install -y -q fonts-noto-cjk fonts-noto-color-emoji)
python -c "import playwright" 2>/dev/null || pip install -q playwright pillow
```
- `playwright install`은 하지 않는다. 렌더러가 `/opt/pw-browsers/chromium`을 자동으로 쓴다.
- 폰트 없이 렌더하면 숫자·영문이 세리프체로 나온다. 렌더 결과에서 꼭 확인한다.
- `git pull origin main`으로 최신 상태를 받는다.

## 2. 주제 고르기
1. 최근 7일 게시물과 겹치지 않는지 확인: `ls published/ queue/ content/`
2. 회차에 맞는 오늘의 이슈를 웹 검색으로 3~5개 후보로 추린 뒤 하나를 고른다. 기준:
   - 많은 사람의 돈에 영향 (금리·환율·주가·부동산·물가·세금·연금·대출)
   - 숫자로 설명할 수 있음
   - 오늘 화제 (포털 경제 섹션 상위, 여러 언론이 다룸)
3. 피할 것: 정치 공방, 인물 가십, 확인되지 않은 루머, 특정 종목 매수·매도 권유로 읽힐 내용.

## 3. 사실 확인 (가장 중요)
- 이미지에 들어가는 **모든 숫자는 2개 이상 출처에서 일치**하는지 확인한다. 하나뿐이면 빼거나 "보도"·"추정"으로 표기한다.
- 날짜와 시간대를 확인한다. 미국 장(현지 날짜)과 한국 장의 선후 관계를 틀리지 않는다.
  예: 미국 금요일 급락은 한국 금요일 장 마감 **이후**다.
- 인과관계는 기사에 나온 만큼만 쓴다. 해석을 덧붙이지 않는다.
- 확신이 없으면 게시하지 않고 7번 "보고"만 한다.

## 4. 게시물 만들기
1. `content/YYYY-MM-DD-영문주제.json` 작성. 형식은 `content/2026-10-31-intel-shock.json`을 따른다.
   - 같은 날 두 번째 게시물이면 이름이 겹치지 않게 한다.
   - `hero`: 상승 `chart_up`, 하락 `chart_down`, 정책·제도 `policy`, 사고·해킹 `hack`
   - `points` 정확히 6개, `impact` 2개, `bars` 2~3개 (4개면 넘침)
   - 투자 관련이면 `investment: true`
   - `sources`: 언론사·날짜
2. 렌더: `python templates/econ_infographic.py content/파일.json`
   - 종료코드 2(넘침)면 문구를 줄여 다시 렌더한다. 보통 impact 문장을 한 줄로 줄이면 된다.
3. **이미지를 Read로 직접 열어서** 확인한다:
   - 글자 잘림, 겹침, 막대 안 숫자 넘침, 이모지 깨짐, 세리프체 숫자
   - 헤드라인 숫자와 본문 숫자가 서로 맞는지
4. 캡션 `output/파일.txt`를 읽고 확인한다: 마크다운 기호 없음, 자기 계정 멘션 1회, 해시태그 5~8개

## 5. 게시
```
python scripts/instagram.py enqueue output/파일.png
git add content/파일.json queue/
git commit -m "게시: <한 줄 제목>"
git pull --rebase origin main && git push origin main
```
- main의 `queue/`에 들어가면 GitHub Actions "Instagram 게시"가 자동으로 올린다.

## 6. 게시 확인
- GitHub MCP로 방금 실행된 "Instagram 게시" 워크플로를 확인한다. 성공하면 `published/이름/result.json`에 permalink가 생긴다.
- 실패하면 로그를 읽고 원인을 고친다. 그다음 workflow_dispatch(mode `publish`, slug=이름)로 다시 실행한다.
  - `published/이름`이 이미 있으면 이미 올라간 것이다. 절대 다시 올리지 않는다.
  - 토큰 오류(code 190)는 운영자만 고칠 수 있다. 보고만 한다.

## 7. 보고
마지막 메시지에 짧게 쓴다: 회차, 주제, 고른 이유 한 줄, permalink(또는 게시하지 않은 이유).
