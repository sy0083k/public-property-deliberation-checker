from pathlib import Path
import tempfile

from fastapi.testclient import TestClient

from app.main import create_app


def test_api_flow() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test_api.db"
        app = create_app(f"sqlite+pysqlite:///{db_path}")
        client = TestClient(app)

        created = client.post(
            "/api/v1/diagnoses",
            json={
                "department": "재산관리과",
                "project_name": "청사 부지 취득",
                "manager_name": "홍길동",
                "admin_phone": "041-000-0000",
                "municipality_code": "SEOSAN",
            },
        )
        assert created.status_code == 200
        created_body = created.json()
        assert created_body["project_name"] == "청사 부지 취득"
        assert created_body["manager_name"] == "홍길동"
        assert created_body["admin_phone"] == "041-000-0000"
        case_id = created_body["id"]

        answered = client.post(
            f"/api/v1/diagnoses/{case_id}/answers",
            json={
                "answers": [
                    {"question_code": "selected_rule_item", "value": "공유재산의 취득"},
                    {"question_code": "exception_reason_code", "value": "none"},
                    {"question_code": "amount_won", "value": 1_000_000_000},
                    {"question_code": "area_sqm", "value": 500},
                ]
            },
        )
        assert answered.status_code == 200

        evaluated = client.post(f"/api/v1/diagnoses/{case_id}/evaluate")
        assert evaluated.status_code == 200
        assert evaluated.json()["final_decision"] == "심의 + 관리계획 수립"

        got = client.get(f"/api/v1/diagnoses/{case_id}")
        assert got.status_code == 200
        got_body = got.json()
        assert got_body["final_decision"] == "심의 + 관리계획 수립"
        assert got_body["created_at"].endswith("+09:00")

        listed = client.get("/api/v1/diagnoses", params={"department": "재산관리과"})
        assert listed.status_code == 200
        items = listed.json()["items"]
        assert len(items) == 1
        assert items[0]["project_name"] == "청사 부지 취득"
        assert items[0]["manager_name"] == "홍길동"
        assert items[0]["admin_phone"] == "041-000-0000"

        profiles = client.get("/api/v1/rule-profiles")
        assert profiles.status_code == 200
        assert profiles.json()[0]["municipality_code"] == "SEOSAN"

        source_items = client.get("/api/v1/source-rule-items")
        assert source_items.status_code == 200
        source_items_body = source_items.json()
        assert len(source_items_body) > 0
        assert "laws" in source_items_body[0]
        assert isinstance(source_items_body[0]["laws"], list)
        assert len(source_items_body[0]["laws"]) > 0
