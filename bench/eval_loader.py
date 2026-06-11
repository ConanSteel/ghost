"""
Parse the eval questions from the anchor folder's markdown.

The markdown format uses:

### Q## — label
**Category:** ...
**Difficulty:** ...
**Question:** ...
**Expected answer / rubric:** ...
**Common failure modes:** ...

We extract: question_id, label, category, difficulty, question text.
Rubric and failure modes are not needed at runtime — they're for manual scoring.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalQuestion:
    qid: str           # e.g. "Q01"
    label: str         # e.g. "Sharpe with risk-free rate"
    category: str
    difficulty: str
    question: str

    def __repr__(self) -> str:
        return f"EvalQuestion({self.qid}: {self.label!r})"


# Matches a question heading like:
#   ### Q01 — Sharpe with risk-free rate
QUESTION_HEADING_RE = re.compile(
    r"^###\s+(Q\d+)\s+[—\-]\s+(.+?)\s*$",
    re.MULTILINE,
)


def _extract_field(block: str, field_name: str) -> str | None:
    """
    Extract a single-line value from a '**Field:**' style line.
    Assumes the value is on the same line as the field name.
    """
    pattern = re.compile(
        rf"^\*\*{re.escape(field_name)}:\*\*\s+(.+?)\s*$",
        re.MULTILINE,
    )
    match = pattern.search(block)
    return match.group(1).strip() if match else None


def parse_eval_questions(markdown_path: Path) -> list[EvalQuestion]:
    """
    Parse the anchor folder's eval_questions.md and return a list of EvalQuestion.
    Raises FileNotFoundError if the path does not exist.
    Raises ValueError if parsing a question fails.
    """
    if not markdown_path.is_file():
        raise FileNotFoundError(
            f"Eval questions file not found at {markdown_path}. "
            f"Expected a copy at this path. Either symlink from the anchor folder "
            f"or copy eval_questions.md into place."
        )

    text = markdown_path.read_text(encoding="utf-8")

    # Find all question headings and their positions.
    headings = list(QUESTION_HEADING_RE.finditer(text))
    if not headings:
        raise ValueError(
            f"No question headings found in {markdown_path}. "
            f"Expected lines matching '### Q01 — label'."
        )

    questions: list[EvalQuestion] = []
    for i, match in enumerate(headings):
        qid = match.group(1)
        label = match.group(2)
        block_start = match.end()
        block_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[block_start:block_end]

        category = _extract_field(block, "Category")
        difficulty = _extract_field(block, "Difficulty")
        question_text = _extract_field(block, "Question")

        missing = [
            name
            for name, value in [
                ("Category", category),
                ("Difficulty", difficulty),
                ("Question", question_text),
            ]
            if value is None
        ]
        if missing:
            raise ValueError(
                f"{qid} ({label!r}) is missing required fields: {missing}"
            )

        questions.append(
            EvalQuestion(
                qid=qid,
                label=label,
                category=category,        # type: ignore[arg-type]
                difficulty=difficulty,    # type: ignore[arg-type]
                question=question_text,   # type: ignore[arg-type]
            )
        )

    return questions


if __name__ == "__main__":
    # Quick self-test.
    import sys

    if len(sys.argv) != 2:
        print("Usage: python eval_loader.py <path-to-eval_questions.md>")
        sys.exit(2)

    path = Path(sys.argv[1])
    qs = parse_eval_questions(path)
    print(f"Parsed {len(qs)} questions.")
    for q in qs:
        print(f"  {q.qid} [{q.category}/{q.difficulty}] {q.label}")
