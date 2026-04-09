/** `SavedSearch.search_type` values used by staff Vue list pages. */
export const STAFF_SAVED_SEARCH_TYPE = Object.freeze({
  APPLICATION_REVIEW_QUEUE: 'application',
  EXCHANGE_AGREEMENT: 'exchange_agreement',
  APPLICATION_DOCUMENT: 'document',
  AGREEMENT_REPOSITORY_DOC: 'agreement_document',
})

const AG_ORDER_DEFAULT = '-end_date'

export function serializeExchangeAgreementFilters(state) {
  return {
    search: state.search || '',
    status: state.status || '',
    agreement_type: state.agreement_type || '',
    program: state.program || '',
    partner: state.partner || '',
    end_date_before: state.end_date_before || '',
    end_date_after: state.end_date_after || '',
    expiring_within_days:
      state.expiring_within_days === '' || state.expiring_within_days == null
        ? ''
        : String(state.expiring_within_days),
    ordering: state.ordering || AG_ORDER_DEFAULT,
  }
}

export function deserializeExchangeAgreementFilters(raw) {
  const f = raw && typeof raw === 'object' ? raw : {}
  return {
    search: f.search ?? '',
    status: f.status ?? '',
    agreement_type: f.agreement_type ?? '',
    program: f.program ?? '',
    partner: f.partner ?? '',
    end_date_before: f.end_date_before ?? '',
    end_date_after: f.end_date_after ?? '',
    expiring_within_days:
      f.expiring_within_days === '' || f.expiring_within_days == null
        ? ''
        : Number(f.expiring_within_days) || f.expiring_within_days,
    ordering: f.ordering || AG_ORDER_DEFAULT,
  }
}

export function serializeDocumentListFilters(state) {
  return {
    application: state.application || '',
    type: state.type || '',
    valid: state.valid === '' || state.valid == null ? '' : String(state.valid),
    ordering: state.ordering || '-created_at',
  }
}

export function deserializeDocumentListFilters(raw) {
  const f = raw && typeof raw === 'object' ? raw : {}
  return {
    application: f.application ?? '',
    type: f.type ?? '',
    valid: f.valid === undefined || f.valid === null ? '' : String(f.valid),
    ordering: f.ordering || '-created_at',
  }
}

const ADOC_ORDER_DEFAULT = '-created_at'

export function serializeAgreementDocumentFilters(state) {
  return {
    search: state.search || '',
    agreement: state.agreement || '',
    category: state.category || '',
    current_only: Boolean(state.current_only),
    ordering: state.ordering || ADOC_ORDER_DEFAULT,
  }
}

export function deserializeAgreementDocumentFilters(raw) {
  const f = raw && typeof raw === 'object' ? raw : {}
  return {
    search: f.search ?? '',
    agreement: f.agreement ?? '',
    category: f.category ?? '',
    current_only: Boolean(f.current_only),
    ordering: f.ordering || ADOC_ORDER_DEFAULT,
  }
}
