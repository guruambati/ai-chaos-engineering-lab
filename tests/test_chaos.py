import asyncio, sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.injectors.faults import FaultConfig, FaultType, inject_fault
from src.detectors.recovery import ChaosReport, ResilienceScore

@pytest.mark.asyncio
async def test_model_crash_recovers():
    cfg = FaultConfig(FaultType.MODEL_CRASH, recovery_ms=100)
    event = await inject_fault(cfg)
    assert event is not None
    assert event.injected
    assert event.recovered
    assert event.recovery_time_ms is not None

@pytest.mark.asyncio
async def test_timeout_detected():
    cfg = FaultConfig(FaultType.TIMEOUT, timeout_ms=200)
    event = await inject_fault(cfg)
    assert event is not None
    assert "timed out" in event.error_message.lower()

@pytest.mark.asyncio
async def test_tool_failure():
    cfg = FaultConfig(FaultType.TOOL_FAILURE)
    event = await inject_fault(cfg)
    assert event is not None
    assert event.fault_type == FaultType.TOOL_FAILURE

@pytest.mark.asyncio
async def test_malformed_prompt():
    cfg = FaultConfig(FaultType.MALFORMED_PROMPT)
    event = await inject_fault(cfg)
    assert event is not None
    assert "prompt_len" in event.metadata

@pytest.mark.asyncio
async def test_rate_limit():
    cfg = FaultConfig(FaultType.RATE_LIMIT)
    event = await inject_fault(cfg)
    assert event is not None
    assert "429" in event.error_message

@pytest.mark.asyncio
async def test_probability_zero_skips():
    cfg = FaultConfig(FaultType.MODEL_CRASH, probability=0.0)
    event = await inject_fault(cfg)
    assert event is None

def test_resilience_score():
    from src.injectors.faults import FaultEvent
    events = [
        FaultEvent(FaultType.MODEL_CRASH, "t", True, True, 500.0, None),
        FaultEvent(FaultType.MODEL_CRASH, "t", True, True, 400.0, None),
        FaultEvent(FaultType.MODEL_CRASH, "t", True, False, None, "unrecovered"),
    ]
    score = ResilienceScore.from_events(FaultType.MODEL_CRASH, events)
    assert score.recovery_rate_pct == pytest.approx(66.67, abs=1)
    assert score.mean_recovery_ms == pytest.approx(450.0)
    assert score.grade == "C"

def test_chaos_report():
    from src.injectors.faults import FaultEvent
    report = ChaosReport("test")
    report.events = [
        FaultEvent(FaultType.TIMEOUT, "t", True, True, 200.0, None),
        FaultEvent(FaultType.TIMEOUT, "t", True, True, 300.0, None),
    ]
    report.compute_scores()
    assert report.overall_recovery_rate == 100.0
    assert report.overall_grade == "A"
    assert len(report.scores) == 1
