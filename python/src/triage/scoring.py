from __future__ import annotations
from typing import Dict, List, Tuple
from .models import SeverityLevel, SeverityScore

# Likert mapping 0-3
LIKERT = {
    "not_at_all": 0,
    "several_days": 1,
    "more_than_half": 2,
    "nearly_every_day": 3,
}

# Thresholds based on PHQ-4 guidance
# PHQ-4 total: 0-2 normal, 3-5 mild, 6-8 moderate, 9-12 severe
# GAD-2 total: 0-2 minimal, 3-4 mild, 5-6 moderate-severe (flag)

def categorize(phq4_total: int, gad2_total: int, crisis_indicators: List[str]) -> SeverityLevel:
    if crisis_indicators:
        return SeverityLevel.crisis
    if phq4_total >= 9 or gad2_total >= 5:
        return SeverityLevel.severe
    if phq4_total >= 6 or gad2_total >= 3:
        return SeverityLevel.moderate
    if phq4_total >= 3:
        return SeverityLevel.mild
    return SeverityLevel.minimal


def compute_score(answers: Dict[str, int], crisis_indicators: List[str] | None = None) -> SeverityScore:
    crisis_indicators = crisis_indicators or []
    phq4_items = ["anhedonia", "depressed", "nervous", "control_worry"]
    gad2_items = ["nervous", "control_worry"]

    phq4_total = sum(answers.get(k, 0) for k in phq4_items)
    gad2_total = sum(answers.get(k, 0) for k in gad2_items)

    level = categorize(phq4_total, gad2_total, crisis_indicators)
    return SeverityScore(phq4_total=phq4_total, gad2_total=gad2_total, crisis_indicators=crisis_indicators, level=level)
