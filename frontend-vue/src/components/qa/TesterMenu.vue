<template>
  <li v-if="qa.isTester" ref="root" class="nav-item dropdown me-1" data-testid="qa-tester-menu" data-qa-ignore>
    <button
      type="button"
      class="nav-link dropdown-toggle seim-nav-text-btn d-inline-flex align-items-center gap-1"
      :class="{ show: open }"
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="menu"
      @click="open = !open"
    >
      <span class="badge text-bg-warning text-uppercase" data-testid="qa-tier-badge">{{ tierLabel }}</span>
      <span class="d-none d-lg-inline">{{ t('qa.menu.label') }}</span>
    </button>
    <ul class="dropdown-menu dropdown-menu-end" :class="{ show: open }">
      <li>
        <button type="button" class="dropdown-item" @click="report">
          <i class="bi bi-bug me-1" aria-hidden="true" />{{ t('qa.widget.open') }}
        </button>
      </li>
      <li v-for="item in links" :key="item.name">
        <router-link class="dropdown-item" :to="{ name: item.name }" @click="open = false">
          <i :class="`bi ${item.icon} me-1`" aria-hidden="true" />{{ t(item.label) }}
        </router-link>
      </li>
      <li><hr class="dropdown-divider" /></li>
      <li>
        <span class="dropdown-item-text small text-muted" data-testid="qa-version-badge">
          {{ versionText }}
          <span v-if="qa.commitMismatch" class="text-danger d-block">{{ t('qa.menu.commitMismatch') }}</span>
        </span>
      </li>
    </ul>
  </li>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQaStore } from '@/stores/qa'
import { shortCommit } from '@/qa/buildInfo'
import { testerMenuLinks } from '@/qa/menuLinks'

const { t, locale } = useI18n()
const qa = useQaStore()
const open = ref(false)
const root = ref(null)

const tierLabel = computed(() => (qa.deployTier === 'development' ? 'DEV' : 'TEST'))
const links = computed(() => testerMenuLinks(qa))

const versionText = computed(() => {
  const parts = [tierLabel.value]
  if (qa.backendVersion) parts.push(`v${qa.backendVersion}`)
  const commit = shortCommit(qa.frontendCommit || qa.backendCommit)
  if (commit) parts.push(commit)
  if (qa.buildTime) {
    const when = new Date(qa.buildTime)
    parts.push(
      t('qa.menu.built', {
        when: Number.isNaN(when.getTime()) ? qa.buildTime : when.toLocaleString(locale.value),
      }),
    )
  }
  return parts.join(' · ')
})

function report() {
  open.value = false
  window.dispatchEvent(new CustomEvent('seim:qa-report'))
}

function onDocClick(e) {
  if (open.value && root.value && !root.value.contains(e.target)) open.value = false
}
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>
