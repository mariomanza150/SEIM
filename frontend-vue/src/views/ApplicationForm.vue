<template>
  <div class="application-form-page">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav :aria-label="t('applicationFormPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Applications' }">{{ t('route.names.Applications') }}</router-link>
          </li>
          <li class="breadcrumb-item active">
            {{ isEditMode ? t('applicationFormPage.breadcrumbEdit') : t('applicationFormPage.breadcrumbNew') }}
          </li>
        </ol>
      </nav>

      <!-- Header -->
      <div class="row mb-4">
        <div class="col-md-8">
          <h2>
            <i class="bi bi-file-earmark-plus me-2"></i>
            {{ isEditMode ? t('applicationFormPage.titleEdit') : t('applicationFormPage.titleNew') }}
          </h2>
          <p class="text-muted">
            {{ isEditMode ? t('applicationFormPage.subtitleEdit') : t('applicationFormPage.subtitleNew') }}
          </p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('applicationFormPage.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ loadingMessage }}</p>
      </div>

      <!-- Form -->
      <div v-else class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <form data-testid="application-form" @submit.prevent="handleSubmit">
                <!-- Program Selection -->
                <div class="mb-4">
                  <label for="program" class="form-label">
                    {{ t('applicationFormPage.programLabel') }} <span class="text-danger">*</span>
                  </label>
                  <div v-if="!isEditMode" class="card mb-3 border-0 bg-light">
                    <div class="card-body py-3">
                      <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
                        <span class="small text-muted fw-semibold">{{ t('applicationFormPage.filterPrograms') }}</span>
                        <button
                          type="button"
                          class="btn btn-link btn-sm p-0"
                          @click="clearProgramFilters"
                        >
                          {{ t('applicationFormPage.clearFilters') }}
                        </button>
                      </div>
                      <div class="row g-2">
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-search">{{ t('applicationFormPage.search') }}</label>
                          <input
                            id="program-filter-search"
                            v-model="programFilters.search"
                            type="search"
                            class="form-control form-control-sm"
                            :placeholder="t('applicationFormPage.programSearchPlaceholder')"
                            autocomplete="off"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-ordering">{{ t('applicationFormPage.sortBy') }}</label>
                          <select
                            id="program-filter-ordering"
                            v-model="programFilters.ordering"
                            class="form-select form-select-sm"
                          >
                            <option value="name">{{ t('applicationFormPage.sortNameAZ') }}</option>
                            <option value="-start_date">{{ t('applicationFormPage.sortStartNewest') }}</option>
                            <option value="start_date">{{ t('applicationFormPage.sortStartSoonest') }}</option>
                            <option value="-end_date">{{ t('applicationFormPage.sortEndLatest') }}</option>
                          </select>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-language">{{ t('applicationFormPage.requiredLanguage') }}</label>
                          <input
                            id="program-filter-language"
                            v-model="programFilters.required_language"
                            type="text"
                            class="form-control form-control-sm"
                            :placeholder="t('applicationFormPage.languagePlaceholder')"
                            autocomplete="off"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-cefr">{{ t('applicationFormPage.minLanguageLevel') }}</label>
                          <select
                            id="program-filter-cefr"
                            v-model="programFilters.min_language_level"
                            class="form-select form-select-sm"
                          >
                            <option value="">{{ t('applicationFormPage.any') }}</option>
                            <option value="A1">A1</option>
                            <option value="A2">A2</option>
                            <option value="B1">B1</option>
                            <option value="B2">B2</option>
                            <option value="C1">C1</option>
                            <option value="C2">C2</option>
                          </select>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-start-after">{{ t('applicationFormPage.programStartsAfter') }}</label>
                          <input
                            id="program-filter-start-after"
                            v-model="programFilters.start_date_after"
                            type="date"
                            class="form-control form-control-sm"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-start-before">{{ t('applicationFormPage.programStartsBefore') }}</label>
                          <input
                            id="program-filter-start-before"
                            v-model="programFilters.start_date_before"
                            type="date"
                            class="form-control form-control-sm"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-gpa">{{ t('applicationFormPage.myGpa') }}</label>
                          <input
                            id="program-filter-gpa"
                            v-model="programFilters.min_gpa_max"
                            type="number"
                            step="0.1"
                            min="0"
                            max="4"
                            class="form-control form-control-sm"
                            :placeholder="t('applicationFormPage.gpaPlaceholder')"
                          >
                        </div>
                        <div class="col-md-6 d-flex align-items-end">
                          <div class="form-check mb-0">
                            <input
                              id="program-filter-accepting"
                              v-model="programFilters.accepting_applications"
                              class="form-check-input"
                              type="checkbox"
                            >
                            <label class="form-check-label small" for="program-filter-accepting">
                              {{ t('applicationFormPage.acceptingNow') }}
                            </label>
                          </div>
                        </div>
                      </div>
                      <p v-if="programsLoading" class="small text-muted mb-0 mt-2" data-testid="programs-filter-loading">
                        {{ t('applicationFormPage.updatingProgramList') }}
                      </p>
                      <p v-else class="small text-muted mb-0 mt-2">
                        {{
                          programs.length === 1
                            ? t('applicationFormPage.programsMatchOne')
                            : t('applicationFormPage.programsMatchMany', { n: programs.length })
                        }}
                      </p>
                      <div class="border-top pt-3 mt-3">
                        <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                          <div class="flex-grow-1" style="min-width: 200px">
                            <label class="form-label small text-muted mb-1">{{ t('applicationFormPage.savePresetLabel') }}</label>
                            <div class="input-group input-group-sm">
                              <input
                                v-model="newPresetName"
                                type="text"
                                class="form-control"
                                :placeholder="t('applicationFormPage.presetNamePlaceholder')"
                                data-testid="program-filter-preset-name"
                              >
                              <button
                                type="button"
                                class="btn btn-outline-primary"
                                :disabled="!newPresetName.trim() || presetsLoading"
                                data-testid="program-filter-preset-save"
                                @click="saveProgramFilterPreset"
                              >
                                {{ t('applicationFormPage.save') }}
                              </button>
                            </div>
                          </div>
                          <div class="form-check mb-1">
                            <input
                              id="program-preset-default"
                              v-model="saveAsDefault"
                              class="form-check-input"
                              type="checkbox"
                            >
                            <label class="form-check-label small" for="program-preset-default">
                              {{ t('applicationFormPage.defaultNewApplication') }}
                            </label>
                          </div>
                        </div>
                        <div v-if="savedPresets.length" class="small">
                          <span class="text-muted me-2">{{ t('applicationFormPage.savedPresetsPrefix') }}</span>
                          <span
                            v-for="p in savedPresets"
                            :key="p.id"
                            class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                          >
                            <button
                              type="button"
                              class="btn btn-link btn-sm p-0"
                              data-testid="program-filter-preset-apply"
                              @click="applyProgramFilterPreset(p)"
                            >
                              {{ p.name }}
                            </button>
                            <i
                              v-if="p.is_default"
                              class="bi bi-star-fill text-warning"
                              :title="t('applicationFormPage.defaultPresetTitle')"
                              :aria-label="t('applicationFormPage.defaultPresetAria')"
                            />
                            <button
                              v-else
                              type="button"
                              class="btn btn-link btn-sm p-0 text-secondary"
                              :title="t('applicationFormPage.setDefaultTitle')"
                              :aria-label="t('applicationFormPage.setDefaultAria')"
                              @click="setDefaultPreset(p)"
                            >
                              <i class="bi bi-star" />
                            </button>
                            <button
                              type="button"
                              class="btn btn-link btn-sm p-0 text-danger"
                              :title="t('applicationFormPage.removePresetTitle')"
                              :aria-label="t('applicationFormPage.removePresetAria')"
                              @click="deletePreset(p)"
                            >
                              <i class="bi bi-trash" />
                            </button>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <select
                    id="program"
                    v-model="form.program"
                    class="form-select"
                    :class="{ 'is-invalid': programErrors.length }"
                    required
                    :disabled="isEditMode"
                    data-testid="program-select"
                  >
                    <option value="">{{ t('applicationFormPage.selectProgram') }}</option>
                    <option v-for="program in programs" :key="program.id" :value="program.id">
                      {{ program.name }}
                    </option>
                  </select>
                  <div v-if="programErrors.length" class="alert alert-danger mt-2 mb-0" role="alert" data-testid="eligibility-alert">
                    <h6 class="alert-heading mb-2">
                      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ t('applicationFormPage.eligibilityHeading') }}
                    </h6>
                    <ul class="mb-0 ps-3">
                      <li v-for="(msg, i) in programErrors" :key="i">{{ msg }}</li>
                    </ul>
                  </div>
                  <div v-else class="form-text">
                    {{ isEditMode ? t('applicationFormPage.programHelpEdit') : t('applicationFormPage.programHelpNew') }}
                  </div>
                </div>

                <!-- Selected Program Info -->
                <div v-if="selectedProgram" class="alert alert-info mb-4">
                  <h6 class="alert-heading">
                    <i class="bi bi-info-circle me-2"></i>{{ t('applicationFormPage.programInformation') }}
                  </h6>
                  <p class="mb-2"><strong>{{ selectedProgram.name }}</strong></p>
                  <p class="small mb-2">{{ selectedProgram.description }}</p>
                  <div class="row small">
                    <div class="col-md-6">
                      <strong>{{ t('applicationFormPage.startDate') }}:</strong> {{ formatDate(selectedProgram.start_date) }}
                    </div>
                    <div class="col-md-6">
                      <strong>{{ t('applicationFormPage.endDate') }}:</strong> {{ formatDate(selectedProgram.end_date) }}
                    </div>
                  </div>
                  <div
                    v-if="selectedProgram.application_open_date || selectedProgram.application_deadline"
                    class="row small mt-2"
                  >
                    <div class="col-md-6" v-if="selectedProgram.application_open_date">
                      <strong>{{ t('applicationFormPage.applicationsOpen') }}:</strong> {{ formatDate(selectedProgram.application_open_date) }}
                    </div>
                    <div class="col-md-6" v-if="selectedProgram.application_deadline">
                      <strong>{{ t('applicationFormPage.applyBy') }}:</strong> {{ formatDate(selectedProgram.application_deadline) }}
                    </div>
                  </div>
                  <div v-if="selectedProgram.min_gpa" class="mt-2 small">
                    <strong>{{ t('applicationFormPage.requirements') }}:</strong> {{ t('applicationFormPage.minGpa') }}: {{ selectedProgram.min_gpa }}
                    <span v-if="selectedProgram.required_language">
                      | {{ selectedProgram.required_language }} ({{ selectedProgram.min_language_level }})
                    </span>
                  </div>
                  <div
                    v-if="selectedProgram.enrollment_capacity != null && selectedProgram.enrollment_capacity !== undefined"
                    class="mt-2 small"
                  >
                    <strong>{{ t('applicationFormPage.enrollment') }}:</strong>
                    {{
                      t('applicationFormPage.seatHoldingApps', {
                        occupied: selectedProgram.enrollment_seats_occupied ?? 0,
                        capacity: selectedProgram.enrollment_capacity,
                      })
                    }}
                    <span v-if="(selectedProgram.enrollment_slots_remaining ?? 0) === 0">
                      <span v-if="selectedProgram.waitlist_when_full" class="text-warning">
                        {{ t('applicationFormPage.waitlistWhenFull') }}
                      </span>
                      <span v-else class="text-danger">{{ t('applicationFormPage.programFull') }}</span>
                    </span>
                  </div>
                </div>

                <div
                  v-if="applicationWindowState && !applicationWindowState.canApply && !isEditMode"
                  class="alert mb-4"
                  :class="applicationWindowState.reason === 'not_open_yet' ? 'alert-info' : 'alert-warning'"
                  data-testid="application-window-alert"
                >
                  <h6 class="alert-heading mb-2">
                    <i class="bi bi-clock-history me-2"></i>{{ t('applicationFormPage.windowUnavailable') }}
                  </h6>
                  <p class="mb-0">{{ applicationWindowState.message }}</p>
                </div>

                <!-- Dynamic Program Form -->
                <div v-if="dynamicFormLoading" class="alert alert-light border mb-4" data-testid="dynamic-form-loading">
                  <div class="d-flex align-items-center">
                    <span class="spinner-border spinner-border-sm text-primary me-2" aria-hidden="true"></span>
                    <span>{{ t('applicationFormPage.loadingDynamicQuestions') }}</span>
                  </div>
                </div>

                <div v-else-if="dynamicFormLoadError" class="alert alert-warning mb-4" data-testid="dynamic-form-load-error">
                  {{ dynamicFormLoadError }}
                </div>

                <div v-else-if="hasDynamicFields" class="mb-4" data-testid="dynamic-form-section">
                  <div class="d-flex align-items-center justify-content-between mb-3">
                    <div>
                      <h5 class="mb-1">{{ t('applicationFormPage.programQuestions') }}</h5>
                      <p v-if="dynamicForm.description" class="text-muted small mb-0">
                        {{ dynamicForm.description }}
                      </p>
                      <p v-if="isMultiStep" class="text-muted small mb-0 mt-1">
                        {{
                          t('applicationFormPage.stepProgress', {
                            current: currentStepIndex + 1,
                            total: visibleFormSteps.length,
                          })
                        }}
                        <span v-if="currentStepTitle"> — {{ currentStepTitle }}</span>
                      </p>
                    </div>
                    <span class="badge bg-light text-dark border">
                      {{
                        visibleDynamicFields.length === 1
                          ? t('applicationFormPage.fieldCountOne', { n: visibleDynamicFields.length })
                          : t('applicationFormPage.fieldCountMany', { n: visibleDynamicFields.length })
                      }}
                      <span v-if="stepScopedDynamicFields.length">{{ t('applicationFormPage.stepFieldSep') }}{{ stepScopedDynamicFields.length }}</span>
                    </span>
                  </div>

                  <div v-if="isMultiStep" class="d-flex gap-2 mb-3">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-secondary"
                      :disabled="currentStepIndex === 0"
                      data-testid="dynamic-step-prev"
                      @click="goToPreviousStep"
                    >
                      <i class="bi bi-chevron-left me-1"></i>{{ t('applicationFormPage.back') }}
                    </button>
                  </div>

                  <div
                    v-for="field in visibleDynamicFields"
                    :key="field.name"
                    class="mb-4"
                  >
                    <label
                      :for="`dynamic-field-${field.name}`"
                      class="form-label"
                    >
                      {{ field.label }}
                      <span v-if="field.required" class="text-danger">*</span>
                    </label>

                    <textarea
                      v-if="isTextareaField(field)"
                      :id="`dynamic-field-${field.name}`"
                      v-model="dynamicFormValues[field.name]"
                      class="form-control"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :rows="getTextareaRows(field)"
                      :placeholder="getFieldPlaceholder(field)"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    ></textarea>

                    <select
                      v-else-if="isSelectField(field)"
                      :id="`dynamic-field-${field.name}`"
                      v-model="dynamicFormValues[field.name]"
                      class="form-select"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    >
                      <option value="">{{ t('applicationFormPage.selectOption') }}</option>
                      <option
                        v-for="option in getFieldOptions(field)"
                        :key="option"
                        :value="option"
                      >
                        {{ option }}
                      </option>
                    </select>

                    <div
                      v-else-if="isArrayField(field)"
                      class="border rounded p-3"
                      :class="{ 'border-danger': dynamicFieldErrors[field.name] }"
                      :data-testid="`dynamic-field-${field.name}`"
                    >
                      <div
                        v-for="option in getFieldOptions(field)"
                        :key="option"
                        class="form-check"
                      >
                        <input
                          :id="`dynamic-field-${field.name}-${option}`"
                          v-model="dynamicFormValues[field.name]"
                          class="form-check-input"
                          type="checkbox"
                          :value="option"
                        />
                        <label
                          class="form-check-label"
                          :for="`dynamic-field-${field.name}-${option}`"
                        >
                          {{ option }}
                        </label>
                      </div>
                    </div>

                    <div
                      v-else-if="isBooleanField(field)"
                      class="form-check"
                    >
                      <input
                        :id="`dynamic-field-${field.name}`"
                        v-model="dynamicFormValues[field.name]"
                        class="form-check-input"
                        type="checkbox"
                        :data-testid="`dynamic-field-${field.name}`"
                      />
                      <label
                        class="form-check-label"
                        :for="`dynamic-field-${field.name}`"
                      >
                        {{ field.description || t('applicationFormPage.booleanYes') }}
                      </label>
                    </div>

                    <input
                      v-else-if="isNumericField(field)"
                      :id="`dynamic-field-${field.name}`"
                      v-model.number="dynamicFormValues[field.name]"
                      class="form-control"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :type="getInputType(field)"
                      :min="field.config.minimum"
                      :max="field.config.maximum"
                      :placeholder="getFieldPlaceholder(field)"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    />

                    <input
                      v-else
                      :id="`dynamic-field-${field.name}`"
                      v-model="dynamicFormValues[field.name]"
                      class="form-control"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :type="getInputType(field)"
                      :placeholder="getFieldPlaceholder(field)"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    />

                    <div v-if="dynamicFieldErrors[field.name]" class="invalid-feedback d-block">
                      {{ dynamicFieldErrors[field.name] }}
                    </div>
                    <div v-else-if="field.description && !isBooleanField(field)" class="form-text">
                      {{ field.description }}
                    </div>
                  </div>

                  <div
                    v-if="isMultiStep && hasCurrentStepDocumentRequirements"
                    class="alert alert-light border mb-0 mt-4"
                    data-testid="dynamic-step-documents"
                  >
                    <h6 class="small fw-semibold mb-2">
                      <i class="bi bi-file-earmark-arrow-up me-1"></i>{{ t('applicationFormPage.documentsThisStep') }}
                    </h6>
                    <p class="small text-muted mb-2 mb-md-3">
                      {{ t('applicationFormPage.documentsStepHint') }}
                    </p>
                    <ul class="list-group list-group-flush small mb-3 border rounded">
                      <li
                        v-for="row in currentStepDocumentTypesDisplay"
                        :key="row.id"
                        class="list-group-item d-flex justify-content-between align-items-center px-3 py-2"
                      >
                        <span>{{ row.name }}</span>
                        <span :class="documentStepStatusClass(row.status)">
                          {{ documentStepStatusLabel(row.status) }}
                        </span>
                      </li>
                    </ul>
                    <router-link
                      v-if="isEditMode && route.params.id"
                      :to="{ name: 'ApplicationDetail', params: { id: route.params.id } }"
                      class="btn btn-sm btn-outline-primary"
                    >
                      <i class="bi bi-folder2-open me-1"></i>{{ t('applicationFormPage.openApplicationDocs') }}
                    </router-link>
                    <p v-else class="small text-muted mb-0">
                      {{ t('applicationFormPage.saveOnceForDocs') }}
                    </p>
                  </div>
                </div>

                <div v-else-if="selectedProgram" class="alert alert-light border mb-4" data-testid="dynamic-form-empty">
                  {{ t('applicationFormPage.noDynamicQuestions') }}
                </div>

                <div v-if="dynamicFormErrors.length" class="alert alert-danger">
                  <h6 class="alert-heading">{{ t('applicationFormPage.validationFailedHeading') }}</h6>
                  <ul class="mb-0 ps-3">
                    <li v-for="(message, index) in dynamicFormErrors" :key="index">{{ message }}</li>
                  </ul>
                </div>

                <!-- Other field errors -->
                <div v-if="otherErrors.length" class="alert alert-danger">
                  <h6 class="alert-heading">{{ t('applicationFormPage.fixFollowingHeading') }}</h6>
                  <ul class="mb-0 ps-3">
                    <li v-for="(text, i) in otherErrors" :key="i">{{ text }}</li>
                  </ul>
                </div>

                <!-- Actions -->
                <div class="d-flex justify-content-between">
                  <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary" data-testid="cancel-link">
                    <i class="bi bi-x-circle me-2"></i>{{ t('applicationFormPage.cancel') }}
                  </router-link>
                  <div>
                    <button
                      type="button"
                      class="btn btn-outline-primary me-2"
                      @click="saveDraft"
                      :disabled="submitting || !form.program || dynamicFormLoading || createBlockedByWindow"
                      data-testid="save-draft-btn"
                    >
                      <i class="bi bi-save me-2"></i>{{ t('applicationFormPage.saveDraft') }}
                    </button>
                    <button
                      type="submit"
                      class="btn btn-primary"
                      :disabled="submitting || !form.program || dynamicFormLoading || createBlockedByWindow"
                      data-testid="create-application-btn"
                    >
                      <span v-if="submitting">
                        <span class="spinner-border spinner-border-sm me-2"></span>
                        {{ isEditMode ? t('applicationFormPage.submitUpdating') : t('applicationFormPage.submitCreating') }}
                      </span>
                      <span v-else>
                        <i class="bi bi-check-circle me-2"></i>
                        <template v-if="isMultiStep && !isLastStep">
                          {{ t('applicationFormPage.saveContinue') }}
                        </template>
                        <template v-else>
                          {{ isEditMode ? t('applicationFormPage.updateApplication') : t('applicationFormPage.createApplication') }}
                        </template>
                      </span>
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-lg-4">
          <!-- Tips -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-lightbulb me-2"></i>{{ t('applicationFormPage.tipsTitle') }}</h6>
            </div>
            <div class="card-body">
              <ul class="small mb-0">
                <li>{{ t('applicationFormPage.tip1') }}</li>
                <li>{{ t('applicationFormPage.tip2') }}</li>
                <li>{{ t('applicationFormPage.tip3') }}</li>
                <li>{{ t('applicationFormPage.tip4') }}</li>
                <li>{{ t('applicationFormPage.tip5') }}</li>
              </ul>
            </div>
          </div>

          <!-- Program Requirements -->
          <div v-if="selectedProgram" class="card">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-clipboard-check me-2"></i>{{ t('applicationFormPage.requirementsTitle') }}</h6>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="text-muted small">{{ t('applicationFormPage.minimumGpa') }}</label>
                <p class="fw-bold">{{ selectedProgram.min_gpa || t('applicationFormPage.none') }}</p>
              </div>
              <div v-if="selectedProgram.application_open_date || selectedProgram.application_deadline" class="mb-3">
                <label class="text-muted small">{{ t('applicationFormPage.applicationWindow') }}</label>
                <p class="fw-bold mb-1">
                  <span v-if="selectedProgram.application_open_date">
                    {{ t('applicationFormPage.opens') }} {{ formatDate(selectedProgram.application_open_date) }}
                  </span>
                  <span v-if="selectedProgram.application_open_date && selectedProgram.application_deadline">
                    <br>
                  </span>
                  <span v-if="selectedProgram.application_deadline">
                    {{ t('applicationFormPage.closes') }} {{ formatDate(selectedProgram.application_deadline) }}
                  </span>
                </p>
                <p v-if="applicationWindowState" class="small text-muted mb-0">
                  {{ applicationWindowState.message }}
                </p>
              </div>
              <div v-if="selectedProgram.required_language" class="mb-3">
                <label class="text-muted small">{{ t('applicationFormPage.language') }}</label>
                <p class="fw-bold">
                  {{ selectedProgram.required_language }}
                  <span class="badge bg-secondary">{{ selectedProgram.min_language_level }}</span>
                </p>
              </div>
              <div class="mb-3">
                <label class="text-muted small">{{ t('applicationFormPage.duration') }}</label>
                <p class="fw-bold">
                  {{ calculateDuration(selectedProgram.start_date, selectedProgram.end_date) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import {
  APPLICATION_PROGRAM_FILTER_SEARCH_TYPE,
  serializeApplicationProgramFilters,
  deserializeApplicationProgramFilters,
} from '@/utils/applicationProgramFilterPresets'
import { fieldMeetsVisibleWhen, stepMeetsVisibleWhen } from '@/utils/dynamicFormVisibility'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const { t, te, locale } = useI18n()
const { success, error: errorToast } = useToast()

const authStore = useAuthStore()
const { user: authUser, isAdmin, isCoordinator } = storeToRefs(authStore)

const {
  savedPresets,
  presetsLoading,
  newPresetName,
  saveAsDefault,
  loadPresets,
  savePreset: savePresetToApi,
  deletePreset,
  setDefaultPreset,
} = useStaffSavedPresets(APPLICATION_PROGRAM_FILTER_SEARCH_TYPE)

const isEditMode = computed(() => route.params.id !== undefined)
const loading = ref(true)
const loadingMessage = ref(t('applicationFormPage.loadingDefault'))
const submitting = ref(false)

const programs = ref([])
const programsLoading = ref(false)
const programFilters = ref({
  search: '',
  required_language: '',
  min_language_level: '',
  start_date_after: '',
  start_date_before: '',
  min_gpa_max: '',
  accepting_applications: false,
  ordering: 'name',
})
let programFilterDebounce = null
let suppressProgramFilterWatch = false

const form = ref({
  program: '',
})
/** For ``visible_when`` rules: ``has_assigned_coordinator`` (program id comes from ``form.program``). */
const applicationVisibilityContext = ref({
  has_assigned_coordinator: false,
})
const errors = ref({})
const dynamicForm = ref({
  id: null,
  name: '',
  description: '',
  schema: {},
  ui_schema: {},
  required_fields: [],
  multi_step: false,
  steps: [],
})
const dynamicFormValues = ref({})
const dynamicFieldErrors = ref({})
const dynamicFormErrors = ref([])
const dynamicFormLoading = ref(false)
const dynamicFormLoadError = ref('')
const pendingDynamicResponses = ref(null)
const applicationDynamicLayout = ref(null)
const currentStepIndex = ref(0)

// Normalize program errors: backend may return string or array
const programErrors = computed(() => {
  const raw = errors.value?.program
  if (!raw) return []
  return Array.isArray(raw) ? raw : [raw]
})

// Errors for other fields (exclude program and dynamic-form specific messages) as list of strings
const otherErrors = computed(() => {
  const list = []
  const omit = ['program', 'dynamic_form']
  for (const [field, value] of Object.entries(errors.value || {})) {
    if (omit.includes(field)) continue
    const texts = Array.isArray(value) ? value : [value]
    list.push(...texts.map((txt) => (typeof txt === 'string' ? txt : `${field}: ${JSON.stringify(txt)}`)))
  }
  return list
})

const selectedProgram = computed(() => {
  if (!form.value.program) return null
  return programs.value.find(p => String(p.id) === String(form.value.program))
})

const applicationWindowState = computed(() => {
  if (!selectedProgram.value) return null

  const fallbackOpen = selectedProgram.value.application_window_open
  const fallbackMessage = selectedProgram.value.application_window_message
  const openDate = parseDateOnly(selectedProgram.value.application_open_date)
  const deadline = parseDateOnly(selectedProgram.value.application_deadline)
  const today = startOfToday()

  if (openDate && today < openDate) {
    return {
      canApply: false,
      reason: 'not_open_yet',
      message: fallbackMessage || t('applicationFormPage.windowOpensOn', {
        date: formatDate(selectedProgram.value.application_open_date),
      }),
    }
  }

  if (deadline && today > deadline) {
    return {
      canApply: false,
      reason: 'closed',
      message: fallbackMessage || t('applicationFormPage.windowClosedOn', {
        date: formatDate(selectedProgram.value.application_deadline),
      }),
    }
  }

  if (openDate && deadline) {
    return {
      canApply: true,
      reason: 'open',
      message: fallbackMessage || t('applicationFormPage.windowOpenRange', {
        open: formatDate(selectedProgram.value.application_open_date),
        close: formatDate(selectedProgram.value.application_deadline),
      }),
    }
  }

  if (deadline) {
    return {
      canApply: true,
      reason: 'open',
      message: fallbackMessage || t('applicationFormPage.windowOpenUntil', {
        date: formatDate(selectedProgram.value.application_deadline),
      }),
    }
  }

  if (openDate) {
    return {
      canApply: true,
      reason: 'open',
      message: fallbackMessage || t('applicationFormPage.windowOpenedOn', {
        date: formatDate(selectedProgram.value.application_open_date),
      }),
    }
  }

  if (fallbackOpen === false) {
    return {
      canApply: false,
      reason: 'closed',
      message: fallbackMessage || t('applicationFormPage.windowNotOpen'),
    }
  }

  return {
    canApply: true,
    reason: 'open',
    message: fallbackMessage || t('applicationFormPage.windowOpenNow'),
  }
})

const createBlockedByWindow = computed(() => (
  !isEditMode.value && Boolean(applicationWindowState.value && !applicationWindowState.value.canApply)
))

const dynamicFields = computed(() => (
  Object.entries(dynamicForm.value.schema?.properties || {}).map(([name, config]) => ({
    name,
    config,
    label: config.title || name,
    description: config.description || '',
    required: dynamicForm.value.required_fields.includes(name),
  }))
))

const hasDynamicFields = computed(() => dynamicFields.value.length > 0)

const isMultiStep = computed(() => (
  Boolean(dynamicForm.value.multi_step && dynamicForm.value.steps?.length)
))

const dynamicFormVisibilityContext = computed(() => {
  const p = form.value.program
  const n = p === '' || p == null ? NaN : Number(p)
  const viewerRoles = new Set()
  const role = authUser.value?.role
  if (role) viewerRoles.add(String(role))
  if (isAdmin.value) viewerRoles.add('admin')
  if (isCoordinator.value) viewerRoles.add('coordinator')
  return {
    program_id: Number.isFinite(n) ? n : null,
    has_assigned_coordinator: Boolean(applicationVisibilityContext.value.has_assigned_coordinator),
    viewer_roles: [...viewerRoles],
  }
})

const visibleFormSteps = computed(() => {
  const steps = dynamicForm.value.steps || []
  if (!isMultiStep.value) return steps
  const ctx = dynamicFormVisibilityContext.value
  return steps.filter(s => stepMeetsVisibleWhen(s, dynamicFormValues.value, ctx))
})

const stepScopedDynamicFields = computed(() => {
  if (!dynamicFields.value.length) return []
  if (!isMultiStep.value) return dynamicFields.value
  const step = visibleFormSteps.value[currentStepIndex.value]
  if (!step?.field_names?.length) return dynamicFields.value
  const allow = new Set(step.field_names)
  return dynamicFields.value.filter(f => allow.has(f.name))
})

const currentStepKey = computed(() => {
  if (!isMultiStep.value) return null
  const step = visibleFormSteps.value[currentStepIndex.value]
  return step?.key ?? null
})

const currentStepTitle = computed(() => {
  if (!isMultiStep.value) return ''
  const step = visibleFormSteps.value[currentStepIndex.value]
  return step?.title || ''
})

const isLastStep = computed(() => {
  if (!isMultiStep.value) return true
  return currentStepIndex.value >= visibleFormSteps.value.length - 1
})

const visibleDynamicFields = computed(() => {
  const ctx = dynamicFormVisibilityContext.value
  return stepScopedDynamicFields.value.filter((f) =>
    fieldMeetsVisibleWhen(f.config, dynamicFormValues.value, ctx))
})

const allVisibleDynamicFields = computed(() => {
  const ctx = dynamicFormVisibilityContext.value
  return dynamicFields.value.filter((f) =>
    fieldMeetsVisibleWhen(f.config, dynamicFormValues.value, ctx))
})

const currentStepDocumentTypesDisplay = computed(() => {
  const step = isMultiStep.value ? visibleFormSteps.value[currentStepIndex.value] : null
  const types = step?.required_document_types || []
  const layout = applicationDynamicLayout.value
  const docBlock =
    layout?.current_step === currentStepKey.value ? layout?.current_step_documents : null
  const items = docBlock?.items || []
  const byId = Object.fromEntries(items.map((i) => [i.document_type_id, i.status]))
  return types.map((t) => ({
    ...t,
    status: byId[t.id] || null,
  }))
})

const hasCurrentStepDocumentRequirements = computed(() => (
  currentStepDocumentTypesDisplay.value.length > 0
))

function documentStepStatusClass(status) {
  if (status === 'approved') return 'text-success text-capitalize small'
  if (status === 'pending_review') return 'text-warning small'
  if (status === 'resubmit_requested') return 'text-danger small'
  if (status === 'missing') return 'text-muted small'
  return 'text-muted small'
}

function documentStepStatusLabel(status) {
  if (!status) return t('applicationFormPage.documentStep.notUploaded')
  const key = `applicationFormPage.documentStep.${status}`
  if (te(key)) return t(key)
  return String(status).replace(/_/g, ' ')
}

function normalizeProgramMatch(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function startOfToday() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

function parseDateOnly(dateString) {
  if (!dateString) return null
  return new Date(`${dateString}T00:00:00`)
}

function applyProgramContext() {
  if (isEditMode.value || !route.query.program || !programs.value.length) return

  const requestedProgram = String(route.query.program)
  const matchedProgram = programs.value.find((program) => (
    String(program.id) === requestedProgram ||
    normalizeProgramMatch(program.name) === normalizeProgramMatch(requestedProgram)
  ))

  if (matchedProgram) {
    form.value.program = matchedProgram.id
  }
}

function buildProgramQueryParams() {
  const base = { is_active: true, ordering: 'name' }
  if (isEditMode.value) return base
  const p = { ...base }
  const f = programFilters.value
  if (f.ordering) p.ordering = f.ordering
  const q = (f.search || '').trim()
  if (q) p.search = q
  const lang = (f.required_language || '').trim()
  if (lang) p.required_language = lang
  if (f.min_language_level) p.min_language_level = f.min_language_level
  if (f.start_date_after) p.start_date_after = f.start_date_after
  if (f.start_date_before) p.start_date_before = f.start_date_before
  if (f.min_gpa_max !== '' && f.min_gpa_max != null) {
    const n = Number(f.min_gpa_max)
    if (!Number.isNaN(n)) p.min_gpa_max = n
  }
  if (f.accepting_applications) p.accepting_applications = true
  return p
}

function clearProgramFilters() {
  if (programFilterDebounce != null) {
    clearTimeout(programFilterDebounce)
    programFilterDebounce = null
  }
  suppressProgramFilterWatch = true
  programFilters.value = deserializeApplicationProgramFilters({})
  fetchPrograms().finally(() => {
    suppressProgramFilterWatch = false
  })
}

function saveProgramFilterPreset() {
  savePresetToApi(() => serializeApplicationProgramFilters(programFilters.value))
}

function applyProgramFilterPreset(p) {
  if (programFilterDebounce != null) {
    clearTimeout(programFilterDebounce)
    programFilterDebounce = null
  }
  suppressProgramFilterWatch = true
  programFilters.value = deserializeApplicationProgramFilters(p.filters)
  fetchPrograms().finally(() => {
    suppressProgramFilterWatch = false
  })
}

async function fetchPrograms() {
  if (!isEditMode.value) programsLoading.value = true
  try {
    loadingMessage.value = t('applicationFormPage.loadingPrograms')
    const response = await api.get('/api/programs/', {
      params: buildProgramQueryParams(),
    })
    const list = response.data.results || response.data
    programs.value = Array.isArray(list) ? list : []
    if (
      form.value.program
      && !programs.value.some((pr) => String(pr.id) === String(form.value.program))
    ) {
      form.value.program = ''
    }
  } catch (err) {
    console.error('Failed to fetch programs:', err)
    errorToast(t('applicationFormPage.toastLoadPrograms'))
  } finally {
    programsLoading.value = false
  }
}

function resetDynamicForm() {
  dynamicForm.value = {
    id: null,
    name: '',
    description: '',
    schema: {},
    ui_schema: {},
    required_fields: [],
    multi_step: false,
    steps: [],
  }
  dynamicFormValues.value = {}
  dynamicFieldErrors.value = {}
  dynamicFormErrors.value = []
  dynamicFormLoadError.value = ''
  currentStepIndex.value = 0
}

function syncStepFromApplicationLayout() {
  const layout = applicationDynamicLayout.value
  if (!layout?.multi_step || !visibleFormSteps.value.length) {
    currentStepIndex.value = 0
    return
  }
  const idx = visibleFormSteps.value.findIndex((s) => s.key === layout.current_step)
  currentStepIndex.value = idx >= 0 ? idx : 0
}

watch(
  visibleFormSteps,
  (steps) => {
    if (!steps.length) {
      currentStepIndex.value = 0
      return
    }
    if (currentStepIndex.value >= steps.length) {
      currentStepIndex.value = steps.length - 1
    }
  },
  { deep: true },
)

function goToPreviousStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value -= 1
  }
}

function normalizeInitialFieldValue(field, value) {
  if (value === undefined || value === null) {
    if (field.type === 'array') return []
    if (field.type === 'boolean') return false
    return ''
  }

  if (field.type === 'array') {
    return Array.isArray(value) ? value : [value]
  }

  if (field.type === 'boolean') {
    return Boolean(value)
  }

  if (field.type === 'number' || field.type === 'integer') {
    return typeof value === 'number' ? value : Number(value)
  }

  return value
}

function initializeDynamicFormValues(schema, responses = {}) {
  const nextValues = {}
  const properties = schema?.properties || {}

  for (const [name, config] of Object.entries(properties)) {
    nextValues[name] = normalizeInitialFieldValue(config, responses[name])
  }

  dynamicFormValues.value = nextValues
  dynamicFieldErrors.value = {}
}

async function loadDynamicForm(formTypeId, responses = null) {
  if (!formTypeId) {
    resetDynamicForm()
    return
  }

  dynamicFormLoading.value = true
  dynamicFormLoadError.value = ''
  dynamicFormErrors.value = []

  try {
    const params = {}
    if (form.value.program) {
      params.program = form.value.program
    }
    const response = await api.get(
      `/api/application-forms/form-types/${formTypeId}/form_schema/`,
      { params },
    )
    dynamicForm.value = {
      ...response.data,
      multi_step: Boolean(response.data.multi_step),
      steps: Array.isArray(response.data.steps) ? response.data.steps : [],
    }
    initializeDynamicFormValues(response.data.schema, responses || {})
    syncStepFromApplicationLayout()
  } catch (err) {
    console.error('Failed to load dynamic form schema:', err)
    resetDynamicForm()
    dynamicFormLoadError.value = t('applicationFormPage.dynamicFormLoadFailed')
  } finally {
    dynamicFormLoading.value = false
  }
}

function applyApplicationVisibilityFromResponse(data) {
  if (!data || typeof data !== 'object') return
  if (!('assigned_coordinator' in data)) return
  applicationVisibilityContext.value = {
    ...applicationVisibilityContext.value,
    has_assigned_coordinator: Boolean(data.assigned_coordinator),
  }
}

async function fetchApplication() {
  if (!isEditMode.value) return

  try {
    loadingMessage.value = t('applicationFormPage.loadingApplication')
    const response = await api.get(`/api/applications/${route.params.id}/`)
    
    form.value = {
      program: response.data.program?.id || response.data.program,
    }
    applyApplicationVisibilityFromResponse(response.data)
    pendingDynamicResponses.value = response.data.dynamic_form_submission?.responses || null
    applicationDynamicLayout.value = response.data.dynamic_form_layout || null
  } catch (err) {
    console.error('Failed to fetch application:', err)
    errorToast(t('applicationFormPage.toastLoadApplication'))
    router.push({ name: 'Applications' })
  }
}

function isSelectField(field) {
  return field.config.type === 'string' && Array.isArray(field.config.enum)
}

function isArrayField(field) {
  return field.config.type === 'array' && Array.isArray(field.config.items?.enum)
}

function isBooleanField(field) {
  return field.config.type === 'boolean'
}

function isNumericField(field) {
  return field.config.type === 'number' || field.config.type === 'integer'
}

function isTextareaField(field) {
  return !isSelectField(field)
    && field.config.type === 'string'
    && (
      field.config.maxLength > 200
      || dynamicForm.value.ui_schema?.[field.name]?.['ui:widget'] === 'textarea'
    )
}

function getFieldOptions(field) {
  if (isSelectField(field)) return field.config.enum
  if (isArrayField(field)) return field.config.items.enum
  return []
}

function getFieldPlaceholder(field) {
  return dynamicForm.value.ui_schema?.[field.name]?.['ui:placeholder'] || ''
}

function getTextareaRows(field) {
  return dynamicForm.value.ui_schema?.[field.name]?.['ui:rows'] || 4
}

function getInputType(field) {
  if (isNumericField(field)) return 'number'

  switch (field.config.format) {
    case 'email':
      return 'email'
    case 'url':
      return 'url'
    case 'date':
      return 'date'
    case 'datetime':
      return 'datetime-local'
    default:
      return 'text'
  }
}

function hasValue(value, field) {
  if (field.config.type === 'boolean') return value === true || value === false
  if (field.config.type === 'array') return Array.isArray(value) && value.length > 0
  return value !== null && value !== undefined && String(value).trim() !== ''
}

function validateDynamicForm(fieldList) {
  const nextErrors = {}
  const list = fieldList || dynamicFields.value

  for (const field of list) {
    if (field.required && !hasValue(dynamicFormValues.value[field.name], field)) {
      nextErrors[field.name] = t('applicationFormPage.fieldRequired')
    }
  }

  dynamicFieldErrors.value = nextErrors
  return Object.keys(nextErrors).length === 0
}

function buildDynamicPayload(fieldList) {
  const payload = {}
  const list = fieldList || dynamicFields.value

  for (const field of list) {
    const value = dynamicFormValues.value[field.name]
    if (!hasValue(value, field)) continue
    payload[`df_${field.name}`] = value
  }

  return payload
}

async function handleSubmit() {
  errors.value = {}
  dynamicFormErrors.value = []

  if (hasDynamicFields.value) {
    if (isMultiStep.value && !isLastStep.value) {
      if (!validateDynamicForm(visibleDynamicFields.value)) {
        errorToast(t('applicationFormPage.toastFixErrors'))
        return
      }
    } else if (!validateDynamicForm(allVisibleDynamicFields.value)) {
      errorToast(t('applicationFormPage.toastFixErrors'))
      return
    }
  }

  submitting.value = true

  try {
    const useMulti = isMultiStep.value
    const fieldsForPayload = useMulti ? visibleDynamicFields.value : allVisibleDynamicFields.value
    const data = {
      program: form.value.program,
      ...buildDynamicPayload(fieldsForPayload),
    }
    if (useMulti && currentStepKey.value) {
      data.dynamic_form_current_step = currentStepKey.value
    }

    let response
    if (isEditMode.value) {
      response = await api.patch(`/api/applications/${route.params.id}/`, data)
    } else {
      response = await api.post('/api/applications/', data)
    }

    applyApplicationVisibilityFromResponse(response.data)

    let okMessage = isEditMode.value
      ? t('applicationFormPage.toastUpdated')
      : t('applicationFormPage.toastCreated')

    if (useMulti && !isLastStep.value) {
      if (!isEditMode.value) {
        await router.replace({ name: 'ApplicationEdit', params: { id: response.data.id } })
      }
      applicationDynamicLayout.value = response.data.dynamic_form_layout || applicationDynamicLayout.value
      syncStepFromApplicationLayout()
      dynamicFieldErrors.value = {}
      const sentStep = data.dynamic_form_current_step
      const newCur = response.data.dynamic_form_layout?.current_step
      if (sentStep && newCur && sentStep === newCur) {
        okMessage += t('applicationFormPage.multiStepDocumentsHint')
      }
      success(okMessage)
    } else {
      success(okMessage)
      router.push({ name: 'ApplicationDetail', params: { id: response.data.id } })
    }
  } catch (err) {
    console.error('Failed to save application:', err)
    
    if (err.response?.data) {
      errors.value = err.response.data
      dynamicFormErrors.value = Array.isArray(err.response.data.dynamic_form)
        ? err.response.data.dynamic_form
        : (err.response.data.dynamic_form ? [err.response.data.dynamic_form] : [])
      errorToast(t('applicationFormPage.toastFixErrors'))
    } else {
      errorToast(t('applicationFormPage.toastSaveFailed'))
    }
  } finally {
    submitting.value = false
  }
}

async function saveDraft() {
  errors.value = {}
  dynamicFormErrors.value = []

  if (hasDynamicFields.value && isMultiStep.value) {
    if (!validateDynamicForm(visibleDynamicFields.value)) {
      errorToast(t('applicationFormPage.toastFixErrors'))
      return
    }
  } else if (hasDynamicFields.value && !validateDynamicForm(allVisibleDynamicFields.value)) {
    errorToast(t('applicationFormPage.toastFixErrors'))
    return
  }

  submitting.value = true
  try {
    const useMulti = isMultiStep.value
    const fieldsForPayload = useMulti ? visibleDynamicFields.value : allVisibleDynamicFields.value
    const data = {
      program: form.value.program,
      ...buildDynamicPayload(fieldsForPayload),
    }
    if (useMulti && currentStepKey.value) {
      data.dynamic_form_current_step = currentStepKey.value
    }

    let response
    if (isEditMode.value) {
      response = await api.patch(`/api/applications/${route.params.id}/`, data)
    } else {
      response = await api.post('/api/applications/', data)
    }
    applyApplicationVisibilityFromResponse(response.data)
    success(t('applicationFormPage.toastDraftSaved'))
    applicationDynamicLayout.value = response.data.dynamic_form_layout || applicationDynamicLayout.value
    if (useMulti) {
      syncStepFromApplicationLayout()
      if (!isEditMode.value && response.data?.id) {
        await router.replace({ name: 'ApplicationEdit', params: { id: response.data.id } })
      }
    } else {
      router.push({ name: 'ApplicationDetail', params: { id: response.data.id } })
    }
  } catch (err) {
    console.error('Failed to save draft:', err)
    if (err.response?.data) {
      errors.value = err.response.data
      dynamicFormErrors.value = Array.isArray(err.response.data.dynamic_form)
        ? err.response.data.dynamic_form
        : (err.response.data.dynamic_form ? [err.response.data.dynamic_form] : [])
      errorToast(t('applicationFormPage.toastFixErrors'))
    } else {
      errorToast(t('applicationFormPage.toastDraftSaveFailed'))
    }
  } finally {
    submitting.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return t('applicationsPage.notAvailable')
  const loc = locale.value === 'es' ? 'es' : 'en-US'
  const date = new Date(dateString)
  return date.toLocaleDateString(loc, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function calculateDuration(startDate, endDate) {
  if (!startDate || !endDate) return t('applicationsPage.notAvailable')

  const start = new Date(startDate)
  const end = new Date(endDate)
  const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
  const months = Math.round(days / 30)

  if (months < 2) return t('applicationFormPage.durationDays', { n: days })
  return t('applicationFormPage.durationMonths', { n: months })
}

onMounted(async () => {
  loading.value = true

  if (!isEditMode.value) {
    await loadPresets()
    const defaultPreset = savedPresets.value.find((preset) => preset.is_default)
    if (defaultPreset) {
      programFilters.value = deserializeApplicationProgramFilters(defaultPreset.filters)
    }
  }

  await fetchPrograms()
  applyProgramContext()

  if (isEditMode.value) {
    await fetchApplication()
  }

  loading.value = false
})

watch(
  programFilters,
  () => {
    if (suppressProgramFilterWatch || isEditMode.value) return
    if (programFilterDebounce != null) clearTimeout(programFilterDebounce)
    programFilterDebounce = setTimeout(() => {
      programFilterDebounce = null
      fetchPrograms()
    }, 400)
  },
  { deep: true },
)

watch(isEditMode, (edit) => {
  if (!edit) {
    applicationVisibilityContext.value = { has_assigned_coordinator: false }
  }
})

watch(
  () => ({
    formTypeId: selectedProgram.value?.application_form || null,
    programId: form.value.program || null,
  }),
  async (curr, prev) => {
    const formTypeId = curr.formTypeId
    if (!formTypeId) {
      resetDynamicForm()
      pendingDynamicResponses.value = null
      applicationDynamicLayout.value = null
      return
    }

    const prevForm = prev?.formTypeId
    const prevProgram = prev?.programId
    if (prevForm !== formTypeId || prevProgram !== curr.programId) {
      currentStepIndex.value = 0
    }

    const responses = prevForm === formTypeId && prevProgram === curr.programId
      ? dynamicFormValues.value
      : (pendingDynamicResponses.value || {})

    await loadDynamicForm(formTypeId, responses)
    pendingDynamicResponses.value = null
  }
)
</script>

<style scoped>
.application-form-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.form-label {
  font-weight: 500;
}

.alert-info {
  background-color: #e7f3ff;
  border-color: #b3d7ff;
}

.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.alert-heading {
  font-size: 0.95rem;
  font-weight: 600;
}

.alert ul {
  font-size: 0.9rem;
}
</style>
