# Ghost — Phase Roadmap

## Timeline overview

| Phase | Name | Window | Time commitment |
|-------|------|--------|-----------------|
| 0 | Foundation | Apr 16 → ~May 20, 2026 | Light touch (exams) |
| 1 | RAG Core | ~May 20 → end June 2026 | Near full-time |
| 2 | OpenClaw + LSEG | July 2026 | Near full-time |
| 3 | Agentic Workflows | August 2026 | Near full-time |
| 4 | Demonstrable v1 | September 2026 | Full-time |
| 5+ | Post-MVP | Oct 2026 → | Part-time alongside job applications / work |

## Phase 0 — Foundation (now → mid-May 2026)

**Goal:** Everything is set up so that the moment exams finish, Phase 1 can start without friction.

**Exit criteria:**
- Anchor folder in place, committed to version control or Obsidian vault.
- Python environment ready (conda or venv) with core libraries installable.
- Ollama installed and at least one model pulled (candidates: Qwen 2.5 7B, Llama 3.1 8B, DeepSeek-R1-Distill-Qwen 7B).
- Baseline benchmarks run: inference speed on the 3070 Ti, memory footprint, quality spot-check on 10 quant-finance questions.
- Obsidian vault decision: keep existing or start fresh? Documented in `03_decisions/`.
- Reading list assembled in `06_references/` covering RAG, LoRA, quant-model design.

**Risks to watch:**
- Exam overspend. Budget < 4 hours/week during revision.
- Scope creep — do not start building RAG in Phase 0.

## Phase 1 — RAG Core (mid-May → end June 2026)

**Goal:** A working command-line pipeline that answers quant questions from your vault + a curated finance corpus, with citations, running entirely locally.

**Exit criteria:**
- Document ingestion pipeline (vault + PDFs + scraped finance pages) into a local vector DB.
- Embedding model chosen and benchmarked (candidates: `bge-large-en-v1.5`, `nomic-embed-text`, `jina-embeddings-v3`).
- Vector DB chosen (likely Chroma or Qdrant, running locally).
- Retrieval + reranking + prompting pipeline producing grounded answers.
- Simple CLI interface: ask a question, get an answer with source citations.
- Evaluation harness: 30+ curated test questions with expected answers or rubrics.
- First pass at prompt templates for Ghost's voice.

**Out of scope:**
- OpenClaw integration (Phase 2).
- Any web/API data sources (Phase 2).
- Multi-panel UI (Phase 2).
- Fine-tuning (Phase 3).

**Risks to watch:**
- Embedding quality on finance jargon. Early benchmark, switch if needed.
- Context-window pressure on 8B models. Plan chunking carefully.

## Phase 2 — OpenClaw + LSEG (July 2026)

**Goal:** Ghost runs as an OpenClaw assistant with LSEG data access and a real multi-panel terminal UI.

**Exit criteria:**
- OpenClaw installed and configured with the Phase 1 RAG pipeline ported as a skill.
- LSEG MCP server connected; basic queries work (quote, historical bars, news).
- Terminal UI (Textual or similar Python TUI framework) with at least three panels: conversation, data stream, task/notification.
- Data ingestion extended: EDGAR filings, arXiv quant-finance papers.
- Ghost's personality / tone baked into system prompts.
- First agentic skill: "summarise today's market movements for [ticker list]".

**Risks to watch:**
- OpenClaw breaking changes (project is young, moves fast). Pin to a release.
- LSEG MCP access patterns and rate limits. Read docs carefully before building.

## Phase 3 — Agentic Workflows (August 2026)

**Goal:** Ghost can take meaningful quant actions on your behalf, and you can measure whether it's any good.

**Exit criteria:**
- Natural-language-to-backtest pipeline: describe a strategy, Ghost writes the backtest code and runs it against historical LSEG data.
- Market-monitoring skill with user-defined alert conditions (e.g., "tell me if XYZ's 20-day vol crosses 30%").
- Evaluation framework: automated scoring of Ghost's answers on a held-out question set, tracked over time.
- LoRA fine-tuning on accumulated strategy notes and backtest transcripts. Compare fine-tuned vs. base with the eval framework.
- Escalation discipline codified: what Ghost can do autonomously vs. what requires confirmation.

**Risks to watch:**
- Backtest correctness. Quant bugs are silent and expensive. Unit test the harness.
- LoRA hurting rather than helping. The eval framework is how you know.

## Phase 4 — Demonstrable v1 (September 2026)

**Goal:** A polished artefact you can show employers.

**Exit criteria:**
- Architecture diagram.
- README for the whole project, written for a technical hiring manager.
- 5–10 minute recorded walkthrough.
- Known-limitations document. Honesty impresses.
- Reproducible setup: fresh machine → working Ghost in < 2 hours with a bootstrap script.
- Public-facing summary (blog post or GitHub README) that doesn't expose proprietary strategy code but shows the system design.

**Risks to watch:**
- The temptation to keep building instead of polishing. Freeze scope early September.

## Phase 5+ — Post-MVP (ongoing)

Candidate next projects, ordered by likely value:
- Voice interaction (Whisper for STT, local TTS).
- Earnings-call ingestion and summarisation pipeline.
- Hardware upgrade (RTX 3090) — revisit once VRAM is proven to be the bottleneck.
- Strategy-research loop: Ghost proposes, backtests, and ranks candidate strategies.
- Mobile read-only companion app.
- Multi-user exploration if there's a commercial angle.
- Bloomberg Terminal integration (if/when access is available).
