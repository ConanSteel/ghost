# Vault structure: fresh dedicated Ghost vault

**Date:** 2026-04-17
**Status:** Accepted
**Supersedes open question:** `05_open_questions/2026-04-16-vault-decision.md`

## Context

Ghost needs an Obsidian vault that functions as both (a) the host for the anchor folder (this project's persistent memory) and (b) the primary retrieval corpus for Ghost's RAG pipeline. The user's existing vault contains ~40 MD files of mixed project material, with an acknowledged messy graph view. The question was whether to reuse the existing vault, start fresh, or run a hybrid.

## Decision

Start a **fresh dedicated Obsidian vault for Ghost**, living inside the Ghost SSD at `/mnt/ghost/vault/` (WSL path; `G:\ghost\vault\` from Windows).

Initial vault contents:
- The anchor folder (at the top level, unchanged from the scaffold).
- A `strategies/` folder for the user's own strategy papers (Shock Absorber, Catching Falling Knives) and supporting code/notes.
- An `interview_prep/` folder for the interview-question material previously held in the existing vault, migrated selectively.
- Other folders grow as needed.

The existing Obsidian vault remains in use for personal/mixed notes not intended for Ghost ingestion. No forced migration. Material moves into the Ghost vault deliberately, when and only when it's Ghost-relevant.

## Rationale

- **Clean retrieval corpus.** Ghost's RAG quality is proportional to corpus signal-to-noise. A fresh vault means every note in it is intentional, tagged consistently, and structured for retrieval. The existing vault carries years of stylistic inconsistency that would drag retrieval quality.
- **Clear ingestion boundary.** "Ghost sees everything in `/mnt/ghost/vault/`, nothing outside it" is a rule the user and Ghost can both enforce trivially. A hybrid approach requires per-note tagging or folder-filter logic, which is fragile.
- **Structural opportunity.** Conventions from `00_meta/README.md` (frontmatter, tag schema, folder taxonomy) can be applied from day one rather than retrofitted.
- **Low migration cost.** The user has ~40 MD files and already plans to restructure. Migrating the Ghost-relevant subset (strategies, interview prep, session logs) is a one-evening job, not a major lift.

## Consequences

- The user maintains two Obsidian vaults. Mild ongoing cost (switch between them in Obsidian). Acceptable given the clean-boundary benefit.
- Ghost's corpus is smaller on day one than it would be with the existing vault. This is fine — RAG quality scales with signal, not raw count. The Shock Absorber and Catching Falling Knives materials alone are more valuable than 30 mixed notes.
- Cross-vault linking is not supported natively in Obsidian; if the user wants to reference the personal vault from the Ghost vault, they use plain file paths, not wikilinks. This is a minor annoyance, not a blocker.
- The Ghost vault's structure becomes part of the project's discipline. Adding a note to it is an intentional act, not a passive capture. This is the right pressure for a research corpus.

## Migration plan

Not on a deadline. Migrate on a rolling basis as material becomes Ghost-relevant:
1. **Anchor folder** — done at vault creation time.
2. **Shock Absorber materials** — before Phase 1 ingestion begins.
3. **Catching Falling Knives materials** — before Phase 1 ingestion begins.
4. **Interview questions** — before Phase 3 (when Ghost becomes an interview-prep aid).
5. **Session logs from the existing vault** — optional; only if they contain Ghost-relevant reasoning.

## Alternatives considered

- **Keep existing vault.** Rejected: mixed content reduces retrieval quality and muddies the ingestion boundary.
- **Hybrid.** Rejected: more operational complexity than the hybrid's marginal benefit justifies. Two clean vaults beats one complicated one.
