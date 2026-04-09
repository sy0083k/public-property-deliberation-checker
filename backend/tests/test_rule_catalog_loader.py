from pathlib import Path

import pytest

from app import rule_catalog_loader as loader


def _write_catalog(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def _base_yaml(source_rule_items: str) -> str:
    return f"""
schema_version: 1
municipality_code: SEOSAN
thresholds:
  acquisition_amount_threshold: 1000000000
  disposal_amount_threshold: 1000000000
  acquisition_area_threshold: 1000
  disposal_area_threshold: 2000
  seosan_private_sale_threshold: 50000000
source_rule_items:
{source_rule_items}
exception_reason_options:
  - code: none
    label: 해당 없음
""".strip()


def test_load_catalog_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        _base_yaml(
            """
  - label: 공유재산의 취득
    group: deliberation
    laws:
      - 공유재산 및 물품 관리법 제16조
""".rstrip()
        ),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    catalog = loader.load_catalog("SEOSAN")

    assert catalog.municipality_code == "SEOSAN"
    assert catalog.source_rule_items[0].group == "deliberation"
    assert catalog.source_rule_items[0].laws == ["공유재산 및 물품 관리법 제16조"]
    assert catalog.exception_reason_options[0] == ("none", "해당 없음")


def test_load_catalog_rejects_invalid_group(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        _base_yaml(
            """
  - label: 공유재산의 취득
    group: wrong_group
    laws:
      - 공유재산 및 물품 관리법 제16조
""".rstrip()
        ),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="group"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_duplicated_label(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        _base_yaml(
            """
  - label: 공유재산의 취득
    group: deliberation
    laws:
      - 공유재산 및 물품 관리법 제16조
  - label: 공유재산의 취득
    group: plan_change
    laws:
      - 공유재산 및 물품 관리법 시행령 제7조의2
""".rstrip()
        ),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="duplicated source_rule_items label"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_missing_required_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        """
schema_version: 1
municipality_code: SEOSAN
thresholds:
  acquisition_amount_threshold: 1000000000
  disposal_amount_threshold: 1000000000
  acquisition_area_threshold: 1000
  disposal_area_threshold: 2000
  seosan_private_sale_threshold: 50000000
exception_reason_options:
  - code: none
    label: 해당 없음
""".strip(),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="source_rule_items"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_duplicated_exception_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        """
schema_version: 1
municipality_code: SEOSAN
thresholds:
  acquisition_amount_threshold: 1000000000
  disposal_amount_threshold: 1000000000
  acquisition_area_threshold: 1000
  disposal_area_threshold: 2000
  seosan_private_sale_threshold: 50000000
source_rule_items:
  - label: 공유재산의 취득
    group: deliberation
    laws:
      - 공유재산 및 물품 관리법 제16조
exception_reason_options:
  - code: none
    label: 해당 없음
  - code: none
    label: 중복
""".strip(),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="duplicated exception_reason_options code"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_wrong_schema_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        """
schema_version: 2
municipality_code: SEOSAN
thresholds:
  acquisition_amount_threshold: 1000000000
  disposal_amount_threshold: 1000000000
  acquisition_area_threshold: 1000
  disposal_area_threshold: 2000
  seosan_private_sale_threshold: 50000000
source_rule_items:
  - label: 공유재산의 취득
    group: deliberation
    laws:
      - 공유재산 및 물품 관리법 제16조
exception_reason_options:
  - code: none
    label: 해당 없음
""".strip(),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="schema_version"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="does not exist"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_missing_thresholds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        """
schema_version: 1
municipality_code: SEOSAN
source_rule_items:
  - label: 공유재산의 취득
    group: deliberation
    laws:
      - 공유재산 및 물품 관리법 제16조
exception_reason_options:
  - code: none
    label: 해당 없음
""".strip(),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="thresholds"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_invalid_threshold_value(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        """
schema_version: 1
municipality_code: SEOSAN
thresholds:
  acquisition_amount_threshold: 0
  disposal_amount_threshold: 1000000000
  acquisition_area_threshold: 1000
  disposal_area_threshold: 2000
  seosan_private_sale_threshold: 50000000
source_rule_items:
  - label: 공유재산의 취득
    group: deliberation
    laws:
      - 공유재산 및 물품 관리법 제16조
exception_reason_options:
  - code: none
    label: 해당 없음
""".strip(),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="thresholds.acquisition_amount_threshold"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_missing_laws(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        _base_yaml(
            """
  - label: 공유재산의 취득
    group: deliberation
""".rstrip()
        ),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="laws"):
        loader.load_catalog("SEOSAN")


def test_load_catalog_rejects_empty_laws(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_catalog(
        tmp_path / "SEOSAN.yaml",
        _base_yaml(
            """
  - label: 공유재산의 취득
    group: deliberation
    laws: []
""".rstrip()
        ),
    )
    monkeypatch.setattr(loader, "CATALOGS_DIR", tmp_path)

    with pytest.raises(ValueError, match="laws"):
        loader.load_catalog("SEOSAN")
