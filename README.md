# Ghost

A local-first AI assistant for quantitative finance research, running open-weights models on consumer hardware.

## What this is

Ghost is a personal research infrastructure tool built for systematic trading and quantitative finance work. It pairs local model inference (7B–8B parameter models on an RTX 3070 Ti) with retrieval-augmented generation over a domain-specific knowledge base, so I can ask questions about my own strategies, market data, and research corpus and get cited answers without sending anything to the cloud.

The interface is modelled on a Bloomberg terminal: a multi-panel layout with live data feeds, a strategy editor with inline backtesting, and a command palette for keyboard-driven navigation.

This project is **actively in development**. Phase 0 (foundation and model benchmarking) is complete. Phase 1 (RAG pipeline with citations) is in progress. The target is a working end-to-end system by September 2026.

## Current status

**Done:**
- Benchmarked four local models (Qwen 2.5 7B, Llama 3.1 8B, DeepSeek-R1 7B, Qwen2.5-Coder 7B) using a custom 15-question evaluation harness covering maths, quant methods, markets, code generation, and reasoning
- Selected Qwen 2.5 7B as the Phase 1 workhorse based on scored results
- Designed the system architecture: hybrid local-frontier model, RAG-first training path with LoRA fine-tuning planned for later phases
- Recorded all major decisions as Architecture Decision Records with trade-off analysis and fallback plans

**In progress:**
- Embedding model selection for the retrieval pipeline
- Document ingestion over vault notes, arXiv q-fin papers, and curated quant-finance corpus
- CLI interface for retrieval-grounded Q&A with citations

**Planned:**
- LSEG market data integration via MCP
- Natural-language-to-backtest pipeline
- Market monitoring and alerting
- Multi-panel terminal UI

## Interface design

The UI mockups can be found in the design folder of this repository.

## Repository structure

```
ghost/
├── bench/          # Model evaluation harness and question bank
├── docs/           # Architecture overview, ADRs, subsystem specs
├── design/         # UI mockups
└── src/            # RAG pipeline (in progress)
```

## Hardware

- CPU: Ryzen 5800X
- GPU: RTX 3070 Ti (8GB VRAM — the binding constraint)
- RAM: 64GB
- Storage: Dedicated SSD, WSL2 on Windows

## Built with

Python · Ollama · Qwen 2.5 7B · ChromaDB (planned) · LSEG Workspace (planned)

## Licence

MIT
