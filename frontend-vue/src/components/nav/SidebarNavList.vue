<template>
  <div class="list-group" :aria-label="ariaLabel">
    <router-link
      v-for="item in primaryItems"
      :key="item.key"
      :to="item.to"
      class="list-group-item list-group-item-action"
      active-class="active"
      @click="emitNavigate"
    >
      <i :class="item.iconClass" class="me-2" aria-hidden="true" />{{ item.label }}
    </router-link>

    <div v-if="showAdmin && adminItems.length" class="mt-3">
      <div class="text-uppercase text-muted small px-2 mb-2">
        {{ adminSectionLabel }}
      </div>
      <router-link
        v-for="item in adminItems"
        :key="item.key"
        :to="item.to"
        class="list-group-item list-group-item-action"
        active-class="active"
        @click="emitNavigate"
      >
        <i :class="item.iconClass" class="me-2" aria-hidden="true" />{{ item.label }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
defineProps({
  ariaLabel: { type: String, required: true },
  primaryItems: { type: Array, required: true },
  adminItems: { type: Array, default: () => [] },
  showAdmin: { type: Boolean, default: false },
  adminSectionLabel: { type: String, default: '' },
})

const emit = defineEmits(['navigate'])

function emitNavigate() {
  emit('navigate')
}
</script>

