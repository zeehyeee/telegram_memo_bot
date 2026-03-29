import logging
import os
from datetime import datetime

import pytz
from notion_client import Client

log = logging.getLogger(__name__)
KST = pytz.timezone("Asia/Seoul")


class NotionMemo:
    def __init__(self):
        token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        if token and self.database_id:
            self.client = Client(auth=token)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            log.warning("NOTION_TOKEN 또는 NOTION_DATABASE_ID 미설정 — 노션 저장 비활성화")

    def save(self, text: str, category: str = "미분류") -> bool:
        if not self.enabled:
            return False
        try:
            date_str = datetime.now(KST).date().isoformat()
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "구분": {
                        "title": [{"text": {"content": text}}]
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
                },
            )
            return True
        except Exception as e:
            log.error("노션 저장 실패: %s", e)
            return False
