import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from backend.config import BASE_DIR, settings
from backend.models.schemas import HistoryItem


class HistoryService:
    def __init__(self) -> None:
        self.path = BASE_DIR / "history.json"

    def _read(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _write(self, items: List[Dict[str, Any]]) -> None:
        self.path.write_text(
            json.dumps(items[: settings.history_limit], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, item_type: str, title: str, payload: Dict[str, Any]) -> HistoryItem:
        item = {
            "id": str(uuid4()),
            "type": item_type,
            "title": title[:140],
            "created_at": datetime.utcnow().isoformat(),
            "payload": payload,
        }
        items = [item, *self._read()]
        self._write(items)
        return HistoryItem(**item)

    def list(self) -> List[HistoryItem]:
        return [HistoryItem(**item) for item in self._read()]

    def clear(self) -> None:
        self._write([])


history_service = HistoryService()
