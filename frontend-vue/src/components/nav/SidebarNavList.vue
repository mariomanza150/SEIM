<template>
  <div>
    <template v-for="section in visibleSections" :key="section.key">
      <div v-if="section.label" class="text-uppercase text-muted small px-2 mb-2 mt-3">
        {{ section.label }}
      </div>
      <div class="list-group" :class="{ 'mb-2': section.label }">
        <router-link
          v-for="item in section.items"
          :key="item.key"
          :to="item.to"
          class="list-group-item list-group-item-action"
          active-class="active"
          @click="emitNavigate"
        >
          <i :class="item.iconClass" class="me-2" aria-hidden="true" />{{ item.label }}
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  sections: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['navigate'])

const visibleSections = computed(() =>
  props.sections
    .filter((section) => section.isVisible !== false)
    .map((section) => ({
      ...section,
      items: (section.items || []).filter((item) => item.isVisible !== false),
    }))
    .filter((section) => section.items.length > 0),
)

function emitNavigate() {
  emit('navigate')
}
</script>
