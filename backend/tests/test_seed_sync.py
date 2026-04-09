from pathlib import Path
import tempfile

from sqlalchemy import and_, select

from app.main import create_app
from app.models import RuleProfile
from app.rule_catalog import CATALOG_THRESHOLDS


def test_startup_overwrites_active_seosan_thresholds_from_yaml() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "sync.db"
        db_url = f"sqlite+pysqlite:///{db_path}"

        app = create_app(db_url)
        with app.state.session_factory() as session:
            profile = session.scalar(
                select(RuleProfile).where(
                    and_(
                        RuleProfile.municipality_code == "SEOSAN",
                        RuleProfile.is_active.is_(True),
                    )
                )
            )
            assert profile is not None
            assert profile.config == CATALOG_THRESHOLDS

            profile.config = {
                "acquisition_amount_threshold": 1,
                "disposal_amount_threshold": 1,
                "acquisition_area_threshold": 1,
                "disposal_area_threshold": 1,
                "seosan_private_sale_threshold": 1,
            }
            session.commit()

        app_restarted = create_app(db_url)
        with app_restarted.state.session_factory() as session:
            profile = session.scalar(
                select(RuleProfile).where(
                    and_(
                        RuleProfile.municipality_code == "SEOSAN",
                        RuleProfile.is_active.is_(True),
                    )
                )
            )
            assert profile is not None
            assert profile.config == CATALOG_THRESHOLDS
