export type DiagnosisDecision =
  | '심의/관리계획 제외'
  | '심의 + 관리계획 변경 수립'
  | '심의 + 관리계획 수립'
  | '심의'
  | '심의 비대상'

export interface DiagnosisCase {
  id: string
  department: string
  project_name: string
  manager_name: string
  admin_phone: string
  municipality_code: string
  final_decision: DiagnosisDecision | null
  final_reason: string | null
  created_at: string
  updated_at: string
  answers: Array<{ question_code: string; value: unknown }>
  traces: Array<{
    step_key: string
    prompt: string
    decision: string
    snapshot: Record<string, unknown>
    created_at: string
  }>
}

export interface RuleProfile {
  id: number
  municipality_code: string
  name: string
  is_active: boolean
  config: Record<string, unknown>
  created_at: string
}

export interface SourceRuleItem {
  label: string
  group: 'plan_change' | 'plan_setup' | 'deliberation'
  laws: string[]
}
