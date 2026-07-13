# 💥 AI Chaos Engineering

Fault injection framework for AI systems. Programmatically injects failures, measures recovery, and grades system resilience A–F across 8 fault categories.

![Python](https://img.shields.io/badge/Python-3.10%2B-yellow) ![pytest](https://img.shields.io/badge/8%20tests-passing-green)

---

## How Fault Injection Works

Each fault type is a real `async` function that raises exceptions, triggers `asyncio.TimeoutError`, or introduces `asyncio.sleep` delays — the same mechanisms a real failure would trigger in production code. The framework then measures whether the calling system detects and recovers from that condition.

| Fault | What's Injected | Real or Simulated |
|-------|-----------------|-------------------|
| `model_crash` | `RuntimeError("SIGKILL")` raised mid-call | Simulated exception |
| `timeout` | `asyncio.wait_for(hang, timeout=N)` → `TimeoutError` | Real async timeout |
| `tool_failure` | Connection refused / 503 error strings | Simulated error messages |
| `context_overflow` | Token count exceeds limit, truncation triggered | Simulated arithmetic |
| `malformed_prompt` | Null bytes, oversized strings, injection attempts | Real string construction |
| `vector_db_unavailable` | Backend connection error messages | Simulated error messages |
| `rate_limit` | HTTP 429 + Retry-After header | Simulated response |
| `network_flap` | Repeated `asyncio.sleep` interruptions | Simulated timing |

> The injectors simulate the **error conditions** that real faults produce. In a production setup you would point these at a real inference server and inject at the HTTP layer (e.g. via a proxy like Toxiproxy). The recovery detection logic and resilience scoring are real and would work identically against live systems.

---

## Quickstart

```bash
pip install -r requirements.txt

# Full suite: all 8 fault types × 3 repetitions
python chaos.py --scenario full --reps 3

# Targeted
python chaos.py --scenario crash    # model crash + timeout
python chaos.py --scenario network  # network flap + vector DB
python chaos.py --scenario prompts  # context overflow + malformed input
```

---

## Sample Output

```
⚡ CHAOS SCENARIO: AI System — full chaos
Faults: 8 types × 3 repetitions = 24 total injections

  💥 Injecting model_crash (3×)...
    [1/3] ✅ Recovered in 502ms — Model process terminated unexpectedly
    [2/3] ✅ Recovered in 498ms — Model process terminated unexpectedly
    [3/3] ✅ Recovered in 501ms — Model process terminated unexpectedly

  ⏱️ Injecting timeout (3×)...
    [1/3] ✅ Recovered in 1001ms — Request timed out after 1000ms
    ...

┌─────────────────────┬──────────┬───────────┬──────┬────────────────┬───────┐
│ Fault               │ Injected │ Recovered │ Rate │ Mean Recovery  │ Grade │
├─────────────────────┼──────────┼───────────┼──────┼────────────────┼───────┤
│ 💥 model_crash      │ 3        │ 3         │ 100% │ 500ms          │   A   │
│ ⏱️  timeout          │ 3        │ 3         │ 100% │ 1001ms         │   A   │
│ 🔧 tool_failure     │ 3        │ 3         │ 100% │ 100ms          │   A   │
└─────────────────────┴──────────┴───────────┴──────┴────────────────┴───────┘
Overall Recovery Rate: 96.4%  Grade: A
```

---

## Resilience Grades

| Grade | Recovery Rate | Meaning |
|-------|--------------|---------|
| **A** | ≥ 95% | Production-ready resilience |
| **B** | ≥ 80% | Minor gaps — acceptable with monitoring |
| **C** | ≥ 60% | Significant reliability risk |
| **D** | ≥ 40% | Unreliable — do not ship |
| **F** | < 40% | Critical failure |

---

## Production Extension

To inject at the HTTP layer against a real system, replace injector bodies with [Toxiproxy](https://github.com/shopify/toxiproxy) API calls:

```python
import httpx

async def inject_real_timeout(proxy_url: str, latency_ms: int):
    async with httpx.AsyncClient() as c:
        await c.post(f"{proxy_url}/proxies/llm/toxics", json={
            "type": "latency", "attributes": {"latency": latency_ms}
        })
```
