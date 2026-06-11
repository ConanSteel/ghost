# Multi-model roster, explicit selection, parallel UI execution

**Date:** 2026-04-20
**Status:** Accepted
**Extends:** `03_decisions/2026-04-16-local-first-frontier-augmented.md`

## Context

Partway through the Phase 0 benchmark, the user proposed three extensions to the model architecture:

1. Multiple local models with per-task routing (not just local-vs-frontier).
2. A Perplexity-style automatic router that classifies prompts and dispatches.
3. Parallel model execution with UI affordances (e.g. a long reasoning call in one panel while the user continues prompting in another).

The original `local-first-frontier-augmented` ADR assumed a single local model as the workhorse with frontier-API escalation for hard reasoning. The user's proposal expands the local layer into a roster, rather than a single pick.

A companion observation: benchmark results already show meaningfully different profiles across the three candidate models (Qwen 2.5 7B, Llama 3.1 8B, DeepSeek-R1 7B). Forcing a single winner discards useful specialisation information.

## Decision

### 1. Multi-model local roster (accepted)

Ghost maintains a **roster** of local models, each assigned a role:

- **Workhorse** — primary model for routine interactive use. Fast, generalist-competent, low response-length variance. Default for everything unless explicitly overridden.
- **Reasoning specialist** — called for hard maths, long chain-of-thought analysis, strategy reasoning. Verbose and slower; worth the cost when quality justifies it.
- **(Future) Code specialist** — candidate slot for a code-tuned model (e.g. Qwen2.5-Coder, DeepSeek-Coder) in Phase 2+ once a concrete need is established.

All roster models stay installed on disk. Only one is loaded into VRAM at a time on current hardware (8GB ceiling). Ollama handles eviction and reload transparently; the model-switch cost is ~5–10 seconds and is acceptable.

The Phase-0-closing ADR selects the roster, not a single model.

### 2. Explicit user selection, not auto-routing (accepted for Phase 1–2)

Model selection in Phase 1 is **user-explicit**:

- Default: workhorse.
- Override: CLI / TUI command like `/model reasoning` or `/model code` sets the active model for the next prompt (or until reset).

No automatic router. No classifier model picking between local options on the user's behalf.

If, by Phase 3, the manual-override pattern has become tedious and a predictable subset of automation is warranted, build a **rule-based** router (keyword/regex match on prompt content), not an ML classifier. Rule-based routers are debuggable and don't add an inference round-trip per prompt.

An ML-based auto-router is explicitly deferred to Phase 4 or beyond, gated on concrete user-experience evidence that the manual pattern is costing more than the router would.

### 3. Parallel execution via multi-panel UI (accepted for Phase 2)

Ghost's terminal-octopus UI will support **multiple concurrent conversation panels**, each with its own active model. Firing a long reasoning-model call in one panel does not block the user from continuing to prompt a faster model in another.

Implementation implications:

- Ollama already supports concurrent requests; the blocker is VRAM, not concurrency primitives.
- On 8GB VRAM, true simultaneity between two different models is not possible; panel-switching triggers Ollama's eviction/reload cycle. Acceptable cost on current hardware.
- On the RTX 3090 upgrade path (24GB), both models stay resident and responses overlap genuinely.
- Each panel's state (active model, conversation history, scroll position) is independent.

This is a **Phase 2 UI deliverable**, aligned with the existing multi-panel specification in `02_subsystems/ui/spec.md`.

## Rationale

### Why a roster over a single winner

- The benchmark's purpose is to inform architecture, not to crown a champion. If different models genuinely excel at different things, discarding the information costs nothing to act on.
- Disk cost of keeping 3 × 5GB models installed is trivial on a dedicated SSD.
- The roster pattern matches how quant research teams actually use model ensembles: specific tools for specific jobs, not one model to rule them all.
- Career positioning: "role-based model assignment" is a stronger signal in quant-shop interviews than "benchmarked three, picked the highest score." It demonstrates system-design thinking, not just model evaluation.

### Why explicit selection beats auto-routing in Phase 1

- Routing errors are worse than no routing. Sending a hard maths question to a fast model that confidently answers wrong is a worse failure than explicitly invoking the reasoning model.
- A router adds its own inference latency before the worker model starts. For simple prompts, this can double total response time.
- Perplexity's architecture is instructive: users *explicitly* pick "Quick / Pro / Deep Research." Perplexity routes between modes, not models, and the user is the router. This is a deliberate design.
- Explicit selection is cheap to implement (one shell argument) and teaches the user which model suits which task — useful calibration for when automation is eventually added.

### Why parallel panels are the right UI solution

- The user's original routing proposal implicitly assumed synchronous single-model use. Parallel panels remove the problem the router was trying to solve: you don't need to route perfectly if you can run both options and pick the better answer.
- Aligns with the existing octopus-terminal vision without introducing a new UI paradigm.
- Gives Ghost a distinctive UX that differentiates it from chat-first assistants, which is a career-positioning asset.

## Consequences

- **Phase 0 close-out ADR** becomes "Phase 1 model roster selection" rather than "Phase 1 base model selection." Document 2–3 roster picks with assigned roles, plus 1 discard (if any candidate is dominated).
- **Phase 1 implementation** adds a lightweight model-selection layer to the CLI from day one. Not a router — just a `/model` slash command (or equivalent) that switches which Ollama model the next request targets.
- **Phase 2 UI** is expanded in scope: the multi-panel TUI now needs per-panel model state and concurrent Ollama request handling. Not a large expansion — most of the infrastructure was already planned.
- **Hardware upgrade path is clearer.** An RTX 3090 unlocks genuine parallel multi-model use, which is now a concrete feature benefit rather than an abstract "more headroom" argument. Phase 3+ hardware decision has sharper justification.
- **Benchmark interpretation changes.** Scoring still proceeds as planned but the output is a roster decision rather than a winner selection. "Second place" is now a role assignment, not a consolation prize.

## Alternatives considered

- **Single winner.** Rejected for the reasons above: wastes specialisation signal, weaker interview narrative, and aligns less well with real-world quant-team patterns.
- **Auto-router in Phase 1.** Rejected: premature automation, adds failure mode, adds latency, and is a research problem, not a solved pattern. Revisit in Phase 3+ with rule-based design first.
- **Parallel execution without UI support (CLI-only).** Technically simpler but loses the "octopus arms" design affordance that makes Ghost's UI distinctive. If UI work slips in Phase 2, fall back to this — but aim for panels.

## Revisit triggers

- If manual model switching proves genuinely annoying after 2–4 weeks of Phase 1 use, revisit rule-based routing earlier than Phase 3.
- If hardware upgrade happens (RTX 3090), revisit the parallel-panel implementation to take advantage of genuine simultaneity rather than alternation.
- If a new open-weights model is released that is materially better across all roles (unifies workhorse + reasoning), revisit whether the roster should collapse back to a single pick. The framework supports single-pick as a special case.
