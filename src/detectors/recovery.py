"""
Recovery detector: analyses fault events, scores system resilience.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from src.injectors.faults import FaultEvent, FaultType


@dataclass
class ResilienceScore:
    fault_type: FaultType
    total_injected: int
    recovered: int
    unrecovered: int
    recovery_rate_pct: float
    mean_recovery_ms: Optional[float]
    max_recovery_ms: Optional[float]
    grade: str  # A/B/C/D/F

    @classmethod
    def from_events(cls, fault_type: FaultType, events: list[FaultEvent]) -> "ResilienceScore":
        recovered = [e for e in events if e.recovered]
        unrecovered = [e for e in events if not e.recovered]
        rate = len(recovered) / len(events) * 100 if events else 0

        rtimes = [e.recovery_time_ms for e in recovered if e.recovery_time_ms is not None]
        mean_rt = sum(rtimes) / len(rtimes) if rtimes else None
        max_rt = max(rtimes) if rtimes else None

        if rate >= 95:   grade = "A"
        elif rate >= 80: grade = "B"
        elif rate >= 60: grade = "C"
        elif rate >= 40: grade = "D"
        else:            grade = "F"

        return cls(
            fault_type=fault_type,
            total_injected=len(events),
            recovered=len(recovered),
            unrecovered=len(unrecovered),
            recovery_rate_pct=rate,
            mean_recovery_ms=mean_rt,
            max_recovery_ms=max_rt,
            grade=grade,
        )


@dataclass
class ChaosReport:
    scenario_name: str
    events: list[FaultEvent] = field(default_factory=list)
    scores: list[ResilienceScore] = field(default_factory=list)

    @property
    def overall_recovery_rate(self) -> float:
        if not self.events:
            return 0.0
        return sum(1 for e in self.events if e.recovered) / len(self.events) * 100

    @property
    def overall_grade(self) -> str:
        r = self.overall_recovery_rate
        if r >= 95:   return "A"
        elif r >= 80: return "B"
        elif r >= 60: return "C"
        elif r >= 40: return "D"
        else:         return "F"

    def compute_scores(self):
        from collections import defaultdict
        by_type: dict[FaultType, list[FaultEvent]] = defaultdict(list)
        for e in self.events:
            by_type[e.fault_type].append(e)
        self.scores = [
            ResilienceScore.from_events(ft, evts)
            for ft, evts in by_type.items()
        ]
