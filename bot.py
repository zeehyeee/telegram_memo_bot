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

TELEGRAM_TOKEN     = os.environ["BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ.get("CHAT_ID", os.environ.get("TELEGRAM_CHAT_ID", ""))
NOTION_TOKEN       = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]

# ── 클라이언트 초기화 ─────────────────────────────────────────

notion           = Client(auth=NOTION_TOKEN)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

KST = timezone(timedelta(hours=9))

# ─────────────────────────────────────────────────────────────
# Claude 프롬프트 정의
# ─────────────────────────────────────────────────────────────

# 【기존】 #업무 / 태그 없음 메모 분석 프롬프트
ANALYZE_SYSTEM_PROMPT = """
당신은 CRM 마케터 지혜의 개인 비서입니다.
사용자가 보내는 자연어 메모를 분석해 아래 JSON 형식으로만 응답하세요.
절대 JSON 외 다른 텍스트를 포함하지 마세요.

-----

【title】 메모 핵심 한 줄 요약
- 메모의 핵심 주제를 15자 이내로 압축
- 원문을 그대로 쓰지 말 것. 반드시 의미를 추출해서 새로 쓸 것
- 예: "내일까지 보고서 써야 함" → "캠페인 보고서 마감"

【category】 분류
- "업무": LG유플러스, CRM, 캠페인, 앱푸시, MMS, 데이터분석, KPI, MAU 등
- "개인": 일상, 감정, 건강, 가족, 남편, 고양이 바다, 여행, 취미 등
- "아이디어": 새 기획, 인사이트, marketerlog, 인스타, 자동화, 부업, 툴 개발 등
- 복합적이면 핵심 의도 기준으로 판단

【target_date】 목표일정
- 메모에서 날짜 힌트 추출 후 오늘 날짜 기준으로 YYYY-MM-DD 변환
- 변환 불가능한 힌트면 텍스트 그대로 (예: "다음 달 초")
- 없으면 null

【content】 내용 정제
- 원문의 의미를 유지하되 자연스러운 문어체로 다듬기
- 구어체/줄임말/감탄사 제거, 문장 완성도 높이기
- 날짜/기한 표현은 포함하지 말 것 (목표일정 컬럼에 별도 저장됨)

【todos】 다음 액션 제안
- 메모 내용을 그대로 반복하지 말 것
- 메모를 읽고 "그다음에 해야 할 일"을 최대 2개만 제안
- 메모에 없는 새로운 관점의 액션이어야 함
- 짧고 구체적으로, 실행 가능한 동사로 시작할 것
- 없으면 빈 배열 []

-----

응답 형식 (JSON만, 다른 텍스트 없이):
{
  "title": "핵심 한 줄 요약",
  "category": "업무|개인|아이디어",
  "target_date": "YYYY-MM-DD 또는 텍스트 또는 null",
  "content": "정제된 내용",
  "todos": ["액션1", "액션2"]
}
"""

# 【신규】 #일상 메모 정리 프롬프트
DAILY_SYSTEM_PROMPT = """
당신은 CRM 마케터 지혜의 개인 비서입니다.
사용자가 보내는 #일상 메모를 간단히 정리해 아래 JSON 형식으로만 응답하세요.
절대 JSON 외 다른 텍스트를 포함하지 마세요.

【title】 15자 이내 핵심 요약
【content】 자연스럽게 다듬은 내용 (구어체 제거, 간결하게)
【todos】 오늘 해야 할 일 목록 추출 (명시된 것만, 없으면 빈 배열)

응답 형식:
{
  "title": "요약",
  "content": "정제된 내용",
  "todos": ["할일1", "할일2"]
}
"""

# 【신규】 #컬쳐 메모 정리 프롬프트
CULTURE_SYSTEM_PROMPT = """
당신은 CRM 마케터 지혜의 개인 비서입니다.
사용자가 보내는 #컬쳐 메모(책/영화/전시 등 문화 감상)를 정리해 아래 JSON 형식으로만 응답하세요.
절대 JSON 외 다른 텍스트를 포함하지 마세요.

【title】 작품명 또는 핵심 키워드 15자 이내
【content】 감상을 한 문장으로 정제 (구어체 → 문어체, 핵심 감정/인사이트 살리기)
  예: "오펜하이머 봤는데 천재도 결국 시스템 안에 갇힌다는 게 씁쓸했음"
   → "천재성도 시스템의 논리를 벗어날 수 없다는 씁쓸함 — 오펜하이머"

응답 형식:
{
  "title": "작품/키워드",
  "content": "정제된 감상"
}
"""

# ─────────────────────────────────────────────────────────────
# 태그 감지 유틸
# ─────────────────────────────────────────────────────────────

def detect_tag(text: str) -> str:
    """메시지에서 태그 감지: #업무 / #일상 / #컬쳐 / 없음"""
    stripped = text.strip()
    if stripped.startswith("#업무"):
        return "업무"
    elif stripped.startswith("#일상"):
        return "일상"
    elif stripped.startswith("#컬쳐"):
        return "컬쳐"
    return "없음"

def remove_tag(text: str) -> str:
    """태그 제거 후 본문만 반환"""
    for tag in ["#업무", "#일상", "#컬쳐"]:
        if text.strip().startswith(tag):
            return text.strip()[len(tag):].strip()
    return text.strip()

# ─────────────────────────────────────────────────────────────
# Claude 분석 함수들
# ─────────────────────────────────────────────────────────────

def analyze_memo(text: str) -> dict:
    """#업무 / 태그없음: Claude로 메모 분석"""
    try:
        today = datetime.now(KST).strftime("%Y-%m-%d")
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=ANALYZE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"[오늘 날짜: {today}]\n\n{text}"}],
        )
        raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return {
            "title":       result.get("title", text[:30]),
            "category":    result.get("category", "업무"),
            "target_date": result.get("target_date"),
            "content":     result.get("content", text),
            "todos":       result.get("todos", []),
        }
    except Exception as e:
        logger.error(f"Claude 분석 오류: {e}")
        return {"title": text[:30], "category": "업무", "target_date": None, "content": text, "todos": []}

def analyze_daily(text: str) -> dict:
    """#일상: 간단 정리"""
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            system=DAILY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return {
            "title":   result.get("title", text[:30]),
            "content": result.get("content", text),
            "todos":   result.get("todos", []),
        }
    except Exception as e:
        logger.error(f"Claude 일상 분석 오류: {e}")
        return {"title": text[:30], "content": text, "todos": []}

def analyze_culture(text: str) -> dict:
    """#컬쳐: 감상 정제"""
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            system=CULTURE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return {
            "title":   result.get("title", text[:30]),
            "content": result.get("content", text),
        }
    except Exception as e:
        logger.error(f"Claude 컬쳐 분석 오류: {e}")
        return {"title": text[:30], "content": text}

# ─────────────────────────────────────────────────────────────
# 노션 저장 함수들
# ─────────────────────────────────────────────────────────────

def save_to_notion(text: str, analysis: dict) -> bool:
    """기존: #업무 / 태그없음 저장"""
    try:
        now_kst     = datetime.now(KST)
        date_str    = now_kst.strftime("%Y-%m-%d")
        category    = analysis["category"]
        target_date = analysis["target_date"]
        todos       = analysis["todos"]
        title       = analysis.get("title", text[:30])
        content     = analysis.get("content", text)
        todos_text  = "\n".join(f"• {t}" for t in todos) if todos else ""

        target_date_prop = None
        if target_date:
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
                target_date_prop = {"date": {"start": target_date}}
            except ValueError:
                target_date_prop = None

        properties = {
            "구분":    {"title": [{"text": {"content": title}}]},
            "날짜":    {"date": {"start": date_str}},
            "카테고리": {"select": {"name": category}},
            "내용":    {"rich_text": [{"text": {"content": content}}]},
        }
        if target_date_prop:
            properties["목표일정"] = target_date_prop
        elif target_date:
            properties["목표일정_메모"] = {"rich_text": [{"text": {"content": target_date}}]}
        if todos_text:
            properties["To-do 제안"] = {"rich_text": [{"text": {"content": todos_text}}]}

        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=properties,
        )
        return True
    except Exception as e:
        logger.error(f"노션 저장 오류: {e}")
        return False

def save_daily_to_notion(text: str, analysis: dict) -> bool:
    """신규: #일상 저장"""
    try:
        now_kst    = datetime.now(KST)
        date_str   = now_kst.strftime("%Y-%m-%d")
        title      = analysis.get("title", text[:30])
        content    = analysis.get("content", text)
        todos      = analysis.get("todos", [])
        todos_text = "\n".join(f"• {t}" for t in todos) if todos else ""

        properties = {
            "구분":    {"title": [{"text": {"content": title}}]},
            "날짜":    {"date": {"start": date_str}},
            "카테고리": {"select": {"name": "일상"}},
            "내용":    {"rich_text": [{"text": {"content": content}}]},
        }
        if todos_text:
            properties["To-do 제안"] = {"rich_text": [{"text": {"content": todos_text}}]}

        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=properties,
        )
        return True
    except Exception as e:
        logger.error(f"노션 일상 저장 오류: {e}")
        return False

def save_culture_to_notion(text: str, analysis: dict) -> bool:
    """신규: #컬쳐 저장"""
    try:
        now_kst  = datetime.now(KST)
        date_str = now_kst.strftime("%Y-%m-%d")
        title    = analysis.get("title", text[:30])
        content  = analysis.get("content", text)

        properties = {
            "구분":    {"title": [{"text": {"content": title}}]},
            "날짜":    {"date": {"start": date_str}},
            "카테고리": {"select": {"name": "컬쳐"}},
            "내용":    {"rich_text": [{"text": {"content": content}}]},
        }

        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=properties,
        )
        return True
    except Exception as e:
        logger.error(f"노션 컬쳐 저장 오류: {e}")
        return False

# ─────────────────────────────────────────────────────────────
# 텔레그램 핸들러
# ─────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 비서봇 가동 중!\n\n"
        "태그를 붙여서 메모를 보내세요:\n"
        "• #업무 → 업무 메모 (Claude 분석 + 노션)\n"
        "• #일상 → 오늘 할 일 / 일상 메모 (노션, 17:30 알림)\n"
        "• #컬쳐 → 책/영화/전시 감상 (Claude 정제 + 노션)\n"
        "• 태그 없음 → 기존 방식으로 분류\n\n"
        "⏰ 자동 알림\n"
        "• 07:30 아침 브리핑\n"
        "• 16:30 업무일지 작성 알림\n"
        "• 17:30 오늘 일상 to-do 알림"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """태그별 분기 처리"""
    text = update.message.text.strip()
    if not text:
        return

    tag     = detect_tag(text)
    content = remove_tag(text)

    processing_msg = await update.message.reply_text("🔍 저장 중...")

    # ── #업무 ──
    if tag == "업무":
        analysis = analyze_memo(content)
        saved    = save_to_notion(content, analysis)
        todos    = analysis.get("todos", [])

        lines = ["💼 *업무* 메모 저장했어요!"]
        if analysis.get("target_date"):
            lines.append(f"📅 목표일정: {analysis['target_date']}")
        if todos:
            lines.append("✅ To-do 제안:")
            for t in todos:
                lines.append(f"  • {t}")
        if not saved:
            lines.append("⚠️ 노션 저장 실패")
        await processing_msg.edit_text("\n".join(lines), parse_mode="Markdown")

    # ── #일상 ──
    elif tag == "일상":
        analysis = analyze_daily(content)
        saved    = save_daily_to_notion(content, analysis)
        todos    = analysis.get("todos", [])

        lines = ["🌿 *일상* 메모 저장했어요!"]
        if todos:
            lines.append("📋 오늘 할 일:")
            for t in todos:
                lines.append(f"  • {t}")
        if not saved:
            lines.append("⚠️ 노션 저장 실패")
        await processing_msg.edit_text("\n".join(lines), parse_mode="Markdown")

    # ── #컬쳐 ──
    elif tag == "컬쳐":
        analysis = analyze_culture(content)
        saved    = save_culture_to_notion(content, analysis)

        lines = [
            "🎬 *컬쳐* 기록 저장했어요!",
            f"📝 {analysis.get('content', content)}",
        ]
        if not saved:
            lines.append("⚠️ 노션 저장 실패")
        await processing_msg.edit_text("\n".join(lines), parse_mode="Markdown")

    # ── 태그 없음 (기존 방식) ──
    else:
        analysis = analyze_memo(text)
        saved    = save_to_notion(text, analysis)
        category = analysis["category"]
        todos    = analysis.get("todos", [])

        emoji_map = {"업무": "💼", "개인": "🌿", "아이디어": "💡"}
        emoji     = emoji_map.get(category, "📝")

        lines = [f"{emoji} *{category}* 으로 저장했어요!"]
        if analysis.get("target_date"):
            lines.append(f"📅 목표일정: {analysis['target_date']}")
        if todos:
            lines.append("✅ To-do 제안:")
            for t in todos:
                lines.append(f"  • {t}")
        if not saved:
            lines.append("⚠️ 노션 저장 실패")
        await processing_msg.edit_text("\n".join(lines), parse_mode="Markdown")

# ─────────────────────────────────────────────────────────────
# 스케줄 알림 함수들
# ─────────────────────────────────────────────────────────────

async def send_morning_briefing(application: Application):
    """07:30 KST — 아침 브리핑 (기존 유지)"""
    try:
        now_kst  = datetime.now(KST)
        today    = now_kst.strftime("%Y-%m-%d")
        tomorrow = (now_kst + timedelta(days=1)).strftime("%Y-%m-%d")

        # 마감 임박 항목
        deadline_pages = []
        for target in [today, tomorrow]:
            res = notion.databases.query(
                database_id=NOTION_DATABASE_ID,
                filter={"property": "목표일정", "date": {"equals": target}}
            )
            for page in res.get("results", []):
                props = page["properties"]
                title = props.get("구분", {}).get("title", [])
                title = title[0]["text"]["content"] if title else "(내용 없음)"
                deadline_pages.append((target, title))

        # 오늘 저장된 메모
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"property": "날짜", "date": {"equals": today}}
        )
        pages = response.get("results", [])

        lines = [f"☀️ {today} 아침 브리핑\n"]

        if deadline_pages:
            lines.append("🚨 마감 임박")
            for target, title in deadline_pages:
                tag = "오늘" if target == today else "내일"
                lines.append(f"  • [{tag}] {title}")
            lines.append("")

        if not pages:
            lines.append("📋 오늘 저장된 메모가 없어요.")
        else:
            by_cat = {"업무": [], "개인": [], "아이디어": [], "일상": [], "컬쳐": []}
            for page in pages:
                props = page["properties"]
                cat   = props.get("카테고리", {}).get("select", {})
                cat   = cat.get("name", "기타") if cat else "기타"
                title = props.get("구분", {}).get("title", [])
                title = title[0]["text"]["content"] if title else "(내용 없음)"
                by_cat.setdefault(cat, []).append(title)

            emoji_map = {"업무": "💼", "개인": "🌿", "아이디어": "💡", "일상": "🗓️", "컬쳐": "🎬"}
            for cat, items in by_cat.items():
                if items:
                    lines.append(f"{emoji_map.get(cat, '📝')} {cat} ({len(items)}건)")
                    for item in items:
                        lines.append(f"  • {item[:60]}")

        await application.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="\n".join(lines),
        )
    except Exception as e:
        logger.error(f"아침 브리핑 오류: {e}")


async def send_work_log_reminder(application: Application):
    """16:30 KST — 업무일지 작성 알림"""
    try:
        msg = (
            "📝 *업무일지 작성 시간이에요!*\n\n"
            "오늘 한 일을 간단히 정리하고 퇴근 준비 시작해요 🙂\n"
            "마무리 못한 업무가 있다면 내일 to-do로 #업무 태그로 남겨두세요!"
        )
        await application.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=msg,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"업무일지 알림 오류: {e}")


async def send_evening_todo(application: Application):
    """17:30 KST — 오늘 #일상 to-do 알림"""
    try:
        now_kst = datetime.now(KST)
        today   = now_kst.strftime("%Y-%m-%d")

        # 오늘 저장된 #일상 메모 조회
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={
                "and": [
                    {"property": "날짜",    "date":   {"equals": today}},
                    {"property": "카테고리", "select": {"equals": "일상"}},
                ]
            }
        )
        pages = response.get("results", [])

        lines = ["🌙 *퇴근 후 할 일*\n"]

        if not pages:
            lines.append("오늘 등록된 일상 to-do가 없어요.\n편하게 쉬어도 돼요 😊")
        else:
            for page in pages:
                props     = page["properties"]
                todos_raw = props.get("To-do 제안", {}).get("rich_text", [])
                todos_str = todos_raw[0]["text"]["content"] if todos_raw else ""

                if todos_str:
                    lines.append(todos_str)
                else:
                    title = props.get("구분", {}).get("title", [])
                    title = title[0]["text"]["content"] if title else "(내용 없음)"
                    lines.append(f"• {title}")

        await application.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="\n".join(lines),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"저녁 to-do 알림 오류: {e}")

# ─────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────

async def post_init(application: Application):
    """봇 시작 후 스케줄러 등록"""
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

    # 07:30 — 아침 브리핑 (기존)
    scheduler.add_job(
        send_morning_briefing,
        trigger="cron", hour=7, minute=30,
        args=[application],
    )
    # 16:30 — 업무일지 작성 알림 (신규)
    scheduler.add_job(
        send_work_log_reminder,
        trigger="cron", hour=16, minute=30,
        args=[application],
    )
    # 17:30 — 퇴근 후 일상 to-do 알림 (신규)
    scheduler.add_job(
        send_evening_todo,
        trigger="cron", hour=17, minute=30,
        args=[application],
    )

    scheduler.start()
    logger.info("⏰ 스케줄러 시작 완료 (07:30 / 16:30 / 17:30)")


def main():
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 비서봇 시작!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
