/**
 * Main entry point for Vue.js application
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Custom styles
import './style.css'

const app = createApp(App)

// Install Pinia (state management)
const pinia = createPinia()
app.use(pinia)

// Install Vue Router
app.use(router)

// Mount app
app.mount('#app')
