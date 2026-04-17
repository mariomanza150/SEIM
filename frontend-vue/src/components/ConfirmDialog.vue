<template>
  <Teleport to="body">
    <div v-if="confirmState.open" class="seim-confirm-backdrop">
      <div
        class="seim-confirm-dialog"
        role="dialog"
        aria-modal="true"
        :aria-label="confirmState.title || 'Confirm'"
        @keydown.esc.prevent="onCancel"
      >
        <div class="seim-confirm-dialog__header">
          <h5 class="mb-0">{{ confirmState.title }}</h5>
        </div>
        <div class="seim-confirm-dialog__body">
          <p class="mb-0">{{ confirmState.message }}</p>
        </div>
        <div class="seim-confirm-dialog__footer">
          <button type="button" class="btn btn-outline-secondary" @click="onCancel" data-testid="confirm-cancel-btn">
            {{ confirmState.cancelText }}
          </button>
          <button
            ref="confirmButton"
            type="button"
            class="btn"
            :class="confirmState.variant === 'primary' ? 'btn-primary' : 'btn-danger'"
            @click="onConfirm"
            data-testid="confirm-accept-btn"
          >
            {{ confirmState.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { useConfirm, resolveConfirm } from '@/composables/useConfirm'

const { confirmState } = useConfirm()
const confirmButton = ref(null)

function onConfirm() {
  resolveConfirm(true)
}

function onCancel() {
  resolveConfirm(false)
}

watch(
  () => confirmState.open,
  async (open) => {
    if (!open) return
    await nextTick()
    confirmButton.value?.focus?.()
  },
)
</script>

<style scoped>
.seim-confirm-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.seim-confirm-dialog {
  width: 100%;
  max-width: 520px;
  background: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border: 1px solid var(--seim-border-color);
  border-radius: 0.75rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
}

.seim-confirm-dialog__header,
.seim-confirm-dialog__body,
.seim-confirm-dialog__footer {
  padding: 1rem 1.25rem;
}

.seim-confirm-dialog__header {
  border-bottom: 1px solid var(--seim-border-color);
}

.seim-confirm-dialog__footer {
  border-top: 1px solid var(--seim-border-color);
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
</style>

