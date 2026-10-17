/**
 * Main entry point for Vue.js application
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { initMonitoring } from './monitoring'
import { installDiagnostics, recordNavigation } from './qa/diagnostics'

// In-memory only; attached to a QA report solely when a tester submits one.
installDiagnostics()

// Bootstrap CSS and icons (JS is loaded by AppShell where Offcanvas is used)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Custom styles
import './style.css'

const app = createApp(App)

// Install Pinia (state management)
const pinia = createPinia()
app.use(pinia)

// Install Vue Router
app.use(router)
router.afterEach((to, from) => recordNavigation(to, from))

app.use(i18n)

// Error reporting and log capture: no-op unless VITE_SENTRY_DSN was set at build time.
// Initialised before mount so errors during the first render are captured; without a DSN it
// resolves immediately and nothing is loaded.
initMonitoring(app, router)
  .catch(() => false)
  .finally(() => app.mount('#app'))
