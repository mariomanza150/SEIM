<template>
  <div
    v-if="qa.actingAs"
    class="alert alert-warning rounded-0 mb-0 py-2 d-flex flex-wrap align-items-center justify-content-center gap-2 small"
    role="status"
    data-testid="qa-acting-as-banner"
    data-qa-ignore
  >
    <i class="bi bi-person-badge" aria-hidden="true" />
    <span>
      {{
        qa.actingAs.mode === 'impersonate'
          ? t('qa.switcher.bannerImpersonating', { email: qa.actingAs.email, role: roleLabel })
          : t('qa.switcher.banner', { email: qa.actingAs.email, role: roleLabel })
      }}
    </span>
    <button
      type="button"
      class="btn btn-sm btn-dark"
      :disabled="busy"
      data-testid="qa-return-button"
      @click="onReturn"
    >
      {{ t('qa.switcher.return') }}
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useQaStore } from '@/stores/qa'
import { returnToMyAccount } from '@/qa/roleSwitch'

const { t, te } = useI18n()
const qa = useQaStore()
const router = useRouter()
const busy = ref(false)

const roleLabel = computed(() => {
  const role = qa.actingAs?.role || ''
  return te(`qa.roles.${role}`) ? t(`qa.roles.${role}`) : role
})

async function onReturn() {
  busy.value = true
  try {
    const restored = await returnToMyAccount()
    await router.push(restored ? { name: 'TesterAccounts' } : { name: 'Login' })
  } finally {
    busy.value = false
  }
}
</script>
