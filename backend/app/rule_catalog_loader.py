from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CATALOG_SCHEMA_VERSION = 1
ALLOWED_GROUPS = {"deliberation", "plan_setup", "plan_change"}
CATALOGS_DIR = Path(__file__).resolve().parent.parent / "rules" / "catalogs"


@dataclass(frozen=True)
class CatalogRuleItem:
    label: str
    group: str
    laws: list[str]


@dataclass(frozen=True)
class CatalogData:
    municipality_code: str
    thresholds: dict[str, float]
    source_rule_items: list[CatalogRuleItem]
    exception_reason_options: list[tuple[str, str]]


def load_catalog(municipality_code: str) -> CatalogData:
    code = str(municipality_code).strip()
    if not code:
        raise ValueError("Catalog validation failed: municipality_code must be a non-empty string.")

    path = CATALOGS_DIR / f"{code}.yaml"
    if not path.exists():
        raise ValueError(f"Catalog validation failed: {path} does not exist.")

    with path.open("r", encoding="utf-8") as handle:
        parsed = yaml.safe_load(handle)

    if not isinstance(parsed, dict):
        raise ValueError(f"Catalog validation failed: {path}: root must be a mapping.")

    _validate_schema_version(parsed, path)
    file_code = _require_non_empty_str(parsed, "municipality_code", path)
    if file_code != code:
        raise ValueError(
            f"Catalog validation failed: {path}: municipality_code '{file_code}' does not match requested '{code}'."
        )

    source_rule_items = _validate_source_rule_items(parsed, path)
    exception_reason_options = _validate_exception_reason_options(parsed, path)
    thresholds = _validate_thresholds(parsed, path)

    return CatalogData(
        municipality_code=file_code,
        thresholds=thresholds,
        source_rule_items=source_rule_items,
        exception_reason_options=exception_reason_options,
    )


def _validate_schema_version(parsed: dict[str, Any], path: Path) -> None:
    value = parsed.get("schema_version")
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"Catalog validation failed: {path}: schema_version must be an integer.")
    if value != CATALOG_SCHEMA_VERSION:
        raise ValueError(
            f"Catalog validation failed: {path}: schema_version must be {CATALOG_SCHEMA_VERSION}, got {value}."
        )


def _validate_source_rule_items(parsed: dict[str, Any], path: Path) -> list[CatalogRuleItem]:
    value = parsed.get("source_rule_items")
    if not isinstance(value, list) or not value:
        raise ValueError(f"Catalog validation failed: {path}: source_rule_items must be a non-empty list.")

    result: list[CatalogRuleItem] = []
    labels: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(
                f"Catalog validation failed: {path}: source_rule_items[{index}] must be a mapping."
            )

        label = _require_non_empty_str(item, "label", path, f"source_rule_items[{index}]")
        group = _require_non_empty_str(item, "group", path, f"source_rule_items[{index}]")
        if group not in ALLOWED_GROUPS:
            allowed = ", ".join(sorted(ALLOWED_GROUPS))
            raise ValueError(
                f"Catalog validation failed: {path}: source_rule_items[{index}].group "
                f"must be one of [{allowed}], got '{group}'."
            )

        if label in labels:
            raise ValueError(
                f"Catalog validation failed: {path}: duplicated source_rule_items label '{label}'."
            )
        labels.add(label)
        laws_raw = item.get("laws")
        if not isinstance(laws_raw, list) or not laws_raw:
            raise ValueError(
                f"Catalog validation failed: {path}: source_rule_items[{index}].laws "
                "must be a non-empty list."
            )
        laws: list[str] = []
        for law_index, law in enumerate(laws_raw):
            if not isinstance(law, str) or not law.strip():
                raise ValueError(
                    f"Catalog validation failed: {path}: source_rule_items[{index}].laws[{law_index}] "
                    "must be a non-empty string."
                )
            laws.append(law.strip())

        result.append(CatalogRuleItem(label=label, group=group, laws=laws))

    return result


def _validate_exception_reason_options(parsed: dict[str, Any], path: Path) -> list[tuple[str, str]]:
    value = parsed.get("exception_reason_options")
    if not isinstance(value, list):
        raise ValueError(f"Catalog validation failed: {path}: exception_reason_options must be a list.")

    result: list[tuple[str, str]] = []
    codes: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(
                f"Catalog validation failed: {path}: exception_reason_options[{index}] must be a mapping."
            )

        code = _require_non_empty_str(item, "code", path, f"exception_reason_options[{index}]")
        label = _require_non_empty_str(item, "label", path, f"exception_reason_options[{index}]")
        if code in codes:
            raise ValueError(
                f"Catalog validation failed: {path}: duplicated exception_reason_options code '{code}'."
            )
        codes.add(code)
        result.append((code, label))

    return result

def _validate_thresholds(parsed: dict[str, Any], path: Path) -> dict[str, float]:
    value = parsed.get("thresholds")
    if not isinstance(value, dict):
        raise ValueError(f"Catalog validation failed: {path}: thresholds must be a mapping.")

    required_keys = (
        "acquisition_amount_threshold",
        "disposal_amount_threshold",
        "acquisition_area_threshold",
        "disposal_area_threshold",
        "seosan_private_sale_threshold",
    )

    result: dict[str, float] = {}
    for key in required_keys:
        raw = value.get(key)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError(
                f"Catalog validation failed: {path}: thresholds.{key} must be a positive number."
            )
        number = float(raw)
        if number <= 0:
            raise ValueError(
                f"Catalog validation failed: {path}: thresholds.{key} must be a positive number."
            )
        result[key] = number

    return result


def _require_non_empty_str(
    values: dict[str, Any],
    key: str,
    path: Path,
    prefix: str | None = None,
) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip():
        key_name = f"{prefix}.{key}" if prefix else key
        raise ValueError(f"Catalog validation failed: {path}: {key_name} must be a non-empty string.")
    return value.strip()
