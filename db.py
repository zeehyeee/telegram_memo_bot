import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

import pytz

KST = pytz.timezone("Asia/Seoul")


class Database:
    def __init__(self, db_path: str = "memos.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memos (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id    INTEGER NOT NULL,
                    text       TEXT    NOT NULL,
                    category   TEXT    NOT NULL,
                    created_at TEXT    NOT NULL,
                    date_kst   TEXT    NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON memos (chat_id, date_kst)")

    def save_memo(self, chat_id: int, text: str, category: str):
        now = datetime.now(KST)
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO memos (chat_id, text, category, created_at, date_kst) VALUES (?,?,?,?,?)",
                (chat_id, text, category, now.isoformat(), now.date().isoformat()),
            )

    def _rows_to_list(self, rows) -> list[dict]:
        result = []
        for row in rows:
            d = dict(row)
            d["created_at"] = datetime.fromisoformat(d["created_at"])
            result.append(d)
        return result

    def get_memos_by_date(self, chat_id: int, date_str: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM memos WHERE chat_id=? AND date_kst=? ORDER BY created_at",
                (chat_id, date_str),
            ).fetchall()
        return self._rows_to_list(rows)

    def get_today_memos(self, chat_id: int) -> list[dict]:
        today = datetime.now(KST).date().isoformat()
        return self.get_memos_by_date(chat_id, today)

    def get_yesterday_memos(self, chat_id: int) -> list[dict]:
        yesterday = (datetime.now(KST) - timedelta(days=1)).date().isoformat()
        return self.get_memos_by_date(chat_id, yesterday)

    def get_yesterday_memos_all(self) -> list[dict]:
        """모든 사용자의 어제 메모 (자동 발송용)."""
        yesterday = (datetime.now(KST) - timedelta(days=1)).date().isoformat()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM memos WHERE date_kst=? ORDER BY chat_id, created_at",
                (yesterday,),
            ).fetchall()
        return self._rows_to_list(rows)

    def get_all_memos(self, chat_id: int) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM memos WHERE chat_id=? ORDER BY created_at DESC LIMIT 50",
                (chat_id,),
            ).fetchall()
        return self._rows_to_list(rows)

    def delete_memo(self, memo_id: int, chat_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "DELETE FROM memos WHERE id=? AND chat_id=?", (memo_id, chat_id)
            )
        return cur.rowcount > 0
