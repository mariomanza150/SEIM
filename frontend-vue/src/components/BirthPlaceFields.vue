<template>
  <div class="row g-3 birth-place-fields" data-testid="birth-place-fields">
    <div v-for="level in levels" :key="level.key" class="col-md-4">
      <label class="form-label" :for="`${idPrefix}-${level.key}`">
        {{ t(`birthPlace.${level.key}`) }}<span v-if="required && level.key !== 'state'"> *</span>
      </label>
      <template v-if="level.options.length && !manual[level.key]">
        <SearchableSelect
          :id="`${idPrefix}-${level.key}`"
          :model-value="selectValue(level)"
          :options="withOther(level.options)"
          :placeholder="t('birthPlace.searchPlaceholder')"
          :disabled="level.disabled"
          :data-testid="`${idPrefix}-${level.key}`"
          @update:model-value="(value) => onSelect(level.key, value)"
        />
      </template>
      <template v-else>
        <input
          :id="`${idPrefix}-${level.key}`"
          :value="values[level.key]"
          type="text"
          class="form-control"
          maxlength="100"
          :disabled="level.disabled"
          :placeholder="t('birthPlace.manualPlaceholder')"
          :data-testid="`${idPrefix}-${level.key}-manual`"
          @input="(event) => emitValue(level.key, event.target.value)"
        >
        <button
          v-if="level.options.length"
          type="button"
          class="btn btn-link btn-sm px-0"
          :data-testid="`${idPrefix}-${level.key}-back-to-list`"
          @click="backToList(level.key)"
        >
          {{ t('birthPlace.backToList') }}
        </button>
      </template>
    </div>
    <div v-if="legacyBirthplace && !country && !state && !city" class="col-12">
      <div class="form-text" data-testid="birth-place-legacy">
        {{ t('birthPlace.legacyValue', { value: legacyBirthplace }) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import SearchableSelect from '@/components/SearchableSelect.vue'

const OTHER = '__other__'

const props = defineProps({
  country: { type: String, default: '' },
  state: { type: String, default: '' },
  city: { type: String, default: '' },
  legacyBirthplace: { type: String, default: '' },
  required: { type: Boolean, default: false },
  idPrefix: { type: String, default: 'birth' },
})
const emit = defineEmits(['update:country', 'update:state', 'update:city'])
const { t } = useI18n()

const countries = ref([])
const states = ref([])
const cities = ref([])
const manual = reactive({ country: false, state: false, city: false })

const values = computed(() => ({ country: props.country, state: props.state, city: props.city }))

const countryRow = computed(() => {
  const needle = String(props.country || '').trim().toLowerCase()
  if (!needle) return null
  return countries.value.find((row) => (
    String(row.value).toLowerCase() === needle
    || String(row.code || '').toLowerCase() === needle
    || (row.aliases || []).some((alias) => String(alias).toLowerCase() === needle)
  )) || null
})

const levels = computed(() => [
  { key: 'country', options: countries.value, disabled: false },
  { key: 'state', options: states.value, disabled: !props.country },
  { key: 'city', options: cities.value, disabled: !props.country },
])

function withOther(options) {
  return [...options, { value: OTHER, label: t('birthPlace.otherOption') }]
}

function inOptions(options, value) {
  const needle = String(value || '').trim().toLowerCase()
  return options.some((row) => String(row.value).toLowerCase() === needle)
}

function selectValue(level) {
  const current = values.value[level.key]
  if (!current) return ''
  const match = level.options.find((row) => String(row.value).toLowerCase() === String(current).toLowerCase())
  return match ? match.value : current
}

function emitValue(key, value) {
  emit(`update:${key}`, String(value ?? ''))
}

function onSelect(key, value) {
  if (value === OTHER) {
    manual[key] = true
    emitValue(key, '')
    return
  }
  if (value === values.value[key]) return
  emitValue(key, value)
  if (key === 'country') {
    emitValue('state', '')
    emitValue('city', '')
    manual.state = false
    manual.city = false
  } else if (key === 'state') {
    emitValue('city', '')
    manual.city = false
  }
}

function backToList(key) {
  manual[key] = false
  emitValue(key, '')
}

function listOf(data) {
  const rows = data?.results || data
  return Array.isArray(rows) ? rows : []
}

async function loadCountries() {
  try {
    const { data } = await api.get('/api/accounts/catalogs/geo/countries/')
    countries.value = listOf(data)
  } catch {
    countries.value = []
  }
}

async function loadStates() {
  const row = countryRow.value
  if (!row || !row.has_states) {
    states.value = []
    return
  }
  try {
    const { data } = await api.get('/api/accounts/catalogs/geo/states/', { params: { country: row.code } })
    states.value = listOf(data)
  } catch {
    states.value = []
  }
}

async function loadCities() {
  const row = countryRow.value
  if (!row || !row.has_states || !props.state) {
    cities.value = []
    return
  }
  try {
    const { data } = await api.get('/api/accounts/catalogs/geo/cities/', {
      params: { country: row.code, state: props.state },
    })
    cities.value = listOf(data)
  } catch {
    cities.value = []
  }
}

/** Saved values that are not in a loaded list are freehand entries: show them as text. */
function syncManualFlags() {
  manual.country = Boolean(props.country) && countries.value.length > 0 && !inOptions(countries.value, props.country)
  manual.state = Boolean(props.state) && states.value.length > 0 && !inOptions(states.value, props.state)
  manual.city = Boolean(props.city) && cities.value.length > 0 && !inOptions(cities.value, props.city)
}

watch(() => countryRow.value?.code, async () => {
  await loadStates()
  await loadCities()
  syncManualFlags()
})

watch(() => props.state, async () => {
  await loadCities()
  syncManualFlags()
})

onMounted(async () => {
  await loadCountries()
  await loadStates()
  await loadCities()
  syncManualFlags()
})
</script>
