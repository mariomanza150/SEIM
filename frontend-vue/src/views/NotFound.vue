<template>
  <div class="not-found">
    <div class="container text-center">
      <h1 class="display-1">404</h1>
      <p class="lead">Page Not Found</p>
      <p>The page you're looking for doesn't exist.</p>
      <router-link to="/" class="btn btn-primary mt-3">
        Go to Dashboard
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
