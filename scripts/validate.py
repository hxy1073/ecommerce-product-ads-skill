#!/usr/bin/env python3
"""Lightweight validation for the ecommerce product ads skill.

The script checks inputs, V2 YAML/JSON state, Design Patterns, and PNG output.
It never makes creative decisions or generates artwork.
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


SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_INPUTS = ("text.pdf", "product.png", "logo.svg")
REQUIRED_WORK = ("brief.yaml", "concepts.yaml", "state.yaml")
PATTERN_FILES = (
    "01_hero_product.json",
    "02_lifestyle_scene.json",
    "03_promotional_poster.json",
    "04_feature_callout.json",
    "05_seasonal_campaign.json",
    "06_premium_minimal.json",
)
PATTERN_FIELDS = (
    "id",
    "name",
    "purpose",
    "use_when",
    "visual_goal",
    "composition_principles",
    "hierarchy_principles",
    "scene_guidance",
    "lighting_guidance",
    "selling_point_expression",
    "suitable_categories",
    "avoid",
)
CONCEPT_FIELDS = (
    "name",
    "concept",
    "key_visual_idea",
    "marketing_focus",
    "scene_direction",
    "selling_point_approach",
    "patterns",
)
STRATEGY_FIELDS = (
    "selected_concept",
    "key_visual_idea",
    "style_direction",
    "design_intent",
    "visual_priority",
    "scene_direction",
    "product_treatment",
    "selling_point_expression",
    "mood_and_light",
    "composition_direction",
    "brand_expression",
    "cta_direction",
    "information_strategy",
    "reference_guidance",
    "typography",
    "avoid",
    "composition_freedom",
)
ALLOWED_SELECTIONS = {"A", "B", "C"}
ALLOWED_METHODS = {"user", "auto"}
ALLOWED_STAGE_STATUS = {"not_started", "pending", "in_progress", "completed"}
ALLOWED_REFERENCE_MODES = {"same_category", "cross_category", "none"}
REFERENCE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
REQUIRED_DO_NOT_COPY = {
    "exact composition",
    "original brand identity",
    "original text",
    "original product form",
}


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


def require_mapping(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a mapping/object")
    return value


def require_list(value, label: str) -> list:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be a list")
    return value


def require_nonempty_text(value, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be non-empty text")
    return value


def resolve_skill_reference(
    value, label: str, allowed_root: Path, *, expect_directory: bool = False
) -> Path:
    text = require_nonempty_text(value, label)
    raw_path = Path(text)
    path = raw_path.resolve() if raw_path.is_absolute() else (SKILL_ROOT / raw_path).resolve()
    allowed_root = allowed_root.resolve()
    try:
        path.relative_to(allowed_root)
    except ValueError as exc:
        raise ValidationError(f"{label} must stay inside {allowed_root}") from exc

    if expect_directory:
        if not path.is_dir():
            raise ValidationError(f"{label} directory does not exist: {path}")
    elif not path.is_file():
        raise ValidationError(f"{label} file does not exist: {path}")
    return path


def require_path(data, dotted_path: str) -> None:
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValidationError(f"Missing structured field: {dotted_path}")
        current = current[part]


def stage_status(state: dict, stage: str) -> str:
    stage_data = require_mapping(state.get(stage), f"state.{stage}")
    status = stage_data.get("status")
    if status not in ALLOWED_STAGE_STATUS:
        raise ValidationError(f"state.{stage}.status is invalid: {status!r}")
    return status


def stage_started(status: str) -> bool:
    return status in {"in_progress", "completed"}


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


def validate_pattern_library() -> set[str]:
    patterns_dir = SKILL_ROOT / "references" / "patterns"
    pattern_ids: set[str] = set()
    for filename in PATTERN_FILES:
        path = patterns_dir / filename
        if not path.is_file():
            raise ValidationError(f"Missing Design Pattern: {path}")
        pattern = require_mapping(load_json(path), f"Pattern {filename}")
        for field in PATTERN_FIELDS:
            if field not in pattern:
                raise ValidationError(f"Pattern {filename} missing field: {field}")
        pattern_id = require_nonempty_text(pattern["id"], f"Pattern {filename}.id")
        if pattern_id in pattern_ids:
            raise ValidationError(f"Duplicate Pattern id: {pattern_id}")
        pattern_ids.add(pattern_id)
        for field in (
            "use_when",
            "composition_principles",
            "hierarchy_principles",
            "scene_guidance",
            "lighting_guidance",
            "selling_point_expression",
            "suitable_categories",
            "avoid",
        ):
            values = require_list(pattern[field], f"Pattern {filename}.{field}")
            if not values or not all(isinstance(item, str) and item.strip() for item in values):
                raise ValidationError(
                    f"Pattern {filename}.{field} must contain non-empty text items"
                )
        require_nonempty_text(pattern["name"], f"Pattern {filename}.name")
        require_nonempty_text(pattern["purpose"], f"Pattern {filename}.purpose")
        require_nonempty_text(pattern["visual_goal"], f"Pattern {filename}.visual_goal")

    actual_files = {path.name for path in patterns_dir.glob("*.json")}
    expected_files = set(PATTERN_FILES)
    if actual_files != expected_files:
        extra = sorted(actual_files - expected_files)
        missing = sorted(expected_files - actual_files)
        raise ValidationError(
            f"Pattern library must contain exactly six V2 JSON files; "
            f"extra={extra}, missing={missing}"
        )
    return pattern_ids


def validate_brief(brief: dict) -> None:
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
        "product_visual.category",
        "product_visual.dominant_colors",
        "product_visual.silhouette",
        "product_visual.visual_features",
        "product_visual.material_impression",
        "product_visual.protected_features",
    ):
        require_path(brief, field)

    product_visual = require_mapping(brief["product_visual"], "brief.product_visual")
    category = product_visual.get("category")
    if category is not None and not isinstance(category, str):
        raise ValidationError("brief.product_visual.category must be text or null")
    for field in (
        "dominant_colors",
        "silhouette",
        "visual_features",
        "material_impression",
        "protected_features",
    ):
        require_list(product_visual[field], f"brief.product_visual.{field}")


def validate_concepts(concepts_doc: dict, pattern_ids: set[str]) -> tuple[str | None, str | None]:
    concepts = require_mapping(concepts_doc.get("concepts"), "concepts.yaml concepts")
    if set(concepts) != ALLOWED_SELECTIONS:
        raise ValidationError("concepts.yaml must contain exactly A, B, and C")

    for concept_id in ("A", "B", "C"):
        concept = require_mapping(concepts[concept_id], f"concepts.{concept_id}")
        for field in CONCEPT_FIELDS:
            if field not in concept:
                raise ValidationError(f"concepts.{concept_id} missing field: {field}")
        for field in CONCEPT_FIELDS[:-1]:
            require_nonempty_text(concept[field], f"concepts.{concept_id}.{field}")
        selected_patterns = require_list(
            concept["patterns"], f"concepts.{concept_id}.patterns"
        )
        if not 1 <= len(selected_patterns) <= 3:
            raise ValidationError(
                f"concepts.{concept_id}.patterns must contain 1 to 3 Pattern ids"
            )
        if len(selected_patterns) != len(set(selected_patterns)):
            raise ValidationError(f"concepts.{concept_id}.patterns contains duplicates")
        unknown = [item for item in selected_patterns if item not in pattern_ids]
        if unknown:
            raise ValidationError(
                f"concepts.{concept_id}.patterns contains unknown ids: {unknown}"
            )

    recommendation = require_mapping(
        concepts_doc.get("recommendation"), "concepts.yaml recommendation"
    )
    recommended = recommendation.get("concept")
    if recommended not in ALLOWED_SELECTIONS:
        raise ValidationError("recommendation.concept must be A, B, or C")
    require_nonempty_text(recommendation.get("reason"), "recommendation.reason")

    selection = require_mapping(concepts_doc.get("selection"), "concepts.yaml selection")
    selected = selection.get("selected")
    method = selection.get("method")
    if selected not in ALLOWED_SELECTIONS | {None}:
        raise ValidationError("selection.selected must be A, B, C, or null")
    if method not in ALLOWED_METHODS | {None}:
        raise ValidationError("selection.method must be user, auto, or null")
    if selected is None and method is not None:
        raise ValidationError("selection.method must be null when no Concept is selected")
    if selected is not None and method is None:
        raise ValidationError("selection.method is required after Concept selection")
    if method == "auto" and selected != recommended:
        raise ValidationError(
            "AUTO selection must match recommendation.concept for traceability"
        )
    return selected, method


def validate_state(state: dict, selected: str | None, method: str | None) -> str:
    statuses = {
        stage: stage_status(state, stage)
        for stage in (
            "stage_0",
            "stage_1",
            "stage_2",
            "stage_3",
            "stage_4",
            "stage_5",
            "stage_6",
        )
    }

    checkpoint = require_mapping(
        state.get("concept_checkpoint"), "state.concept_checkpoint"
    )
    checkpoint_status = checkpoint.get("status")
    if checkpoint_status not in {"pending", "completed"}:
        raise ValidationError("state.concept_checkpoint.status must be pending or completed")
    if checkpoint.get("selected") != selected or checkpoint.get("method") != method:
        raise ValidationError(
            "state.concept_checkpoint must match concepts.yaml selection"
        )
    if checkpoint.get("choices") != ["A", "B", "C", "AUTO"]:
        raise ValidationError("Concept checkpoint choices must be exactly A/B/C/AUTO")
    if selected is None and checkpoint_status != "pending":
        raise ValidationError("Unselected Concept checkpoint must remain pending")
    if selected is not None and checkpoint_status != "completed":
        raise ValidationError("Selected Concept checkpoint must be completed")
    if checkpoint_status == "completed" and statuses["stage_1"] != "completed":
        raise ValidationError(
            "Concept Checkpoint cannot complete before Stage 1 is completed"
        )

    stage_2_status = statuses["stage_2"]
    if stage_started(stage_2_status):
        if (
            statuses["stage_1"] != "completed"
            or selected is None
            or method is None
            or checkpoint_status != "completed"
        ):
            raise ValidationError(
                "Stage 2 cannot start before Concept Selection is completed"
            )

    visual_checkpoint = require_mapping(
        state.get("visual_direction_checkpoint"),
        "state.visual_direction_checkpoint",
    )
    visual_checkpoint_status = visual_checkpoint.get("status")
    if visual_checkpoint_status not in {"pending", "completed"}:
        raise ValidationError(
            "state.visual_direction_checkpoint.status must be pending or completed"
    )
    confirmed = visual_checkpoint.get("confirmed")
    if confirmed is not None and not isinstance(confirmed, bool):
        raise ValidationError(
            "state.visual_direction_checkpoint.confirmed must be true, false, or null"
        )
    adjusted_fields = require_list(
        visual_checkpoint.get("adjusted_fields"),
        "state.visual_direction_checkpoint.adjusted_fields",
    )
    if not all(isinstance(item, str) and item.strip() for item in adjusted_fields):
        raise ValidationError(
            "state.visual_direction_checkpoint.adjusted_fields must contain text items"
        )
    if visual_checkpoint_status == "completed" and confirmed is not True:
        raise ValidationError(
            "Completed Visual Direction Checkpoint requires confirmed=true"
        )
    if confirmed is True and visual_checkpoint_status != "completed":
        raise ValidationError(
            "confirmed=true requires a completed Visual Direction Checkpoint"
        )
    if confirmed is True and stage_2_status != "completed":
        raise ValidationError(
            "Visual Direction Checkpoint cannot complete before Stage 2 is completed"
        )
    if stage_started(statuses["stage_3"]):
        if (
            stage_2_status != "completed"
            or visual_checkpoint_status != "completed"
            or confirmed is not True
        ):
            raise ValidationError(
                "Stage 3 cannot start before Visual Direction Checkpoint is confirmed"
            )
    if stage_started(statuses["stage_4"]) and statuses["stage_3"] != "completed":
        raise ValidationError("Stage 4 cannot start before Stage 3 is completed")
    if statuses["stage_3"] == "completed" and statuses["stage_4"] == "not_started":
        raise ValidationError("Completed Stage 3 must proceed to Stage 4")

    stage_5 = require_mapping(state.get("stage_5"), "state.stage_5")
    expected_choices = {
        "A": "接受当前结果",
        "B": "根据问题继续迭代",
        "C": "商品或 Logo 失真，使用原始资产恢复",
    }
    if stage_5.get("choices") != expected_choices:
        raise ValidationError("Stage 5 choices must be exactly the V2 A/B/C options")
    stage_5_decision = stage_5.get("decision")
    if stage_5_decision not in ALLOWED_SELECTIONS | {None}:
        raise ValidationError("state.stage_5.decision must be A, B, C, or null")
    if stage_5_decision is not None and statuses["stage_5"] != "completed":
        raise ValidationError("A Stage 5 decision requires stage_5.status=completed")
    if statuses["stage_5"] == "completed" and stage_5_decision is None:
        raise ValidationError("Completed Stage 5 requires decision A, B, or C")
    if stage_started(statuses["stage_5"]) and statuses["stage_4"] != "completed":
        raise ValidationError("Stage 5 cannot start before Stage 4 is completed")
    if statuses["stage_4"] == "completed" and statuses["stage_5"] == "not_started":
        raise ValidationError("Completed Stage 4 must proceed to Stage 5 Final Check")
    if stage_started(statuses["stage_6"]):
        if statuses["stage_5"] != "completed" or stage_5_decision != "A":
            raise ValidationError(
                "Stage 6 cannot start before Stage 5 explicitly selects A"
            )
    return stage_2_status


def find_forbidden_layout_keys(value, path: str = "layout") -> list[str]:
    forbidden = {"x", "y", "font_size", "max_width", "max_height", "safe_margin"}
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in forbidden:
                found.append(child_path)
            found.extend(find_forbidden_layout_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_layout_keys(child, f"{path}[{index}]"))
    return found


def validate_stage_2_outputs(
    work_dir: Path, selected: str | None, concepts_doc: dict
) -> None:
    strategy_path = work_dir / "visual_strategy.yaml"
    layout_path = work_dir / "layout.json"
    if not strategy_path.is_file() or not layout_path.is_file():
        raise ValidationError(
            "Stage 2 requires work/visual_strategy.yaml and work/layout.json"
        )

    strategy = require_mapping(load_yaml(strategy_path), "visual_strategy.yaml")
    for field in STRATEGY_FIELDS:
        if field not in strategy:
            raise ValidationError(f"visual_strategy.yaml missing field: {field}")
    selected_concept = require_mapping(
        strategy["selected_concept"], "visual_strategy.selected_concept"
    )
    if selected_concept.get("id") != selected:
        raise ValidationError(
            "visual_strategy.selected_concept.id must match concepts selection"
        )
    selected_name = concepts_doc["concepts"][selected]["name"]
    if selected_concept.get("name") != selected_name:
        raise ValidationError(
            "visual_strategy.selected_concept.name must match concepts.yaml"
        )
    key_visual_idea = require_nonempty_text(
        strategy.get("key_visual_idea"), "visual_strategy.key_visual_idea"
    )
    if key_visual_idea != concepts_doc["concepts"][selected]["key_visual_idea"]:
        raise ValidationError(
            "visual_strategy.key_visual_idea must match the selected Concept"
        )

    style_direction = require_mapping(
        strategy.get("style_direction"), "visual_strategy.style_direction"
    )
    require_nonempty_text(
        style_direction.get("primary_style"),
        "visual_strategy.style_direction.primary_style",
    )
    product_brand_alignment = require_list(
        style_direction.get("product_brand_alignment"),
        "visual_strategy.style_direction.product_brand_alignment",
    )
    if not product_brand_alignment or not all(
        isinstance(item, str) and item.strip() for item in product_brand_alignment
    ):
        raise ValidationError(
            "visual_strategy.style_direction.product_brand_alignment must contain text items"
        )
    secondary_mood = require_list(
        style_direction.get("secondary_mood"),
        "visual_strategy.style_direction.secondary_mood",
    )
    if not all(isinstance(item, str) and item.strip() for item in secondary_mood):
        raise ValidationError(
            "visual_strategy.style_direction.secondary_mood must contain text items"
        )
    require_nonempty_text(
        style_direction.get("rationale"),
        "visual_strategy.style_direction.rationale",
    )
    style_avoid = require_list(
        style_direction.get("avoid"), "visual_strategy.style_direction.avoid"
    )
    if not all(isinstance(item, str) and item.strip() for item in style_avoid):
        raise ValidationError(
            "visual_strategy.style_direction.avoid must contain text items"
        )

    information_strategy = require_mapping(
        strategy.get("information_strategy"), "visual_strategy.information_strategy"
    )
    if information_strategy.get("density") != "low_or_moderate":
        raise ValidationError(
            "visual_strategy.information_strategy.density must be low_or_moderate"
        )
    if information_strategy.get("secondary_information_treatment") != "subordinate":
        raise ValidationError(
            "visual_strategy.information_strategy.secondary_information_treatment "
            "must be subordinate"
        )

    reference_guidance = require_mapping(
        strategy.get("reference_guidance"), "visual_strategy.reference_guidance"
    )
    reference_mode = reference_guidance.get("mode")
    if reference_mode not in ALLOWED_REFERENCE_MODES:
        raise ValidationError(
            "visual_strategy.reference_guidance.mode must be "
            "same_category, cross_category, or none"
        )
    selected_references = require_list(
        reference_guidance.get("selected"),
        "visual_strategy.reference_guidance.selected",
    )
    if len(selected_references) > 2:
        raise ValidationError(
            "visual_strategy.reference_guidance.selected may contain at most 2 images"
        )
    if not all(isinstance(item, str) and item.strip() for item in selected_references):
        raise ValidationError(
            "visual_strategy.reference_guidance.selected must contain path strings"
        )
    if len(selected_references) != len(set(selected_references)):
        raise ValidationError(
            "visual_strategy.reference_guidance.selected contains duplicates"
        )
    if reference_mode == "none" and selected_references:
        raise ValidationError(
            "reference_guidance.selected must be empty when mode is none"
        )
    if reference_mode != "none" and not selected_references:
        raise ValidationError(
            "same_category or cross_category requires at least 1 selected image"
        )
    style_reference_root = SKILL_ROOT / "references" / "风格案例图"
    for index, value in enumerate(selected_references):
        path = resolve_skill_reference(
            value,
            f"visual_strategy.reference_guidance.selected[{index}]",
            style_reference_root,
        )
        if path.suffix.lower() not in REFERENCE_IMAGE_EXTENSIONS:
            raise ValidationError(
                f"Style reference must be JPG, JPEG, or PNG: {path}"
            )

    learn_from = require_list(
        reference_guidance.get("learn_from"),
        "visual_strategy.reference_guidance.learn_from",
    )
    if not all(isinstance(item, str) and item.strip() for item in learn_from):
        raise ValidationError("reference_guidance.learn_from must contain text items")
    if reference_mode != "none" and not learn_from:
        raise ValidationError(
            "Selected style references require at least one learn_from principle"
        )
    do_not_copy = require_list(
        reference_guidance.get("do_not_copy"),
        "visual_strategy.reference_guidance.do_not_copy",
    )
    if not all(isinstance(item, str) and item.strip() for item in do_not_copy):
        raise ValidationError("reference_guidance.do_not_copy must contain text items")
    missing_constraints = sorted(REQUIRED_DO_NOT_COPY - set(do_not_copy))
    if missing_constraints:
        raise ValidationError(
            "reference_guidance.do_not_copy missing required constraints: "
            + ", ".join(missing_constraints)
        )

    typography = require_mapping(
        strategy.get("typography"), "visual_strategy.typography"
    )
    require_nonempty_text(
        typography.get("headline_direction"),
        "visual_strategy.typography.headline_direction",
    )
    characteristics = require_list(
        typography.get("characteristics"),
        "visual_strategy.typography.characteristics",
    )
    if not characteristics or not all(
        isinstance(item, str) and item.strip() for item in characteristics
    ):
        raise ValidationError(
            "visual_strategy.typography.characteristics must contain text items"
        )
    require_nonempty_text(
        typography.get("rationale"), "visual_strategy.typography.rationale"
    )
    require_nonempty_text(
        typography.get("imagegen_instruction"),
        "visual_strategy.typography.imagegen_instruction",
    )
    use_preview = typography.get("use_preview_as_image_reference")
    if not isinstance(use_preview, bool):
        raise ValidationError(
            "visual_strategy.typography.use_preview_as_image_reference must be boolean"
        )
    font_reference_root = SKILL_ROOT / "references" / "手写合集字体"
    font_source = typography.get("selected_source")
    if font_source is not None:
        resolve_skill_reference(
            font_source,
            "visual_strategy.typography.selected_source",
            font_reference_root,
            expect_directory=True,
        )
    if use_preview and font_source is None:
        raise ValidationError(
            "Typography preview reference requires a selected_source directory"
        )
    if strategy.get("composition_freedom") != "high":
        raise ValidationError("visual_strategy composition_freedom must be high")

    layout = require_mapping(load_json(layout_path), "layout.json")
    for field in (
        "canvas",
        "hierarchy",
        "major_visual_regions",
        "preferred_relationships",
        "composition",
        "safe_areas",
        "asset_protection",
        "composition_freedom",
    ):
        if field not in layout:
            raise ValidationError(f"layout.json missing field: {field}")
    canvas = require_mapping(layout["canvas"], "layout.canvas")
    for field in ("ratio", "width", "height"):
        if field not in canvas:
            raise ValidationError(f"layout.canvas missing field: {field}")
    require_list(layout["hierarchy"], "layout.hierarchy")
    require_mapping(layout["major_visual_regions"], "layout.major_visual_regions")
    require_mapping(layout["preferred_relationships"], "layout.preferred_relationships")
    composition = require_mapping(layout["composition"], "layout.composition")
    require_nonempty_text(
        composition.get("primary_archetype"),
        "layout.composition.primary_archetype",
    )
    secondary_device = composition.get("secondary_device")
    if secondary_device is not None:
        require_nonempty_text(
            secondary_device, "layout.composition.secondary_device"
        )
    for field in (
        "visual_flow",
        "product_placement_logic",
        "text_product_relationship",
        "distinctive_device",
    ):
        require_nonempty_text(
            composition.get(field), f"layout.composition.{field}"
        )
    if not isinstance(composition.get("avoid_default_stack"), bool):
        raise ValidationError(
            "layout.composition.avoid_default_stack must be boolean"
        )
    require_list(layout["safe_areas"], "layout.safe_areas")
    require_list(layout["asset_protection"], "layout.asset_protection")
    if layout.get("composition_freedom") != "high":
        raise ValidationError("layout.json composition_freedom must be high")
    forbidden = find_forbidden_layout_keys(layout)
    if forbidden:
        raise ValidationError(
            "layout.json contains pixel-style positioning keys: " + ", ".join(forbidden)
        )


def validate_work(project: Path) -> list[str]:
    work_dir = project / "work"
    for name in REQUIRED_WORK:
        path = work_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValidationError(f"Missing or empty work file: {path}")

    pattern_ids = validate_pattern_library()
    brief = require_mapping(load_yaml(work_dir / "brief.yaml"), "brief.yaml")
    concepts_doc = require_mapping(
        load_yaml(work_dir / "concepts.yaml"), "concepts.yaml"
    )
    state = require_mapping(load_yaml(work_dir / "state.yaml"), "state.yaml")

    validate_brief(brief)
    selected, method = validate_concepts(concepts_doc, pattern_ids)
    stage_2_status = validate_state(state, selected, method)
    stage_2_message = "Stage 2 outputs are correctly deferred until Concept Selection"
    if stage_started(stage_2_status):
        validate_stage_2_outputs(work_dir, selected, concepts_doc)
        stage_2_message = "Art Direction and layout are valid for the selected Concept"

    return [
        "Brief includes structured product_visual analysis",
        "Concepts A/B/C, recommendation, and selection are valid",
        "Concept and Visual Direction checkpoints are consistent",
        stage_2_message,
        "Key Visual, Style, Composition, Typography, and optional references are valid",
        "All six Design Pattern JSON files parsed successfully",
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

    brief = require_mapping(load_yaml(project / "work" / "brief.yaml"), "brief.yaml")
    layout = require_mapping(load_json(project / "work" / "layout.json"), "layout.json")
    expected_ratio = parse_ratio(
        brief.get("deliverables", {}).get("canvas", {}).get("ratio")
    )
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
