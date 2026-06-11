# Subsystem: Data

## Purpose

All external data sources Ghost ingests or queries: market data, filings, news, research, user vault.

## Sources by phase

### Phase 0
- None (no ingestion yet).

### Phase 1
- Obsidian vault (local).
- arXiv q-fin papers (scraped via arXiv API).
- Selected public quant-finance texts (user-curated).

### Phase 2
- **LSEG Workspace via LSEG MCP server** — primary market data. Quotes, historical bars, news, company data.
- SEC EDGAR filings (public API).
- Company earnings transcripts (via LSEG if available).

### Phase 3+
- Real-time alerting streams (LSEG + scheduled polling).
- Alternative data to be scoped later (sentiment, web scraping of selected sources, etc.).

### Deferred / conditional
- Bloomberg Terminal — only if user gains access. Assume very limited programmatic access.
- Paid data vendors — budget-dependent, unlikely during student phase.

## LSEG MCP integration notes

- LSEG has published an official MCP server. This is the preferred integration path — no custom API client needed.
- Check authentication requirements, rate limits, and entitlements on the user's Workspace subscription before relying on any specific endpoint.
- Data lineage matters: every retrieved data point gets a timestamp and source tag in Ghost's context.

## Ingestion pipeline (Phase 1 baseline)

```
[Source] → [Loader] → [Normaliser] → [Chunker] → [Embedder] → [Vector DB]
                              ↓
                       [Metadata store]
```

Run as a scheduled job (daily for news/filings, weekly for papers) once Phase 2 is live.

## Data storage on the Ghost SSD

```
/ghost_ssd/
├── vault/              # User's Obsidian vault (or symlink if kept elsewhere)
├── corpus/             # Raw ingested documents
│   ├── arxiv/
│   ├── edgar/
│   ├── news/
│   └── research/
├── vector_db/          # Chroma/Qdrant persistent storage
├── models/             # Ollama models live here
├── logs/               # Ingestion + interaction logs
└── artefacts/          # Generated: backtests, strategy reports, code
```

## Retention

- Raw corpus: retained indefinitely unless user prunes.
- Interaction logs: retained for Ghost's memory; user can purge via explicit command.
- Backtests: retained for reproducibility. Tag with strategy ID.

## Compliance

- No data leaves the SSD for retrieval. External API calls (LSEG, Perplexity if used) are for fetching, not for sending local content out.
- If the user's LSEG entitlements restrict certain uses (e.g. redistribution), document here and enforce in code.
