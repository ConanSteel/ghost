# Phase 1 model selection: Qwen 2.5 7B solo with swappable roster infrastructure

**Date:** 2026-04-20
**Status:** Accepted
**Closes:** Phase 0 — Foundation
**Builds on:** `2026-04-16-training-path.md`, `2026-04-16-local-first-frontier-augmented.md`, `2026-04-20-multi-model-roster.md`

## Context

Phase 0 benchmarked three candidate local models against a 15-question eval bank covering maths, quant-methods, markets, code, and reasoning categories. The initial framing assumed selection of a single workhorse model. Partway through scoring, the user proposed expanding to a role-based roster (workhorse, reasoning specialist, potentially code specialist), captured in `2026-04-20-multi-model-roster.md`. A subsequent targeted test added Qwen2.5-Coder-7B to evaluate the code-specialist hypothesis directly.

Benchmark results across the four models tested:

| Model | Score /40 | Notes |
|-------|-----------|-------|
| Qwen 2.5 7B | 35 | Consistent generalist, strong across all categories, ~99 tok/s |
| DeepSeek-R1 7B | 30 | Slower, more verbose, timed out on Q08, hedged on Q15 |
| Llama 3.1 8B | 24 | Fabricated arithmetic on Q13, basic errors elsewhere |
| Qwen2.5-Coder 7B | scored on 2 code questions: 2/8 | Confidently wrong on code-reasoning questions |

Full scoring detail lives in `$GHOST_ROOT/artefacts/bench/scores.md`.

## Decision

### Phase 1 base model

**Qwen 2.5 7B (`qwen2.5:7b` in Ollama)** is adopted as Ghost's sole local model for Phase 1.

### Roster architecture

Even though the Phase 1 roster contains a single model, Ghost's codebase is structured so that adding a model later is a configuration change, not a refactor. Specifically:

- The model identifier is a configurable parameter, never a literal string in code outside a single config file.
- The prompting / generation layer accepts any Ollama-compatible model identifier without code changes.
- A `/model <tag>` CLI command (to be implemented in Phase 1) allows runtime switching to any pulled Ollama model.
- The benchmark harness already supports arbitrary model lists via `--models` and is the canonical mechanism for evaluating additions.

This leaves Ghost in a position where, if a future model (Qwen 3, a proven specialist, a LoRA-tuned variant in Phase 3) earns a roster slot, the engineering cost to add it is: pull the model, run the benchmark, update the config. No architectural refactor.

### Models kept on disk

- `qwen2.5:7b` — active workhorse.
- `deepseek-r1:7b` — retained for potential future experiments (multi-turn RAG, long-context retrieval grounding) without re-download.
- `qwen2.5-coder:7b` — retained for potential future targeted use (code generation tasks distinct from code reasoning), with the caveat that Phase 0 evidence was unfavourable.
- `llama3.1:8b` — can be deleted (disqualified, unlikely to return).
- `tinyllama:latest` — retained for dry-run testing.

### Explicitly rejected

- **Multi-model roster at Phase 1 start.** No specialist model demonstrated sufficient advantage on targeted questions to justify its inclusion and the attendant routing complexity.
- **Auto-routing between models.** Covered by `2026-04-20-multi-model-roster.md` — deferred to Phase 3+ with rule-based design, not ML classification.
- **Pre-training or heavy fine-tuning.** Covered by `2026-04-16-training-path.md`.

## Rationale

### Why Qwen 2.5 7B specifically

- Highest total score (35/40, 87.5%) on the eval bank.
- Consistent across categories — no single-category collapse.
- Fastest interactive response (~99 tok/s after model load, with short responses completing in 1–5 seconds).
- Handled the Q08 code-reasoning question (which Coder failed, DeepSeek-R1 timed out on, Llama botched) cleanly.
- Apache 2.0 licensed, actively maintained, strong ecosystem presence.

### Why solo rather than multi-model

The benchmark was designed to reveal specialisation advantage. It revealed the opposite:

- DeepSeek-R1 did not outperform Qwen on reasoning-heavy questions (Q09, Q13, Q15).
- Qwen2.5-Coder underperformed Qwen on code-reasoning questions (Q08, Q12).
- No model tested carved out a defensible role that Qwen couldn't cover equally well.

The principled position is: do not add models to the roster without evidence of specialisation benefit. Complexity carries cost (routing decisions, user cognitive overhead, testing burden, failure-mode multiplication). The cost must be earned.

### Why the swappable-roster infrastructure still matters

- Model landscape is moving fast. Qwen 3, Llama 4, and new specialist tunes will land within the Phase 1–4 window. We want to be able to evaluate and swap without rework.
- Phase 3 LoRA fine-tuning will produce custom model variants. These are most usefully added alongside the base model, not as replacements, so the infrastructure needs to support this naturally.
- Phase 2's OpenClaw integration operates on a model-agnostic interface; maintaining this abstraction throughout Phase 1 keeps the Phase 2 transition cheap.
- Interview narrative: demonstrating that the system was *designed* to hold multiple models, and the single-model roster is a *deliberate* choice backed by data, is materially stronger than either "I picked one model and hard-coded it" or "I built a complex roster without evidence it helps."

## Consequences

- **Phase 1 implementation is simpler than originally scoped.** No router, no routing logic, no per-model prompt calibration. Build for one model, architect for N.
- **RAG pipeline development proceeds against Qwen 2.5 7B specifically.** Embedding model choice, chunk-size tuning, and prompt engineering are all calibrated to Qwen's context-handling characteristics.
- **Any Phase 1 finding that reveals Qwen-specific weakness** triggers a targeted additional benchmark (not a wholesale re-evaluation). The scoring rubric established in `$GHOST_ROOT/artefacts/bench/scores.md` is reusable.
- **DeepSeek-R1 remains on disk as a candidate for Phase 1 experimentation** — specifically for testing whether long-context / multi-turn RAG-grounded scenarios show differential behaviour that the single-shot benchmark didn't capture.

## Revisit triggers

- **Phase 1 concrete failure in a category:** if Qwen fails on real Ghost workloads in a category the benchmark scored well (e.g. live strategy writeup generation produces weak output despite Q03-style in-bench strength), re-benchmark with updated rubrics.
- **Major new model release:** Qwen 3, Llama 4, or equivalent generational advance. Re-benchmark the top candidate(s) against existing eval bank + any new Phase 1 eval additions.
- **Phase 3 LoRA readiness:** fine-tuned Qwen 2.5 7B variants are additions to the roster, not replacements. The swappable infrastructure carries them without friction.
- **Hardware upgrade:** an RTX 3090 enables 13B+ models at Q4 and two simultaneously-resident models for genuine parallel execution. Re-evaluate roster at that point.

## What Phase 0 produced

For the retrospective record:

- Four ADRs (training path, OpenClaw adoption, local-first-frontier-augmented, multi-model-roster) plus this closing one.
- Anchor folder scaffold with ~20 documents covering meta, phases, subsystems, decisions, sessions, open questions, references.
- Working WSL2 + Ubuntu + Ollama environment with GPU passthrough and five installed models.
- Benchmark harness (`$GHOST_ROOT/code/bench/benchmark.py`) and 15-question eval bank.
- Full scoring record for 4 models × 15 questions.
- Version-controlled `ghost-anchor` and `ghost-code` repos on GitHub.

Phase 0 closes clean. Ghost has a foundation to build on.
