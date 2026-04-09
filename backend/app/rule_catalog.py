from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from .rule_catalog_loader import load_catalog

DecisionType = Literal[
    "심의/관리계획 제외",
    "심의 + 관리계획 변경 수립",
    "심의 + 관리계획 수립",
    "심의",
    "심의 비대상",
]

RuleGroup = Literal["plan_change", "plan_setup", "deliberation"]


@dataclass(frozen=True)
class SourceRuleItem:
    label: str
    group: RuleGroup
    laws: list[str]


_catalog = load_catalog("SEOSAN")
CATALOG_THRESHOLDS: dict[str, float] = _catalog.thresholds

SOURCE_RULE_ITEMS: list[SourceRuleItem] = [
    SourceRuleItem(
        label=item.label,
        group=cast(RuleGroup, item.group),
        laws=item.laws,
    )
    for item in _catalog.source_rule_items
]

EXCEPTION_REASON_OPTIONS: list[tuple[str, str]] = _catalog.exception_reason_options

LABEL_TO_ITEM: dict[str, SourceRuleItem] = {item.label: item for item in SOURCE_RULE_ITEMS}

_EXCEPTION_ENABLED_ITEMS = {"공유재산의 취득", "공유재산의 처분"}


def is_property_related_label(label: str) -> bool:
    return label in _EXCEPTION_ENABLED_ITEMS


def decision_for_group(group: RuleGroup) -> DecisionType:
    if group == "plan_change":
        return "심의 + 관리계획 변경 수립"
    if group == "plan_setup":
        return "심의 + 관리계획 수립"
    return "심의"
