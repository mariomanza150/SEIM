<template>
  <div class="searchable-select" ref="root">
    <input
      v-model="query"
      type="text"
      class="form-control"
      :placeholder="placeholder"
      :disabled="disabled"
      :data-testid="dataTestid || undefined"
      autocomplete="off"
      :aria-expanded="isOpen ? 'true' : 'false'"
      aria-autocomplete="list"
      @focus="isOpen = true"
      @input="onInput"
      @keydown.down.prevent="moveHighlight(1)"
      @keydown.up.prevent="moveHighlight(-1)"
      @keydown.enter.prevent="selectHighlighted"
      @blur="onBlur"
    >
    <ul
      v-if="isOpen && filteredOptions.length"
      class="searchable-select-dropdown list-group"
      :class="{ 'searchable-select-dropdown--up': placement === 'up' }"
      role="listbox"
    >
      <li
        v-for="(option, index) in filteredOptions"
        :key="`opt-${option.value}-${index}`"
        class="list-group-item list-group-item-action"
        :class="{ active: index === highlightedIndex }"
        role="option"
        :aria-selected="index === highlightedIndex"
        @mousedown.prevent="selectOption(option)"
      >
        {{ option.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  dataTestid: { type: String, default: '' },
  /** Dropdown direction: ``down`` (default) or ``up`` (opens above the input). */
  placement: { type: String, default: 'down', validator: (v) => v === 'down' || v === 'up' },
  /**
   * When true, typed text that does not match an option is kept as the value
   * (suggestions remain available). Used for host-university name autocomplete.
   */
  allowCustom: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'query-change'])
const query = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)

const normalizedOptions = computed(() =>
  props.options
    .map((option) => ({
      value: option?.value == null ? '' : String(option.value),
      label: String(option?.label ?? option?.value ?? ''),
      aliases: Array.isArray(option?.aliases)
        ? option.aliases.map((alias) => String(alias || '').trim()).filter(Boolean)
        : [],
    }))
    .filter((option) => {
      if (!option.label) return false
      // Keep labeled options even when value is '' (e.g. "No grade scale").
      return true
    }),
)

function optionMatches(option, term) {
  if (!term) return true
  if (option.label.toLowerCase().includes(term) || option.value.toLowerCase().includes(term)) {
    return true
  }
  return option.aliases.some((alias) => alias.toLowerCase().includes(term))
}

const filteredOptions = computed(() => {
  const term = query.value.trim().toLowerCase()
  if (!term) return normalizedOptions.value
  return normalizedOptions.value.filter((option) => optionMatches(option, term))
})

watch(
  () => props.modelValue,
  (value) => {
    const selected = normalizedOptions.value.find((option) => option.value === value)
    if (selected) {
      query.value = selected.label
      return
    }
    // Custom / free-text values (or encoded suggestions) show the raw name portion when possible.
    if (props.allowCustom && value && String(value).includes('\u001f')) {
      query.value = String(value).split('\u001f')[0] || ''
      return
    }
    query.value = value || ''
  },
  { immediate: true },
)

watch(filteredOptions, () => {
  highlightedIndex.value = filteredOptions.value.length ? 0 : -1
})

function onInput() {
  isOpen.value = true
  emit('query-change', query.value)
}

function selectOption(option) {
  emit('update:modelValue', option.value)
  query.value = option.label
  isOpen.value = false
  emit('query-change', option.label)
}

function resolveTypedOption(term) {
  const needle = String(term || '').trim().toLowerCase()
  if (!needle) return null

  const exact = normalizedOptions.value.find((option) => {
    if (option.label.toLowerCase() === needle || option.value.toLowerCase() === needle) {
      return true
    }
    return option.aliases.some((alias) => alias.toLowerCase() === needle)
  })
  if (exact) return exact

  const filtered = filteredOptions.value
  if (filtered.length === 1) return filtered[0]
  return null
}

function syncQueryToSelection() {
  const selected = normalizedOptions.value.find((option) => option.value === props.modelValue)
  query.value = selected?.label || props.modelValue || ''
}

function onBlur() {
  setTimeout(() => {
    isOpen.value = false
    const resolved = resolveTypedOption(query.value)
    if (resolved && resolved.value !== props.modelValue) {
      selectOption(resolved)
      return
    }
    if (props.allowCustom) {
      const custom = String(query.value || '').trim()
      if (custom !== props.modelValue) {
        emit('update:modelValue', custom)
      }
      emit('query-change', custom)
      return
    }
    syncQueryToSelection()
  }, 100)
}

function moveHighlight(step) {
  if (!isOpen.value || !filteredOptions.value.length) {
    isOpen.value = true
    highlightedIndex.value = 0
    return
  }
  const last = filteredOptions.value.length - 1
  highlightedIndex.value = Math.max(0, Math.min(last, highlightedIndex.value + step))
}

function selectHighlighted() {
  if (highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
    selectOption(filteredOptions.value[highlightedIndex.value])
    return
  }
  const resolved = resolveTypedOption(query.value)
  if (resolved) {
    selectOption(resolved)
    return
  }
  if (props.allowCustom) {
    const custom = String(query.value || '').trim()
    emit('update:modelValue', custom)
    emit('query-change', custom)
    isOpen.value = false
  }
}
</script>

<style scoped>
.searchable-select {
  position: relative;
}

.searchable-select-dropdown {
  position: absolute;
  top: calc(100% + 0.25rem);
  left: 0;
  right: 0;
  z-index: 20;
  max-height: 14rem;
  overflow-y: auto;
}

.searchable-select-dropdown--up {
  top: auto;
  bottom: calc(100% + 0.25rem);
}
</style>
