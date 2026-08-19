<template>
  <div class="searchable-select" ref="root">
    <input
      v-model="query"
      type="text"
      class="form-control"
      :placeholder="placeholder"
      :disabled="disabled"
      @focus="isOpen = true"
      @input="isOpen = true"
      @keydown.down.prevent="moveHighlight(1)"
      @keydown.up.prevent="moveHighlight(-1)"
      @keydown.enter.prevent="selectHighlighted"
      @blur="closeDropdown"
    >
    <ul v-if="isOpen && filteredOptions.length" class="searchable-select-dropdown list-group">
      <li
        v-for="(option, index) in filteredOptions"
        :key="`${option.value}-${index}`"
        class="list-group-item list-group-item-action"
        :class="{ active: index === highlightedIndex }"
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
})

const emit = defineEmits(['update:modelValue'])
const query = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)

const normalizedOptions = computed(() =>
  props.options
    .map((option) => ({
      value: String(option?.value ?? ''),
      label: String(option?.label ?? option?.value ?? ''),
    }))
    .filter((option) => option.value && option.label),
)

const filteredOptions = computed(() => {
  const term = query.value.trim().toLowerCase()
  if (!term) return normalizedOptions.value
  return normalizedOptions.value.filter(
    (option) =>
      option.label.toLowerCase().includes(term) ||
      option.value.toLowerCase().includes(term),
  )
})

watch(
  () => props.modelValue,
  (value) => {
    const selected = normalizedOptions.value.find((option) => option.value === value)
    query.value = selected?.label || value || ''
  },
  { immediate: true },
)

watch(filteredOptions, () => {
  highlightedIndex.value = filteredOptions.value.length ? 0 : -1
})

function selectOption(option) {
  emit('update:modelValue', option.value)
  query.value = option.label
  isOpen.value = false
}

function closeDropdown() {
  setTimeout(() => {
    isOpen.value = false
    const selected = normalizedOptions.value.find(
      (option) => option.value === props.modelValue,
    )
    query.value = selected?.label || props.modelValue || ''
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
  if (!isOpen.value || highlightedIndex.value < 0) return
  const option = filteredOptions.value[highlightedIndex.value]
  if (option) selectOption(option)
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
</style>
