from app.rules import evaluate_answers


def test_exception_applies_for_property_related_item() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "court_judgment",
            "amount_won": 1_000,
            "area_sqm": 1,
        },
        {},
    )
    assert result.final_decision == "심의/관리계획 제외"


def test_exception_ignored_for_non_property_related_item() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "행정재산의 용도변경·폐지",
            "exception_reason_code": "court_judgment",
        },
        {},
    )
    assert result.final_decision == "심의"


def test_exception_disabled_for_plan_change_item() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산관리계획 수립 후 취득·처분 대상 공유재산의 위치 변경",
            "exception_reason_code": "court_judgment",
        },
        {},
    )
    assert result.final_decision == "심의 + 관리계획 변경 수립"


def test_acquisition_plan_setup_by_amount() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 1_000_000_000,
            "area_sqm": 100,
        },
        {},
    )
    assert result.final_decision == "심의 + 관리계획 수립"


def test_acquisition_plan_setup_by_area() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 10_000_000,
            "area_sqm": 1000,
        },
        {},
    )
    assert result.final_decision == "심의 + 관리계획 수립"


def test_acquisition_deliberation_by_amount() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 50_000_001,
            "area_sqm": 999,
        },
        {},
    )
    assert result.final_decision == "심의"


def test_acquisition_non_target() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 50_000_000,
            "area_sqm": 999,
        },
        {},
    )
    assert result.final_decision == "심의 비대상"


def test_disposal_plan_setup_by_area() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 처분",
            "exception_reason_code": "none",
            "amount_won": 10_000_000,
            "area_sqm": 2000,
        },
        {},
    )
    assert result.final_decision == "심의 + 관리계획 수립"


def test_plan_change_item() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산관리계획 수립 후 취득·처분 대상 공유재산의 위치 변경",
            "exception_reason_code": "none",
        },
        {},
    )
    assert result.final_decision == "심의 + 관리계획 변경 수립"


def test_unknown_item_is_non_target() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "알 수 없는 항목",
            "exception_reason_code": "none",
        },
        {},
    )
    assert result.final_decision == "심의 비대상"


def test_amount_threshold_override_changes_decision() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 100_000_000,
            "area_sqm": 100,
        },
        {
            "amount_threshold": 100_000_000,
            "acquisition_area_threshold": 1000,
            "disposal_area_threshold": 2000,
            "seosan_private_sale_threshold": 50_000_000,
        },
    )
    assert result.final_decision == "심의 + 관리계획 수립"


def test_disposal_area_threshold_override_changes_decision() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 처분",
            "exception_reason_code": "none",
            "amount_won": 10_000_000,
            "area_sqm": 1500,
        },
        {
            "amount_threshold": 1_000_000_000,
            "acquisition_area_threshold": 1000,
            "disposal_area_threshold": 1500,
            "seosan_private_sale_threshold": 50_000_000,
        },
    )
    assert result.final_decision == "심의 + 관리계획 수립"


def test_private_sale_threshold_override_changes_decision() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 10_000_001,
            "area_sqm": 10,
        },
        {
            "amount_threshold": 1_000_000_000,
            "acquisition_area_threshold": 1000,
            "disposal_area_threshold": 2000,
            "seosan_private_sale_threshold": 10_000_000,
        },
    )
    assert result.final_decision == "심의"


def test_invalid_config_values_fall_back_to_defaults() -> None:
    result = evaluate_answers(
        {
            "selected_rule_item": "공유재산의 취득",
            "exception_reason_code": "none",
            "amount_won": 50_000_000,
            "area_sqm": 999,
        },
        {
            "amount_threshold": "bad",
            "acquisition_area_threshold": -1,
            "disposal_area_threshold": None,
            "seosan_private_sale_threshold": 0,
        },
    )
    assert result.final_decision == "심의 비대상"
