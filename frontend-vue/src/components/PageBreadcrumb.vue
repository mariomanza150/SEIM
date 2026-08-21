<template>
  <nav class="seim-page-breadcrumb" :aria-label="ariaLabel">
    <ol class="breadcrumb seim-page-breadcrumb__list">
      <li
        v-for="(item, index) in items"
        :key="`${item.label}-${index}`"
        class="breadcrumb-item seim-page-breadcrumb__item"
        :class="{
          active: index === lastIndex,
          'seim-page-breadcrumb__item--truncate': item.truncate,
        }"
        :aria-current="index === lastIndex ? 'page' : undefined"
      >
        <router-link
          v-if="item.to && index !== lastIndex"
          :to="item.to"
          class="seim-page-breadcrumb__text"
          :title="item.label"
        >
          {{ item.label }}
        </router-link>
        <span v-else class="seim-page-breadcrumb__text" :title="item.label">{{ item.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  ariaLabel: { type: String, required: true },
  items: {
    type: Array,
    required: true,
  },
})

const lastIndex = computed(() => Math.max(0, props.items.length - 1))
</script>

<style scoped>
.seim-page-breadcrumb {
  background: transparent;
  color: var(--seim-surface-text);
}

.seim-page-breadcrumb__list {
  background: transparent;
  margin-bottom: 0.75rem;
  --bs-breadcrumb-bg: transparent;
  --bs-breadcrumb-divider-color: var(--seim-muted);
  --bs-breadcrumb-item-active-color: var(--seim-surface-text);
}

.seim-page-breadcrumb__item {
  color: var(--seim-muted);
}

.seim-page-breadcrumb__item.active {
  color: var(--seim-surface-text);
}

.seim-page-breadcrumb__text {
  color: inherit;
  max-width: 100%;
}

.seim-page-breadcrumb__item--truncate {
  max-width: min(520px, 70vw);
  display: inline-block;
  vertical-align: bottom;
}

.seim-page-breadcrumb__item--truncate .seim-page-breadcrumb__text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}
</style>
