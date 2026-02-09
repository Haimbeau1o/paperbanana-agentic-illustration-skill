#!/usr/bin/env python3
"""Generate scorecard templates for paperbanana-agentic-illustration evaluations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DIMENSIONS = [
    "Faithfulness",
    "Conciseness",
    "Readability",
    "Aesthetics",
]


def build_json_template(case_id: str) -> dict:
    return {
        "case_id": case_id,
        "source_context_ref": "",
        "caption": "",
        "mode": "diagram_image",
        "round_summary": {
            "total_rounds": 0,
            "stopped_early": False,
            "termination_reason": "",
        },
        "dimensions": {
            name.lower(): {
                "score": None,
                "evidence": "",
                "issues": [],
                "severity": "none",
            }
            for name in DIMENSIONS
        },
        "overall": {
            "ready_for_publish": False,
            "manual_review_required": True,
            "notes": "",
        },
    }


def build_markdown_template(case_id: str) -> str:
    lines = [
        f"# Scorecard - {case_id}",
        "",
        "## Metadata",
        "",
        "- Source context ref: ",
        "- Caption: ",
        "- Mode: diagram_image | plot_code",
        "- Total rounds: ",
        "- Early stop: true/false",
        "- Termination reason: ",
        "",
        "## Dimension Scores",
        "",
        "| Dimension | Score (0-100) | Evidence | Key Issues | Severity |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for name in DIMENSIONS:
        lines.append(f"| {name} |  |  |  | none |")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Ready for publish: true/false",
            "- Manual review required: true/false",
            "- Notes:",
            "",
            "## Reviewer Checklist",
            "",
            "- [ ] Checked source-context alignment",
            "- [ ] Checked caption alignment",
            "- [ ] Checked readability defects",
            "- [ ] Checked factual and numeric consistency",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate scorecard templates.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory where template files will be written",
    )
    parser.add_argument(
        "--case-id",
        default="demo-001",
        help="Case id used in generated template files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{args.case_id}-scorecard.json"
    md_path = output_dir / f"{args.case_id}-scorecard.md"

    json_path.write_text(
        json.dumps(build_json_template(args.case_id), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(build_markdown_template(args.case_id) + "\n", encoding="utf-8")

    print(f"OK: wrote {json_path}")
    print(f"OK: wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
