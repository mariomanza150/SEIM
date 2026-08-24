<template>
  <div class="row" aria-hidden="true">
    <div v-for="n in count" :key="n" class="col-md-6 mb-4">
      <div class="card h-100">
        <div class="card-body placeholder-glow">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <span class="placeholder col-7"></span>
            <span class="placeholder col-3"></span>
          </div>
          <div class="mb-3">
            <span class="placeholder col-4"></span>
            <div class="mt-2">
              <span class="placeholder col-9"></span>
            </div>
          </div>
          <div class="mb-3">
            <span class="placeholder col-6"></span>
          </div>
          <div class="row mb-3">
            <div class="col-6"><span class="placeholder col-10"></span></div>
            <div class="col-6"><span class="placeholder col-10"></span></div>
          </div>
          <div class="d-flex justify-content-between align-items-center">
            <span class="placeholder col-4"></span>
            <span class="placeholder col-3"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  count: { type: Number, default: 6 },
})
</script>
