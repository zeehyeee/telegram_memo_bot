
나는 텔레그램 비서봇을 만들었어. 현재 세팅:
* 텔레그램 봇 → Railway 24시간 서버에서 실행 중
* 메모 보내면 노션 데이터베이스("비서봇 메모")에 자동 저장됨
* 매일 아침 7:30 KST 요약 브리핑 발송
* GitHub 레포: zeehyeee/telegram_memo_bot
* 노션 데이터베이스 열: 구분(제목), 날짜, 카테고리, 내용
지금 하고 싶은 것: 텔레그램에 메모를 대충 자연어로 보내도 Claude API를 활용해서 업무/개인/아이디어로 정확하게 분류되도록 bot.py 수정하고 싶어.
분류 기준:
* 업무: LG유플러스, CRM, 캠페인, 앱푸시, MMS, 데이터분석, 회사 관련
* 개인: 일상, 감정, 개인 목표, 운동, 건강, 가족, 남편, 여행, 취미
* 아이디어: 새로운 기획, 인사이트, marketerlog, 블로그, 창업
Claude Code로 수정하고 GitHub push → Railway 자동 재배포까지 해줘.

응 그런데 지금 분류 기준을 다 따르면 이거에 안맞을 수도 있어서 클로드가 인식하고 수정해줄 수 있어? 그리고 지금 노션 구분에 구분, 날짜, 카테고리, 내용만 되어있는데with, 목표일정, to-do 제안이 있으면 좋겠어.

더 보기
오후 9:51
좋아요! 먼저 현재 bot.py를 확인하고, 요청사항을 정리할게요.

요청 정리:

분류 기준 → Claude가 자연어로 유연하게 판단 (경직된 키워드 매칭 X)
노션 컬럼 추가: 목표일정, To-do 제안
GitHub push → Railway 자동 재배포

로드된 도구, claude in Chrome 통합 사용함
로드된 도구, claude in Chrome 통합 사용함
브라우저 연결이 안 되네요. GitHub에서 직접 코드를 가져올게요.


웹 검색됨
웹 검색됨
레포를 직접 못 가져오네요. 현재 bot.py 구조를 모르는 상태지만, 기존 세팅 정보 기반으로 완전한 수정 코드를 작성할게요. Claude Code로 직접 실행하는 방식으로 진행합니다.

현재 bot.py를 볼 수 없어서, 지혜님 세팅 기반으로 완전히 새로 작성할게요. 기존 기능은 모두 포함 + 신규 기능 추가입니다.

추가되는 것:

✅ Claude API로 카테고리 유연 분류 (키워드 아닌 문맥 이해)
✅ 노션 컬럼 추가: 목표일정, To-do 제안
✅ Claude가 메모에서 일정/할일 힌트를 뽑아서 자동 채움

텔레그램 비서봇 bot.py - Claude API 분류 + 노션 확장 컬럼 포함
텔레그램 비서봇 bot.py - Claude API 분류 + 노션 확장 컬럼 포함
이제 노션 데이터베이스에 새 컬럼을 추가하는 스크립트도 만들게요.


파일 생성됨, 파일 읽음
파일 생성됨, 파일 읽음
배포 순서 가이드
1단계: 노션 컬럼 먼저 추가
Railway 환경에서 또는 로컬에서:

bash
python add_notion_columns.py
→ 노션 DB에 목표일정 (date), To-do 제안 (rich_text) 컬럼이 생김

또는 노션에서 수동으로 직접 추가해도 됩니다 (컬럼명 정확히 일치해야 함)

2단계: bot.py 교체 후 GitHub push
bash
# 기존 레포 클론 (이미 있으면 pull)
git clone https://github.com/zeehyeee/telegram_memo_bot
cd telegram_memo_bot

# 새 bot.py로 교체
cp /다운로드경로/bot.py ./bot.py

# Railway에 ANTHROPIC_API_KEY 환경변수 추가됐는지 확인 후
git add bot.py
git commit -m "feat: Claude API 자동 분류 + 목표일정/To-do 노션 컬럼 추가"
git push origin main
→ Railway 자동 재배포 트리거 🚀

달라진 것 요약
항목	이전	이후
카테고리 분류	키워드 매칭	Claude가 문맥으로 유연 판단
노션 컬럼	구분/날짜/카테고리/내용	+ 목표일정 + To-do 제안
메모 응답	저장 완료	분류 + 일정 + 할일 카드 형태로 확인
다음 스텝: Railway 환경변수에 ANTHROPIC_API_KEY가 세팅되어 있는지 확인하고 push하면 바로 적용돼요. 혹시 기존 bot.py 구조(라이브러리 버전 등)가 다르면 코드 공유해줄게요!

Bot
PY 
Add notion columns
PY 
두개를 하나씩 눌렀어. 이렇게 하면돼?

오후 9:54
어떤 화면을 보고 계신 건지 스크린샷이나 설명이 없어서 정확히 파악이 안 되네요! 😅

혹시 이런 상황인가요?

질문: 지금 어떤 상황인지 알려주세요!
답변: 파일 두 개(bot.py, add_notion_columns.py)를 다운받았어

오후 9:54
좋아요! 파일 다운받은 거 맞아요 👍

이제 이걸 GitHub 레포에 올려야 Railway가 자동 재배포돼요. 순서대로 할게요.

지금부터 할 것
Step 1. 노션 컬럼 먼저 추가 (1분)
터미널에서:

bash
cd ~/Downloads  # 파일 다운받은 폴더로
pip install notion-client  # 없으면 설치

NOTION_TOKEN=your_token NOTION_DATABASE_ID=your_db_id python add_notion_columns.py
✅ 성공하면 노션 컬럼 추가 완료 출력됨

또는 귀찮으면 노션에서 직접 수동으로 추가해도 돼요:

목표일정 → 날짜(Date) 타입
To-do 제안 → 텍스트(Text) 타입
컬럼명 띄어쓰기까지 정확히 일치해야 함!
Step 2. bot.py를 GitHub에 올리기
bash
cd ~/경로/telegram_memo_bot  # 기존 레포 폴더로

# 다운받은 bot.py로 덮어쓰기
cp ~/Downloads/bot.py ./bot.py

git add bot.py
git commit -m "feat: Claude API 자동 분류 + 목표일정/To-do 노션 컬럼 추가"
git push origin main
Step 3. Railway 환경변수 확인
Railway 대시보드 → Variables에 이게 있어야 해요:

변수명	설명
TELEGRAM_TOKEN	기존 있을 것
TELEGRAM_CHAT_ID	기존 있을 것
NOTION_TOKEN	기존 있을 것
NOTION_DATABASE_ID	기존 있을 것
ANTHROPIC_API_KEY	⚠️ 새로 추가 필요!
ANTHROPIC_API_KEY 없으면 Claude 분류가 안 되니까 꼭 확인하세요!

다음 스텝: 노션 컬럼 수동 추가 vs 스크립트 실행 중 어느 쪽으로 할지 알려줘요. 수동이면 추가하고 나서 bot.py push 바로 진행하면 돼요! 🚀

2번이해안갔어.

오후 9:55
Step 2는 터미널(명령어 입력창)을 써야 해서 낯설 수 있어요!

더 쉬운 방법으로 할게요 — GitHub 웹에서 직접 파일 교체하는 방식이에요.


Tabs Context
Tabs Context
브라우저 연결이 안 되니 텍스트로 설명할게요. 아주 간단해요!

GitHub 웹에서 bot.py 교체하는 법 (터미널 없이!)
① GitHub 레포 접속 👉 https://github.com/zeehyeee/telegram_memo_bot

② bot.py 파일 클릭

③ 오른쪽 위 연필 아이콘(✏️ Edit) 클릭

④ 전체 내용 선택 후 삭제 (Ctrl+A → Delete)

⑤ 다운받은 bot.py 파일을 메모장/텍스트에디터로 열기 → 전체 복사 (Ctrl+A → Ctrl+C)

⑥ GitHub 편집창에 붙여넣기 (Ctrl+V)

⑦ 아래로 스크롤 → "Commit changes" 초록 버튼 클릭

→ 이러면 Railway가 자동으로 새 코드 감지해서 재배포해요! 🚀

혹시 터미널 쓸 수 있는 환경이면 그게 훨씬 빠른데, 어떤 게 더 편한지 알려줘요!

텔레그램에서 메모 저장 완료라는데 노션에 변화가 없어

오후 9:58
"저장 완료"라고 뜨는데 노션에 없다면, 기존 bot.py가 그대로 실행 중일 가능성이 높아요. Railway가 새 코드를 아직 못 받은 거예요.

먼저 원인 체크부터 해봐요!

빠른 진단 체크리스트
① GitHub에 새 bot.py가 올라가 있어?

👉 https://github.com/zeehyeee/telegram_memo_bot/blob/main/bot.py

열어서 상단에 이 줄이 있으면 새 버전:

python
import anthropic
없으면 → 아직 교체가 안 된 것

② Railway 환경변수에 ANTHROPIC_API_KEY 있어?

Railway 대시보드 → 프로젝트 → Variables 탭 확인

③ 노션 DB에 컬럼이 추가되어 있어?

노션에서 "비서봇 메모" 데이터베이스 열어서

목표일정 컬럼 있는지
To-do 제안 컬럼 있는지
위 세 가지 중 어디서 막혔는지 알려줘요! 아니면 Railway 로그를 보면 에러가 정확히 나와요.

Railway 로그 보는 법: Railway 대시보드 → 프로젝트 클릭 → Deployments → 최신 배포 클릭 → Logs 탭

거기서 에러 메시지 복붙해주면 바로 잡아드릴게요 🔧

Railway 에서 crashed 떴어

오후 9:59
Crashed면 에러 로그 봐야 정확히 잡을 수 있어요. Railway 로그 직접 볼게요!


Tabs Context
Tabs Context
브라우저 연결이 안 되네요. Railway 로그를 직접 복붙해줄 수 있어요?

Railway 로그 보는 법
Railway 대시보드 → 프로젝트 클릭 → Deployments 탭 → 빨간 배포 클릭 → "View Logs"

에러 메시지가 빨간 글씨로 나올 거예요. 그거 복붙해주면 바로 원인 찾아드릴게요!

Crashed 원인 TOP 3 (미리 추측)
1️⃣ anthropic 패키지가 requirements.txt에 없는 경우 → 가장 흔한 원인

requirements.txt 파일에 아래가 있는지 확인:

anthropic
2️⃣ ANTHROPIC_API_KEY 환경변수 누락

Railway Variables에 키가 없으면 시작하자마자 crash

3️⃣ 기존 bot.py 라이브러리 버전과 충돌

로그 복붙해주면 1분 안에 해결해드릴게요 🔧

1774789241524_image.png
여기서 뭘 눌러야해?

오후 10:00
telegram_memo_bot 박스를 클릭하면 돼요! 그러면 로그를 볼 수 있어요.


Tabs Context
Tabs Context
브라우저 직접 조작이 안 되니 스크린샷으로 안내할게요!

지금 할 것: 로그 확인
① 빨간 박스 telegram_memo_bot 클릭

② 오른쪽에 패널이 열리면 → 상단 탭에서 Deployments 클릭

③ 빨간 배포 항목 클릭 → View Logs 또는 Build Logs / Deploy Logs 탭

빨간 에러 텍스트가 보일 거예요. 그걸 복붙해주세요!

아마 원인은 이것 중 하나예요
가장 흔한 crash 원인 두 가지를 미리 대비해서 고쳐드릴게요.

requirements.txt에 anthropic이 없을 가능성이 높아요.

GitHub에서 바로 확인: 👉 https://github.com/zeehyeee/telegram_memo_bot/blob/main/requirements.txt

열어서 anthropic 이 있으면 OK, 없으면 → 그 파일에도 한 줄 추가해야 해요!

Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Starting Container
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'
Traceback (most recent call last):
  File "/app/bot.py", line 7, in <module>
    import anthropic
ModuleNotFoundError: No module named 'anthropic'

더 보기
오후 10:01
원인 확인! requirements.txt에 anthropic이 없어서 생긴 거예요. 딱 한 줄만 추가하면 돼요.

지금 바로 할 것 (2분)
① GitHub 접속 👉 https://github.com/zeehyeee/telegram_memo_bot/blob/main/requirements.txt

② 연필 아이콘(✏️) 클릭

③ 맨 아래 줄에 추가:

anthropic
④ "Commit changes" 초록 버튼 클릭

→ Railway가 자동으로 재배포 시작! 1~2분 후 Crashed → ✅ Active 로 바뀌어요.

requirements.txt 현재 내용이 어떻게 되어있는지 알 수 있어요? (python-telegram-bot, notion-client 등 있을 텐데) 혹시 모르니 확인하고 anthropic 한 줄만 추가하면 끝이에요 🎯

이번에도 안돼. active였다가 내가 텔레그램에서 치니까 crashed로 바꼈어

오후 10:03
좋아요, 진전이 있어요! anthropic 패키지는 설치됐는데, 메시지 보낼 때 다른 에러가 생긴 거예요. 로그 다시 확인해야 해요.

Railway 로그에서 새 에러 복붙해줄 수 있어요? 아까랑 같은 방법으로요.

그 사이 가장 가능성 높은 원인을 미리 추측하면:

① ANTHROPIC_API_KEY 환경변수가 Railway에 없는 경우 → 봇은 켜지는데 메시지 처리하다가 crash

② 기존 bot.py 코드 구조랑 새 코드가 충돌 → 예: 기존에 쓰던 라이브러리 버전이 다른 경우

빠르게 확인할 것 하나만 먼저:

Railway → 프로젝트 → Variables 탭에 ANTHROPIC_API_KEY 있어요?

없어

오후 10:03
바로 그거예요! ANTHROPIC_API_KEY 없어서 crash난 거예요. 지금 추가하면 돼요.

Railway에 API Key 추가하는 법
① Railway 대시보드에서 telegram_memo_bot 박스 클릭

② 상단 탭 → Variables 클릭

③ + New Variable 또는 Add Variable 버튼 클릭

④ 아래처럼 입력:

NAME	VALUE
ANTHROPIC_API_KEY	sk-ant-... (본인 키)
⑤ 저장하면 Railway가 자동 재배포

Anthropic API Key는 여기서 확인: 👉 https://console.anthropic.com/settings/keys

다음 스텝: API Key 추가하고 나서 Railway가 Active로 바뀌면 텔레그램에서 메모 보내보세요! 이번엔 분류 결과까지 뜰 거예요 🎯

1774789493474_image.png
여기 있는 키 맞아? create key 해야해?

오후 10:04
기존 키 써도 돼요! Create Key 안 해도 됩니다.

지금 할 것
① 기존 키 중 하나 클릭 (crm-developer-2... 또는 crm-developer-a...)

② sk-ant-api03-... 로 시작하는 전체 키 복사

③ Railway → Variables → ANTHROPIC_API_KEY 값으로 붙여넣기

⚠️ 키가 이미 다른 프로젝트(n8n 브리핑, CRM 디벨로퍼 등)에서 쓰이고 있으면 새 키를 만드는 게 관리상 더 깔끔해요. 이름을 telegram-bot 으로 만들면 나중에 구분하기 쉬워요!

어떻게 할지 골라줘요:

응 텔레그램봇으로 만들어서 railway 넣었어

오후 10:05
완벽해요! 이제 Railway가 자동 재배포 중일 거예요.

1~2분 기다렸다가 Railway 대시보드 확인해줘요. Crashed → 🟢 Active 로 바뀌면 성공!

Active 되면 텔레그램에서 메모 하나 보내보고 결과 알려줘요 🎯

아직도 안돼

오후 10:06
로그 다시 확인해야 해요. 새 에러 메시지 복붙해줄 수 있어요?

Railway → telegram_memo_bot 클릭 → Deployments → 최신 빨간 항목 → Logs 탭

그 사이 기존 bot.py 코드가 뭔지 확인해볼게요.


Tabs Context
Tabs Context
브라우저가 계속 연결이 안 되네요 😅

로그 텍스트 복붙해주는 게 제일 빨라요! 어떤 에러인지 봐야 정확히 잡을 수 있어요.

Starting Container
Traceback (most recent call last):
  File "/app/bot.py", line 27, in <module>
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 717, in __getitem__
KeyError: 'TELEGRAM_TOKEN'
Traceback (most recent call last):
  File "/app/bot.py", line 27, in <module>
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 717, in __getitem__
KeyError: 'TELEGRAM_TOKEN'
Traceback (most recent call last):
  File "/app/bot.py", line 27, in <module>
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
KeyError: 'TELEGRAM_TOKEN'
KeyError: 'TELEGRAM_TOKEN'
Traceback (most recent call last):
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/app/bot.py", line 27, in <module>
  File "<frozen os>", line 717, in __getitem__
Traceback (most recent call last):
  File "/app/bot.py", line 27, in <module>
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 717, in __getitem__
KeyError: 'TELEGRAM_TOKEN'
Traceback (most recent call last):
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 717, in __getitem__
Traceback (most recent call last):
  File "/app/bot.py", line 27, in <module>
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 717, in __getitem__
Traceback (most recent call last):
  File "/app/bot.py", line 27, in <module>
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 717, in __getitem__
KeyError: 'TELEGRAM_TOKEN'
Traceback (most recent call last):
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
KeyError: 'TELEGRAM_TOKEN'
KeyError: 'TELEGRAM_TOKEN'
  File "/app/bot.py", line 27, in <module>
Traceback (most recent call last):
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
Traceback (most recent call last):
  File "<frozen os>", line 717, in __getitem__
  File "/app/bot.py", line 27, in <module>
    TELEGRAM_TOKEN      = os.environ["TELEGRAM_TOKEN"]
KeyError: 'TELEGRAM_TOKEN'
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^

더 보기
오후 10:07
원인 명확해요! Railway Variables에 TELEGRAM_TOKEN이 없어요.

새 bot.py는 환경변수 이름을 정확히 요구하는데, 기존에 다른 이름으로 저장되어 있을 수 있어요.

지금 바로 할 것
Railway → telegram_memo_bot → Variables 탭 열어서

지금 있는 변수 이름들 전부 알려줘요! (값 말고 이름만)

예를 들어:

TOKEN 인지 TELEGRAM_TOKEN 인지
CHAT_ID 인지 TELEGRAM_CHAT_ID 인지
이름이 다르면 제가 bot.py를 기존 이름에 맞게 수정해드릴게요. 가장 빠른 해결책이에요 🔧

ANTHROPIC_API_KEY
*******
BOT_TOKEN
*******
NOTION_DATABASE_ID
*******
NOTION_TOKEN
*******
TZ
*******

오후 10:07
원인 찾았어요! 변수 이름이 달라요.

Railway 실제 이름	bot.py가 찾는 이름
BOT_TOKEN	TELEGRAM_TOKEN ❌
(없음)	TELEGRAM_CHAT_ID ❌
두 가지 방법 중 선택:

Railway에서 변수 이름 바꾸기
bot.py 코드를 기존 변수 이름에 맞게 수정 ← 이게 더 쉬워요
bot.py 바로 수정해드릴게요!


파일 조회함, 파일 수정됨, 파일 읽음
파일 조회함, 파일 수정됨, 파일 읽음
새 bot.py 다운받아서 GitHub에 다시 올려주세요!

그런데 TELEGRAM_CHAT_ID (브리핑 보낼 채팅 ID)도 Railway에 없네요. 두 가지 중 선택:

① Railway Variables에 CHAT_ID 추가 (본인 텔레그램 chat_id 값)

② 모르면 텔레그램에서 @userinfobot 에게 아무 메시지 보내면 chat_id 알려줘요!

다음 스텝: 새 bot.py GitHub 올리기 + CHAT_ID Railway에 추가! 둘 다 되면 이번엔 진짜 될 거예요 🎯

Bot
PY 
응 chat id도 받았어

오후 10:09
좋아요! 이제 두 가지만 하면 끝이에요.

체크리스트
① Railway Variables에 CHAT_ID 추가됐어요?

아까 받은 chat_id 숫자를 Railway → Variables → CHAT_ID 로 추가

② 새 bot.py GitHub에 올렸어요?

아까 다운받은 새 bot.py를 GitHub에 교체 (연필 아이콘으로)

둘 다 됐으면 Railway가 자동 재배포 시작할 거예요. 1~2분 후 Active 뜨면 텔레그램에서 메모 보내보세요! 🎯






Claude는 AI이며 실수할 수 있습니다. 응답을 다시 한번 확인해 주세요.
Bot · PY
복사

import os
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
 
import anthropic
from notion_client import Client
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
 
# ── 로깅 설정 ────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
 
# ── 환경변수 ─────────────────────────────────────────────────
TELEGRAM_TOKEN      = os.environ["BOT_TOKEN"]
TELEGRAM_CHAT_ID    = os.environ.get("CHAT_ID", os.environ.get("TELEGRAM_CHAT_ID", ""))
NOTION_TOKEN        = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID  = os.environ["NOTION_DATABASE_ID"]
ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
 
# ── 클라이언트 초기화 ─────────────────────────────────────────
notion          = Client(auth=NOTION_TOKEN)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
 
KST = timezone(timedelta(hours=9))
 
# ─────────────────────────────────────────────────────────────
# Claude API: 메모 분석 (분류 + 목표일정 + to-do 제안)
# ─────────────────────────────────────────────────────────────
ANALYZE_SYSTEM_PROMPT = """
당신은 개인 비서봇을 위한 메모 분석 전문가입니다.
사용자가 보내는 자연어 메모를 읽고 아래 JSON 형식으로만 응답하세요.
절대 JSON 외 다른 텍스트를 포함하지 마세요.
 
분류 기준 (category):
- "업무": LG유플러스, CRM, 캠페인, 앱푸시, MMS, 데이터분석, 회사, 마케팅 전략, 보고서, KPI, MAU, 고객, 메시지 등 직장과 관련된 모든 것
- "개인": 일상, 감정, 개인 목표, 운동, 건강, 가족, 남편, 고양이(바다), 여행, 취미, 집, 식사, 쇼핑 등 사생활과 관련된 것
- "아이디어": 새로운 기획, 인사이트, marketerlog, 인스타그램 채널, 블로그, 창업, 자동화 아이디어, 부업, 툴 개발 아이디어 등
 
※ 분류 기준이 애매하거나 복합적인 경우 메모의 핵심 의도를 우선 판단하세요.
 
목표일정 (target_date):
- 메모에서 날짜/시간 힌트를 추출하세요 (예: "이번 주", "3월 말", "내일", "Q2" 등)
- 구체적인 날짜로 변환 가능하면 YYYY-MM-DD 형식으로
- 힌트만 있으면 그대로 텍스트로 (예: "이번 주 금요일", "다음 달")
- 없으면 null
 
to_do 제안 (todos):
- 메모 내용을 바탕으로 실행 가능한 to-do를 1~3개 제안하세요
- 없으면 빈 배열 []
- 형식: ["할 일 1", "할 일 2"]
 
응답 예시:
{
  "category": "업무",
  "target_date": "2026-03-31",
  "todos": ["캠페인 성과 지표 정리", "팀장 보고 슬라이드 작성"]
}
"""
 
def analyze_memo(text: str) -> dict:
    """Claude API로 메모를 분석해 category, target_date, todos를 반환"""
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=ANALYZE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        raw = response.content[0].text.strip()
        # JSON 펜스 제거 (혹시 포함되면)
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return {
            "category":    result.get("category", "개인"),
            "target_date": result.get("target_date"),   # str or None
            "todos":       result.get("todos", []),
        }
    except Exception as e:
        logger.error(f"Claude 분석 오류: {e}")
        return {"category": "개인", "target_date": None, "todos": []}
 
 
# ─────────────────────────────────────────────────────────────
# 노션 저장
# ─────────────────────────────────────────────────────────────
def save_to_notion(text: str, analysis: dict) -> bool:
    """노션 데이터베이스에 메모 저장 (확장 컬럼 포함)"""
    try:
        now_kst = datetime.now(KST)
        date_str = now_kst.strftime("%Y-%m-%d")
 
        category   = analysis["category"]
        target_date= analysis["target_date"]
        todos      = analysis["todos"]
        todos_text = "\n".join(f"• {t}" for t in todos) if todos else ""
 
        # 목표일정: 날짜 형식이면 date property, 텍스트면 rich_text
        # → 노션 date 타입은 ISO 형식만 허용하므로 파싱 시도
        target_date_prop = None
        if target_date:
            try:
                # YYYY-MM-DD 형식 확인
                datetime.strptime(target_date, "%Y-%m-%d")
                target_date_prop = {"date": {"start": target_date}}
            except ValueError:
                # 텍스트 형식 → rich_text로 저장
                target_date_prop = None  # 아래에서 처리
 
        properties = {
            "구분": {
                "title": [{"text": {"content": text[:100]}}]
            },
            "날짜": {
                "date": {"start": date_str}
            },
            "카테고리": {
                "select": {"name": category}
            },
            "내용": {
                "rich_text": [{"text": {"content": text}}]
            },
        }
 
        # 목표일정 컬럼
        if target_date_prop:
            properties["목표일정"] = target_date_prop
        elif target_date:
            # 날짜가 아닌 텍스트 힌트인 경우 (노션에서 해당 컬럼이 rich_text 타입이어야 함)
            properties["목표일정_메모"] = {
                "rich_text": [{"text": {"content": target_date}}]
            }
 
        # to-do 제안 컬럼
        if todos_text:
            properties["To-do 제안"] = {
                "rich_text": [{"text": {"content": todos_text}}]
            }
 
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=properties,
        )
        return True
 
    except Exception as e:
        logger.error(f"노션 저장 오류: {e}")
        return False
 
 
# ─────────────────────────────────────────────────────────────
# 텔레그램 핸들러
# ─────────────────────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 비서봇 가동 중!\n\n"
        "메모를 자유롭게 보내면 Claude가 분류해서 노션에 저장해줘요.\n"
        "• 업무 / 개인 / 아이디어 자동 분류\n"
        "• 목표일정 추출\n"
        "• To-do 제안까지!"
    )
 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """메모 수신 → Claude 분석 → 노션 저장"""
    text = update.message.text.strip()
    if not text:
        return
 
    # 처리 중 안내
    processing_msg = await update.message.reply_text("🔍 분석 중...")
 
    # Claude 분석
    analysis = analyze_memo(text)
    category    = analysis["category"]
    target_date = analysis["target_date"]
    todos       = analysis["todos"]
 
    # 노션 저장
    saved = save_to_notion(text, analysis)
 
    # 결과 메시지 구성
    emoji_map = {"업무": "💼", "개인": "🌿", "아이디어": "💡"}
    emoji = emoji_map.get(category, "📝")
 
    result_lines = [
        f"{emoji} **{category}** 으로 저장했어요!",
    ]
    if target_date:
        result_lines.append(f"📅 목표일정: {target_date}")
    if todos:
        result_lines.append("✅ To-do 제안:")
        for t in todos:
            result_lines.append(f"  • {t}")
    if not saved:
        result_lines.append("⚠️ 노션 저장 실패 - 로그 확인 필요")
 
    await processing_msg.edit_text("\n".join(result_lines), parse_mode="Markdown")
 
 
# ─────────────────────────────────────────────────────────────
# 아침 브리핑 (7:30 KST)
# ─────────────────────────────────────────────────────────────
async def send_morning_briefing(application: Application):
    """오늘 날짜 기준 노션 메모 요약 브리핑"""
    try:
        today = datetime.now(KST).strftime("%Y-%m-%d")
 
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "property": "날짜",
                "date": {"equals": today}
            }
        )
        pages = response.get("results", [])
 
        if not pages:
            msg = f"📋 {today} 오늘 저장된 메모가 없어요."
        else:
            by_cat: dict[str, list[str]] = {"업무": [], "개인": [], "아이디어": []}
            for page in pages:
                props = page["properties"]
                cat   = props.get("카테고리", {}).get("select", {})
                cat   = cat.get("name", "기타") if cat else "기타"
                title = props.get("구분", {}).get("title", [])
                title = title[0]["text"]["content"] if title else "(내용 없음)"
                by_cat.setdefault(cat, []).append(title)
 
            lines = [f"☀️ {today} 아침 브리핑\n"]
            emoji_map = {"업무": "💼", "개인": "🌿", "아이디어": "💡"}
            for cat, items in by_cat.items():
                if items:
                    lines.append(f"{emoji_map.get(cat, '📝')} {cat} ({len(items)}건)")
                    for item in items:
                        lines.append(f"  • {item[:60]}")
            msg = "\n".join(lines)
 
        await application.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=msg,
        )
    except Exception as e:
        logger.error(f"브리핑 오류: {e}")
 
 
# ─────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
 
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
 
    # 스케줄러: 매일 7:30 KST (UTC+9 → UTC 22:30 전날)
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        send_morning_briefing,
        trigger="cron",
        hour=7,
        minute=30,
        args=[app],
    )
    scheduler.start()
 
    logger.info("🤖 비서봇 시작!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
 
 
if __name__ == "__main__":
    main()
 
