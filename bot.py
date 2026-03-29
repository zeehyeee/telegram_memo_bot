import asyncio
import logging
import os
from collections import defaultdict
from datetime import datetime, time, timedelta

import pytz
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from db import Database

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
KST = pytz.timezone("Asia/Seoul")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

db = Database()

# ── 요약 텍스트 빌더 ──────────────────────────────────────────────────────────

def build_summary(memos: list[dict], title: str) -> str:
    text = f"📊 *{title}*\n총 {len(memos)}개의 메모\n\n"
    for m in memos:
        text += f"  • {m['text']}\n"
    return text.strip()


# ── 핸들러 ────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "안녕하세요! 메모 봇입니다 🗒️\n\n"
        "메시지를 보내면 업무/개인/아이디어로 자동 분류하여 저장합니다.\n\n"
        "📌 *명령어*\n"
        "/today — 오늘 메모 보기\n"
        "/yesterday — 어제 메모 보기\n"
        "/all — 최근 메모 50개\n"
        "/summary — 어제 메모 요약 받기\n"
        "/delete `<id>` — 메모 삭제\n"
        "/myid — 내 채팅 ID 확인",
        parse_mode="Markdown",
    )


async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"채팅 ID: `{update.effective_chat.id}`", parse_mode="Markdown"
    )


async def handle_memo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    db.save_memo(update.effective_chat.id, text, "미분류")
    await update.message.reply_text("📝 메모 저장 완료!")


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memos = db.get_today_memos(update.effective_chat.id)
    if not memos:
        await update.message.reply_text("오늘 저장된 메모가 없습니다.")
        return
    date_str = datetime.now(KST).strftime("%Y년 %m월 %d일")
    await update.message.reply_text(
        build_summary(memos, f"{date_str} 오늘 메모"), parse_mode="Markdown"
    )


async def cmd_yesterday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memos = db.get_yesterday_memos(update.effective_chat.id)
    if not memos:
        await update.message.reply_text("어제 저장된 메모가 없습니다.")
        return
    date_str = (datetime.now(KST) - timedelta(days=1)).strftime("%Y년 %m월 %d일")
    await update.message.reply_text(
        build_summary(memos, f"{date_str} 어제 메모"), parse_mode="Markdown"
    )


async def cmd_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memos = db.get_all_memos(update.effective_chat.id)
    if not memos:
        await update.message.reply_text("저장된 메모가 없습니다.")
        return
    lines = []
    for m in memos:
        ts = m["created_at"].strftime("%m/%d %H:%M")
        lines.append(f"`[{m['id']}]` {ts}  {m['text']}")
    await update.message.reply_text(
        "📋 *최근 메모 (최대 50개)*\n\n" + "\n".join(lines),
        parse_mode="Markdown",
    )


async def cmd_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memos = db.get_yesterday_memos(update.effective_chat.id)
    if not memos:
        await update.message.reply_text("어제 저장된 메모가 없습니다.")
        return
    date_str = (datetime.now(KST) - timedelta(days=1)).strftime("%Y년 %m월 %d일")
    await update.message.reply_text(
        build_summary(memos, f"{date_str} 메모 요약"), parse_mode="Markdown"
    )


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("사용법: /delete `<id>`\n/all 에서 ID를 확인하세요.", parse_mode="Markdown")
        return
    try:
        memo_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID는 숫자여야 합니다.")
        return
    if db.delete_memo(memo_id, update.effective_chat.id):
        await update.message.reply_text(f"메모 #{memo_id} 삭제 완료.")
    else:
        await update.message.reply_text(f"메모 #{memo_id}를 찾을 수 없습니다.")


# ── 스케줄 작업 ───────────────────────────────────────────────────────────────

async def scheduled_daily_summary(context: ContextTypes.DEFAULT_TYPE):
    """매일 KST 07:30에 전날 메모 요약 발송."""
    all_memos = db.get_yesterday_memos_all()
    if not all_memos:
        log.info("어제 메모 없음, 요약 발송 생략.")
        return

    by_chat: dict[int, list] = defaultdict(list)
    for memo in all_memos:
        by_chat[memo["chat_id"]].append(memo)

    date_str = (datetime.now(KST) - timedelta(days=1)).strftime("%Y년 %m월 %d일")
    for chat_id, memos in by_chat.items():
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=build_summary(memos, f"{date_str} 메모 요약"),
                parse_mode="Markdown",
            )
            log.info("요약 발송 완료: chat_id=%s (%d개)", chat_id, len(memos))
        except Exception as e:
            log.error("요약 발송 실패 chat_id=%s: %s", chat_id, e)


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        raise ValueError(".env 파일에 BOT_TOKEN을 설정해주세요.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("yesterday", cmd_yesterday))
    app.add_handler(CommandHandler("all", cmd_all))
    app.add_handler(CommandHandler("summary", cmd_summary))
    app.add_handler(CommandHandler("delete", cmd_delete))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_memo))

    # 매일 KST 07:30 요약 발송
    app.job_queue.run_daily(
        scheduled_daily_summary,
        time=time(hour=7, minute=30, tzinfo=KST),
        name="daily_summary",
    )

    log.info("봇 시작!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
