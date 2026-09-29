<template>
  <div class="placeholder-glow text-start" aria-hidden="true">
    <div class="mb-4">
      <h2 class="mb-1"><span class="placeholder col-6"></span></h2>
      <p class="text-muted mb-0"><span class="placeholder col-4"></span></p>
    </div>
    <div class="row">
      <div class="col-lg-8">
        <div v-for="n in 2" :key="`left-${n}`" class="card mb-4">
          <div class="card-header"><span class="placeholder col-4"></span></div>
          <div class="card-body">
            <p><span class="placeholder col-8"></span></p>
            <p v-if="n === 1"><span class="placeholder col-6"></span></p>
            <p class="mb-0"><span class="placeholder col-7"></span></p>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div v-for="n in 2" :key="`right-${n}`" class="card mb-4">
          <div class="card-header"><span class="placeholder col-6"></span></div>
          <div class="card-body">
            <p><span class="placeholder col-9"></span></p>
            <p class="mb-0"><span class="placeholder col-8"></span></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({ name: 'SkeletonDetail' })
</script>
