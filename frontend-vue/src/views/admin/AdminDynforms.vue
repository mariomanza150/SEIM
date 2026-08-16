<template>
  <div class="admin-dynforms-page">
    <PageHeader :title="t('adminDynforms.title')" :subtitle="t('adminDynforms.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminDynforms') }}</li>
          </ol>
        </nav>
      </template>
    </PageHeader>

    <div class="row g-3">
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h2 class="h5">{{ t('adminDynforms.spaTitle') }}</h2>
            <p class="text-muted flex-grow-1">{{ t('adminDynforms.spaBody') }}</p>
            <router-link class="btn btn-primary" :to="{ name: 'AdminForms' }" data-testid="dynforms-spa-forms">
              {{ t('adminDynforms.openSpa') }}
            </router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h2 class="h5">{{ t('adminDynforms.legacyTitle') }}</h2>
            <p class="text-muted flex-grow-1">{{ t('adminDynforms.legacyBody') }}</p>
            <a class="btn btn-outline-primary" href="/dynforms/" data-testid="dynforms-legacy-builder">
              {{ t('adminDynforms.openLegacy') }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
</script>
