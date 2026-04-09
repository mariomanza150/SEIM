<template>
  <div class="not-found" data-testid="not-found-page">
    <div class="container text-center">
      <h1 class="display-1">404</h1>
      <p class="lead">{{ t('notFound.title') }}</p>
      <p>{{ t('notFound.body') }}</p>
      <router-link :to="{ name: 'Dashboard' }" class="btn btn-primary mt-3" data-testid="go-to-dashboard-link">
        {{ t('notFound.goDashboard') }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
