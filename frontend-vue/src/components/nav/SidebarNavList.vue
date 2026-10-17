<template>
  <div class="seim-sidebar-nav" :class="{ 'seim-sidebar-nav--rail': rail }">
    <template v-for="section in visibleSections" :key="section.key">
      <template v-if="rail">
        <div class="list-group seim-sidebar-nav__rail-group" :data-testid="`sidebar-section-${section.key}`">
          <router-link
            v-for="item in section.items"
            :key="item.key"
            :to="item.to"
            class="list-group-item list-group-item-action text-center px-0"
            active-class="active"
            :title="item.label"
            :aria-label="item.label"
            :data-tour="tourAttrFor(item.key)"
            @click="emitNavigate"
          >
            <i :class="item.iconClass" aria-hidden="true" />
          </router-link>
        </div>
      </template>
      <template v-else>
        <button
          v-if="section.label && collapsible"
          :id="headerId(section.key)"
          type="button"
          class="seim-sidebar-nav__section-toggle btn btn-link text-decoration-none text-uppercase text-muted small px-2 mb-2 mt-3 w-100 d-flex align-items-center justify-content-between"
          :aria-expanded="isOpen(section.key) ? 'true' : 'false'"
          :aria-controls="panelId(section.key)"
          :data-testid="`sidebar-section-toggle-${section.key}`"
          @click="toggleSection(section.key)"
        >
          <span>{{ section.label }}</span>
          <i
            class="bi bi-chevron-down seim-sidebar-nav__chevron"
            :class="{ 'seim-sidebar-nav__chevron--closed': !isOpen(section.key) }"
            aria-hidden="true"
          />
        </button>
        <div v-else-if="section.label" class="text-uppercase text-muted small px-2 mb-2 mt-3">
          {{ section.label }}
        </div>
        <div
          v-show="!collapsible || !section.label || isOpen(section.key)"
          :id="panelId(section.key)"
          class="list-group"
          :class="{ 'mb-2': section.label }"
          role="group"
          :aria-labelledby="section.label && collapsible ? headerId(section.key) : undefined"
          :data-testid="`sidebar-section-${section.key}`"
        >
          <router-link
            v-for="item in section.items"
            :key="item.key"
            :to="item.to"
            class="list-group-item list-group-item-action"
            active-class="active"
            :data-tour="tourAttrFor(item.key)"
            @click="emitNavigate"
          >
            <i :class="item.iconClass" class="me-2" aria-hidden="true" />{{ item.label }}
          </router-link>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { readCollapsedSections, writeCollapsedSections } from '@/utils/sidebarPrefs'

const props = defineProps({
  sections: {
    type: Array,
    default: () => [],
  },
  /** Accordion-style section headers (state persisted in localStorage). */
  collapsible: {
    type: Boolean,
    default: true,
  },
  /** Icon-only rail used when the desktop sidebar is collapsed. */
  rail: {
    type: Boolean,
    default: false,
  },
  /** Distinguishes element ids when the list is rendered twice (offcanvas + aside). */
  idPrefix: {
    type: String,
    default: 'seim-nav',
  },
})

const emit = defineEmits(['navigate'])
const route = useRoute()

const TOUR_ATTRS = {
  applications: 'nav-applications',
  reviewQueue: 'nav-review-queue',
  partnerPortal: 'nav-partner',
}

const collapsed = ref(readCollapsedSections())

function persist() {
  writeCollapsedSections(collapsed.value)
}

const visibleSections = computed(() =>
  props.sections
    .filter((section) => section.isVisible !== false)
    .map((section) => ({
      ...section,
      items: (section.items || []).filter((item) => item.isVisible !== false),
    }))
    .filter((section) => section.items.length > 0),
)

function isOpen(key) {
  return !collapsed.value[key]
}

function toggleSection(key) {
  const next = { ...collapsed.value }
  if (next[key]) delete next[key]
  else next[key] = true
  collapsed.value = next
  persist()
}

/** Expand the section holding the active route so the current page stays visible. */
watch(
  () => route?.name,
  (name) => {
    if (!name || !props.collapsible) return
    const owner = visibleSections.value.find((section) =>
      section.items.some((item) => item.to?.name === name),
    )
    if (owner && collapsed.value[owner.key]) {
      toggleSection(owner.key)
    }
  },
  { immediate: true },
)

function headerId(key) {
  return `${props.idPrefix}-section-${key}-header`
}

function panelId(key) {
  return `${props.idPrefix}-section-${key}`
}

function tourAttrFor(key) {
  return TOUR_ATTRS[key] || undefined
}

function emitNavigate() {
  emit('navigate')
}
</script>

<style scoped>
.seim-sidebar-nav__section-toggle {
  font-size: 0.8rem;
  letter-spacing: 0.02em;
}

.seim-sidebar-nav__section-toggle:hover,
.seim-sidebar-nav__section-toggle:focus-visible {
  color: var(--bs-body-color) !important;
}

.seim-sidebar-nav__chevron {
  transition: transform 0.2s ease;
}

.seim-sidebar-nav__chevron--closed {
  transform: rotate(-90deg);
}

.seim-sidebar-nav__rail-group {
  margin-bottom: 0.5rem;
}

.seim-sidebar-nav__rail-group + .seim-sidebar-nav__rail-group {
  border-top: 1px solid var(--bs-border-color);
  padding-top: 0.5rem;
}

@media (prefers-reduced-motion: reduce) {
  .seim-sidebar-nav__chevron {
    transition: none;
  }
}
</style>
