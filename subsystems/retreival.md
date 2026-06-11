# Subsystem: Retrieval

## Purpose

The RAG pipeline that grounds Ghost's answers in the user's vault and a curated finance corpus.

## Current state

Design stage. No implementation yet.

## Target architecture (Phase 1)

```
[Documents] → [Chunker] → [Embedder] → [Vector DB]
                                            ↓
[Question] → [Query rewriter] → [Retriever] → [Reranker] → [LLM context] → [Answer + citations]
```

## Open design questions

- **Embedding model.** Candidates: `bge-large-en-v1.5` (strong general), `nomic-embed-text` (open, local-friendly), `jina-embeddings-v3` (long context). Decide after benchmarking on finance text.
- **Vector DB.** Chroma (simple, file-based) vs. Qdrant (faster, more features, still local). Lean Chroma for Phase 1 simplicity; revisit for Phase 2 if scale demands.
- **Chunking strategy.** Fixed-size with overlap is baseline. Semantic chunking (e.g. via `unstructured` or LangChain splitters) is better but slower. Test both on vault notes.
- **Reranking.** Optional in Phase 1. A cross-encoder reranker (e.g. `bge-reranker-v2-m3`) typically lifts retrieval quality 10–20%. Add if time permits.
- **Query rewriting.** HyDE or multi-query expansion. Consider in Phase 1 or defer to Phase 2.

## Document sources (initial)

- **Vault notes** — all MD files in Obsidian vault (scoped to the Ghost-relevant portions if the user keeps a mixed vault).
- **Curated quant-finance corpus** — to be assembled in Phase 1 from:
  - Selected textbook excerpts (legally obtained).
  - arXiv q-fin papers (scraped via arXiv API).
  - SEC filings from EDGAR (Phase 2).
  - LSEG research (Phase 2).

## Metadata schema (draft)

Each chunk should carry:
- `source_uri` — origin document.
- `doc_type` — note / paper / filing / news / code.
- `ingested_at` — timestamp.
- `tags` — free-form (e.g. "mean-reversion", "microstructure", "options").
- `recency_bucket` — for time-weighted retrieval on news/filings.

## Evaluation

A held-out set of ~30 curated questions with gold-standard answers or rubrics. Runs before any architectural change. Metrics: answer correctness, citation precision (did the cited chunks support the claim?), citation recall (were the relevant chunks cited?).

Questions live in `06_references/eval_questions.md` (to be created in Phase 1).

## Privacy

All retrieval is local. No document content leaves the SSD for any retrieval step. Embedding model runs locally via Ollama or `sentence-transformers`.
