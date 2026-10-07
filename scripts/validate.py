#!/usr/bin/env python3
"""Lightweight validation for the ecommerce product ads skill.

This script checks files, structured data, and image dimensions only. It does
not generate concepts, prompts, layouts, or artwork.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml
from PIL import Image


REQUIRED_INPUTS = ("text.pdf", "product.png", "logo.svg")
REQUIRED_WORK = (
    "brief.yaml",
    "layout.json",
    "state.yaml",
    "visual_strategy.yaml",
)


class ValidationError(Exception):
    pass


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"Invalid YAML: {path}: {exc}") from exc


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"Invalid JSON: {path}: {exc}") from exc


def validate_input(project: Path) -> list[str]:
    input_dir = project / "input"
    messages: list[str] = []
    for name in REQUIRED_INPUTS:
        path = input_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValidationError(f"Missing or empty input: {path}")

    pdf = input_dir / "text.pdf"
    if not pdf.read_bytes().startswith(b"%PDF-"):
        raise ValidationError(f"Not a valid PDF signature: {pdf}")
    messages.append(f"PDF present: {pdf.name}")

    product = input_dir / "product.png"
    try:
        with Image.open(product) as image:
            image.verify()
        with Image.open(product) as image:
            if image.format != "PNG":
                raise ValidationError(f"Product image is not PNG: {product}")
            messages.append(
                f"Product PNG: {image.width}x{image.height}, mode={image.mode}"
            )
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(f"Invalid product PNG: {product}: {exc}") from exc

    logo = input_dir / "logo.svg"
    try:
        root = ET.parse(logo).getroot()
    except Exception as exc:
        raise ValidationError(f"Invalid logo SVG: {logo}: {exc}") from exc
    if root.tag.split("}")[-1].lower() != "svg":
        raise ValidationError(f"Root element is not <svg>: {logo}")
    if not (root.get("viewBox") or (root.get("width") and root.get("height"))):
        raise ValidationError(f"SVG needs viewBox or width/height: {logo}")
    messages.append("Logo SVG parsed successfully")
    return messages


def require_path(data, dotted_path: str) -> None:
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValidationError(f"Missing structured field: {dotted_path}")
        current = current[part]


def validate_work(project: Path) -> list[str]:
    work_dir = project / "work"
    for name in REQUIRED_WORK:
        path = work_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValidationError(f"Missing or empty work file: {path}")

    brief = load_yaml(work_dir / "brief.yaml")
    layout = load_json(work_dir / "layout.json")
    state = load_yaml(work_dir / "state.yaml")
    strategy = load_yaml(work_dir / "visual_strategy.yaml")
    for field in (
        "project.marketing_goal",
        "project.target_audience",
        "product.brand",
        "product.name.zh",
        "product.name.en",
        "brand.tone",
        "copy.zh.title",
        "copy.zh.selling_points",
        "copy.zh.price",
        "copy.zh.campaign_period",
        "copy.zh.cta",
        "copy.en.title",
        "copy.en.selling_points",
        "copy.en.price",
        "copy.en.campaign_period",
        "copy.en.cta",
        "deliverables.canvas.ratio",
        "asset_constraints.product",
        "asset_constraints.logo",
        "missing_fields",
    ):
        require_path(brief, field)

    if not isinstance(layout, dict) or "canvas" not in layout or "regions" not in layout:
        raise ValidationError("layout.json needs canvas and regions objects")
    if not isinstance(strategy, dict) or "strategy" not in strategy:
        raise ValidationError("visual_strategy.yaml needs a strategy object")

    choices = state.get("human_confirmation", {}).get("choices", {})
    if set(choices) != {"A", "B", "C"}:
        raise ValidationError("state.yaml human confirmation choices must be exactly A/B/C")

    return [
        "All four work files parsed successfully",
        "Brief contains required factual fields",
        "Human confirmation choices are exactly A/B/C",
    ]


def parse_ratio(value: str | None) -> tuple[int, int] | None:
    if not value or ":" not in str(value):
        return None
    left, right = str(value).split(":", 1)
    try:
        a, b = int(left), int(right)
    except ValueError as exc:
        raise ValidationError(f"Invalid ratio: {value}") from exc
    if a <= 0 or b <= 0:
        raise ValidationError(f"Invalid ratio: {value}")
    divisor = math.gcd(a, b)
    return a // divisor, b // divisor


def validate_output(project: Path, source: str) -> list[str]:
    source_dir = project / source
    if not source_dir.is_dir():
        raise ValidationError(f"Output source directory does not exist: {source_dir}")

    brief_path = project / "work" / "brief.yaml"
    layout_path = project / "work" / "layout.json"
    brief = load_yaml(brief_path)
    layout = load_json(layout_path)
    expected_ratio = parse_ratio(brief.get("deliverables", {}).get("canvas", {}).get("ratio"))
    expected_width = layout.get("canvas", {}).get("width")
    expected_height = layout.get("canvas", {}).get("height")

    pngs = sorted(source_dir.glob("*.png"))
    if not pngs:
        raise ValidationError(f"No PNG files found in: {source_dir}")

    messages: list[str] = []
    for path in pngs:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
        except Exception as exc:
            raise ValidationError(f"Invalid PNG: {path}: {exc}") from exc

        if expected_width and expected_height and (width, height) != (
            expected_width,
            expected_height,
        ):
            raise ValidationError(
                f"Wrong dimensions for {path.name}: {width}x{height}; "
                f"expected {expected_width}x{expected_height}"
            )
        if expected_ratio:
            divisor = math.gcd(width, height)
            actual_ratio = (width // divisor, height // divisor)
            if actual_ratio != expected_ratio:
                raise ValidationError(
                    f"Wrong ratio for {path.name}: {actual_ratio[0]}:{actual_ratio[1]}; "
                    f"expected {expected_ratio[0]}:{expected_ratio[1]}"
                )
        messages.append(f"PNG valid: {path.name} ({width}x{height})")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="Project directory")
    parser.add_argument(
        "--stage", choices=("input", "work", "output", "all"), default="all"
    )
    parser.add_argument(
        "--source",
        default="output",
        help="PNG directory relative to project for output validation",
    )
    args = parser.parse_args()
    project = Path(args.project).resolve()

    try:
        messages: list[str] = []
        if args.stage in ("input", "all"):
            messages.extend(validate_input(project))
        if args.stage in ("work", "all"):
            messages.extend(validate_work(project))
        if args.stage in ("output", "all"):
            messages.extend(validate_output(project, args.source))
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for message in messages:
        print(f"OK: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

