<template>
  <div class="table-responsive" aria-hidden="true">
    <table class="table">
      <thead>
        <tr>
          <th v-for="n in columns" :key="`head-${n}`">
            <span class="placeholder col-8"></span>
          </th>
        </tr>
      </thead>
      <tbody class="placeholder-glow">
        <tr v-for="row in rows" :key="`row-${row}`">
          <td v-for="col in columns" :key="`cell-${row}-${col}`">
            <span class="placeholder col-10"></span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  rows: { type: Number, default: 5 },
  columns: { type: Number, default: 4 },
})
</script>
