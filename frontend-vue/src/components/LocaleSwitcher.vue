<template>
  <div
    class="btn-group btn-group-sm seim-locale-switcher"
    role="group"
    :aria-label="t('dashboard.localeToggleAria')"
  >
    <button
      v-for="opt in options"
      :key="opt.code"
      type="button"
      class="btn"
      :class="locale === opt.code ? activeClass : inactiveClass"
      :aria-pressed="locale === opt.code ? 'true' : 'false'"
      :data-testid="`locale-${opt.code}`"
      @click="selectLocale(opt.code)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { setAppLocale } from '@/i18n'

defineProps({
  activeClass: { type: String, default: 'btn-primary' },
  inactiveClass: { type: String, default: 'btn-outline-secondary' },
})

const { t, locale } = useI18n()

const options = [
  { code: 'en', label: 'EN' },
  { code: 'es', label: 'ES' },
]

function selectLocale(code) {
  if (locale.value === code) return
  setAppLocale(code)
}
</script>

<style scoped>
.seim-locale-switcher .btn {
  min-width: 2.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
</style>
