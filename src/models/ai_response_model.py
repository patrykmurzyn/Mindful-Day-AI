from dataclasses import dataclass
from typing import List, Dict

@dataclass
class BreakRecommendation:
    time: str
    duration: str
    activity: str

@dataclass
class Plan:
    hours: Dict[str, str]

@dataclass
class AIResponse:
    summary: str
    today_fact: str
    plan: Plan
    break_recommendations: List[BreakRecommendation]
