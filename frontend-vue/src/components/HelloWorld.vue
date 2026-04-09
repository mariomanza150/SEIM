<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  msg: String,
})

const { t } = useI18n()
const count = ref(0)
</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <button type="button" @click="count++">{{ t('helloWorld.countLabel', { count }) }}</button>
    <p>
      {{ t('helloWorld.editHintBefore') }}
      <code>{{ t('helloWorld.editHintFile') }}</code>
      {{ t('helloWorld.editHintAfter') }}
    </p>
  </div>

  <p>
    {{ t('helloWorld.starterLineBefore') }}
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank" rel="noopener noreferrer">{{
      t('helloWorld.createVueLink')
    }}</a
    >{{ t('helloWorld.starterLineAfter') }}
  </p>
  <p>
    {{ t('helloWorld.ideLineBefore') }}
    <a
      href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support"
      target="_blank"
      rel="noopener noreferrer"
      >{{ t('helloWorld.ideGuideLink') }}</a
    >{{ t('helloWorld.ideLineAfter') }}
  </p>
  <p class="read-the-docs">{{ t('helloWorld.footerHint') }}</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
