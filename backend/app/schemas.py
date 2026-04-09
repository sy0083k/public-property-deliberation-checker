from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DecisionType = Literal[
    "심의/관리계획 제외",
    "심의 + 관리계획 변경 수립",
    "심의 + 관리계획 수립",
    "심의",
    "심의 비대상",
]


class DiagnosisCreateRequest(BaseModel):
    department: str = Field(min_length=1, max_length=100)
    project_name: str = Field(min_length=1, max_length=200)
    manager_name: str = Field(min_length=1, max_length=100)
    admin_phone: str = Field(min_length=1, max_length=30)
    municipality_code: str = Field(default="SEOSAN", min_length=1, max_length=30)


class AnswerInput(BaseModel):
    question_code: str = Field(min_length=1, max_length=40)
    value: Any


class AnswerBatchRequest(BaseModel):
    answers: list[AnswerInput]


class DiagnosisAnswerResponse(BaseModel):
    question_code: str
    value: Any


class DiagnosisTraceResponse(BaseModel):
    step_key: str
    prompt: str
    decision: str
    snapshot: dict[str, Any]
    created_at: datetime


class DiagnosisCaseResponse(BaseModel):
    id: str
    department: str
    project_name: str
    manager_name: str
    admin_phone: str
    municipality_code: str
    final_decision: str | None
    final_reason: str | None
    created_at: datetime
    updated_at: datetime
    answers: list[DiagnosisAnswerResponse] = []
    traces: list[DiagnosisTraceResponse] = []


class EvaluateResponse(BaseModel):
    case_id: str
    final_decision: DecisionType
    final_reason: str


class DiagnosisListResponse(BaseModel):
    items: list[DiagnosisCaseResponse]


class RuleProfileResponse(BaseModel):
    id: int
    municipality_code: str
    name: str
    is_active: bool
    config: dict[str, Any]
    created_at: datetime


RuleGroupType = Literal["plan_change", "plan_setup", "deliberation"]


class SourceRuleItemResponse(BaseModel):
    label: str
    group: RuleGroupType
    laws: list[str]
