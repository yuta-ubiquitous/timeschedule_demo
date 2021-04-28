from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class Schedule(BaseModel):
    """名前と時間を含んだスケジュール"""

    id: Optional[int]
    name: str
    datetime_start: datetime
    datetime_end: datetime
    createdAt: Optional[datetime]

    def createdAtToLocal(self) -> Optional[datetime]:
        """DBに保存されているUTCの時間をJSTに変換する"""
        if self.createdAt is None:
            return None
        else:
            return self.createdAt.replace(tzinfo=timezone.utc).astimezone()
