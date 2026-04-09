import type { DiagnosisCase, RuleProfile, SourceRuleItem } from './types'

const API_BASE = `${import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'}/api/v1`

export async function createDiagnosis(payload: {
  department: string
  project_name: string
  manager_name: string
  admin_phone: string
}): Promise<DiagnosisCase> {
  const response = await fetch(`${API_BASE}/diagnoses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, municipality_code: 'SEOSAN' })
  })
  if (!response.ok) throw new Error('진단 건 생성에 실패했습니다.')
  return response.json()
}

export async function saveAnswers(caseId: string, payload: Array<{ question_code: string; value: unknown }>): Promise<DiagnosisCase> {
  const response = await fetch(`${API_BASE}/diagnoses/${caseId}/answers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers: payload })
  })
  if (!response.ok) throw new Error('답변 저장에 실패했습니다.')
  return response.json()
}

export async function evaluateDiagnosis(caseId: string): Promise<{ final_decision: string; final_reason: string }> {
  const response = await fetch(`${API_BASE}/diagnoses/${caseId}/evaluate`, { method: 'POST' })
  if (!response.ok) throw new Error('평가 실행에 실패했습니다.')
  return response.json()
}

export async function getDiagnosis(caseId: string): Promise<DiagnosisCase> {
  const response = await fetch(`${API_BASE}/diagnoses/${caseId}`)
  if (!response.ok) throw new Error('진단 조회에 실패했습니다.')
  return response.json()
}

export async function listDiagnoses(filters: {
  from?: string
  to?: string
  department?: string
  decision?: string
}): Promise<DiagnosisCase[]> {
  const params = new URLSearchParams()
  if (filters.from) params.set('from', filters.from)
  if (filters.to) params.set('to', filters.to)
  if (filters.department) params.set('department', filters.department)
  if (filters.decision) params.set('decision', filters.decision)

  const response = await fetch(`${API_BASE}/diagnoses?${params.toString()}`)
  if (!response.ok) throw new Error('진단 목록 조회에 실패했습니다.')
  const data = await response.json()
  return data.items
}

export async function listRuleProfiles(): Promise<RuleProfile[]> {
  const response = await fetch(`${API_BASE}/rule-profiles`)
  if (!response.ok) throw new Error('규칙 프로파일 조회에 실패했습니다.')
  return response.json()
}

export async function listSourceRuleItems(): Promise<SourceRuleItem[]> {
  const response = await fetch(`${API_BASE}/source-rule-items`)
  if (!response.ok) throw new Error('사례 기준 조회에 실패했습니다.')
  return response.json()
}
