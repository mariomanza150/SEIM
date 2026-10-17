<template>
  <div class="container py-3" style="max-width: 52rem" data-testid="qa-guide-page">
    <h1 class="h3 mb-3">{{ t('qa.guide.title') }}</h1>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <template v-else>
      <section v-for="key in sections" :key="key" class="mb-4">
        <h2 class="h5">{{ t(`qa.guide.${key}.title`) }}</h2>
        <ul class="mb-0">
          <li v-for="(_, i) in tm(`qa.guide.${key}.items`)" :key="i">{{ t(`qa.guide.${key}.items.${i}`) }}</li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQaStore } from '@/stores/qa'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t, tm } = useI18n()
const qa = useQaStore()
const sections = ['start', 'accounts', 'report', 'email', 'rules']

onMounted(() => qa.load())
</script>
