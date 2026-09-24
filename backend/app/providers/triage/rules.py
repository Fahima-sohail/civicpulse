from app.providers.triage.base import TriageResult
from app.schemas import Category, Priority

class RuleBasedTriage:
    name = "rules"
    keywords = {
        Category.water: ("water", "pipe", "sewer", "flood", "leak", "tap", "drain"),
        Category.electricity: ("electric", "electricity", "transformer", "power", "wire", "voltage"),
        Category.sanitation: ("garbage", "trash", "waste", "kooda", "sweep", "smell", "clean"),
        Category.roads: ("road", "pothole", "footpath", "asphalt", "street broken", "rasta"),
        Category.streetlights: ("streetlight", "street light", "lamp", "dark road", "light pole"),
    }
    high_words = ("burst", "flood", "fire", "danger", "shock", "sparking", "accident", "urgent", "emergency")
    low_words = ("minor", "when possible", "small", "request")

    def triage(self, text: str, location: str) -> TriageResult:
        lower = text.lower()
        category = max(self.keywords, key=lambda item: sum(word in lower for word in self.keywords[item]), default=Category.other)
        if not any(word in lower for word in self.keywords[category]): category = Category.other
        priority = Priority.high if any(word in lower for word in self.high_words) else Priority.low if any(word in lower for word in self.low_words) else Priority.normal
        summary = " ".join(text.strip().split())[:140]
        return TriageResult(category=category, priority=priority, summary=summary, confidence=0.72)
