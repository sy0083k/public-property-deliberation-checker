from __future__ import annotations

from datetime import datetime, timezone
from typing import Generator
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, inspect, select
from sqlalchemy.orm import Session

from .config import settings
from .db import create_db_engine, create_session_factory
from .models import Base, DiagnosisAnswer, DiagnosisCase, DiagnosisTrace, RuleProfile
from .rule_catalog import CATALOG_THRESHOLDS, SOURCE_RULE_ITEMS
from .rules import evaluate_answers
from .schemas import (
    AnswerBatchRequest,
    DiagnosisCaseResponse,
    DiagnosisListResponse,
    DiagnosisTraceResponse,
    EvaluateResponse,
    DiagnosisCreateRequest,
    DiagnosisAnswerResponse,
    RuleProfileResponse,
    SourceRuleItemResponse,
)


def _serialize_source_rule_items(items) -> list[SourceRuleItemResponse]:
    return [
        SourceRuleItemResponse(
            label=item.label,
            group=item.group,
            laws=item.laws,
        )
        for item in items
    ]


def create_app(db_url: str | None = None) -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = create_db_engine(db_url or settings.db_url)
    session_factory = create_session_factory(engine)

    app.state.engine = engine
    app.state.session_factory = session_factory

    Base.metadata.create_all(bind=engine)
    _assert_required_schema(engine)

    with session_factory() as session:
        _seed_default_rule_profile(session)

    def get_db(request: Request) -> Generator[Session, None, None]:
        db = request.app.state.session_factory()
        try:
            yield db
        finally:
            db.close()

    @app.post("/api/v1/diagnoses", response_model=DiagnosisCaseResponse)
    def create_diagnosis(payload: DiagnosisCreateRequest, db: Session = Depends(get_db)) -> DiagnosisCaseResponse:
        case = DiagnosisCase(
            department=payload.department,
            project_name=payload.project_name,
            manager_name=payload.manager_name,
            admin_phone=payload.admin_phone,
            municipality_code=payload.municipality_code,
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return _case_to_response(db, case, include_details=True)

    @app.post("/api/v1/diagnoses/{case_id}/answers", response_model=DiagnosisCaseResponse)
    def upsert_answers(case_id: str, payload: AnswerBatchRequest, db: Session = Depends(get_db)) -> DiagnosisCaseResponse:
        case = _get_case_or_404(db, case_id)

        existing_answers = {
            row.question_code: row
            for row in db.scalars(select(DiagnosisAnswer).where(DiagnosisAnswer.case_id == case_id)).all()
        }

        for answer in payload.answers:
            row = existing_answers.get(answer.question_code)
            if row:
                row.value = answer.value
            else:
                db.add(DiagnosisAnswer(case_id=case_id, question_code=answer.question_code, value=answer.value))

        db.commit()
        db.refresh(case)
        return _case_to_response(db, case, include_details=True)

    @app.post("/api/v1/diagnoses/{case_id}/evaluate", response_model=EvaluateResponse)
    def evaluate(case_id: str, db: Session = Depends(get_db)) -> EvaluateResponse:
        case = _get_case_or_404(db, case_id)

        answers = db.scalars(select(DiagnosisAnswer).where(DiagnosisAnswer.case_id == case_id)).all()
        answer_map = {a.question_code: a.value for a in answers}

        profile = db.scalar(
            select(RuleProfile).where(
                and_(
                    RuleProfile.municipality_code == case.municipality_code,
                    RuleProfile.is_active.is_(True),
                )
            )
        )
        if profile is None:
            raise HTTPException(status_code=400, detail="활성화된 규칙 프로파일이 없습니다.")

        result = evaluate_answers(answer_map, profile.config)

        case.final_decision = result.final_decision
        case.final_reason = result.final_reason

        db.query(DiagnosisTrace).filter(DiagnosisTrace.case_id == case_id).delete()
        for item in result.trace:
            db.add(
                DiagnosisTrace(
                    case_id=case_id,
                    step_key=item["step_key"],
                    prompt=item["prompt"],
                    decision=item["decision"],
                    snapshot=item["snapshot"],
                )
            )

        db.commit()

        return EvaluateResponse(
            case_id=case_id,
            final_decision=result.final_decision,
            final_reason=result.final_reason,
        )

    @app.get("/api/v1/diagnoses/{case_id}", response_model=DiagnosisCaseResponse)
    def get_diagnosis(case_id: str, db: Session = Depends(get_db)) -> DiagnosisCaseResponse:
        case = _get_case_or_404(db, case_id)
        return _case_to_response(db, case, include_details=True)

    @app.get("/api/v1/diagnoses", response_model=DiagnosisListResponse)
    def list_diagnoses(
        from_date: datetime | None = Query(default=None, alias="from"),
        to_date: datetime | None = Query(default=None, alias="to"),
        department: str | None = None,
        decision: str | None = None,
        db: Session = Depends(get_db),
    ) -> DiagnosisListResponse:
        query = select(DiagnosisCase)

        if from_date is not None:
            query = query.where(DiagnosisCase.created_at >= from_date)
        if to_date is not None:
            query = query.where(DiagnosisCase.created_at <= to_date)
        if department:
            query = query.where(DiagnosisCase.department == department)
        if decision:
            query = query.where(DiagnosisCase.final_decision == decision)

        query = query.order_by(DiagnosisCase.created_at.desc())
        items = db.scalars(query).all()
        return DiagnosisListResponse(items=[_case_to_response(db, item, include_details=False) for item in items])

    @app.get("/api/v1/rule-profiles", response_model=list[RuleProfileResponse])
    def list_rule_profiles(db: Session = Depends(get_db)) -> list[RuleProfileResponse]:
        rows = db.scalars(select(RuleProfile).order_by(RuleProfile.id.asc())).all()
        return [
            RuleProfileResponse(
                id=row.id,
                municipality_code=row.municipality_code,
                name=row.name,
                is_active=row.is_active,
                config=row.config,
                created_at=row.created_at,
            )
            for row in rows
        ]

    @app.get("/api/v1/source-rule-items", response_model=list[SourceRuleItemResponse])
    def list_source_rule_items() -> list[SourceRuleItemResponse]:
        return _serialize_source_rule_items(SOURCE_RULE_ITEMS)

    return app


def _seed_default_rule_profile(db: Session) -> None:
    exists = db.scalar(
        select(RuleProfile).where(
            and_(
                RuleProfile.municipality_code == "SEOSAN",
                RuleProfile.is_active.is_(True),
            )
        )
    )
    if exists:
        exists.config = dict(CATALOG_THRESHOLDS)
        db.commit()
        return

    db.add(
        RuleProfile(
            municipality_code="SEOSAN",
            name="서산시 기본 규칙",
            is_active=True,
            config=dict(CATALOG_THRESHOLDS),
        )
    )
    db.commit()


def _assert_required_schema(engine) -> None:
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns("diagnosis_case")}
    required = {"department", "project_name", "manager_name", "admin_phone"}
    missing = sorted(required - columns)
    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(
            f"DB schema is out of date. Missing diagnosis_case columns: {missing_list}. "
            "Run migration: `cd backend && alembic upgrade head` (or apply against the DB in use)."
        )


def _get_case_or_404(db: Session, case_id: str) -> DiagnosisCase:
    case = db.get(DiagnosisCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="진단 건을 찾을 수 없습니다.")
    return case


def _case_to_response(db: Session, case: DiagnosisCase, include_details: bool) -> DiagnosisCaseResponse:
    answers: list[DiagnosisAnswerResponse] = []
    traces: list[DiagnosisTraceResponse] = []

    if include_details:
        answer_rows = db.scalars(
            select(DiagnosisAnswer).where(DiagnosisAnswer.case_id == case.id).order_by(DiagnosisAnswer.question_code.asc())
        ).all()
        trace_rows = db.scalars(
            select(DiagnosisTrace).where(DiagnosisTrace.case_id == case.id).order_by(DiagnosisTrace.id.asc())
        ).all()

        answers = [DiagnosisAnswerResponse(question_code=row.question_code, value=row.value) for row in answer_rows]
        traces = [
            DiagnosisTraceResponse(
                step_key=row.step_key,
                prompt=row.prompt,
                decision=row.decision,
                snapshot=row.snapshot,
                created_at=_to_kst(row.created_at),
            )
            for row in trace_rows
        ]

    return DiagnosisCaseResponse(
        id=case.id,
        department=case.department,
        project_name=case.project_name,
        manager_name=case.manager_name,
        admin_phone=case.admin_phone,
        municipality_code=case.municipality_code,
        final_decision=case.final_decision,
        final_reason=case.final_reason,
        created_at=_to_kst(case.created_at),
        updated_at=_to_kst(case.updated_at),
        answers=answers,
        traces=traces,
    )


def _to_kst(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(ZoneInfo("Asia/Seoul"))


app = create_app()
