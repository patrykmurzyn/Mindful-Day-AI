from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Task:
    id: str
    title: str
    notes: Optional[str]
    due: Optional[datetime]
    status: str