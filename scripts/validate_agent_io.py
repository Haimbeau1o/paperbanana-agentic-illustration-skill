#!/usr/bin/env python3
"""Validate single-stage agent input/output payloads for paperbanana-agentic-illustration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROLE_NAMES = {
    "retriever",
    "planner",
    "stylist",
    "visualizer",
    "critic",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}")


def require_fields(obj: Any, required: Dict[str, Any], context: str, errors: List[str]) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{context} must be an object.")
        return
    for key, expected_type in required.items():
        if key not in obj:
            errors.append(f"{context}.{key} is required.")
            continue
        if not isinstance(obj[key], expected_type):
            expected_name = expected_type.__name__
            actual_name = type(obj[key]).__name__
            errors.append(
                f"{context}.{key} must be {expected_name}, got {actual_name}."
            )


def validate_candidate_pool(pool: Any, errors: List[str]) -> None:
    if not isinstance(pool, list):
        errors.append("input.candidate_pool must be a list.")
        return
    for idx, item in enumerate(pool):
        if not isinstance(item, dict):
            errors.append(f"input.candidate_pool[{idx}] must be an object.")
            continue
        for field in ("id", "summary"):
            if field not in item or not isinstance(item[field], str):
                errors.append(f"input.candidate_pool[{idx}].{field} must be a string.")


def validate_artifact(artifact: Any, context: str, errors: List[str]) -> None:
    required = {"type": str, "value": str}
    require_fields(artifact, required, context, errors)
    if isinstance(artifact, dict):
        allowed_types = {"image_path", "image_prompt", "code_text"}
        artifact_type = artifact.get("type")
        if artifact_type not in allowed_types:
            errors.append(
                f"{context}.type must be one of {sorted(allowed_types)}, got {artifact_type!r}."
            )


def validate_retriever(input_obj: Any, output_obj: Any, errors: List[str]) -> None:
    require_fields(
        input_obj,
        {
            "source_context": str,
            "communicative_intent": str,
            "caption": str,
            "candidate_pool": list,
        },
        "input",
        errors,
    )
    if isinstance(input_obj, dict):
        validate_candidate_pool(input_obj.get("candidate_pool"), errors)

    require_fields(
        output_obj,
        {
            "top_refs": list,
            "selection_rationale": str,
        },
        "output",
        errors,
    )

    if not isinstance(output_obj, dict):
        return

    top_refs = output_obj.get("top_refs")
    if isinstance(top_refs, list):
        if not (1 <= len(top_refs) <= 10):
            errors.append("output.top_refs length must be between 1 and 10.")
        for idx, ref_id in enumerate(top_refs):
            if not isinstance(ref_id, str):
                errors.append(f"output.top_refs[{idx}] must be a string.")

    if isinstance(input_obj, dict) and isinstance(top_refs, list):
        pool_ids = {
            item.get("id")
            for item in input_obj.get("candidate_pool", [])
            if isinstance(item, dict)
        }
        missing = [ref_id for ref_id in top_refs if ref_id not in pool_ids]
        if missing:
            errors.append(
                "output.top_refs contains ids not in input.candidate_pool: "
                + ", ".join(missing)
            )


def validate_planner(input_obj: Any, output_obj: Any, errors: List[str]) -> None:
    require_fields(
        input_obj,
        {
            "source_context": str,
            "communicative_intent": str,
            "caption": str,
            "retrieved_examples": list,
        },
        "input",
        errors,
    )
    if isinstance(input_obj, dict):
        examples = input_obj.get("retrieved_examples")
        if isinstance(examples, list):
            for idx, item in enumerate(examples):
                if not isinstance(item, dict):
                    errors.append(f"input.retrieved_examples[{idx}] must be an object.")
                    continue
                if not isinstance(item.get("id"), str):
                    errors.append(f"input.retrieved_examples[{idx}].id must be a string.")

    require_fields(output_obj, {"initial_description": str}, "output", errors)
    if isinstance(output_obj, dict) and "assumption_block" in output_obj:
        if not isinstance(output_obj["assumption_block"], str):
            errors.append("output.assumption_block must be a string when present.")


def validate_stylist(input_obj: Any, output_obj: Any, errors: List[str]) -> None:
    require_fields(
        input_obj,
        {
            "initial_description": str,
            "style_guidelines": str,
            "source_context": str,
            "caption": str,
        },
        "input",
        errors,
    )
    require_fields(
        output_obj,
        {
            "optimized_description": str,
            "style_actions": list,
        },
        "output",
        errors,
    )
    if isinstance(output_obj, dict):
        actions = output_obj.get("style_actions")
        if isinstance(actions, list):
            for idx, action in enumerate(actions):
                if not isinstance(action, str):
                    errors.append(f"output.style_actions[{idx}] must be a string.")


def validate_visualizer(input_obj: Any, output_obj: Any, errors: List[str]) -> None:
    require_fields(
        input_obj,
        {
            "description_t": str,
            "mode": str,
            "round": int,
        },
        "input",
        errors,
    )
    if isinstance(input_obj, dict):
        mode = input_obj.get("mode")
        if mode not in {"diagram_image", "plot_code"}:
            errors.append("input.mode must be 'diagram_image' or 'plot_code'.")

    require_fields(output_obj, {"artifact": dict}, "output", errors)
    if isinstance(output_obj, dict):
        validate_artifact(output_obj.get("artifact"), "output.artifact", errors)


def validate_critic(input_obj: Any, output_obj: Any, errors: List[str]) -> None:
    require_fields(
        input_obj,
        {
            "artifact": dict,
            "description_t": str,
            "source_context": str,
            "caption": str,
            "round": int,
        },
        "input",
        errors,
    )
    if isinstance(input_obj, dict):
        validate_artifact(input_obj.get("artifact"), "input.artifact", errors)

    require_fields(
        output_obj,
        {
            "critic_suggestions": str,
            "revised_description": str,
            "stop_flag": bool,
        },
        "output",
        errors,
    )
    if isinstance(output_obj, dict) and "quality_gate" in output_obj:
        quality_gate = output_obj["quality_gate"]
        if not isinstance(quality_gate, dict):
            errors.append("output.quality_gate must be an object when present.")
        else:
            for key in ("faithfulness_ok", "readability_ok"):
                if key in quality_gate and not isinstance(quality_gate[key], bool):
                    errors.append(f"output.quality_gate.{key} must be a boolean.")


def validate(role: str, input_obj: Any, output_obj: Any) -> List[str]:
    errors: List[str] = []
    validators = {
        "retriever": validate_retriever,
        "planner": validate_planner,
        "stylist": validate_stylist,
        "visualizer": validate_visualizer,
        "critic": validate_critic,
    }
    validators[role](input_obj, output_obj, errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate agent input/output JSON payloads for PaperBanana skill."
    )
    parser.add_argument("--role", choices=sorted(ROLE_NAMES), required=True)
    parser.add_argument("--input", dest="input_path", type=Path, required=True)
    parser.add_argument("--output", dest="output_path", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        input_obj = load_json(args.input_path)
        output_obj = load_json(args.output_path)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate(args.role, input_obj, output_obj)
    if errors:
        print("ERROR: validation failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: {args.role} payload is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
