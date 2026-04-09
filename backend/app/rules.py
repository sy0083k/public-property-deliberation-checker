from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .rule_catalog import LABEL_TO_ITEM, decision_for_group, is_property_related_label

DecisionType = Literal[
    "심의/관리계획 제외",
    "심의 + 관리계획 변경 수립",
    "심의 + 관리계획 수립",
    "심의",
    "심의 비대상",
]


@dataclass
class RuleResult:
    final_decision: DecisionType
    final_reason: str
    trace: list[dict[str, Any]]


DEFAULT_THRESHOLDS = {
    "amount_threshold": 1_000_000_000,
    "acquisition_area_threshold": 1000,
    "disposal_area_threshold": 2000,
    "seosan_private_sale_threshold": 50_000_000,
}


def _to_float(answers: dict[str, Any], key: str) -> float:
    value = answers.get(key, 0)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number > 0 else 0.0


def _get_positive_float(config: dict[str, Any], key: str, default: float) -> float:
    value = config.get(key, default)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def evaluate_answers(answers: dict[str, Any], config: dict[str, Any]) -> RuleResult:
    selected_rule_item = str(answers.get("selected_rule_item", "") or "")
    exception_reason_code = str(answers.get("exception_reason_code", "none") or "none")
    amount_won = _to_float(answers, "amount_won")
    area_sqm = _to_float(answers, "area_sqm")
    amount_threshold = _get_positive_float(
        config, "amount_threshold", float(DEFAULT_THRESHOLDS["amount_threshold"])
    )
    acquisition_area_threshold = _get_positive_float(
        config, "acquisition_area_threshold", float(DEFAULT_THRESHOLDS["acquisition_area_threshold"])
    )
    disposal_area_threshold = _get_positive_float(
        config, "disposal_area_threshold", float(DEFAULT_THRESHOLDS["disposal_area_threshold"])
    )
    private_sale_threshold = _get_positive_float(
        config,
        "seosan_private_sale_threshold",
        float(DEFAULT_THRESHOLDS["seosan_private_sale_threshold"]),
    )

    trace: list[dict[str, Any]] = []

    is_property_related = is_property_related_label(selected_rule_item)
    exception_applied = is_property_related and exception_reason_code != "none"

    trace.append(
        {
            "step_key": "D1",
            "prompt": "예외 적용 여부",
            "decision": "예외 적용" if exception_applied else "예외 미적용",
            "snapshot": {
                "selected_rule_item": selected_rule_item,
                "is_property_related": is_property_related,
                "exception_reason_code": exception_reason_code,
            },
        }
    )

    if exception_applied:
        return RuleResult("심의/관리계획 제외", "예외 사유가 적용되어 심의/관리계획 대상에서 제외됩니다.", trace)

    if selected_rule_item == "공유재산의 취득":
        trace.append(
            {
                "step_key": "D2",
                "prompt": "취득 수치 판정",
                "decision": "수치 판정",
                "snapshot": {
                    "amount_won": amount_won,
                    "area_sqm": area_sqm,
                    "amount_threshold": amount_threshold,
                    "acquisition_area_threshold": acquisition_area_threshold,
                    "seosan_private_sale_threshold": private_sale_threshold,
                },
            }
        )
        if amount_won >= amount_threshold or area_sqm >= acquisition_area_threshold:
            return RuleResult("심의 + 관리계획 수립", "취득 기준(10억원 이상 또는 1,000㎡ 이상)에 해당합니다.", trace)
        if amount_won > private_sale_threshold:
            return RuleResult("심의", "취득 기준(5천만원 초과)에 해당합니다.", trace)
        return RuleResult("심의 비대상", "취득 기준에 해당하지 않습니다.", trace)

    if selected_rule_item == "공유재산의 처분":
        trace.append(
            {
                "step_key": "D2",
                "prompt": "처분 수치 판정",
                "decision": "수치 판정",
                "snapshot": {
                    "amount_won": amount_won,
                    "area_sqm": area_sqm,
                    "amount_threshold": amount_threshold,
                    "disposal_area_threshold": disposal_area_threshold,
                    "seosan_private_sale_threshold": private_sale_threshold,
                },
            }
        )
        if amount_won >= amount_threshold or area_sqm >= disposal_area_threshold:
            return RuleResult("심의 + 관리계획 수립", "처분 기준(10억원 이상 또는 2,000㎡ 이상)에 해당합니다.", trace)
        if amount_won > private_sale_threshold:
            return RuleResult("심의", "처분 기준(5천만원 초과)에 해당합니다.", trace)
        return RuleResult("심의 비대상", "처분 기준에 해당하지 않습니다.", trace)

    mapped = LABEL_TO_ITEM.get(selected_rule_item)
    if mapped is None:
        trace.append(
            {
                "step_key": "D2",
                "prompt": "원문 항목 해석",
                "decision": "매핑 없음",
                "snapshot": {"selected_rule_item": selected_rule_item},
            }
        )
        return RuleResult("심의 비대상", "원문 항목 매핑이 없어 심의 비대상으로 처리합니다.", trace)

    final_decision = decision_for_group(mapped.group)
    trace.append(
        {
            "step_key": "D2",
            "prompt": "원문 항목 해석",
            "decision": mapped.group,
            "snapshot": {
                "selected_rule_item": selected_rule_item,
                "resolved_group": mapped.group,
            },
        }
    )

    reason_map = {
        "심의 + 관리계획 변경 수립": "원문 항목이 관리계획 변경 수립 대상에 해당합니다.",
        "심의 + 관리계획 수립": "원문 항목이 관리계획 수립 대상에 해당합니다.",
        "심의": "원문 항목이 심의 대상에 해당합니다.",
    }
    return RuleResult(final_decision, reason_map[final_decision], trace)
