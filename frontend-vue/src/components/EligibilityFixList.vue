<template>
  <ol class="eligibility-fix-list mb-0 ps-3" data-testid="eligibility-fix-list">
    <li
      v-for="item in items"
      :key="item.key"
      class="mb-2"
      data-testid="eligibility-fix-item"
    >
      <span>{{ item.message }}</span>
      <router-link
        v-if="item.to && item.actionLabel"
        :to="item.to"
        class="d-inline-block ms-2 small"
        data-testid="eligibility-fix-action"
      >
        {{ item.actionLabel }}
      </router-link>
    </li>
  </ol>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})
</script>
