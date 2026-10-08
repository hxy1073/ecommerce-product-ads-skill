#!/usr/bin/env python3
"""Initialize a task workspace without copying the installed Skill.

The script only writes inside the selected task directory. Skill templates,
Design Patterns, and validation code remain read-only resources beside this
script.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_INPUTS = ("text.pdf", "product.png", "logo.svg")
REQUIRED_TEMPLATES = (
    "brief.template.yaml",
    "concepts.template.yaml",
    "layout.template.json",
    "state.template.yaml",
    "visual_strategy.template.yaml",
)
REQUIRED_PATTERNS = (
    "01_hero_product.json",
    "02_lifestyle_scene.json",
    "03_promotional_poster.json",
    "04_feature_callout.json",
    "05_seasonal_campaign.json",
    "06_premium_minimal.json",
)


class BootstrapError(Exception):
    pass


def is_nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def missing_inputs(directory: Path) -> list[str]:
    return [name for name in REQUIRED_INPUTS if not is_nonempty_file(directory / name)]


def directory_has_content(path: Path) -> bool:
    return path.is_dir() and any(path.iterdir())


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_skill_resources() -> dict[str, str]:
    templates = SKILL_ROOT / "templates"
    patterns = SKILL_ROOT / "references" / "patterns"
    validator = SKILL_ROOT / "scripts" / "validate.py"

    missing: list[str] = []
    missing.extend(str(templates / name) for name in REQUIRED_TEMPLATES if not (templates / name).is_file())
    missing.extend(str(patterns / name) for name in REQUIRED_PATTERNS if not (patterns / name).is_file())
    if not validator.is_file():
        missing.append(str(validator))
    if missing:
        raise BootstrapError("Skill resources are incomplete: " + ", ".join(missing))

    return {
        "templates": str(templates),
        "patterns": str(patterns),
        "validator": str(validator),
    }


def inspect_task_status(task_root: Path) -> tuple[str, str | None]:
    work_dir = task_root / "work"
    output_dir = task_root / "output"
    state_path = work_dir / "state.yaml"

    if not state_path.exists():
        if directory_has_content(work_dir) or directory_has_content(output_dir):
            raise BootstrapError(
                "work/ or output/ already contains files, but work/state.yaml is missing; "
                "cannot safely determine whether to resume or preserve a completed task."
            )
        return "new", "stage_0"

    try:
        state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BootstrapError(f"Cannot read existing state file {state_path}: {exc}") from exc
    if not isinstance(state, dict):
        raise BootstrapError(f"Existing state file must contain a YAML mapping: {state_path}")

    stage_6 = state.get("stage_6")
    if isinstance(stage_6, dict) and stage_6.get("status") == "completed":
        return "completed", None

    current_stage = state.get("current_stage")
    if not isinstance(current_stage, str) or not current_stage.strip():
        current_stage = "stage_0"
    return "continue", current_stage


def copy_root_inputs(task_root: Path) -> list[str]:
    input_dir = task_root / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []

    for name in REQUIRED_INPUTS:
        source = task_root / name
        target = input_dir / name
        if target.exists():
            if not target.is_file():
                raise BootstrapError(f"Input target is not a file: {target}")
            if not filecmp.cmp(source, target, shallow=False):
                raise BootstrapError(
                    f"Refusing to overwrite different existing input file: {target}"
                )
            continue
        shutil.copy2(source, target)
        copied.append(name)
    return copied


def bootstrap(task_root: Path) -> dict:
    task_root = task_root.resolve()
    if not task_root.is_dir():
        raise BootstrapError(f"Task directory does not exist: {task_root}")

    skill_is_development_repo = (SKILL_ROOT / ".git").exists()
    task_uses_development_repo = skill_is_development_repo and is_within(
        task_root, SKILL_ROOT
    )
    if not skill_is_development_repo and is_within(task_root, SKILL_ROOT):
        raise BootstrapError(
            "The installed Skill directory is read-only for task artifacts. "
            "Choose a separate task directory."
        )

    resources = validate_skill_resources()
    task_status, resume_stage = inspect_task_status(task_root)

    root_missing = missing_inputs(task_root)
    input_dir = task_root / "input"
    input_missing = missing_inputs(input_dir)
    if not input_missing:
        input_form = "input_directory"
    elif not root_missing:
        input_form = "task_root"
    else:
        raise BootstrapError(
            "Required inputs are incomplete. "
            f"Task-root form missing: {', '.join(root_missing) or 'none'}; "
            f"input/ form missing: {', '.join(input_missing) or 'none'}."
        )

    copied: list[str] = []
    if task_status != "completed":
        if input_form == "task_root":
            copied = copy_root_inputs(task_root)
        (task_root / "work").mkdir(exist_ok=True)
        (task_root / "output").mkdir(exist_ok=True)

    next_action = {
        "new": "start_stage_0",
        "continue": f"resume_{resume_stage}",
        "completed": "preserve_completed_task",
    }[task_status]

    return {
        "task_root": str(task_root),
        "skill_root": str(SKILL_ROOT),
        "workspace_mode": (
            "development_repository" if task_uses_development_repo else "standalone_task"
        ),
        "input_form": input_form,
        "task_status": task_status,
        "next_action": next_action,
        "copied_to_input": copied,
        "resources": resources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", default=".", help="Task directory to initialize")
    args = parser.parse_args()

    try:
        result = bootstrap(Path(args.task))
    except BootstrapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
