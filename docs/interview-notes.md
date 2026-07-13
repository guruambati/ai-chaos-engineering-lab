# Interview Notes — AI Chaos Engineering Lab

## What this project demonstrates
Systematic fault injection and resilience measurement — a discipline borrowed from distributed systems engineering (Netflix Chaos Monkey) and applied to AI stacks.

## Key talking points

### "What is chaos engineering for AI?"
"Traditional chaos engineering kills servers or drops network packets. AI systems have an additional failure surface: the model itself can degrade gracefully in non-obvious ways — timeouts, context overflow, malformed inputs, tool failures. This framework injects those AI-specific faults and measures whether the system detects and recovers."

### On the simulation vs real injection distinction
"The injectors simulate error *conditions* — raising exceptions, triggering timeouts, constructing malformed strings — which is what you'd do in unit and integration testing. For production chaos testing you'd use a proxy like Toxiproxy to inject at the HTTP layer. I've included the upgrade path in the README. The recovery detection and resilience scoring logic is real and works identically either way."

### On grading A–F
"The grade is based on recovery rate, not just whether tests pass. A system that recovers 95%+ of the time gets an A. This gives you a quantified resilience posture rather than a binary pass/fail."

## Questions they might ask

**Q: How does this differ from just writing try/except?**
try/except handles known errors. Chaos engineering finds the unknown unknowns — what happens when 3 things fail simultaneously? What if the tool fails *after* partial state has been written? This framework makes those scenarios repeatable and measurable.

**Q: How would you do this in production?**
Deploy Toxiproxy as a sidecar. Write chaos scenarios that call the Toxiproxy API to inject latency, reset connections, or introduce packet loss. Run scenarios during off-peak hours, measure system dashboards (not just this framework's output).

**Q: What's the most interesting fault type here?**
Malformed prompts — specifically prompt injection. Testing whether the system blocks `Ignore all previous instructions` is a real security concern for any production agent.

## Technical depth

**Q: How would you test recovery of multi-agent systems specifically?**
Inject a fault at agent handoff points — where agent A passes context to agent B. Does agent B get partial context? Does it retry? Does it fail open or closed? The workflow evaluator in P5 is designed for exactly this.
