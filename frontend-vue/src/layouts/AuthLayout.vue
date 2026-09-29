<template>
  <div class="seim-auth-layout">
    <div class="seim-auth-layout__utilities">
      <button
        type="button"
        class="btn btn-sm seim-auth-layout__theme-btn"
        :aria-label="themeToggleAria"
        data-testid="auth-theme-toggle"
        @click="toggleTheme"
      >
        <i :class="resolvedIsDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill'" aria-hidden="true" />
      </button>
      <LocaleSwitcher
        active-class="btn-light"
        inactive-class="btn-outline-light"
      />
    </div>

    <div class="container">
      <div class="row justify-content-center">
        <div :class="colClass">
          <div class="text-center mb-4 seim-auth-layout__brand">
            <img
              v-if="brandLogoUrl"
              :src="brandLogoUrl"
              :alt="brandLabel"
              class="seim-auth-layout__logo mb-3"
              height="48"
            />
            <h1 class="h3 mb-2 fw-normal text-white">{{ brandLabel }}</h1>
            <p v-if="subtitle" class="text-white-50 mb-0">{{ subtitle }}</p>
          </div>

          <div class="card shadow seim-auth-layout__card">
            <div class="card-body p-4">
              <router-view />
            </div>
          </div>

          <div v-if="showVersion" class="text-center mt-3 text-white-50 small">
            <p class="mb-0">{{ versionCaption }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { version as vueRuntimeVersion } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'
import { useBranding } from '@/composables/useBranding'
import { useThemeToggle } from '@/composables/useThemeToggle'

const { t } = useI18n()
const route = useRoute()
const { branding, loadBranding } = useBranding()
const { resolvedIsDark, themeToggleAria, toggleTheme } = useThemeToggle()

const buildTag = import.meta.env.VITE_APP_VERSION || ''

onMounted(() => {
  loadBranding()
})

const brandLogoUrl = computed(() => branding.value?.logo_url || '')
const brandLabel = computed(() => branding.value?.nav_brand || branding.value?.short_name || 'SEIM')

const subtitle = computed(() => {
  const key = route.meta.authSubtitleKey
  return key ? t(key) : ''
})

const colClass = computed(() => route.meta.authColClass || 'col-md-6 col-lg-4')

const showVersion = computed(() => route.meta.authShowVersion !== false)

const versionCaption = computed(() => {
  const vue = vueRuntimeVersion
  if (buildTag) {
    return t('login.versionLineWithBuild', { build: buildTag, vue })
  }
  return t('login.versionLine', { vue })
})
</script>

<style scoped>
.seim-auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 2rem 0;
  background: linear-gradient(
    135deg,
    var(--seim-brand-primary, var(--brand-primary, #667eea)) 0%,
    var(--seim-brand-secondary, var(--brand-accent, #764ba2)) 100%
  );
  position: relative;
}

.seim-auth-layout__utilities {
  position: absolute;
  top: max(1rem, env(safe-area-inset-top, 0px));
  right: max(1rem, env(safe-area-inset-right, 0px));
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 2;
}

.seim-auth-layout__theme-btn {
  color: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.12);
}

.seim-auth-layout__theme-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.seim-auth-layout__logo {
  max-height: 48px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
}

.seim-auth-layout__card {
  border: none;
  border-radius: 1rem;
}

html[data-theme='dark'] .seim-auth-layout__card {
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
}
</style>
