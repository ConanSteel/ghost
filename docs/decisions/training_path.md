# Training path: RAG-first, LoRA later, no pre-training from scratch

**Date:** 2026-04-16
**Status:** Accepted

## Context

User initially proposed pre-training a custom model from scratch, citing cost efficiency and the methods used by Chinese AI labs. User also flagged interest in specialising Ghost for STEM (maths, finance, physics) rather than building a general-purpose model.

## Decision

Ghost will be built via **RAG first, then LoRA/QLoRA fine-tuning as a later phase**. Pre-training a foundation model from scratch is ruled out for this project.

Training path in order:
1. RAG over the user's vault and a curated finance corpus, using a strong open-weights base model (candidates: Qwen 2.5 7B/14B, Llama 3.1 8B, DeepSeek-R1-Distill).
2. QLoRA fine-tuning once a meaningful corpus of the user's own strategies, annotations, and Q&A exists (Phase 3).
3. More exotic methods (full fine-tuning, distillation) only revisited if points 1 and 2 prove insufficient and justify the investment.

## Rationale

The user's original plan conflated two distinct techniques:
- Pre-training from scratch requires compute budgets on the order of tens of millions of dollars and thousands of GPUs. It is infeasible on consumer hardware regardless of budget — this is a physics / scaling-laws constraint, not a cost preference.
- Distillation (what the user attributed to Chinese labs as "training by prompting existing models") requires a capable teacher model and a well-curated dataset, and even then typically sits on top of a pre-trained base. It is not a substitute for pre-training.

The open-weights frontier is advancing fast enough that any custom pre-trained model would be strictly worse than a freely downloadable one, while costing months of effort.

RAG provides the "specialisation" the user wants (domain-relevant answers grounded in their own materials) without modifying weights. QLoRA provides genuine behavioural customisation on consumer hardware. Together they cover the user's real goals.

## Consequences

- Commits the project to open-weights base models and off-the-shelf infrastructure for the foreseeable future.
- Frees substantial time and budget to invest in retrieval quality, UI, and integrations — where marginal effort actually moves the needle.
- If the user's future employer adopts a proprietary model stack, Ghost is decoupled: swap the base model without rebuilding the system.
- If the user encounters someone claiming to have "trained their own model," they should probe what that actually means — it is almost always fine-tuning.

## Alternatives considered

- **Pre-training from scratch.** Ruled out on feasibility grounds, as above.
- **Distillation from a teacher.** Could become viable in Phase 3+ if the user accumulates a large enough high-quality interaction corpus and has a strong teacher model available (e.g. via API). Revisit then, not now.
- **Start with LoRA immediately, skip RAG.** Rejected: LoRA without RAG means Ghost cannot reference the user's actual documents, only patterns learned from them. RAG is the mechanism for grounded citation.
