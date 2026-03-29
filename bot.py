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
async def post_init(application: Application):
    """봇 시작 후 스케줄러 실행 (event loop 안에서)"""
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        send_morning_briefing,
        trigger="cron",
        hour=7,
        minute=30,
        args=[application],
    )
    scheduler.start()
    logger.info("⏰ 스케줄러 시작 완료")


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
