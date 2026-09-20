<template>
  <div class="file-type-family-picker">
    <SearchableSelect
      v-model="searchValue"
      :options="selectOptions"
      :placeholder="searchPlaceholder"
      data-testid="file-type-family-search"
      @update:model-value="onSearchSelect"
    />
    <div class="d-flex flex-wrap gap-2 mt-2" data-testid="file-type-family-buttons">
      <button
        v-for="family in families"
        :key="family.id"
        type="button"
        class="btn btn-sm"
        :class="isSelected(family.id) ? 'btn-success' : 'btn-outline-secondary'"
        :data-testid="`file-type-family-${family.slug}`"
        :title="family.extensions"
        @click="toggle(family.id)"
      >
        <i
          v-if="isSelected(family.id)"
          class="bi bi-check-lg me-1"
          aria-hidden="true"
        ></i>
        {{ family.name }}
      </button>
    </div>
    <div class="form-text">{{ helpText }}</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import SearchableSelect from '@/components/SearchableSelect.vue'

const props = defineProps({
  families: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] },
  searchPlaceholder: { type: String, default: '' },
  helpText: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
const searchValue = ref('')

const selectedIds = computed(() => (props.modelValue || []).map((id) => Number(id)))

const selectOptions = computed(() =>
  (props.families || []).map((family) => ({
    value: String(family.id),
    label: `${family.name} (${family.extensions})`,
    aliases: String(family.aliases || '')
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean)
      .concat([family.slug, family.extensions]),
  })),
)

function isSelected(id) {
  return selectedIds.value.includes(Number(id))
}

function toggle(id) {
  const num = Number(id)
  const next = selectedIds.value.includes(num)
    ? selectedIds.value.filter((item) => item !== num)
    : [...selectedIds.value, num]
  emit('update:modelValue', next)
}

function onSearchSelect(value) {
  if (!value) return
  if (!isSelected(value)) {
    toggle(value)
  }
  searchValue.value = ''
}
</script>
