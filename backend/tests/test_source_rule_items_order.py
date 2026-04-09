from app.main import _serialize_source_rule_items
from app.rule_catalog import SourceRuleItem


def test_serialize_source_rule_items_keeps_input_order() -> None:
    items = [
        SourceRuleItem(
            label="B 항목",
            group="plan_change",
            laws=["법령 B"],
        ),
        SourceRuleItem(
            label="A 항목",
            group="deliberation",
            laws=["법령 A"],
        ),
        SourceRuleItem(
            label="C 항목",
            group="plan_setup",
            laws=["법령 C"],
        ),
    ]

    serialized = _serialize_source_rule_items(items)

    assert [item.label for item in serialized] == ["B 항목", "A 항목", "C 항목"]
