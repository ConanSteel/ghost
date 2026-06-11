"""
Ghost Phase 0 benchmark harness.

Iterates over a list of Ollama models and runs them against the Phase 0
smoke-test eval bank (15 questions). For each (model, question) pair it
records:

- The raw response text
- Wall-clock time for the generation
- Ollama's reported eval_count (tokens generated), prompt_eval_count,
  and timings (total_duration, eval_duration) so we can compute tok/s

Writes two files to the output directory:

- results-<timestamp>.csv      : one row per (model, question)
- results-<timestamp>.jsonl    : full raw responses (for later re-scoring
                                 without re-running the benchmark)

Usage (from ghost-env activated venv):

    python benchmark.py \\
        --eval-questions "$GHOST_ROOT/anchor/06_references/eval_questions.md" \\
        --output-dir    "$GHOST_ROOT/artefacts/bench" \\
        --models        qwen2.5:7b llama3.1:8b deepseek-r1:7b

Safety rails:

- Dry-run mode (`--dry-run`) runs only Q01 on only the first model.
- If Ollama is unreachable, fails loudly before touching any files.
- Output files are timestamped so re-runs never overwrite prior results.

Requires:
    pip install requests

(Already installed in the starter package set.)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from eval_loader import EvalQuestion, parse_eval_questions


OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODELS = ["qwen2.5:7b", "llama3.1:8b", "deepseek-r1:7b"]

# No retrieval context yet — this is a pre-RAG smoke test of the base model.
# The system prompt keeps the model from refusing financial questions on
# unnecessary disclaimer grounds and sets the register we want.
SYSTEM_PROMPT = (
    "You are an expert quantitative finance assistant helping with a benchmark "
    "evaluation. Answer questions directly and show your working where relevant. "
    "Do not add unnecessary disclaimers about consulting a professional; the user "
    "is a finance professional and understands the context. If you do not know "
    "something, say so plainly rather than guessing."
)


@dataclass
class GenerationResult:
    model: str
    qid: str
    label: str
    category: str
    difficulty: str
    question: str
    response: str
    wall_seconds: float
    eval_count: int | None            # tokens generated
    prompt_eval_count: int | None     # prompt tokens processed
    total_duration_ns: int | None     # Ollama's total
    eval_duration_ns: int | None      # generation only
    load_duration_ns: int | None      # model-load time (relevant on first call)
    tokens_per_second: float | None
    error: str | None = None
    raw_ollama_response: dict[str, Any] = field(default_factory=dict)


def check_ollama_reachable() -> None:
    """Fail loudly if Ollama is not running or unreachable."""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        r.raise_for_status()
    except requests.RequestException as exc:
        sys.exit(
            f"ERROR: Ollama not reachable at {OLLAMA_HOST}.\n"
            f"  Detail: {exc}\n"
            f"  Fix: ensure `systemctl status ollama` shows active, and that\n"
            f"  `ollama list` works from the shell."
        )


def check_models_available(models: list[str]) -> None:
    """Verify each requested model is in `ollama list`."""
    r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
    r.raise_for_status()
    available = {m["name"] for m in r.json().get("models", [])}
    missing = [m for m in models if m not in available]
    if missing:
        sys.exit(
            f"ERROR: the following requested models are not available in Ollama:\n"
            f"  {missing}\n"
            f"  Available: {sorted(available)}\n"
            f"  Fix: `ollama pull <model>` for each missing one."
        )


def run_one(model: str, question: EvalQuestion, timeout_s: int = 300) -> GenerationResult:
    """
    Run a single (model, question) generation via Ollama's /api/chat endpoint.
    Returns a GenerationResult even on failure — errors are captured, not raised,
    so the benchmark can complete and we can see partial results.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question.question},
        ],
        "stream": False,
        "options": {
            # Deterministic-ish. Not fully deterministic because batch ordering
            # and quantisation make bit-exact reproducibility elusive, but this
            # reduces run-to-run variance meaningfully.
            "temperature": 0.2,
            "seed": 42,
            "num_ctx": 4096,
        },
    }

    start = time.perf_counter()
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=timeout_s)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as exc:
        wall = time.perf_counter() - start
        return GenerationResult(
            model=model,
            qid=question.qid,
            label=question.label,
            category=question.category,
            difficulty=question.difficulty,
            question=question.question,
            response="",
            wall_seconds=wall,
            eval_count=None,
            prompt_eval_count=None,
            total_duration_ns=None,
            eval_duration_ns=None,
            load_duration_ns=None,
            tokens_per_second=None,
            error=f"{type(exc).__name__}: {exc}",
        )
    wall = time.perf_counter() - start

    response_text = data.get("message", {}).get("content", "").strip()
    eval_count = data.get("eval_count")
    eval_duration_ns = data.get("eval_duration")
    tps = None
    if eval_count and eval_duration_ns:
        tps = eval_count / (eval_duration_ns / 1e9)

    return GenerationResult(
        model=model,
        qid=question.qid,
        label=question.label,
        category=question.category,
        difficulty=question.difficulty,
        question=question.question,
        response=response_text,
        wall_seconds=wall,
        eval_count=eval_count,
        prompt_eval_count=data.get("prompt_eval_count"),
        total_duration_ns=data.get("total_duration"),
        eval_duration_ns=eval_duration_ns,
        load_duration_ns=data.get("load_duration"),
        tokens_per_second=tps,
        error=None,
        raw_ollama_response=data,
    )


def write_outputs(results: list[GenerationResult], output_dir: Path) -> tuple[Path, Path]:
    """
    Write CSV (summary) and JSONL (full) outputs with a timestamp in the filename.
    Returns the two paths written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    csv_path = output_dir / f"results-{timestamp}.csv"
    jsonl_path = output_dir / f"results-{timestamp}.jsonl"

    csv_fields = [
        "model", "qid", "label", "category", "difficulty",
        "wall_seconds", "eval_count", "prompt_eval_count",
        "tokens_per_second", "error",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for r in results:
            row = {k: getattr(r, k) for k in csv_fields}
            # Round tok/s for readability; keep full precision in JSONL.
            if row["tokens_per_second"] is not None:
                row["tokens_per_second"] = round(row["tokens_per_second"], 2)
            writer.writerow(row)

    with jsonl_path.open("w", encoding="utf-8") as f:
        for r in results:
            record = asdict(r)
            # raw_ollama_response can be bulky but we want it for re-scoring.
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return csv_path, jsonl_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Ghost Phase 0 benchmark harness.")
    parser.add_argument(
        "--eval-questions",
        type=Path,
        required=True,
        help="Path to eval_questions.md (in the anchor folder).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for results CSV/JSONL (will be created if missing).",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help=f"Model tags to benchmark. Default: {DEFAULT_MODELS}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run only Q01 on the first model as a smoke test.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-generation timeout in seconds (default 300).",
    )
    args = parser.parse_args()

    print(f"[benchmark] Ollama host: {OLLAMA_HOST}")
    check_ollama_reachable()

    print(f"[benchmark] Loading questions from: {args.eval_questions}")
    questions = parse_eval_questions(args.eval_questions)
    print(f"[benchmark] Loaded {len(questions)} questions.")

    models = args.models
    if args.dry_run:
        models = models[:1]
        questions = questions[:1]
        print(f"[benchmark] DRY RUN — restricting to {models[0]} × {questions[0].qid}.")

    print(f"[benchmark] Checking model availability: {models}")
    check_models_available(models)

    total = len(models) * len(questions)
    print(f"[benchmark] Running {total} generation(s).")
    print(f"[benchmark] Expect ~15–30 s per generation on an RTX 3070 Ti.\n")

    results: list[GenerationResult] = []
    counter = 0
    overall_start = time.perf_counter()

    for model in models:
        print(f"[benchmark] === model: {model} ===")
        for q in questions:
            counter += 1
            print(f"[benchmark]   [{counter}/{total}] {q.qid} {q.label[:50]}...", end=" ", flush=True)
            result = run_one(model, q, timeout_s=args.timeout)
            results.append(result)
            if result.error:
                print(f"ERROR after {result.wall_seconds:.1f}s: {result.error}")
            else:
                tps = f"{result.tokens_per_second:.1f} tok/s" if result.tokens_per_second else "?"
                print(f"{result.wall_seconds:.1f}s, {result.eval_count} tok, {tps}")

    overall_wall = time.perf_counter() - overall_start
    print(f"\n[benchmark] Done. Total wall time: {overall_wall:.1f}s ({overall_wall/60:.1f} min).")

    csv_path, jsonl_path = write_outputs(results, args.output_dir)
    print(f"[benchmark] Wrote: {csv_path}")
    print(f"[benchmark] Wrote: {jsonl_path}")

    # Summary by model.
    print(f"\n[benchmark] Summary by model:")
    for model in models:
        model_results = [r for r in results if r.model == model]
        errors = [r for r in model_results if r.error]
        ok = [r for r in model_results if not r.error]
        avg_tps = None
        if ok:
            valid_tps = [r.tokens_per_second for r in ok if r.tokens_per_second]
            if valid_tps:
                avg_tps = sum(valid_tps) / len(valid_tps)
        print(
            f"  {model}: {len(ok)}/{len(model_results)} ok, "
            f"avg {avg_tps:.1f} tok/s" if avg_tps else f"  {model}: {len(ok)}/{len(model_results)} ok"
        )
        if errors:
            print(f"    errors: {[e.qid for e in errors]}")

    return 0 if all(not r.error for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
