"""Lightweight timing/metrics helpers used by the Streamlit demo dashboard."""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class StageTiming:
    stage: str
    duration_ms: float


@dataclass
class PipelineMetrics:
    pipeline_name: str
    stages: list[StageTiming] = field(default_factory=list)

    @property
    def total_ms(self) -> float:
        return sum(s.duration_ms for s in self.stages)


@contextmanager
def timed_stage(metrics: PipelineMetrics, stage_name: str):
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1000
    metrics.stages.append(StageTiming(stage=stage_name, duration_ms=elapsed_ms))
