<template>

  <div class="seim-page-state-shell">

    <LoadingState

      v-if="loading && skeleton === 'none'"

      :spinner-label="resolvedLoadingLabel"

      :hint="loadingHint"

    />

    <SkeletonStats v-else-if="loading && skeleton === 'stats'" :count="skeletonCount" />

    <SkeletonCards v-else-if="loading && skeleton === 'cards'" :count="skeletonCount" />

    <SkeletonTable

      v-else-if="loading && skeleton === 'table'"

      :rows="skeletonRows"

      :columns="skeletonColumns"

    />

    <SkeletonDetail v-else-if="loading && skeleton === 'detail'" />

    <ErrorAlert

      v-else-if="error"

      :message="error"

      :test-id="errorTestId || undefined"

    />

    <EmptyState

      v-else-if="empty"

      :icon-class="emptyIconClass"

      :title="emptyTitle"

      :body="emptyBody"

      :test-id="emptyTestId || undefined"

      :heading-level="emptyHeadingLevel"

    >

      <template v-if="$slots.emptyActions" #actions>

        <slot name="emptyActions" />

      </template>

    </EmptyState>

    <slot v-else />

  </div>

</template>



<script setup>

import { computed } from 'vue'

import { useI18n } from 'vue-i18n'

import LoadingState from '@/components/State/LoadingState.vue'

import ErrorAlert from '@/components/State/ErrorAlert.vue'

import EmptyState from '@/components/State/EmptyState.vue'

import SkeletonStats from '@/components/State/SkeletonStats.vue'

import SkeletonCards from '@/components/State/SkeletonCards.vue'

import SkeletonTable from '@/components/State/SkeletonTable.vue'

import SkeletonDetail from '@/components/State/SkeletonDetail.vue'



const props = defineProps({

  loading: { type: Boolean, default: false },

  error: { type: String, default: '' },

  empty: { type: Boolean, default: false },

  emptyTitle: { type: String, default: '' },

  emptyBody: { type: String, default: '' },

  emptyIconClass: { type: String, default: 'bi bi-inbox' },

  emptyTestId: { type: String, default: '' },

  emptyHeadingLevel: { type: Number, default: 4 },

  errorTestId: { type: String, default: '' },

  loadingLabel: { type: String, default: '' },

  loadingHint: { type: String, default: '' },

  skeleton: {

    type: String,

    default: 'none',

    validator: (v) => ['none', 'cards', 'table', 'stats', 'detail'].includes(v),

  },

  skeletonCount: { type: Number, default: 6 },

  skeletonRows: { type: Number, default: 5 },

  skeletonColumns: { type: Number, default: 4 },

})



const { t } = useI18n()



const resolvedLoadingLabel = computed(() => props.loadingLabel || t('common.loading'))

</script>

