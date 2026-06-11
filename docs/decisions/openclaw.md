# Adopt OpenClaw as the execution substrate from Phase 2

**Date:** 2026-04-16
**Status:** Accepted

## Context

The user raised OpenClaw as a candidate framework. OpenClaw is an open-source personal AI agent framework launched November 2025 by Peter Steinberger. It provides a local gateway, skills system, persistent memory, multi-channel I/O, proactive scheduling (cron/heartbeat), and a permission model.

As of early April 2026, the project has 310k+ GitHub stars, active development, and a growing ecosystem of community skills.

## Decision

Ghost will adopt OpenClaw as its execution and skills layer starting in **Phase 2** (July 2026). Ghost's identity, personality, and domain specialisation will live in OpenClaw skills and configuration.

Phase 1 will *not* use OpenClaw. The RAG pipeline will be built from primitives (Ollama + Python + a vector DB) so the user understands the underlying mechanics before adopting a framework on top.

## Rationale

Building from scratch the things OpenClaw provides — a skills system, persistent memory, scheduling, a permission model, multi-interface support — would consume most of the summer and result in a worse version of what already exists. Adopting OpenClaw frees that time for the things that actually differentiate Ghost: the finance specialisation, the data integrations, the evaluation framework.

Phase 1 remains hand-built because:
- Understanding RAG primitives is essential for debugging them later.
- It keeps the dependency graph shallow while core retrieval decisions are being made.
- It gives the user a minimum viable Ghost within weeks, not months.

## Consequences

- **Commits the project to TypeScript/Node as a surface language** (OpenClaw is written in TypeScript). The user's Python code lives inside skills and is invoked via OpenClaw's shell/subprocess interfaces. This is manageable but means some learning.
- **Couples Ghost to OpenClaw's release cadence.** A young project with fast-moving breaking changes. Mitigation: pin to a known-good release, upgrade deliberately not reflexively.
- **Inherits OpenClaw's security posture.** Generally good (local-first, user-controlled) but the broad-permissions design has drawn scrutiny. Mitigation: use OpenClaw's restricted mode, audit skills, keep the SSD sandbox.
- **Unlocks community skills.** Useful but the ecosystem is young — enable each skill only after reading its source.
- **Removes a lot of boilerplate.** Memory, cron, multi-interface, permission prompts come for free.

## Alternatives considered

- **Build the agent layer from scratch on top of LangChain / LlamaIndex.** Rejected: more work, less integrated, weaker out-of-the-box experience. Could be reconsidered if OpenClaw proves unstable.
- **Use a hosted agent platform (e.g. a cloud agent service).** Rejected: contradicts the local-first principle and introduces per-call costs.
- **Defer any framework decision.** Rejected: the user needs a clear target architecture to work toward. Re-evaluating monthly would cause scope churn.

## Revisit triggers

- If OpenClaw's breaking-change cadence imposes more maintenance cost than the framework saves.
- If a superior local-first alternative emerges with a clearly better fit for quant workflows.
- If the community skill ecosystem stagnates or becomes a supply-chain risk.
