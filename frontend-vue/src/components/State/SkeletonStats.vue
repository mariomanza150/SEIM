<template>
  <div class="row mb-4" aria-hidden="true">
    <div v-for="n in count" :key="n" class="col-6 col-md-3 mb-3">
      <div class="card text-center">
        <div class="card-body placeholder-glow">
          <span class="placeholder rounded-circle d-inline-block mb-2" style="width: 3rem; height: 3rem;"></span>
          <div class="mt-2">
            <span class="placeholder col-4 d-block mx-auto"></span>
          </div>
          <div class="mt-2">
            <span class="placeholder col-6 d-block mx-auto"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  count: { type: Number, default: 4 },
})
</script>
