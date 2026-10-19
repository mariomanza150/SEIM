<template>
  <details
    v-if="qa.isTester && hiddenRows.length"
    class="mt-2 small border rounded p-2 bg-light"
    data-testid="tester-eligibility-overview"
    data-qa-ignore
  >
    <summary class="fw-semibold">
      <i class="bi bi-bug me-1" aria-hidden="true"></i>{{ t('testerEligibility.summary', { n: hiddenRows.length }) }}
    </summary>
    <p class="text-muted mb-2 mt-2">{{ t('testerEligibility.intro') }}</p>
    <ul class="list-unstyled mb-0">
      <li v-for="row in hiddenRows" :key="row.id" class="mb-2" data-testid="tester-eligibility-row">
        <strong>{{ row.name }}</strong>
        <ul class="mb-0">
          <li v-for="check in row.blocking" :key="check.id">{{ formatEligibilityRuleMessage(check, t) }}</li>
        </ul>
      </li>
    </ul>
  </details>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useQaStore } from '@/stores/qa'
import { formatEligibilityRuleMessage } from '@/utils/eligibilityMessages'

const { t } = useI18n()
const qa = useQaStore()
const rows = ref([])

const hiddenRows = computed(() => rows.value.filter((r) => !r.listed))

async function load() {
  await qa.load()
  if (!qa.isTester) return
  try {
    const { data } = await api.get('/api/programs/eligibility-overview/')
    rows.value = Array.isArray(data?.results) ? data.results : []
  } catch {
    rows.value = []
  }
}

onMounted(load)
defineExpose({ load })
</script>
