<template>
  <div class="admin-document-type-edit">
    <PageHeader :title="pageTitle" :subtitle="t('adminDocuments.editorSubtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { to: { name: 'AdminDocuments' }, label: t('route.names.AdminDocuments') },
            { label: pageTitle, truncate: true },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="saving" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button
          type="button"
          class="btn btn-primary"
          :disabled="saving || loading"
          data-testid="admin-document-type-save"
          @click="save"
        >
          <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
          {{ t('adminCommon.save') }}
        </button>
      </template>
    </PageHeader>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      skeleton="none"
      :loading-label="t('adminCommon.loading')"
    >
    <div class="row g-4">
      <div class="col-lg-8">
        <div v-if="formError" class="alert alert-danger" role="alert">{{ formError }}</div>

        <CollapsibleCard
          test-id="admin-document-section-identity"
          :default-open="sectionOpen.identity"
        >
          <template #title>{{ t('adminDocuments.sections.identity') }}</template>
          <div class="row g-3">
            <div class="col-md-8">
              <label class="form-label">{{ t('adminDocuments.fields.name') }}</label>
              <input v-model="form.name" class="form-control" type="text" data-testid="admin-document-type-name" />
            </div>
            <div class="col-md-4">
              <label class="form-label">{{ t('adminDocuments.fields.slug') }}</label>
              <input v-model="form.slug" class="form-control" type="text" />
            </div>
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.description') }}</label>
              <textarea v-model="form.description" class="form-control" rows="2" />
            </div>
            <div class="col-md-6">
              <label class="form-label">{{ t('adminDocuments.fields.submissionMode') }}</label>
              <select v-model="form.submission_mode" class="form-select">
                <option v-for="opt in submissionModes" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">{{ t('adminDocuments.fields.allowsMultiple') }}</label>
              <div class="form-check mt-2">
                <input id="allowsMultiple" v-model="form.allows_multiple" class="form-check-input" type="checkbox" />
                <label class="form-check-label" for="allowsMultiple">{{ t('adminDocuments.fields.allowsMultipleHelp') }}</label>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">{{ t('adminDocuments.fields.versionHistoryVisibility') }}</label>
              <select
                v-model="form.version_history_visibility"
                class="form-select"
                data-testid="admin-document-version-history-visibility"
              >
                <option value="inherit">{{ t('adminDocuments.versionHistoryModes.inherit') }}</option>
                <option value="hidden">{{ t('adminDocuments.versionHistoryModes.hidden') }}</option>
                <option value="custom">{{ t('adminDocuments.versionHistoryModes.custom') }}</option>
              </select>
              <div class="form-text">{{ t('adminDocuments.fields.versionHistoryVisibilityHelp') }}</div>
            </div>
            <div
              v-if="form.version_history_visibility === 'custom'"
              class="col-12"
              data-testid="admin-document-version-history-custom"
            >
              <div class="row g-2">
                <div class="col-md-4">
                  <div class="form-check">
                    <input
                      id="vh-student"
                      v-model="form.version_history_student"
                      class="form-check-input"
                      type="checkbox"
                      :true-value="true"
                      :false-value="false"
                    />
                    <label class="form-check-label" for="vh-student">{{ t('adminDocuments.fields.versionHistoryStudent') }}</label>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-check">
                    <input
                      id="vh-coordinator"
                      v-model="form.version_history_coordinator"
                      class="form-check-input"
                      type="checkbox"
                      :true-value="true"
                      :false-value="false"
                    />
                    <label class="form-check-label" for="vh-coordinator">{{ t('adminDocuments.fields.versionHistoryCoordinator') }}</label>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-check">
                    <input
                      id="vh-admin"
                      v-model="form.version_history_admin"
                      class="form-check-input"
                      type="checkbox"
                      :true-value="true"
                      :false-value="false"
                    />
                    <label class="form-check-label" for="vh-admin">{{ t('adminDocuments.fields.versionHistoryAdmin') }}</label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CollapsibleCard>

        <CollapsibleCard
          test-id="admin-document-section-instructions"
          :default-open="sectionOpen.instructions"
        >
          <template #title>{{ t('adminDocuments.sections.instructions') }}</template>
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.instructions') }}</label>
              <textarea
                v-model="form.instructions"
                class="form-control"
                rows="5"
                data-testid="admin-document-type-instructions"
              />
              <div class="form-text">{{ t('adminDocuments.fields.instructionsHelp') }}</div>
            </div>
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.faq') }}</label>
              <textarea v-model="form.faq" class="form-control" rows="3" />
            </div>
          </div>
        </CollapsibleCard>

        <CollapsibleCard
          test-id="admin-document-section-constraints"
          :default-open="sectionOpen.constraints"
        >
          <template #title>{{ t('adminDocuments.sections.constraints') }}</template>
          <div class="row g-3">
            <div class="col-md-8">
              <label class="form-label">{{ t('adminDocuments.fields.fileTypeFamilies') }}</label>
              <FileTypeFamilyPicker
                v-model="form.file_type_family_ids"
                :families="fileTypeFamilies"
                :search-placeholder="t('adminDocuments.fields.fileTypeFamiliesSearch')"
                :help-text="t('adminDocuments.fields.fileTypeFamiliesHelp')"
              />
            </div>
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.acceptedExtensions') }}</label>
              <input
                v-model="form.accepted_extensions"
                class="form-control"
                type="text"
                :placeholder="t('adminDocuments.fields.acceptedExtensionsPlaceholder')"
              />
              <div class="form-text">{{ t('adminDocuments.fields.acceptedExtensionsHelp') }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">{{ t('adminDocuments.fields.maxFileSizeMb') }}</label>
              <input v-model.number="form.max_file_size_mb" class="form-control" type="number" min="1" />
              <div class="form-text">{{ t('adminDocuments.fields.maxFileSizeMbHelp') }}</div>
            </div>
          </div>
        </CollapsibleCard>

        <CollapsibleCard
          test-id="admin-document-section-template"
          :default-open="sectionOpen.template"
        >
          <template #title>{{ t('adminDocuments.sections.template') }}</template>
          <template v-if="hasTemplate" #header-extra>
            <span class="badge bg-secondary">{{ t('adminDocuments.templateAttached') }}</span>
          </template>
          <p class="small text-muted">{{ t('adminDocuments.fields.templateHelp') }}</p>
          <p v-if="hasTemplate" class="mb-2">
            <i class="bi bi-file-earmark-word me-1" aria-hidden="true"></i>
            {{ templateFilename || t('adminDocuments.templateAttached') }}
          </p>
          <p v-else class="text-muted small">{{ t('adminDocuments.noTemplate') }}</p>
          <div
            v-if="pendingTemplate"
            class="alert alert-warning py-2 px-3 small mb-2"
            role="status"
            data-testid="admin-document-template-pending"
          >
            <i class="bi bi-exclamation-triangle me-1" aria-hidden="true"></i>
            {{
              t('adminDocuments.templatePendingHint', {
                name: pendingTemplate.name || t('adminDocuments.templatePendingFile'),
              })
            }}
          </div>
          <div class="d-flex flex-wrap gap-2 align-items-center">
            <input
              ref="templateInput"
              class="form-control"
              type="file"
              accept=".docx,.doc,.pdf,.odt,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              data-testid="admin-document-type-template"
              @change="onTemplateChosen"
            />
            <button
              type="button"
              class="btn btn-outline-primary"
              :disabled="templateBusy || !pendingTemplate"
              data-testid="admin-document-type-upload-template"
              @click="uploadTemplate"
            >
              {{ t('adminDocuments.uploadTemplate') }}
            </button>
            <button
              v-if="hasTemplate"
              type="button"
              class="btn btn-outline-danger"
              :disabled="templateBusy"
              @click="removeTemplate"
            >
              {{ t('adminDocuments.removeTemplate') }}
            </button>
          </div>
        </CollapsibleCard>

        <CollapsibleCard
          test-id="admin-document-section-prefill-students"
          :default-open="sectionOpen.prefillStudents"
        >
          <template #title>{{ t('adminDocuments.sections.prefillStudents') }}</template>
          <template v-if="prefillStudents.length" #header-extra>
            <span class="badge bg-secondary">{{ prefillStudents.length }}</span>
          </template>
          <p class="small text-muted mb-3">{{ t('adminDocuments.prefillStudents.help') }}</p>

          <div class="mb-3">
            <label class="form-label" for="prefill-student-search">{{ t('adminDocuments.prefillStudents.searchLabel') }}</label>
            <input
              id="prefill-student-search"
              v-model="prefillSearch"
              class="form-control"
              type="search"
              autocomplete="off"
              data-testid="admin-prefill-student-search"
              :placeholder="t('adminDocuments.prefillStudents.searchPlaceholder')"
              @input="onPrefillSearchInput"
            />
            <ul
              v-if="prefillCandidates.length"
              class="list-group mt-2"
              data-testid="admin-prefill-student-candidates"
            >
              <li
                v-for="candidate in prefillCandidates"
                :key="candidate.id"
                class="list-group-item d-flex flex-column flex-sm-row align-items-sm-center justify-content-between gap-2"
              >
                <div class="min-w-0">
                  <div class="fw-medium text-truncate">{{ candidate.full_name || candidate.username }}</div>
                  <div class="small text-muted text-break">
                    {{ candidate.matricula || t('adminDocuments.prefillStudents.noMatricula') }}
                    · {{ candidate.email }}
                  </div>
                </div>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-primary flex-shrink-0"
                  :disabled="candidate.already_listed || prefillBusy"
                  data-testid="admin-prefill-student-add"
                  @click="addPrefillStudent(candidate)"
                >
                  {{
                    candidate.already_listed
                      ? t('adminDocuments.prefillStudents.alreadyListed')
                      : t('adminDocuments.prefillStudents.add')
                  }}
                </button>
              </li>
            </ul>
          </div>

          <div class="mb-3">
            <label class="form-label" for="prefill-bulk-text">{{ t('adminDocuments.prefillStudents.bulkLabel') }}</label>
            <textarea
              id="prefill-bulk-text"
              v-model="prefillBulkText"
              class="form-control"
              rows="3"
              data-testid="admin-prefill-bulk-text"
              :placeholder="t('adminDocuments.prefillStudents.bulkPlaceholder')"
            />
            <div class="d-flex flex-wrap gap-2 mt-2">
              <input
                ref="prefillCsvInput"
                class="form-control"
                type="file"
                accept=".csv,.txt,text/csv,text/plain"
                data-testid="admin-prefill-bulk-file"
                @change="onPrefillCsvChosen"
              />
              <button
                type="button"
                class="btn btn-outline-primary"
                :disabled="prefillBusy || (!prefillBulkText.trim() && !prefillBulkFile)"
                data-testid="admin-prefill-bulk-submit"
                @click="submitPrefillBulk"
              >
                {{ t('adminDocuments.prefillStudents.bulkSubmit') }}
              </button>
            </div>
            <div
              v-if="prefillBulkResult"
              class="alert alert-info small mt-2 mb-0"
              data-testid="admin-prefill-bulk-result"
            >
              <div>
                {{
                  t('adminDocuments.prefillStudents.bulkResult', {
                    added: prefillBulkResult.added,
                    already: prefillBulkResult.already_listed,
                  })
                }}
              </div>
              <div v-if="prefillBulkResult.not_found?.length" class="mt-1">
                {{ t('adminDocuments.prefillStudents.bulkNotFound') }}:
                <span class="text-break">{{ prefillBulkResult.not_found.join(', ') }}</span>
              </div>
            </div>
          </div>

          <div
            v-if="prefillActiveFilters?.active"
            class="alert alert-success small mb-3"
            data-testid="admin-prefill-active-filters"
            role="status"
          >
            <div class="d-flex flex-column flex-sm-row align-items-sm-start justify-content-between gap-2">
              <div class="min-w-0">
                <div class="fw-medium" data-testid="admin-prefill-active-filters-title">
                  {{ t('adminDocuments.prefillStudents.activeFiltersTitle') }}
                </div>
                <div class="mt-1" data-testid="admin-prefill-active-filters-summary">
                  {{ activeFiltersSummary }}
                </div>
                <div class="text-muted mt-1">{{ t('adminDocuments.prefillStudents.activeFiltersHelp') }}</div>
              </div>
              <div class="d-flex flex-wrap gap-2 flex-shrink-0">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  :disabled="prefillBusy || prefillFilterBusy"
                  data-testid="admin-prefill-active-filters-edit"
                  @click="editActiveFilters"
                >
                  {{ t('adminDocuments.prefillStudents.activeFiltersEdit') }}
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  :disabled="prefillBusy || prefillFilterBusy"
                  data-testid="admin-prefill-active-filters-clear"
                  @click="clearActiveFilters"
                >
                  {{ t('adminDocuments.prefillStudents.activeFiltersClear') }}
                </button>
              </div>
            </div>
          </div>

          <div class="mb-3 border-top pt-3" data-testid="admin-prefill-filter-panel">
            <h3 class="h6 mb-1">{{ t('adminDocuments.prefillStudents.filterTitle') }}</h3>
            <p class="small text-muted mb-3">{{ t('adminDocuments.prefillStudents.filterHelp') }}</p>
            <div class="row g-2">
              <div class="col-md-4">
                <label class="form-label" for="prefill-filter-domain">{{ t('adminDocuments.prefillStudents.filterDomain') }}</label>
                <select
                  id="prefill-filter-domain"
                  v-model="prefillFilter.domain"
                  class="form-select"
                  data-testid="admin-prefill-filter-domain"
                  @change="clearPrefillFilterPreview"
                >
                  <option value="">{{ t('adminDocuments.prefillStudents.filterDomainAll') }}</option>
                  <option v-for="domain in prefillFilterOptions.domains" :key="domain" :value="domain">
                    @{{ domain }}
                  </option>
                </select>
                <div class="form-text">{{ t('adminDocuments.prefillStudents.filterDomainHint') }}</div>
              </div>
              <div class="col-md-4">
                <label class="form-label" for="prefill-filter-unidad">{{ t('adminDocuments.prefillStudents.filterUnidad') }}</label>
                <select
                  id="prefill-filter-unidad"
                  v-model="prefillFilter.unidad_id"
                  class="form-select"
                  data-testid="admin-prefill-filter-unidad"
                  @change="onPrefillFilterUnidadChange"
                >
                  <option value="">{{ t('adminDocuments.prefillStudents.filterUnidadAll') }}</option>
                  <option v-for="row in prefillFilterOptions.unidades" :key="row.id" :value="row.id">
                    {{ row.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label" for="prefill-filter-school">{{ t('adminDocuments.prefillStudents.filterSchool') }}</label>
                <select
                  id="prefill-filter-school"
                  v-model="prefillFilter.school_id"
                  class="form-select"
                  data-testid="admin-prefill-filter-school"
                  @change="clearPrefillFilterPreview"
                >
                  <option value="">{{ t('adminDocuments.prefillStudents.filterSchoolAll') }}</option>
                  <option v-for="row in filteredPrefillSchools" :key="row.id" :value="row.id">
                    {{ row.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="d-flex flex-wrap gap-2 mt-3">
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="prefillBusy || prefillFilterBusy"
                data-testid="admin-prefill-filter-preview"
                @click="previewPrefillFilter"
              >
                {{ t('adminDocuments.prefillStudents.filterPreview') }}
              </button>
              <button
                type="button"
                class="btn btn-primary"
                :disabled="prefillBusy || prefillFilterBusy || !prefillFilterPreview || !prefillFilterPreview.new_count"
                data-testid="admin-prefill-filter-confirm"
                @click="confirmPrefillFilter"
              >
                {{ t('adminDocuments.prefillStudents.filterConfirm') }}
              </button>
              <button
                type="button"
                class="btn btn-outline-primary"
                :disabled="prefillBusy || prefillFilterBusy"
                data-testid="admin-prefill-filter-save-active"
                @click="saveActiveFilters"
              >
                {{ t('adminDocuments.prefillStudents.filterSaveActive') }}
              </button>
            </div>
            <div
              v-if="prefillFilterPreview"
              class="alert alert-info small mt-2 mb-0"
              data-testid="admin-prefill-filter-preview-result"
            >
              <div>
                {{
                  t('adminDocuments.prefillStudents.filterPreviewSummary', {
                    matched: prefillFilterPreview.matched,
                    newCount: prefillFilterPreview.new_count,
                    already: prefillFilterPreview.already_listed,
                  })
                }}
              </div>
              <div v-if="prefillFilterPreview.samples?.length" class="mt-2">
                <div class="fw-medium">{{ t('adminDocuments.prefillStudents.filterSamples') }}</div>
                <ul class="mb-0 ps-3">
                  <li v-for="sample in prefillFilterPreview.samples" :key="sample.id">
                    {{ sample.full_name || sample.username }}
                    <span class="text-muted">· {{ sample.email }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <ul
            v-if="prefillStudents.length"
            class="list-group"
            data-testid="admin-prefill-student-list"
          >
            <li
              v-for="student in prefillStudents"
              :key="student.id"
              class="list-group-item d-flex flex-column flex-sm-row align-items-sm-center justify-content-between gap-2"
            >
              <div class="min-w-0">
                <div class="fw-medium text-truncate">{{ student.full_name || student.username }}</div>
                <div class="small text-muted text-break">
                  {{ student.matricula || t('adminDocuments.prefillStudents.noMatricula') }}
                  · {{ student.email }}
                </div>
              </div>
              <div class="d-flex flex-wrap gap-2 flex-shrink-0">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  :disabled="prefillBusy || prefillPreviewId === student.id"
                  data-testid="admin-prefill-student-preview"
                  :aria-label="t('adminDocuments.prefillStudents.previewAria', { name: student.full_name || student.username })"
                  @click="previewPrefillStudent(student)"
                >
                  <span
                    v-if="prefillPreviewId === student.id"
                    class="spinner-border spinner-border-sm me-1"
                    role="status"
                    aria-hidden="true"
                  />
                  <i v-else class="bi bi-download me-1" aria-hidden="true"></i>
                  {{ t('adminDocuments.prefillStudents.preview') }}
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  :disabled="prefillBusy || prefillPreviewId === student.id"
                  data-testid="admin-prefill-student-remove"
                  @click="removePrefillStudent(student)"
                >
                  {{ t('adminDocuments.prefillStudents.remove') }}
                </button>
              </div>
            </li>
          </ul>
          <p v-else class="text-muted small mb-0" data-testid="admin-prefill-student-empty">
            {{ t('adminDocuments.prefillStudents.empty') }}
          </p>
        </CollapsibleCard>

        <CollapsibleCard
          test-id="admin-document-requirements"
          :default-open="sectionOpen.workflow"
        >
          <template #title>{{ t('adminDocuments.sections.workflow') }}</template>
          <template v-if="form.program_requirements.length" #header-extra>
            <span class="badge bg-secondary">{{ form.program_requirements.length }}</span>
          </template>
          <p class="small text-muted">{{ t('adminDocuments.workflowHelp') }}</p>
          <div class="row g-2 align-items-end mb-3">
            <div class="col-md-8">
              <label class="form-label">{{ t('adminDocuments.addProgram') }}</label>
              <select v-model="addProgramId" class="form-select" data-testid="admin-document-add-program">
                <option value="">{{ t('adminCommon.notSet') }}</option>
                <option v-for="p in availablePrograms" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <button type="button" class="btn btn-outline-primary w-100" :disabled="!addProgramId" @click="addRequirement">
                {{ t('adminDocuments.addRequirement') }}
              </button>
            </div>
          </div>
          <div class="table-responsive">
            <table class="table table-sm align-middle mb-0">
              <thead>
                <tr>
                  <th>{{ t('adminDocuments.req.program') }}</th>
                  <th>{{ t('adminDocuments.req.requiredFrom') }}</th>
                  <th>{{ t('adminDocuments.req.daysAfterStart') }}</th>
                  <th>{{ t('adminDocuments.req.daysBeforeDeadline') }}</th>
                  <th>{{ t('adminDocuments.req.absolute') }}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!form.program_requirements.length">
                  <td colspan="6" class="text-muted text-center py-3">{{ t('adminDocuments.req.empty') }}</td>
                </tr>
                <tr v-for="(req, idx) in form.program_requirements" :key="req.program">
                  <td>
                    <div class="fw-medium">{{ req.program_name }}</div>
                    <div class="small text-muted">
                      {{ t('adminDocuments.req.resolved', { date: req.resolved_deadline || t('adminCommon.notSet') }) }}
                    </div>
                    <textarea
                      v-model="req.instructions_override"
                      class="form-control form-control-sm mt-1"
                      rows="2"
                      :placeholder="t('adminDocuments.req.instructionsOverride')"
                    />
                  </td>
                  <td>
                    <select
                      v-model="req.required_from_status"
                      class="form-select form-select-sm"
                      data-testid="admin-document-required-from"
                      @change="onRequiredFromChange(req)"
                    >
                      <option value="">{{ t('adminDocuments.req.optionalThroughout') }}</option>
                      <option v-for="st in documentPipelineStatuses" :key="st" :value="st">
                        {{ t(`applicationDetailPage.status.${st}`) }}
                      </option>
                    </select>
                  </td>
                  <td>
                    <input v-model.number="req.deadline_days_after_program_start" class="form-control form-control-sm" type="number" min="0" />
                  </td>
                  <td>
                    <input v-model.number="req.deadline_days_before_program_deadline" class="form-control form-control-sm" type="number" min="0" />
                  </td>
                  <td>
                    <input v-model="req.deadline" class="form-control form-control-sm" type="date" />
                  </td>
                  <td class="text-end">
                    <button type="button" class="btn btn-sm btn-outline-danger" @click="removeRequirement(idx)">
                      {{ t('adminCommon.delete') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CollapsibleCard>
      </div>

      <div class="col-lg-4">
        <CollapsibleCard
          test-id="admin-document-section-merge-fields"
          :default-open="sectionOpen.mergeFields"
          card-class="merge-fields-card"
        >
          <template #title>{{ t('adminDocuments.sections.mergeFields') }}</template>
          <template v-if="mergeFieldCount" #header-extra>
            <span class="badge bg-secondary">{{ mergeFieldCount }}</span>
          </template>
          <p class="small text-muted">{{ t('adminDocuments.mergeFieldsHelp') }}</p>
          <CollapsibleCard
            v-for="group in mergeFieldGroups"
            :key="group.key"
            :test-id="`admin-document-merge-group-${group.key}`"
            :default-open="false"
            compact-header
            :with-margin="false"
            card-class="mb-2 border merge-fields-group"
            title-class="mb-0 small text-uppercase text-muted"
          >
            <template #title>{{ group.label }}</template>
            <template #header-extra>
              <span class="badge bg-light text-dark border">{{ group.fields.length }}</span>
            </template>
            <ul class="list-unstyled small mb-0">
              <li v-for="field in group.fields" :key="field.name" class="mb-1">
                <code>{{ field.name }}</code>
                <span class="text-muted"> — {{ field.description }}</span>
              </li>
            </ul>
          </CollapsibleCard>
        </CollapsibleCard>
        <div class="d-grid">
          <button type="button" class="btn btn-outline-danger" :disabled="saving" @click="confirmDelete">
            {{ t('adminDocuments.deleteType') }}
          </button>
        </div>
      </div>
    </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import FileTypeFamilyPicker from '@/components/FileTypeFamilyPicker.vue'
import CollapsibleCard from '@/components/CollapsibleCard.vue'
import { resolveSectionDefaultsMap } from '@/utils/sectionDefaults'
import {
  filenameFromContentDisposition,
  sanitizeDownloadFilename,
} from '@/utils/documentApi'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const formError = ref(null)
const programs = ref([])
const mergeFields = ref([])
const fileTypeFamilies = ref([])
const addProgramId = ref('')
const templateInput = ref(null)
const pendingTemplate = ref(null)
const templateBusy = ref(false)
const hasTemplate = ref(false)
const templateFilename = ref('')
const prefillStudents = ref([])
const prefillCandidates = ref([])
const prefillSearch = ref('')
const prefillBulkText = ref('')
const prefillBulkFile = ref(null)
const prefillCsvInput = ref(null)
const prefillBulkResult = ref(null)
const prefillBusy = ref(false)
const prefillPreviewId = ref(null)
const prefillFilterBusy = ref(false)
const prefillFilterOptions = ref({ domains: [], unidades: [], schools: [] })
const prefillFilter = ref({ domain: '', unidad_id: '', school_id: '' })
const prefillFilterPreview = ref(null)
const prefillActiveFilters = ref(null)
let prefillSearchTimer = null

const form = ref(emptyForm())
const documentPipelineStatuses = ['submitted', 'under_review', 'nominated', 'approved', 'completed']

/** Admin editor: open task-relevant sections via context; density-first otherwise. */
const EDITOR_SECTION_DEFS = [
  { id: 'identity', openWhen: () => true },
  { id: 'instructions', defaultOpen: false },
  { id: 'constraints', defaultOpen: false },
  { id: 'template', openWhen: () => true },
  {
    id: 'prefillStudents',
    defaultOpen: false,
    openWhen: (ctx) => Boolean(ctx.hasPrefillStudents),
  },
  {
    id: 'workflow',
    defaultOpen: false,
    openWhen: (ctx) => Boolean(ctx.hasRequirements),
  },
  {
    id: 'mergeFields',
    defaultOpen: false,
    openWhen: (ctx) => Boolean(ctx.hasTemplate),
  },
]

const sectionContext = computed(() => ({
  hasTemplate: hasTemplate.value,
  hasRequirements: form.value.program_requirements.length > 0,
  hasPrefillStudents: prefillStudents.value.length > 0 || Boolean(prefillActiveFilters.value?.active),
}))

const activeFiltersSummary = computed(() => {
  const labels = prefillActiveFilters.value?.labels || {}
  const filter = prefillActiveFilters.value?.filter || {}
  const parts = []
  if (labels.domain || filter.domain) {
    parts.push(
      t('adminDocuments.prefillStudents.activeFiltersDomain', {
        domain: labels.domain || filter.domain,
      }),
    )
  }
  if (labels.unidad || filter.unidad_id) {
    parts.push(
      t('adminDocuments.prefillStudents.activeFiltersUnidad', {
        name: labels.unidad || filter.unidad_id,
      }),
    )
  }
  if (labels.school || filter.school_id) {
    parts.push(
      t('adminDocuments.prefillStudents.activeFiltersSchool', {
        name: labels.school || filter.school_id,
      }),
    )
  }
  if (!parts.length) {
    return t('adminDocuments.prefillStudents.activeFiltersAll')
  }
  return parts.join(' · ')
})

const sectionOpen = computed(() =>
  resolveSectionDefaultsMap(EDITOR_SECTION_DEFS, { isAdmin: true }, sectionContext.value),
)

const mergeFieldCount = computed(() => mergeFields.value.length)

const filteredPrefillSchools = computed(() => {
  const schools = prefillFilterOptions.value.schools || []
  const unidadId = prefillFilter.value.unidad_id
  if (!unidadId) return schools
  return schools.filter((row) => !row.unidad_id || String(row.unidad_id) === String(unidadId))
})

function normalizeRequirementRow(row) {
  const requiredFrom = row.is_required === false ? '' : (row.required_from_status || 'submitted')
  return {
    ...row,
    required_from_status: requiredFrom,
    is_required: Boolean(requiredFrom),
  }
}

function onRequiredFromChange(req) {
  req.is_required = Boolean(req.required_from_status)
}

const submissionModes = computed(() => [
  { value: 'upload', label: t('adminDocuments.modes.upload') },
  { value: 'template_download', label: t('adminDocuments.modes.template_download') },
  { value: 'system_generated', label: t('adminDocuments.modes.system_generated') },
  { value: 'instructions_only', label: t('adminDocuments.modes.instructions_only') },
  { value: 'download_only', label: t('adminDocuments.modes.download_only') },
])

const pageTitle = computed(() => form.value.name || t('adminDocuments.editorTitle'))

const availablePrograms = computed(() => {
  const used = new Set(form.value.program_requirements.map((r) => String(r.program)))
  return programs.value.filter((p) => !used.has(String(p.id)))
})

const mergeFieldGroups = computed(() => {
  const groups = [
    { key: 'student', label: t('adminDocuments.mergeGroups.student'), fields: [] },
    { key: 'program', label: t('adminDocuments.mergeGroups.program'), fields: [] },
    { key: 'application', label: t('adminDocuments.mergeGroups.application'), fields: [] },
  ]
  for (const field of mergeFields.value) {
    const group = groups.find((g) => g.key === field.group) || groups[0]
    group.fields.push(field)
  }
  return groups.filter((g) => g.fields.length)
})

function emptyForm() {
  return {
    name: '',
    slug: '',
    description: '',
    submission_mode: 'upload',
    instructions: '',
    faq: '',
    accepted_extensions: '',
    file_type_family_ids: [],
    max_file_size_mb: null,
    allows_multiple: false,
    version_history_visibility: 'inherit',
    version_history_student: false,
    version_history_coordinator: true,
    version_history_admin: true,
    program_requirements: [],
  }
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function emptyToNull(value) {
  if (value === '' || value === undefined || Number.isNaN(value)) return null
  return value
}

async function loadPrefillStudents() {
  const res = await api.get(`/api/document-types/${route.params.id}/prefill-students/`)
  prefillStudents.value = normalizeApiList(res.data)
}

function buildPrefillFilterPayload() {
  const payload = {}
  const domain = String(prefillFilter.value.domain || '').trim()
  const unidadId = String(prefillFilter.value.unidad_id || '').trim()
  const schoolId = String(prefillFilter.value.school_id || '').trim()
  if (domain) payload.domain = domain
  if (unidadId) payload.unidad_id = unidadId
  if (schoolId) payload.school_id = schoolId
  return payload
}

function clearPrefillFilterPreview() {
  prefillFilterPreview.value = null
}

function onPrefillFilterUnidadChange() {
  const unidadId = prefillFilter.value.unidad_id
  const schoolId = prefillFilter.value.school_id
  if (schoolId) {
    const stillValid = filteredPrefillSchools.value.some((row) => String(row.id) === String(schoolId))
    if (!stillValid) prefillFilter.value.school_id = ''
  }
  if (!unidadId) {
    // keep school selection when clearing unidad
  }
  clearPrefillFilterPreview()
}

async function loadPrefillFilterOptions() {
  try {
    const res = await api.get(`/api/document-types/${route.params.id}/prefill-students/filter-options/`)
    prefillFilterOptions.value = {
      domains: Array.isArray(res.data?.domains) ? res.data.domains : [],
      unidades: Array.isArray(res.data?.unidades) ? res.data.unidades : [],
      schools: Array.isArray(res.data?.schools) ? res.data.schools : [],
    }
  } catch (err) {
    console.error('Prefill filter options failed:', err)
    errorToast(t('adminDocuments.prefillStudents.filterOptionsError'))
  }
}

async function loadPrefillActiveFilters() {
  try {
    const res = await api.get(`/api/document-types/${route.params.id}/prefill-students/active-filters/`)
    prefillActiveFilters.value = res.data || { active: false, filter: null, labels: {} }
  } catch (err) {
    console.error('Prefill active filters failed:', err)
    prefillActiveFilters.value = { active: false, filter: null, labels: {} }
  }
}

function applyActiveFiltersToForm(payload) {
  const filter = payload?.filter || {}
  prefillFilter.value = {
    domain: filter.domain || '',
    unidad_id: filter.unidad_id || '',
    school_id: filter.school_id || '',
  }
  clearPrefillFilterPreview()
}

function editActiveFilters() {
  applyActiveFiltersToForm(prefillActiveFilters.value)
  const panel = document.querySelector('[data-testid="admin-prefill-filter-panel"]')
  if (panel && typeof panel.scrollIntoView === 'function') {
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

async function clearActiveFilters() {
  const ok = await confirm({
    title: t('adminDocuments.prefillStudents.activeFiltersClearTitle'),
    message: t('adminDocuments.prefillStudents.activeFiltersClearMessage'),
    confirmText: t('adminDocuments.prefillStudents.activeFiltersClearOk'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  prefillFilterBusy.value = true
  try {
    const res = await api.delete(`/api/document-types/${route.params.id}/prefill-students/active-filters/`)
    prefillActiveFilters.value = res.data || { active: false, filter: null, labels: {} }
    success(t('adminDocuments.prefillStudents.activeFiltersCleared'))
  } catch (err) {
    console.error('Clear active filters failed:', err)
    errorToast(t('adminDocuments.prefillStudents.activeFiltersClearError'))
  } finally {
    prefillFilterBusy.value = false
  }
}

async function saveActiveFilters() {
  const ok = await confirm({
    title: t('adminDocuments.prefillStudents.filterSaveActiveTitle'),
    message: t('adminDocuments.prefillStudents.filterSaveActiveMessage'),
    confirmText: t('adminDocuments.prefillStudents.filterSaveActiveOk'),
    cancelText: t('adminCommon.cancel'),
    variant: 'primary',
  })
  if (!ok) return
  prefillFilterBusy.value = true
  try {
    const res = await api.put(
      `/api/document-types/${route.params.id}/prefill-students/active-filters/`,
      buildPrefillFilterPayload(),
    )
    prefillActiveFilters.value = {
      active: Boolean(res.data?.active),
      filter: res.data?.filter ?? null,
      labels: res.data?.labels || {},
    }
    const added = res.data?.added ?? 0
    await loadPrefillStudents()
    await loadPrefillFilterOptions()
    prefillFilterPreview.value = null
    success(
      t('adminDocuments.prefillStudents.filterSaveActiveToast', {
        added,
      }),
    )
  } catch (err) {
    console.error('Save active filters failed:', err)
    errorToast(t('adminDocuments.prefillStudents.filterSaveActiveError'))
  } finally {
    prefillFilterBusy.value = false
  }
}

async function previewPrefillFilter() {
  prefillFilterBusy.value = true
  prefillFilterPreview.value = null
  try {
    const res = await api.post(
      `/api/document-types/${route.params.id}/prefill-students/filter-preview/`,
      buildPrefillFilterPayload(),
    )
    prefillFilterPreview.value = res.data || {
      matched: 0,
      new_count: 0,
      already_listed: 0,
      samples: [],
    }
  } catch (err) {
    console.error('Prefill filter preview failed:', err)
    errorToast(t('adminDocuments.prefillStudents.filterPreviewError'))
  } finally {
    prefillFilterBusy.value = false
  }
}

async function confirmPrefillFilter() {
  const preview = prefillFilterPreview.value
  if (!preview?.new_count) {
    errorToast(t('adminDocuments.prefillStudents.filterNothingNew'))
    return
  }
  const ok = await confirm({
    title: t('adminDocuments.prefillStudents.filterConfirmTitle'),
    message: t('adminDocuments.prefillStudents.filterConfirmMessage', {
      newCount: preview.new_count,
      matched: preview.matched,
    }),
    confirmText: t('adminDocuments.prefillStudents.filterConfirmOk'),
    cancelText: t('adminCommon.cancel'),
    variant: 'primary',
  })
  if (!ok) return
  prefillFilterBusy.value = true
  try {
    const res = await api.post(
      `/api/document-types/${route.params.id}/prefill-students/filter-confirm/`,
      buildPrefillFilterPayload(),
    )
    const added = res.data?.added ?? 0
    if (res.data?.active_filters) {
      prefillActiveFilters.value = res.data.active_filters
    } else {
      await loadPrefillActiveFilters()
    }
    await loadPrefillStudents()
    await loadPrefillFilterOptions()
    prefillFilterPreview.value = null
    success(t('adminDocuments.prefillStudents.filterToastAdded', { added }))
  } catch (err) {
    console.error('Prefill filter confirm failed:', err)
    errorToast(t('adminDocuments.prefillStudents.filterConfirmError'))
  } finally {
    prefillFilterBusy.value = false
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const [typeRes, programRes, fieldsRes, familyRes, prefillRes, filterOptsRes, activeFiltersRes] =
      await Promise.all([
      api.get(`/api/document-types/${route.params.id}/`),
      api.get('/api/programs/', { params: { ordering: 'name', page_size: 100 } }),
      api.get('/api/document-types/merge-fields/'),
      api.get('/api/document-types/file-type-families/'),
      api.get(`/api/document-types/${route.params.id}/prefill-students/`),
      api.get(`/api/document-types/${route.params.id}/prefill-students/filter-options/`).catch(() => null),
      api.get(`/api/document-types/${route.params.id}/prefill-students/active-filters/`).catch(() => null),
    ])
    const dt = typeRes.data || {}
    form.value = {
      name: dt.name || '',
      slug: dt.slug || '',
      description: dt.description || '',
      submission_mode: dt.submission_mode || 'upload',
      instructions: dt.instructions || '',
      faq: dt.faq || '',
      accepted_extensions: dt.accepted_extensions || '',
      file_type_family_ids: (dt.file_type_family_ids || (dt.file_type_families || []).map((f) => f.id)).map(
        (id) => Number(id),
      ),
      max_file_size_mb: dt.max_file_size_mb,
      allows_multiple: Boolean(dt.allows_multiple),
      version_history_visibility: dt.version_history_visibility || 'inherit',
      version_history_student: dt.version_history_student ?? false,
      version_history_coordinator: dt.version_history_coordinator ?? true,
      version_history_admin: dt.version_history_admin ?? true,
      program_requirements: (dt.program_requirements || []).map((row) => normalizeRequirementRow(row)),
    }
    hasTemplate.value = Boolean(dt.has_template)
    templateFilename.value = dt.template_filename || ''
    programs.value = normalizeApiList(programRes.data)
    mergeFields.value = fieldsRes.data?.fields || []
    fileTypeFamilies.value = normalizeApiList(familyRes.data)
    prefillStudents.value = normalizeApiList(prefillRes.data)
    if (filterOptsRes?.data) {
      prefillFilterOptions.value = {
        domains: Array.isArray(filterOptsRes.data.domains) ? filterOptsRes.data.domains : [],
        unidades: Array.isArray(filterOptsRes.data.unidades) ? filterOptsRes.data.unidades : [],
        schools: Array.isArray(filterOptsRes.data.schools) ? filterOptsRes.data.schools : [],
      }
    }
    prefillActiveFilters.value = activeFiltersRes?.data || {
      active: false,
      filter: null,
      labels: {},
    }
  } catch (err) {
    console.error('Failed to load document type:', err)
    error.value = t('adminDocuments.loadDetailError')
  } finally {
    loading.value = false
  }
}

function onPrefillSearchInput() {
  clearTimeout(prefillSearchTimer)
  prefillSearchTimer = setTimeout(searchPrefillCandidates, 300)
}

async function searchPrefillCandidates() {
  const q = prefillSearch.value.trim()
  if (!q) {
    prefillCandidates.value = []
    return
  }
  try {
    const res = await api.get(`/api/document-types/${route.params.id}/prefill-students/candidates/`, {
      params: { search: q },
    })
    prefillCandidates.value = normalizeApiList(res.data)
  } catch (err) {
    console.error('Prefill student search failed:', err)
    prefillCandidates.value = []
  }
}

async function addPrefillStudent(candidate) {
  if (!candidate?.id || candidate.already_listed) return
  prefillBusy.value = true
  try {
    await api.post(`/api/document-types/${route.params.id}/prefill-students/`, {
      user_id: candidate.id,
    })
    await loadPrefillStudents()
    prefillCandidates.value = prefillCandidates.value.map((row) =>
      row.id === candidate.id ? { ...row, already_listed: true } : row,
    )
    success(t('adminDocuments.prefillStudents.toastAdded'))
  } catch (err) {
    console.error('Add prefill student failed:', err)
    errorToast(t('adminDocuments.prefillStudents.addError'))
  } finally {
    prefillBusy.value = false
  }
}

async function removePrefillStudent(student) {
  if (!student?.id) return
  prefillBusy.value = true
  try {
    await api.delete(`/api/document-types/${route.params.id}/prefill-students/${student.id}/`)
    prefillStudents.value = prefillStudents.value.filter((row) => row.id !== student.id)
    success(t('adminDocuments.prefillStudents.toastRemoved'))
  } catch (err) {
    console.error('Remove prefill student failed:', err)
    errorToast(t('adminDocuments.prefillStudents.removeError'))
  } finally {
    prefillBusy.value = false
  }
}

function prefillPreviewFilename(student) {
  const typePart = sanitizeDownloadFilename(
    form.value.slug || form.value.name || templateFilename.value || 'template',
    'template',
  )
  const studentPart = sanitizeDownloadFilename(
    student?.username || student?.matricula || student?.full_name || student?.id,
    'student',
  )
  return `${typePart}-${studentPart}.docx`
}

async function previewPrefillStudent(student) {
  if (!student?.id || prefillPreviewId.value === student.id) return
  prefillPreviewId.value = student.id
  try {
    const response = await api.get(
      `/api/document-types/${route.params.id}/download-template/`,
      {
        params: { student: student.id },
        responseType: 'blob',
      },
    )
    const blob = new Blob([response.data], {
      type: response.headers?.['content-type'] || 'application/octet-stream',
    })
    const objectUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = objectUrl
    a.download = filenameFromContentDisposition(
      response.headers?.['content-disposition'],
      prefillPreviewFilename(student),
    )
    a.rel = 'noopener noreferrer'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(objectUrl)
  } catch (err) {
    console.error('Prefill student preview failed:', err)
    errorToast(t('adminDocuments.prefillStudents.previewError'))
  } finally {
    prefillPreviewId.value = null
  }
}

function onPrefillCsvChosen(event) {
  prefillBulkFile.value = event.target.files?.[0] || null
}

async function submitPrefillBulk() {
  prefillBusy.value = true
  prefillBulkResult.value = null
  try {
    let res
    if (prefillBulkFile.value) {
      const data = new FormData()
      data.append('file', prefillBulkFile.value)
      if (prefillBulkText.value.trim()) data.append('text', prefillBulkText.value)
      res = await api.post(`/api/document-types/${route.params.id}/prefill-students/bulk/`, data)
    } else {
      res = await api.post(`/api/document-types/${route.params.id}/prefill-students/bulk/`, {
        text: prefillBulkText.value,
      })
    }
    prefillBulkResult.value = res.data || { added: 0, already_listed: 0, not_found: [] }
    await loadPrefillStudents()
    prefillBulkText.value = ''
    prefillBulkFile.value = null
    if (prefillCsvInput.value) prefillCsvInput.value.value = ''
  } catch (err) {
    console.error('Bulk prefill add failed:', err)
    errorToast(t('adminDocuments.prefillStudents.bulkError'))
  } finally {
    prefillBusy.value = false
  }
}

function addRequirement() {
  const program = programs.value.find((p) => String(p.id) === String(addProgramId.value))
  if (!program) return
  form.value.program_requirements.push({
    program: program.id,
    program_name: program.name,
    is_required: true,
    required_from_status: 'submitted',
    deadline: null,
    deadline_days_before_program_deadline: null,
    deadline_days_after_program_start: null,
    instructions_override: '',
    sort_order: form.value.program_requirements.length,
    resolved_deadline: null,
  })
  addProgramId.value = ''
}

function removeRequirement(idx) {
  form.value.program_requirements.splice(idx, 1)
}

function onTemplateChosen(event) {
  pendingTemplate.value = event.target.files?.[0] || null
}

async function uploadTemplate() {
  if (!pendingTemplate.value) return
  templateBusy.value = true
  try {
    const data = new FormData()
    data.append('template_file', pendingTemplate.value)
    const res = await api.post(`/api/document-types/${route.params.id}/upload-template/`, data)
    hasTemplate.value = Boolean(res.data?.has_template)
    templateFilename.value = res.data?.template_filename || pendingTemplate.value.name
    pendingTemplate.value = null
    if (templateInput.value) templateInput.value.value = ''
    success(t('adminDocuments.toastTemplateUploaded'))
  } catch (err) {
    console.error('Template upload failed:', err)
    errorToast(t('adminDocuments.templateUploadError'))
  } finally {
    templateBusy.value = false
  }
}

async function removeTemplate() {
  templateBusy.value = true
  try {
    await api.delete(`/api/document-types/${route.params.id}/template/`)
    hasTemplate.value = false
    templateFilename.value = ''
    success(t('adminDocuments.toastTemplateRemoved'))
  } catch (err) {
    console.error('Template remove failed:', err)
    errorToast(t('adminDocuments.templateRemoveError'))
  } finally {
    templateBusy.value = false
  }
}

async function save() {
  formError.value = null
  saving.value = true
  const hadPendingTemplate = Boolean(pendingTemplate.value)
  try {
    const payload = {
      name: form.value.name,
      slug: form.value.slug || null,
      description: form.value.description,
      submission_mode: form.value.submission_mode,
      instructions: form.value.instructions,
      faq: form.value.faq,
      accepted_extensions: form.value.accepted_extensions,
      file_type_family_ids: form.value.file_type_family_ids,
      max_file_size_mb: emptyToNull(form.value.max_file_size_mb),
      allows_multiple: Boolean(form.value.allows_multiple),
      version_history_visibility: form.value.version_history_visibility || 'inherit',
      version_history_student:
        form.value.version_history_visibility === 'custom'
          ? Boolean(form.value.version_history_student)
          : null,
      version_history_coordinator:
        form.value.version_history_visibility === 'custom'
          ? Boolean(form.value.version_history_coordinator)
          : null,
      version_history_admin:
        form.value.version_history_visibility === 'custom'
          ? Boolean(form.value.version_history_admin)
          : null,
      program_requirements: form.value.program_requirements.map((row, idx) => ({
        id: row.id || undefined,
        program: row.program,
        is_required: Boolean(row.required_from_status),
        required_from_status: row.required_from_status || null,
        deadline: emptyToNull(row.deadline),
        deadline_days_before_program_deadline: emptyToNull(row.deadline_days_before_program_deadline),
        deadline_days_after_program_start: emptyToNull(row.deadline_days_after_program_start),
        instructions_override: row.instructions_override || '',
        sort_order: idx,
      })),
    }
    const res = await api.patch(`/api/document-types/${route.params.id}/`, payload)
    form.value.program_requirements = (res.data.program_requirements || []).map((row) =>
      normalizeRequirementRow(row),
    )

    if (hadPendingTemplate && pendingTemplate.value) {
      templateBusy.value = true
      try {
        const data = new FormData()
        data.append('template_file', pendingTemplate.value)
        const uploadRes = await api.post(
          `/api/document-types/${route.params.id}/upload-template/`,
          data,
        )
        hasTemplate.value = Boolean(uploadRes.data?.has_template)
        templateFilename.value = uploadRes.data?.template_filename || pendingTemplate.value.name
        pendingTemplate.value = null
        if (templateInput.value) templateInput.value.value = ''
        success(t('adminDocuments.toastSavedWithTemplate'))
      } catch (uploadErr) {
        console.error('Template upload failed after save:', uploadErr)
        errorToast(t('adminDocuments.templateNotSavedAfterSave'))
      } finally {
        templateBusy.value = false
      }
    } else {
      success(t('adminDocuments.toastSaved'))
    }
  } catch (err) {
    console.error('Failed to save document type:', err)
    formError.value = t('adminDocuments.saveError')
    errorToast(t('adminDocuments.saveToastError'))
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminDocuments.deleteConfirm', { name: form.value.name || '' }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await api.delete(`/api/document-types/${route.params.id}/`)
    success(t('adminDocuments.toastDeleted'))
    await router.push({ name: 'AdminDocuments' })
  } catch (err) {
    console.error('Failed to delete document type:', err)
    errorToast(t('adminDocuments.deleteToastError'))
  } finally {
    saving.value = false
  }
}

function onBeforeUnload(event) {
  if (!pendingTemplate.value) return
  event.preventDefault()
  event.returnValue = ''
}

onBeforeRouteLeave(async () => {
  if (!pendingTemplate.value) return true
  const ok = await confirm({
    title: t('adminDocuments.templatePendingLeaveTitle'),
    message: t('adminDocuments.templatePendingLeaveMessage'),
    confirmText: t('adminDocuments.templatePendingLeaveConfirm'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  return ok
})

onMounted(() => {
  window.addEventListener('beforeunload', onBeforeUnload)
  load()
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', onBeforeUnload)
})
</script>

<style scoped>
.admin-document-type-edit {
  min-height: 60vh;
}

.merge-fields-group :deep(.card-header) {
  background-color: transparent;
}
</style>
