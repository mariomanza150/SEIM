<template>
  <Teleport to="body">
    <template v-if="open">
      <div class="modal-backdrop show" aria-hidden="true" />
      <div
        class="modal d-block"
        tabindex="-1"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        data-testid="form-modal"
        @keydown.esc.prevent="onClose"
      >
        <div
          class="modal-dialog modal-dialog-scrollable"
          :class="dialogClass"
        >
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ title }}</h5>
              <button
                type="button"
                class="btn-close"
                :aria-label="resolvedCloseLabel"
                data-testid="form-modal-close"
                @click="onClose"
              />
            </div>
            <div class="modal-body">
              <ErrorAlert v-if="error" :message="error" test-id="form-modal-error" />
              <slot />
            </div>
            <div class="modal-footer">
              <slot name="footer-extra" />
              <button
                type="button"
                class="btn btn-outline-secondary"
                data-testid="form-modal-cancel"
                @click="onClose"
              >
                {{ resolvedCancelLabel }}
              </button>
              <button
                ref="submitButton"
                type="button"
                class="btn btn-primary"
                :disabled="saving"
                data-testid="form-modal-submit"
                @click="$emit('submit')"
              >
                <span v-if="saving" class="spinner-border spinner-border-sm me-1" aria-hidden="true" />
                {{ resolvedSubmitLabel }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import ErrorAlert from '@/components/State/ErrorAlert.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, required: true },
  error: { type: String, default: '' },
  saving: { type: Boolean, default: false },
  submitLabel: { type: String, default: '' },
  cancelLabel: { type: String, default: '' },
  closeLabel: { type: String, default: '' },
  size: {
    type: String,
    default: 'lg',
    validator: (v) => ['sm', 'md', 'lg', 'xl'].includes(v),
  },
})

const emit = defineEmits(['close', 'submit'])

const { t } = useI18n()
const submitButton = ref(null)

const dialogClass = computed(() => {
  if (props.size === 'sm') return 'modal-sm'
  if (props.size === 'md') return ''
  if (props.size === 'xl') return 'modal-xl'
  return 'modal-lg'
})

const resolvedSubmitLabel = computed(() => props.submitLabel || t('adminCommon.save'))
const resolvedCancelLabel = computed(() => props.cancelLabel || t('adminCommon.cancel'))
const resolvedCloseLabel = computed(() => props.closeLabel || t('adminCommon.close'))

function onClose() {
  emit('close')
}

watch(
  () => props.open,
  async (isOpen) => {
    if (!isOpen) return
    await nextTick()
    submitButton.value?.focus?.()
  },
)
</script>
