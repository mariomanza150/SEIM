<template>
  <header class="seim-page-header">
    <div v-if="$slots.breadcrumb" class="seim-page-header__breadcrumb">
      <slot name="breadcrumb" />
    </div>

    <div class="row align-items-start g-3 mb-4">
      <div class="col-12 col-md-8">
        <h2 class="seim-page-header__title mb-1" :data-testid="testId">
          <i v-if="iconClass" :class="iconClass" class="me-2" aria-hidden="true" />
          <slot name="title">{{ title }}</slot>
        </h2>
        <p v-if="subtitle || $slots.subtitle" class="text-muted mb-0">
          <slot name="subtitle">{{ subtitle }}</slot>
        </p>
      </div>

      <div v-if="$slots.actions" class="col-12 col-md-4 d-flex justify-content-md-end">
        <div class="d-flex flex-wrap gap-2 justify-content-md-end">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  iconClass: { type: String, default: '' },
  testId: { type: String, default: undefined },
})
</script>

<style scoped>
.seim-page-header__breadcrumb :deep(.breadcrumb) {
  margin-bottom: 0.75rem;
}

.seim-page-header__title {
  line-height: 1.2;
}
</style>

