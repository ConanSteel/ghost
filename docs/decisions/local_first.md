# Architecture posture: local-first, frontier-augmented

**Date:** 2026-04-16
**Status:** Accepted

## Context

The user is cost-constrained and has expressed a preference for running Ghost locally to avoid API token costs. The user's reasoning included the argument that local open-weights models will close the capability gap to frontier models by 2027, making "local only" a defensible bet.

## Decision

Ghost is **local-first but frontier-augmented**. Local models handle the majority of routine work. Frontier APIs are used selectively for tasks where quality clearly justifies the cost.

Routing heuristic:
- **Local model** for: retrieval-grounded Q&A, code snippets, summarisation, formatting, routine reasoning, anything the user does frequently.
- **Frontier API** for: novel or open-ended reasoning, high-stakes analysis (e.g. finalising a backtest's logic), tasks where a wrong answer compounds into expensive downstream errors.
- **Perplexity** (user has unlimited) for: external research, "what's the current state of X" queries, paper discovery.

## Rationale

The user's argument that open-weights models are catching up to the frontier is correct in aggregate and will likely remain so. However:
- The gap closes unevenly. Open models catch up fastest on general chat and coding, slowest on frontier reasoning and niche domains. Quant strategy development sits squarely in the "slowest" category.
- The relevant comparison is not local-Ghost vs. today's Claude, but local-Ghost vs. whatever frontier model the user will have access to in 2027. The user's future employer will almost certainly provide API access to frontier models.
- Ghost's value is not being a cheaper Claude — it is being the orchestration layer that uses frontier models effectively on the user's behalf, with context, memory, and tool access.

Therefore the investment thesis is: build Ghost as the thing that orchestrates, contextualises, and automates. Use local models for the 95% of tasks where they suffice; keep frontier-API calls available for the 5% where quality genuinely matters.

This also solves the token-budget problem today: cheap local inference covers the bulk of usage, API spend is reserved for high-value queries.

## Consequences

- Architectural flexibility is preserved. Local model can be swapped as the open-weights frontier advances. Frontier API provider can be swapped as models change.
- The routing layer becomes a first-class component. Needs explicit design in Phase 3.
- A confidence heuristic is needed to escalate automatically. Likely starts as a manual toggle in Phase 2 and becomes automatic in Phase 3.
- Budget discipline remains: the user sets a monthly API spend ceiling, and Ghost enforces it.
- This decision explicitly admits that "pure local" is not the goal. If the user later insists on true zero external calls, that is a different product (and a weaker one).

## Alternatives considered

- **Pure local.** Rejected for reasons above. Revisit if the user's employment situation or constraints change.
- **Pure cloud (API-only).** Rejected: contradicts the user's cost constraints and misses the learning value of building local infrastructure.
- **Local for privacy-sensitive, cloud for everything else.** Closer to right, but "privacy" is not the main axis of the user's decision — quality-vs-cost is. The routing heuristic should reflect that directly.
