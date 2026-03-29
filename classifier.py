WORK_KEYWORDS = [
    # LG유플러스 / CRM
    "유플러스", "uplus", "lg u+", "crm", "고객관리", "고객 관리",
    # 캠페인 / 마케팅
    "캠페인", "campaign", "앱푸시", "app push", "push", "푸시",
    "mms", "문자", "sms", "lms", "발송", "타겟", "타깃", "수신",
    # 데이터 분석
    "데이터분석", "데이터 분석", "분석", "지표", "kpi", "대시보드",
    "sql", "쿼리", "query", "tableau", "태블로", "excel", "엑셀",
    "통계", "세그먼트", "코호트", "cohort", "funnel", "퍼널",
    # 회사 업무 일반
    "회의", "미팅", "meeting", "보고", "보고서", "기획서", "제안서",
    "프로젝트", "project", "마감", "deadline", "업무", "작업", "task",
    "태스크", "일정", "발표", "pt", "ppt", "검토", "수정", "피드백",
    "결재", "승인", "처리", "담당", "진행", "협의", "협업",
    "팀", "부서", "상사", "동료", "슬랙", "slack", "이메일", "메일",
    "출근", "퇴근", "야근", "출장", "직장", "회사", "office", "work",
    "클라이언트", "고객", "계약", "대응", "요청", "산출물",
]

IDEA_KEYWORDS = [
    # marketerlog / 블로그
    "marketerlog", "마케터로그", "블로그", "blog", "포스팅", "글쓰기",
    "뉴스레터", "newsletter", "콘텐츠", "content",
    # 창업 / 기획
    "창업", "사이드프로젝트", "사이드 프로젝트", "side project",
    "스타트업", "startup", "런칭", "launch", "서비스기획", "서비스 기획",
    "프로토타입", "prototype", "mvp", "린", "린스타트업",
    # 아이디어 / 인사이트
    "아이디어", "idea", "인사이트", "insight", "영감", "구상",
    "어떨까", "해보면", "만들면", "개발하면", "만약", "가능할까",
    "시도", "새로운", "창의", "발명", "concept", "brainstorm",
    "떠올랐", "생각났", "문득", "불현듯", "왜 안될까", "해볼까",
    "실험", "테스트해", "기획",
]

PERSONAL_KEYWORDS = [
    # 일상 / 감정
    "일상", "오늘", "기분", "감정", "느낌", "행복", "슬픔", "피곤",
    "스트레스", "힘들", "좋았", "나빴", "즐거", "우울",
    # 건강 / 운동
    "운동", "헬스", "gym", "러닝", "달리기", "요가", "필라테스",
    "다이어트", "식단", "몸무게", "체중", "건강", "병원", "약",
    # 가족 / 남편
    "남편", "가족", "부모님", "엄마", "아빠", "아이", "아기",
    "집", "육아", "결혼", "부부",
    # 개인 목표
    "목표", "계획", "독서", "책", "공부", "자기계발", "습관",
    "루틴", "routine",
]


def classify_memo(text: str) -> str:
    text_lower = text.lower()

    work_score = sum(1 for kw in WORK_KEYWORDS if kw in text_lower)
    idea_score = sum(1 for kw in IDEA_KEYWORDS if kw in text_lower)
    personal_score = sum(1 for kw in PERSONAL_KEYWORDS if kw in text_lower)

    # 키워드 없으면 → 개인
    if work_score == 0 and idea_score == 0 and personal_score == 0:
        return "개인"

    # 개인 키워드가 있고 업무/아이디어 키워드와 동점이면 → 개인 우선
    top = max(work_score, idea_score, personal_score)
    if personal_score == top:
        return "개인"
    if work_score == top:
        return "업무"
    return "아이디어"
