<template>
  <div class="alert alert-secondary" data-testid="qa-not-available">
    <i class="bi bi-lock me-1" aria-hidden="true" />{{ t('qa.common.notAvailable') }}
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>
