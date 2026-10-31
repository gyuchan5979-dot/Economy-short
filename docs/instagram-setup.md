# 인스타 자동 게시 세팅 가이드 (운영자용)

순서대로 따라 하면 된다. 단계가 끝날 때마다 Claude에게 "N단계 끝"이라고 알려주면 다음 단계로 넘어간다.
Meta 화면은 자주 바뀐다. 메뉴 이름이 다르면 화면 캡처를 보여주면 된다 (토큰 값은 가리고).

> ⚠️ 액세스 토큰·앱 시크릿은 Claude 채팅, 카톡, 메모앱 어디에도 붙여 넣지 않는다. GitHub Secrets에만 넣는다.
> 계정 ID(숫자)는 비밀이 아니라서 채팅에 적어도 된다.

| 단계 | 내용 | 기기 | 시간 |
|---|---|---|---|
| 1 | 페이스북 페이지 만들기 | 휴대폰 OK | 5분 |
| 2 | 인스타 ↔ 페이지 연결 | 휴대폰 OK | 3분 |
| 3 | Meta 개발자 계정 등록 | PC 권장 | 5분 |
| 4 | 앱 만들기 | PC | 5분 |
| 5 | 토큰 발급 (Graph API 탐색기) | PC | 10분 |
| 6 | 만료 없는 토큰으로 바꾸기 + 계정 ID 확인 | PC | 10분 |
| 7 | GitHub Secrets 등록 | PC | 3분 |
| 8 | 연결 테스트 (게시 안 함) | 휴대폰 OK | 2분 |

---

## 1단계. 페이스북 페이지 만들기
1. 페이스북 앱 → 오른쪽 아래(아이폰) / 오른쪽 위(안드로이드) **☰ 메뉴** → **페이지** → **＋ 만들기** (또는 "페이지 만들기")
   - PC: facebook.com/pages/create
2. 페이지 이름: `경제한장`
3. 카테고리: `미디어/뉴스 회사` (검색창에 "뉴스" 입력 후 선택)
4. 소개: `오늘의 경제 이슈, 한 장으로 끝`
5. 프로필 사진: `assets/profile/A_sheet.png` (인스타와 동일). 커버 사진은 건너뛰어도 된다.
6. 연락처·웹사이트 등은 모두 **건너뛰기**. 친구 초대도 건너뛰기.

체크: 페이지가 생기고 내가 관리자로 되어 있다.

## 2단계. 인스타 계정을 페이지에 연결
방법 A (인스타 앱, 추천)
1. 인스타 @econ.oneshot 로그인 → 프로필 → **프로필 편집**
2. "공개 비즈니스 정보" 아래 **페이지** → **기존 페이지 연결** → `경제한장` 선택 → 완료
   - 페이스북 로그인 창이 뜨면 1단계 페이지를 만든 계정으로 로그인

방법 B (페이스북 쪽에서)
- 페이지로 전환 → 설정 → **연결된 계정** (또는 "링크된 계정") → Instagram → 연결

체크: 프로필 편집 → 페이지 칸에 "경제한장"이 보인다.

## 3단계. Meta 개발자 계정 등록 (PC)
1. https://developers.facebook.com 접속 → 오른쪽 위 **시작하기** (또는 "로그인")
2. 1단계 페이스북 계정으로 로그인 → 휴대폰 번호 인증 → 직업은 "개발자" 또는 "기타" 아무거나
체크: 오른쪽 위에 **내 앱** 메뉴가 보인다.

## 4단계. 앱 만들기 (PC)
1. **내 앱** → **앱 만들기**
2. 앱 이름: `econ-oneshot-publisher` / 연락처 이메일: 본인 이메일
3. 사용 사례(Use case) 선택 화면:
   - **기타(Other)** 선택 → 다음 → 앱 유형 **비즈니스(Business)** 선택
   - "Instagram에서 메시지 및 콘텐츠 관리" 같은 항목이 보여도 이번에는 **기타 → 비즈니스**로 간다 (페이스북 페이지 연결 방식을 쓰기 때문)
4. 비즈니스 포트폴리오(비즈니스 계정) 연결은 "지금은 연결 안 함"으로 넘어가도 된다.
5. 앱 대시보드 → **제품 추가**에서 **Instagram** (Instagram Graph API / "Facebook 로그인을 통한 API 설정") 의 **설정** 클릭
6. 앱은 **개발 모드** 그대로 둔다. 내 계정에만 올리는 용도라 앱 검수(App Review)는 필요 없다.

체크: 앱 대시보드 왼쪽 메뉴에 Instagram 항목이 생겼다. **앱 설정 → 기본 설정**에서 앱 ID가 보인다.

## 5단계. 토큰 발급 — Graph API 탐색기 (PC)
1. https://developers.facebook.com/tools/explorer 접속
2. 오른쪽 **Meta 앱**: `econ-oneshot-publisher` 선택
3. **사용자 또는 페이지**: "사용자 토큰(User Token)"
4. **권한 추가**에서 아래 5개 체크
   - `pages_show_list`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
   - `business_management`
5. **Generate Access Token** → 팝업에서 **경제한장 페이지**와 **@econ.oneshot** 을 선택(체크)하고 모두 허용
6. 위쪽 입력칸에 아래를 붙여 넣고 **제출**
   ```
   me/accounts?fields=id,name,instagram_business_account{id,username}
   ```
   결과에 `"username": "econ.oneshot"` 이 보이면 성공. 그 옆 `instagram_business_account`의 `id` (17로 시작하는 긴 숫자)가 **IG_USER_ID**다. 메모해 둔다.

## 6단계. 만료 없는 토큰으로 바꾸기 (PC)
5단계 토큰은 1~2시간이면 만료된다. 아래처럼 바꾸면 만료 없는 **페이지 토큰**을 얻는다.
1. 탐색기의 토큰 칸 옆 **ⓘ** 아이콘 → **액세스 토큰 도구에서 열기** (또는 https://developers.facebook.com/tools/debug/accesstoken 에 토큰 붙여 넣기 → 디버그)
2. 맨 아래 **액세스 토큰 연장(Extend Access Token)** 클릭 → 비밀번호 확인 → 새 토큰(장기 사용자 토큰, 60일) 이 나온다 → 복사
3. 탐색기로 돌아가 토큰 칸에 그 장기 토큰을 붙여 넣고 다시 실행
   ```
   me/accounts?fields=id,name,access_token,instagram_business_account{id,username}
   ```
4. 결과의 `access_token` (경제한장 페이지 것) = **IG_ACCESS_TOKEN** 후보
5. 이 값을 액세스 토큰 디버거에 넣어 확인: **유형: Page**, **만료: 안 함(Never)** 이면 완성
   - 바로 7단계로 가서 GitHub Secrets에 넣고, 복사해 둔 곳(메모 등)은 지운다.

## 7단계. GitHub Secrets 등록 (PC 권장, 휴대폰은 브라우저 "데스크톱 사이트"로)
1. https://github.com/gyuchan5979-dot/Economy-short → **Settings** → 왼쪽 **Secrets and variables → Actions**
2. **New repository secret** 두 번:
   | Name | Secret |
   |---|---|
   | `IG_ACCESS_TOKEN` | 6단계의 페이지 토큰 |
   | `IG_USER_ID` | 5단계의 인스타 비즈니스 계정 ID (17...) |

## 8단계. 연결 테스트 (게시 안 함)
1. 저장소 → **Actions** 탭 → 왼쪽 **Instagram 게시** → **Run workflow**
2. mode: `check` 그대로 → **Run workflow**
3. 1분 뒤 초록색 ✅ 이면 성공. 로그 "토큰·계정 확인"에 `계정: @econ.oneshot` 이 찍힌다.
   - 빨간색이면 로그의 ❌ 줄을 Claude에게 보여준다 (토큰 값은 로그에 `***`로 가려져 나온다).

---

## 세팅 후: 매일 게시 흐름 (승인 방식)
1. Claude 예약 작업이 게시물을 만들고 `post/날짜-주제` 브랜치로 **PR**을 연다. PR 제목은 `📮 게시 대기: …`
2. 운영자는 GitHub 앱(휴대폰)에서 PR → **Files changed** 탭에서 이미지와 캡션 확인
3. 괜찮으면 **Merge** → 1~2분 안에 인스타에 올라가고, 파일이 `published/`로 옮겨진다
4. 고칠 게 있으면 PR에 댓글로 남기거나, 올리지 않으려면 **Close**
- 수동으로 다시 올리기: Actions → Instagram 게시 → Run workflow → mode `publish`, slug에 이름 입력
- 완전 자동 전환: 예약 작업이 PR 대신 main에 바로 푸시하도록 바꾸면 끝 (워크플로는 그대로)

## 저장소를 비공개로 바꿀 때
인스타 API는 **공개 이미지 URL**만 받는다. 지금은 저장소가 공개라 `media` 브랜치의 raw URL을 쓴다.
비공개로 바꾸기 전에:
1. 공개 저장소 `econ-oneshot-media` 를 새로 만든다 (빈 저장소, README만)
2. GitHub → Settings(개인) → Developer settings → **Fine-grained token** 생성: 대상 저장소 `econ-oneshot-media`만, 권한 Contents: Read and write
3. Economy-short 저장소 Secrets에 `MEDIA_TOKEN` (위 토큰), **Variables** 탭에 `MEDIA_REPO` = `gyuchan5979-dot/econ-oneshot-media`
(게시되는 이미지는 어차피 인스타에 공개되는 것이라 이미지 저장소가 공개여도 문제없다.)

## 문제 해결
- `계정이 config.json과 다릅니다` → 다른 인스타 계정이 연결됨. 2단계 확인
- `code 190` → 토큰 만료/무효. 6단계 다시
- `code 10` 또는 `200` 권한 오류 → 5단계 권한 5개 중 빠진 것이 있음. 다시 Generate
- `이미지 공개 URL에 접근할 수 없습니다` → 저장소가 비공개가 됐는데 MEDIA_REPO 설정 안 함
- 페이지 토큰으로 게시가 거부되면 → 6단계 2번의 장기 사용자 토큰을 대신 넣는다 (단 60일마다 갱신 필요)
- 24시간 게시 한도: check 로그에 "24시간 게시량: 사용/한도"로 표시 (2026-10 기준 100개)
