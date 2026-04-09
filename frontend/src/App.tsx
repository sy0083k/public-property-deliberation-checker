import { FormEvent, useEffect, useMemo, useState } from 'react'
import {
  createDiagnosis,
  evaluateDiagnosis,
  getDiagnosis,
  listDiagnoses,
  listRuleProfiles,
  listSourceRuleItems,
  saveAnswers
} from './api'
import type { DiagnosisCase, DiagnosisDecision, RuleProfile, SourceRuleItem } from './types'
import {
  EXCEPTION_REASON_OPTIONS,
  type ExceptionReasonCode,
  isPropertyRelatedSourceItem
} from './ruleCatalog'

const decisionOptions: DiagnosisDecision[] = [
  '심의/관리계획 제외',
  '심의 + 관리계획 변경 수립',
  '심의 + 관리계획 수립',
  '심의',
  '심의 비대상'
]

function toNumberOrZero(value: string): number {
  const n = Number(value)
  if (!Number.isFinite(n) || n < 0) return 0
  return n
}

function isSimplePropertyItem(item: string): boolean {
  return item === '공유재산의 취득' || item === '공유재산의 처분'
}

function formatKstDate(value: string): string {
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  const parts = new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).formatToParts(d)

  const get = (type: Intl.DateTimeFormatPartTypes): string =>
    parts.find((p) => p.type === type)?.value ?? '00'

  return `${get('year')}-${get('month')}-${get('day')} ${get('hour')}:${get('minute')}:${get('second')}`
}

function formatNowKstDateTime(): string {
  return formatKstDate(new Date().toISOString())
}

function getAnswerValue(caseInfo: DiagnosisCase | null, questionCode: string): unknown {
  if (!caseInfo) return undefined
  return caseInfo.answers.find((entry) => entry.question_code === questionCode)?.value
}

function buildAnswerPayloadFromSelections(input: {
  selectedRuleItemLabel: string
  exceptionReasonCode: ExceptionReasonCode
  amountWonInput: string
  areaSqmInput: string
}): Array<{ question_code: string; value: unknown }> {
  const exceptionEnabled = isPropertyRelatedSourceItem(input.selectedRuleItemLabel)
  const hasLegalException = exceptionEnabled && input.exceptionReasonCode !== 'none'
  const useNumericInputs = isSimplePropertyItem(input.selectedRuleItemLabel)

  return [
    { question_code: 'selected_rule_item', value: input.selectedRuleItemLabel },
    { question_code: 'exception_reason_code', value: input.exceptionReasonCode },
    { question_code: 'exception_reason_enabled', value: exceptionEnabled },
    { question_code: 'has_legal_exception', value: hasLegalException },
    { question_code: 'amount_won', value: useNumericInputs ? toNumberOrZero(input.amountWonInput) : 0 },
    { question_code: 'area_sqm', value: useNumericInputs ? toNumberOrZero(input.areaSqmInput) : 0 }
  ]
}

function App() {
  const [department, setDepartment] = useState('재산관리과')
  const [projectName, setProjectName] = useState('000사업')
  const [managerName, setManagerName] = useState('홍길동')
  const [adminPhone, setAdminPhone] = useState('9999')

  const [caseInfo, setCaseInfo] = useState<DiagnosisCase | null>(null)
  const [profiles, setProfiles] = useState<RuleProfile[]>([])
  const [sourceRuleItems, setSourceRuleItems] = useState<SourceRuleItem[]>([])
  const [sourceRuleItemsError, setSourceRuleItemsError] = useState<string | null>(null)
  const [list, setList] = useState<DiagnosisCase[]>([])
  const [decisionFilter, setDecisionFilter] = useState('')
  const [loading, setLoading] = useState(false)

  const [selectedRuleItemLabel, setSelectedRuleItemLabel] = useState('')
  const [exceptionReasonCode, setExceptionReasonCode] = useState<ExceptionReasonCode>('none')
  const [amountWonInput, setAmountWonInput] = useState('0')
  const [areaSqmInput, setAreaSqmInput] = useState('0')

  const selectedRuleItem = useMemo(
    () => sourceRuleItems.find((item) => item.label === selectedRuleItemLabel) ?? null,
    [sourceRuleItems, selectedRuleItemLabel]
  )

  const selectedRuleItemLabelForResult = useMemo(() => {
    if (!caseInfo) return selectedRuleItemLabel
    const answer = caseInfo.answers.find((entry) => entry.question_code === 'selected_rule_item')
    return typeof answer?.value === 'string' ? answer.value : selectedRuleItemLabel
  }, [caseInfo, selectedRuleItemLabel])

  const selectedRuleItemForResult = useMemo(
    () => sourceRuleItems.find((item) => item.label === selectedRuleItemLabelForResult) ?? null,
    [sourceRuleItems, selectedRuleItemLabelForResult]
  )
  const relatedLawsForResult = useMemo(
    () => selectedRuleItemForResult?.laws ?? [],
    [selectedRuleItemForResult]
  )

  const currentDecision = useMemo(() => caseInfo?.final_decision ?? '-', [caseInfo])
  const canPrint = useMemo(() => Boolean(caseInfo?.final_decision), [caseInfo])
  const isPropertyRelatedForPrint = useMemo(
    () => isPropertyRelatedSourceItem(selectedRuleItemLabelForResult),
    [selectedRuleItemLabelForResult]
  )
  const amountWonForPrint = useMemo(
    () => toNumberOrZero(String(getAnswerValue(caseInfo, 'amount_won') ?? '0')),
    [caseInfo]
  )
  const areaSqmForPrint = useMemo(
    () => toNumberOrZero(String(getAnswerValue(caseInfo, 'area_sqm') ?? '0')),
    [caseInfo]
  )
  const exceptionReasonCodeForPrint = useMemo(
    () => String(getAnswerValue(caseInfo, 'exception_reason_code') ?? 'none'),
    [caseInfo]
  )
  const exceptionReasonLabelForPrint = useMemo(() => {
    const found = EXCEPTION_REASON_OPTIONS.find((option) => option.code === exceptionReasonCodeForPrint)
    return found?.label ?? '해당 없음'
  }, [exceptionReasonCodeForPrint])
  const exceptionReasonEnabled = useMemo(
    () => isPropertyRelatedSourceItem(selectedRuleItemLabel),
    [selectedRuleItemLabel]
  )
  const numericInputEnabled = useMemo(
    () => isSimplePropertyItem(selectedRuleItemLabel),
    [selectedRuleItemLabel]
  )

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const [profilesData, sourceItems] = await Promise.all([
          listRuleProfiles(),
          listSourceRuleItems()
        ])
        setProfiles(profilesData)
        setSourceRuleItems(sourceItems)
        setSourceRuleItemsError(null)
        if (sourceItems.length > 0) {
          setSelectedRuleItemLabel((prev) => prev || sourceItems[0].label)
        }
      } catch (error) {
        console.error(error)
        setSourceRuleItemsError('사례 기준을 불러오지 못했습니다.')
      }

      await refreshList()
    }

    void bootstrap()
  }, [])

  useEffect(() => {
    if (sourceRuleItems.length > 0 && !selectedRuleItemLabel) {
      setSelectedRuleItemLabel(sourceRuleItems[0].label)
    }
  }, [sourceRuleItems, selectedRuleItemLabel])

  useEffect(() => {
    if (!exceptionReasonEnabled && exceptionReasonCode !== 'none') {
      setExceptionReasonCode('none')
    }
  }, [exceptionReasonCode, exceptionReasonEnabled])

  useEffect(() => {
    if (!numericInputEnabled) {
      setAmountWonInput('0')
      setAreaSqmInput('0')
    }
  }, [numericInputEnabled])

  const refreshList = async () => {
    const items = await listDiagnoses({ decision: decisionFilter || undefined })
    setList(items)
  }

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    try {
      const created = await createDiagnosis({
        department: department.trim(),
        project_name: projectName.trim(),
        manager_name: managerName.trim(),
        admin_phone: adminPhone.trim()
      })
      setCaseInfo(created)
      await refreshList()
    } finally {
      setLoading(false)
    }
  }

  const handleDiagnose = async () => {
    if (!caseInfo || !selectedRuleItemLabel) return
    setLoading(true)
    try {
      const payload = buildAnswerPayloadFromSelections({
        selectedRuleItemLabel,
        exceptionReasonCode,
        amountWonInput,
        areaSqmInput
      })
      await saveAnswers(caseInfo.id, payload)
      await evaluateDiagnosis(caseInfo.id)
      const refreshed = await getDiagnosis(caseInfo.id)
      setCaseInfo(refreshed)
      await refreshList()
    } finally {
      setLoading(false)
    }
  }

  const handleResetInputs = () => {
    setSelectedRuleItemLabel(sourceRuleItems.length > 0 ? sourceRuleItems[0].label : '')
    setExceptionReasonCode('none')
    setAmountWonInput('0')
    setAreaSqmInput('0')
  }

  const handlePrintResult = () => {
    if (!canPrint) {
      window.alert('진단 후 출력할 수 있습니다.')
      return
    }
    window.print()
  }

  const summary = useMemo(() => {
    const exceptionLabel =
      exceptionReasonEnabled && exceptionReasonCode !== 'none' ? '예외 사유 선택됨' : '예외 사유 미선택'
    const numericLabel = numericInputEnabled
      ? `기준가격 ${toNumberOrZero(amountWonInput).toLocaleString('ko-KR')}원 / 면적 ${toNumberOrZero(areaSqmInput).toLocaleString('ko-KR')}㎡`
      : '기준가격/면적 입력 미사용'
    return `${selectedRuleItemLabel || '-'} / ${exceptionLabel} / ${numericLabel}`
  }, [amountWonInput, areaSqmInput, exceptionReasonCode, exceptionReasonEnabled, numericInputEnabled, selectedRuleItemLabel])

  return (
    <div className="page">
      <header>
        <h1>공유재산 심의·관리계획 대상 판별 도구</h1>
        <p>원문 항목, 예외 사유, 취득·처분 수치를 바탕으로 대상 여부를 판별합니다.</p>
      </header>

      <section className="panel">
        <h2>1) 기초정보</h2>
        <form onSubmit={handleCreate} className="row">
          <input value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="부서명" required />
          <input value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="사업명" required />
          <input value={managerName} onChange={(e) => setManagerName(e.target.value)} placeholder="담당자" required />
          <input value={adminPhone} onChange={(e) => setAdminPhone(e.target.value)} placeholder="행정전화" required />
          <button type="submit" disabled={loading}>생성</button>
        </form>
      </section>

      <section className="panel">
        <h2>2) 문답 입력</h2>
        {sourceRuleItemsError && <p>{sourceRuleItemsError}</p>}
        {!caseInfo && <p>먼저 진단 건을 생성하세요.</p>}
        {caseInfo && (
          <div className="form-steps">
            <label>
              사례 유형
              <select
                value={selectedRuleItemLabel}
                onChange={(e) => setSelectedRuleItemLabel(e.target.value)}
                disabled={sourceRuleItems.length === 0}
              >
                {sourceRuleItems.map((item) => (
                  <option key={item.label} value={item.label}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              예외 사유
              <select
                value={exceptionReasonCode}
                onChange={(e) => setExceptionReasonCode(e.target.value as ExceptionReasonCode)}
                disabled={!exceptionReasonEnabled}
              >
                {EXCEPTION_REASON_OPTIONS.map((option) => (
                  <option key={option.code} value={option.code}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              1건당 기준가격(원)
              <input
                type="number"
                min={0}
                value={amountWonInput}
                onChange={(e) => setAmountWonInput(e.target.value)}
                disabled={!numericInputEnabled}
              />
            </label>

            <label>
              토지 면적(㎡)
              <input
                type="number"
                min={0}
                value={areaSqmInput}
                onChange={(e) => setAreaSqmInput(e.target.value)}
                disabled={!numericInputEnabled}
              />
            </label>

            {selectedRuleItem && (
              <div className="law-box">
                <strong>관련 법령</strong>
                <ul>
                  {selectedRuleItem.laws.map((law) => (
                    <li key={law}>{law}</li>
                  ))}
                </ul>
              </div>
            )}

            <p className="summary-line">선택 요약: {summary}</p>

            <div className="row actions">
              <button type="button" onClick={handleDiagnose} disabled={loading || !selectedRuleItemLabel || !caseInfo}>진단</button>
              <button type="button" onClick={handleResetInputs} disabled={loading}>초기화</button>
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>3) 결과 및 감사 이력</h2>
        {caseInfo ? (
          <>
            <div className="row no-print">
              <button type="button" onClick={handlePrintResult} disabled={!canPrint}>
                문서 출력
              </button>
            </div>
            <p>
              <strong>진단일시:</strong> {formatKstDate(caseInfo.created_at)}
            </p>
            <p>
              <strong>부서:</strong> {caseInfo.department}
            </p>
            <p>
              <strong>사업명:</strong> {caseInfo.project_name}
            </p>
            <p>
              <strong>담당자:</strong> {caseInfo.manager_name}
            </p>
            <p>
              <strong>행정전화:</strong> {caseInfo.admin_phone}
            </p>
            <p>
              <strong>최종 결정:</strong> {currentDecision}
            </p>
            <p>
              <strong>사유:</strong> {caseInfo.final_reason ?? '-'}
            </p>
            <div className="law-box">
              <strong>관련 법령</strong>
              {relatedLawsForResult.length > 0 ? (
                <ul>
                  {relatedLawsForResult.map((law) => (
                    <li key={`result-${law}`}>{law}</li>
                  ))}
                </ul>
              ) : (
                <p>관련 법령 정보 없음</p>
              )}
            </div>
            <table>
              <thead>
                <tr>
                  <th>단계</th>
                  <th>질문</th>
                  <th>판정</th>
                </tr>
              </thead>
              <tbody>
                {caseInfo.traces.map((trace) => (
                  <tr key={`${trace.step_key}-${trace.created_at}`}>
                    <td>{trace.step_key}</td>
                    <td>{trace.prompt}</td>
                    <td>{trace.decision}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        ) : (
          <p>선택된 진단 건이 없습니다.</p>
        )}
      </section>

      <section className="panel">
        <h2>4) 진단 목록 조회</h2>
        <div className="row">
          <select value={decisionFilter} onChange={(e) => setDecisionFilter(e.target.value)}>
            <option value="">전체 결정</option>
            {decisionOptions.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
          <button type="button" onClick={refreshList}>조회</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>진단일시</th>
              <th>부서</th>
              <th>사업명</th>
              <th>진단결과</th>
              <th>담당자</th>
              <th>행정전화</th>
            </tr>
          </thead>
          <tbody>
            {list.map((item) => (
              <tr key={item.id}>
                <td>{formatKstDate(item.created_at)}</td>
                <td>{item.department}</td>
                <td>{item.project_name}</td>
                <td>{item.final_decision ?? '-'}</td>
                <td>{item.manager_name}</td>
                <td>{item.admin_phone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h2>활성 규칙 프로파일</h2>
        <ul>
          {profiles.map((p) => (
            <li key={p.id}>
              {p.name} ({p.municipality_code}) - {p.is_active ? '활성' : '비활성'}
            </li>
          ))}
        </ul>
      </section>

      <section className="print-doc">
        <h1>공유재산 심의·관리계획 대상 판별 결과서</h1>
        <p>출력일시: {formatNowKstDateTime()}</p>
        {caseInfo ? (
          <>
            <p>진단번호: {caseInfo.id}</p>
            <table>
              <tbody>
                <tr>
                  <th>진단일시</th>
                  <td>{formatKstDate(caseInfo.created_at)}</td>
                </tr>
                <tr>
                  <th>부서</th>
                  <td>{caseInfo.department}</td>
                </tr>
                <tr>
                  <th>사업명</th>
                  <td>{caseInfo.project_name}</td>
                </tr>
                <tr>
                  <th>담당자</th>
                  <td>{caseInfo.manager_name}</td>
                </tr>
                <tr>
                  <th>행정전화</th>
                  <td>{caseInfo.admin_phone}</td>
                </tr>
              </tbody>
            </table>

            <div className="print-input-summary">
              <p>
                <strong>사례 유형:</strong> {selectedRuleItemLabelForResult || '-'}
              </p>
              {isPropertyRelatedForPrint && (
                <>
                  <p>
                    <strong>1건당 기준가격:</strong> {amountWonForPrint.toLocaleString('ko-KR')}원
                  </p>
                  <p>
                    <strong>토지 면적:</strong> {areaSqmForPrint.toLocaleString('ko-KR')}㎡
                  </p>
                  <p>
                    <strong>예외 사유:</strong> {exceptionReasonLabelForPrint}
                  </p>
                </>
              )}
            </div>

            <div className="print-result-summary">
              <p>
                <strong>최종 결정:</strong> {caseInfo.final_decision ?? '-'}
              </p>
              <p>
                <strong>사유:</strong> {caseInfo.final_reason ?? '-'}
              </p>
            </div>

            <div className="print-law-box">
              <strong>관련 법령</strong>
              {relatedLawsForResult.length > 0 ? (
                <ul>
                  {relatedLawsForResult.map((law) => (
                    <li key={`print-law-${law}`}>{law}</li>
                  ))}
                </ul>
              ) : (
                <p className="print-law-empty">관련 법령 정보 없음</p>
              )}
            </div>
          </>
        ) : (
          <p>선택된 진단 건이 없습니다.</p>
        )}
        <p className="print-footnote">본 문서는 입력된 판별 기준값을 바탕으로 자동 생성되었습니다.</p>
      </section>
    </div>
  )
}

export default App
