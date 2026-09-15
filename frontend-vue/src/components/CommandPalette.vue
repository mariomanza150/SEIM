<template>
  <Teleport to="body">
    <div
      v-if="paletteState.open"
      class="seim-command-palette-backdrop"
      data-testid="command-palette"
      @mousedown.self="closePalette"
    >
      <div
        ref="dialogEl"
        class="seim-command-palette"
        role="dialog"
        aria-modal="true"
        :aria-label="t('commandPalette.ariaLabel')"
        @keydown.esc.prevent="closePalette"
        @keydown.tab="onTabTrap"
        @keydown.down.prevent="moveActive(1)"
        @keydown.up.prevent="moveActive(-1)"
        @keydown.enter.prevent="runActive"
      >
        <div class="seim-command-palette__header">
          <label class="visually-hidden" for="seim-command-palette-input">{{
            t('commandPalette.searchLabel')
          }}</label>
          <div class="input-group">
            <span class="input-group-text" aria-hidden="true"><i class="bi bi-search" /></span>
            <input
              id="seim-command-palette-input"
              ref="inputEl"
              v-model="query"
              type="search"
              class="form-control"
              autocomplete="off"
              data-testid="command-palette-input"
              :placeholder="t('commandPalette.searchPlaceholder')"
            />
            <button
              type="button"
              class="btn btn-outline-secondary"
              data-testid="command-palette-close"
              :aria-label="t('common.close')"
              @click="closePalette"
            >
              <i class="bi bi-x-lg" aria-hidden="true" />
            </button>
          </div>
          <p class="small text-muted mb-0 mt-2">{{ t('commandPalette.hint') }}</p>
        </div>

        <div
          class="seim-command-palette__list"
          role="listbox"
          :aria-label="t('commandPalette.resultsAria')"
          data-testid="command-palette-results"
        >
          <p v-if="!filtered.length" class="text-muted px-3 py-3 mb-0" data-testid="command-palette-empty">
            {{ t('commandPalette.empty') }}
          </p>
          <template v-for="group in grouped" :key="group.sectionKey">
            <div class="seim-command-palette__group-label">{{ group.section }}</div>
            <button
              v-for="item in group.items"
              :key="item.id"
              type="button"
              class="seim-command-palette__item"
              role="option"
              :aria-selected="item.id === activeId ? 'true' : 'false'"
              :class="{ 'is-active': item.id === activeId }"
              :data-testid="`command-palette-item-${item.id}`"
              @mouseenter="activeId = item.id"
              @click="runItem(item)"
            >
              <i :class="item.iconClass" class="me-2" aria-hidden="true" />
              <span>{{ item.label }}</span>
            </button>
          </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeToggle } from '@/composables/useThemeToggle'
import {
  handleCommandPaletteShortcut,
  useCommandPalette,
} from '@/composables/useCommandPalette'
import {
  buildCommandPaletteItems,
  filterCommandPaletteItems,
} from '@/utils/commandPaletteItems'

const FOCUSABLE =
  'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const { toggleTheme } = useThemeToggle()
const { paletteState, openPalette, closePalette, togglePalette } = useCommandPalette()

const query = ref('')
const activeId = ref('')
const inputEl = ref(null)
const dialogEl = ref(null)
const previouslyFocused = ref(null)

const allItems = computed(() =>
  buildCommandPaletteItems({
    t,
    canUsePartnerPortal: authStore.canUsePartnerPortal,
    canUseStaffReviewQueue: authStore.canUseStaffReviewQueue,
    isAdmin: authStore.isAdmin,
  }),
)

const filtered = computed(() => filterCommandPaletteItems(allItems.value, query.value))

const grouped = computed(() => {
  const order = []
  const map = new Map()
  for (const item of filtered.value) {
    if (!map.has(item.sectionKey)) {
      map.set(item.sectionKey, { sectionKey: item.sectionKey, section: item.section, items: [] })
      order.push(item.sectionKey)
    }
    map.get(item.sectionKey).items.push(item)
  }
  return order.map((key) => map.get(key))
})

watch(filtered, (list) => {
  if (!list.length) {
    activeId.value = ''
    return
  }
  if (!list.some((item) => item.id === activeId.value)) {
    activeId.value = list[0].id
  }
})

watch(
  () => paletteState.open,
  async (open) => {
    if (open) {
      previouslyFocused.value =
        document.activeElement instanceof HTMLElement ? document.activeElement : null
      query.value = ''
      activeId.value = filtered.value[0]?.id || ''
      await nextTick()
      inputEl.value?.focus?.()
      return
    }
    const restore = previouslyFocused.value
    previouslyFocused.value = null
    await nextTick()
    if (restore && typeof restore.focus === 'function') {
      restore.focus()
    }
  },
)

function moveActive(delta) {
  const list = filtered.value
  if (!list.length) return
  const idx = list.findIndex((item) => item.id === activeId.value)
  const next = idx < 0 ? 0 : (idx + delta + list.length) % list.length
  activeId.value = list[next].id
}

function runActive() {
  const item = filtered.value.find((entry) => entry.id === activeId.value)
  if (item) runItem(item)
}

async function runItem(item) {
  closePalette()
  if (item.type === 'route' && item.to) {
    await router.push(item.to)
    return
  }
  if (item.action === 'toggleTheme') {
    await toggleTheme()
    return
  }
  if (item.action === 'openHelp') {
    await router.push({ name: 'HelpCenter' })
    return
  }
  if (item.action === 'logout') {
    await authStore.logout()
    await router.push({ name: 'Login' })
  }
}

function getFocusableElements() {
  const root = dialogEl.value
  if (!root) return []
  return Array.from(root.querySelectorAll(FOCUSABLE))
}

function onTabTrap(event) {
  const focusable = getFocusableElements()
  if (!focusable.length) {
    event.preventDefault()
    return
  }
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

function onGlobalKeydown(event) {
  if (!authStore.isAuthenticated) return
  handleCommandPaletteShortcut(event, {
    open: paletteState.open,
    openPalette,
    closePalette,
    togglePalette,
  })
}

onMounted(() => {
  window.addEventListener('keydown', onGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<style scoped>
.seim-command-palette-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1250;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 12vh 1rem 1rem;
}

.seim-command-palette {
  width: 100%;
  max-width: 560px;
  max-height: min(70vh, 520px);
  display: flex;
  flex-direction: column;
  background: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border: 1px solid var(--seim-border-color);
  border-radius: 0.75rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.seim-command-palette__header {
  padding: 1rem 1.25rem 0.75rem;
  border-bottom: 1px solid var(--seim-border-color);
}

.seim-command-palette__list {
  overflow: auto;
  padding-bottom: 0.5rem;
}

.seim-command-palette__group-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--seim-muted-text, #6c757d);
  padding: 0.75rem 1.25rem 0.25rem;
}

.seim-command-palette__item {
  display: flex;
  align-items: center;
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  text-align: left;
  padding: 0.55rem 1.25rem;
}

.seim-command-palette__item:hover,
.seim-command-palette__item.is-active {
  background: var(--seim-muted-bg, #f8f9fa);
}

html[data-theme='dark'] .seim-command-palette__item:hover,
html[data-theme='dark'] .seim-command-palette__item.is-active {
  background: #111827;
}
</style>
