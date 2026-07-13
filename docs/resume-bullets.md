# Resume Bullets — AI Chaos Engineering Lab

## Senior level
- Designed AI chaos engineering framework injecting 8 fault categories (model crash, timeout, tool failure, context overflow, malformed prompt, vector DB outage, rate limiting, network flap) with quantified resilience scoring (A–F grade by recovery rate)
- Built async fault injection engine using asyncio timeouts and exception injection; recovery detector measures time-to-recovery per fault type across configurable repetitions

## Mid level
- Built Python chaos engineering framework for AI systems; injects model crashes, timeouts, tool failures, and adversarial prompts; grades system resilience A–F based on recovery rate across 8 fault categories
- Implemented resilience scoring system tracking per-fault-type recovery rates and mean recovery times; outputs structured JSON reports suitable for CI artifact ingestion

## Technical summary line
**AI Chaos Engineering:** Python · asyncio · Rich · pytest · fault injection · resilience scoring
