from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CalendarEvent:
    summary: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None