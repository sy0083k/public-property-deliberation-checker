export type ExceptionReasonCode =
  | 'none'
  | 'other_law_free_transfer'
  | 'land_readjustment'
  | 'court_judgment'
  | 'public_project_acquisition_disposal'
  | 'urban_renewal_free_grant'
  | 'factory_site_sale_sme'
  | 'local_council_approved'
  | 'tax_payment_in_kind'
  | 'law_excluded_from_plan'
  | 'law_mandated_acquisition_disposal'
  | 'permit_condition_public_facility'
  | 'same_purpose_scale_replacement'

export const EXCEPTION_REASON_OPTIONS: Array<{ code: ExceptionReasonCode; label: string }> = [
  { code: 'none', label: '해당 없음' },
  { code: 'other_law_free_transfer', label: '공유재산 및 물품 관리법이 아닌 다른 법률에 따른 무상귀속' },
  { code: 'land_readjustment', label: '도시개발법 등 다른 법률에 따른 환지' },
  { code: 'court_judgment', label: '법원의 판결에 따른 소유권 등의 취득 또는 상실' },
  { code: 'public_project_acquisition_disposal', label: '공익사업을 위한 토지 등의 취득 및 보상에 관한 법률에 따른 취득·처분' },
  { code: 'urban_renewal_free_grant', label: '도시 및 주거환경정비법 제101조에 따른 무상양여' },
  { code: 'factory_site_sale_sme', label: '기업활동 규제완화에 관한 특별조치법 제14조에 따른 중소기업자에 대한 공장용지 매각' },
  { code: 'local_council_approved', label: '지방의회의 의결 또는 동의를 받은 재산의 취득·처분' },
  { code: 'tax_payment_in_kind', label: '지방세법 제117조에 따른 물납 취득' },
  { code: 'law_excluded_from_plan', label: '다른 법률에 따라 공유재산관리계획의 적용이 배제된 재산의 취득·처분' },
  { code: 'law_mandated_acquisition_disposal', label: '다른 법률에 따라 해당 지방자치단체의 취득·처분이 의무화된 재산의 취득·처분' },
  { code: 'permit_condition_public_facility', label: '다른 법률에 따라 인가·허가 또는 사업승인 시 조건에 의하여 주된 사업대상물에 딸린 공공시설의 취득' },
  { code: 'same_purpose_scale_replacement', label: '공유재산을 종전과 동일한 목적과 규모로 대체하는 재산의 취득' }
]

const EXCEPTION_ENABLED_ITEMS = new Set<string>(['공유재산의 취득', '공유재산의 처분'])

export function isPropertyRelatedSourceItem(label: string): boolean {
  return EXCEPTION_ENABLED_ITEMS.has(label)
}
