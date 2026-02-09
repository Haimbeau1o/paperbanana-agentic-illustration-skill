#!/usr/bin/env python3
"""Validate iterative round logs for paperbanana-agentic-illustration."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}")


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def validate_round(round_obj: Any, idx: int, errors: List[str]) -> None:
    if not isinstance(round_obj, dict):
        errors.append(f"rounds[{idx}] must be an object.")
        return

    if round_obj.get("round") != idx:
        errors.append(f"rounds[{idx}].round must equal {idx}.")

    if not isinstance(round_obj.get("description_t"), str):
        errors.append(f"rounds[{idx}].description_t must be a string.")

    artifact = round_obj.get("artifact")
    if not isinstance(artifact, dict):
        errors.append(f"rounds[{idx}].artifact must be an object.")
    else:
        if artifact.get("type") not in {"image_path", "image_prompt", "code_text"}:
            errors.append(f"rounds[{idx}].artifact.type is invalid.")
        if not isinstance(artifact.get("value"), str):
            errors.append(f"rounds[{idx}].artifact.value must be a string.")

    critique = round_obj.get("critique")
    if not isinstance(critique, dict):
        errors.append(f"rounds[{idx}].critique must be an object.")
        return

    for key in ("critic_suggestions", "revised_description"):
        if not isinstance(critique.get(key), str):
            errors.append(f"rounds[{idx}].critique.{key} must be a string.")

    if not isinstance(critique.get("stop_flag"), bool):
        errors.append(f"rounds[{idx}].critique.stop_flag must be a boolean.")


def validate_log(log_obj: Any, forced_max_rounds: int | None, allow_description_drift: bool) -> List[str]:
    errors: List[str] = []

    if not isinstance(log_obj, dict):
        return ["Root log must be an object."]

    max_rounds = forced_max_rounds
    if max_rounds is None:
        max_rounds = log_obj.get("max_rounds")
    if not isinstance(max_rounds, int) or max_rounds <= 0:
        errors.append("max_rounds must be a positive integer.")
        return errors

    rounds = log_obj.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        errors.append("rounds must be a non-empty list.")
        return errors

    if len(rounds) > max_rounds:
        errors.append("rounds length cannot exceed max_rounds.")

    for idx, round_obj in enumerate(rounds):
        validate_round(round_obj, idx, errors)

    stop_flags: List[bool] = []
    for round_obj in rounds:
        critique = round_obj.get("critique") if isinstance(round_obj, dict) else None
        stop_flags.append(bool(isinstance(critique, dict) and critique.get("stop_flag") is True))

    for idx, stop_flag in enumerate(stop_flags[:-1]):
        if stop_flag:
            errors.append(
                f"rounds[{idx}] sets stop_flag=true but additional rounds exist afterward."
            )

    if not allow_description_drift:
        for idx in range(len(rounds) - 1):
            this_round = rounds[idx]
            next_round = rounds[idx + 1]
            if not isinstance(this_round, dict) or not isinstance(next_round, dict):
                continue
            critique = this_round.get("critique")
            if not isinstance(critique, dict):
                continue
            revised = critique.get("revised_description")
            next_desc = next_round.get("description_t")
            if isinstance(revised, str) and isinstance(next_desc, str):
                if normalize_text(revised) != normalize_text(next_desc):
                    errors.append(
                        f"rounds[{idx + 1}].description_t must match rounds[{idx}].critique.revised_description (whitespace-insensitive)."
                    )

    terminated_early = log_obj.get("terminated_early", False)
    if not isinstance(terminated_early, bool):
        errors.append("terminated_early must be a boolean when present.")
        terminated_early = False

    last_stop = stop_flags[-1]

    if terminated_early:
        if len(rounds) >= max_rounds:
            errors.append("terminated_early=true requires rounds length < max_rounds.")
        if not last_stop:
            errors.append("terminated_early=true requires last round stop_flag=true.")
        reason = log_obj.get("termination_reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("terminated_early=true requires non-empty termination_reason.")
    else:
        if len(rounds) < max_rounds and not last_stop:
            errors.append(
                "If rounds length < max_rounds, either set terminated_early=true or stop_flag=true on last round."
            )

    mode = log_obj.get("mode")
    if mode is not None and mode not in {"diagram_image", "plot_code"}:
        errors.append("mode must be 'diagram_image' or 'plot_code' when present.")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate iterative round logs.")
    parser.add_argument("--log", type=Path, required=True, help="Path to round log JSON")
    parser.add_argument("--max-rounds", type=int, help="Override max rounds expected")
    parser.add_argument(
        "--allow-description-drift",
        action="store_true",
        help="Disable strict revised_description -> next description_t continuity checks",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        log_obj = load_json(args.log)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate_log(log_obj, args.max_rounds, args.allow_description_drift)
    if errors:
        print("ERROR: round log validation failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK: round log is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
