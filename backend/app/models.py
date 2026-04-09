from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DiagnosisCase(Base):
    __tablename__ = "diagnosis_case"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    manager_name: Mapped[str] = mapped_column(String(100), nullable=False)
    admin_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    municipality_code: Mapped[str] = mapped_column(String(30), nullable=False, default="SEOSAN")
    final_decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    final_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    answers: Mapped[list[DiagnosisAnswer]] = relationship(
        back_populates="diagnosis_case", cascade="all, delete-orphan"
    )
    traces: Mapped[list[DiagnosisTrace]] = relationship(
        back_populates="diagnosis_case", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_diagnosis_case_created_at", "created_at"),
        Index("ix_diagnosis_case_final_decision", "final_decision"),
        Index("ix_diagnosis_case_department", "department"),
    )


class DiagnosisAnswer(Base):
    __tablename__ = "diagnosis_answer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnosis_case.id", ondelete="CASCADE"), nullable=False)
    question_code: Mapped[str] = mapped_column(String(40), nullable=False)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    diagnosis_case: Mapped[DiagnosisCase] = relationship(back_populates="answers")

    __table_args__ = (UniqueConstraint("case_id", "question_code", name="uq_case_question"),)


class DiagnosisTrace(Base):
    __tablename__ = "diagnosis_trace"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("diagnosis_case.id", ondelete="CASCADE"), nullable=False)
    step_key: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    diagnosis_case: Mapped[DiagnosisCase] = relationship(back_populates="traces")


class RuleProfile(Base):
    __tablename__ = "rule_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    municipality_code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (Index("ix_rule_profile_municipality_active", "municipality_code", "is_active"),)
