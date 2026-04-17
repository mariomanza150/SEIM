<template>
  <div class="seim-app-shell" data-testid="app-shell">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top seim-app-shell__navbar" :aria-label="t('dashboard.mainNavAria')">
      <div class="container-fluid">
        <button
          class="btn btn-outline-light me-2 d-lg-none"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#seimSidebarOffcanvas"
          aria-controls="seimSidebarOffcanvas"
          :aria-label="t('dashboard.toggleNav')"
        >
          <i class="bi bi-list" aria-hidden="true" />
        </button>
        <button
          type="button"
          class="btn btn-outline-light me-2 d-none d-md-inline-flex align-items-center"
          :aria-pressed="sidebarCollapsed ? 'true' : 'false'"
          :aria-label="t('dashboard.toggleSidebar')"
          @click="toggleSidebarCollapsed"
        >
          <i
            :class="sidebarCollapsed ? 'bi bi-layout-sidebar' : 'bi bi-layout-sidebar-inset'"
            aria-hidden="true"
          />
        </button>
        <router-link class="navbar-brand" :to="{ name: 'Dashboard' }">SEIM</router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          :aria-label="t('dashboard.toggleNav')"
          aria-controls="navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto align-items-center">
            <li class="nav-item d-flex align-items-center">
              <button
                type="button"
                class="btn btn-link nav-link py-2 seim-theme-toggle"
                data-testid="app-shell-theme-toggle"
                :aria-label="themeToggleAria"
                @click="toggleNavTheme"
              >
                <i :class="resolvedIsDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill'" aria-hidden="true" />
              </button>
            </li>
            <NotificationDropdown />

            <li class="nav-item dropdown" v-if="authStore.isAdmin">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                id="spaAdminNavDropdown"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                aria-haspopup="menu"
              >
                <i class="bi bi-sliders me-1" aria-hidden="true"></i>
                {{ t('adminNav.consoleMenu') }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="spaAdminNavDropdown">
                <li>
                  <router-link class="dropdown-item" :to="{ name: 'AdminPrograms' }">
                    {{ t('route.names.AdminPrograms') }}
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" :to="{ name: 'AdminForms' }">
                    {{ t('route.names.AdminForms') }}
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" :to="{ name: 'AdminWorkflows' }">
                    {{ t('route.names.AdminWorkflows') }}
                  </router-link>
                </li>
              </ul>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <a class="nav-link" href="/seim/django-admin/" target="_blank" rel="noopener noreferrer">
                <i class="bi bi-gear-wide-connected me-1"></i> {{ t('dashboard.djangoAdmin') }}
              </a>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <a class="nav-link" href="/cms/" target="_blank" rel="noopener noreferrer">
                <i class="bi bi-layout-wtf me-1"></i> {{ t('dashboard.cmsAdmin') }}
              </a>
            </li>

            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                id="userDropdown"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                aria-haspopup="menu"
                :aria-label="t('dashboard.userMenuAria', { name: userName })"
              >
                <i class="bi bi-person-circle me-1"></i>
                {{ userName }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li>
                  <router-link :to="{ name: 'Profile' }" class="dropdown-item">{{ t('route.names.Profile') }}</router-link>
                </li>
                <li>
                  <router-link :to="{ name: 'Settings' }" class="dropdown-item">{{ t('route.names.Settings') }}</router-link>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="handleLogout" data-testid="logout-link">
                    {{ t('dashboard.logout') }}
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div
      id="seimSidebarOffcanvas"
      class="offcanvas offcanvas-start d-lg-none"
      tabindex="-1"
      :aria-label="t('dashboard.mainNavAria')"
    >
      <div class="offcanvas-header">
        <h5 class="offcanvas-title">SEIM</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" :aria-label="t('common.close')" />
      </div>
      <div class="offcanvas-body pt-0">
        <SidebarNavList
          :aria-label="t('dashboard.mainNavAria')"
          :primary-items="primaryNavItemsVisible"
          :admin-items="adminNavItems"
          :show-admin="authStore.isAdmin"
          :admin-section-label="t('adminNav.sectionTitle')"
          @navigate="closeSidebarOffcanvas"
        />
      </div>
    </div>

    <div class="container-fluid mt-4">
      <div class="row">
        <aside
          v-show="!sidebarCollapsed"
          class="col-md-3 col-lg-2 d-none d-md-block seim-app-shell__aside"
        >
          <SidebarNavList
            :aria-label="t('dashboard.mainNavAria')"
            :primary-items="primaryNavItemsVisible"
            :admin-items="adminNavItems"
            :show-admin="authStore.isAdmin"
            :admin-section-label="t('adminNav.sectionTitle')"
          />
        </aside>

        <section class="col-12" :class="sidebarCollapsed ? '' : 'col-md-9 col-lg-10'">
          <router-view />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NotificationDropdown from '@/components/NotificationDropdown.vue'
import SidebarNavList from '@/components/nav/SidebarNavList.vue'
import api from '@/services/api'
import { applyUiPreferences, readStoredUiPreferences, resolveTheme } from '@/services/uiPreferences'
import { Offcanvas } from 'bootstrap'

const SIDEBAR_COLLAPSED_KEY = 'seim.sidebarCollapsed'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.userName)

const sidebarCollapsed = ref(false)

onMounted(() => {
  try {
    sidebarCollapsed.value = localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1'
  } catch {
    sidebarCollapsed.value = false
  }
})

function toggleSidebarCollapsed() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  try {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, sidebarCollapsed.value ? '1' : '0')
  } catch {
    /* ignore */
  }
}

const themeUiTick = ref(0)
const resolvedIsDark = computed(() => {
  themeUiTick.value
  const cur = readStoredUiPreferences() || {}
  return resolveTheme(cur.theme || 'auto') === 'dark'
})

const themeToggleAria = computed(() =>
  resolvedIsDark.value ? t('dashboard.themeToggleAriaLight') : t('dashboard.themeToggleAriaDark'),
)

const primaryNavItems = computed(() => [
  {
    key: 'dashboard',
    to: { name: 'Dashboard' },
    label: t('route.names.Dashboard'),
    iconClass: 'bi bi-house-door',
    isVisible: true,
  },
  {
    key: 'applications',
    to: { name: 'Applications' },
    label: t('route.names.Applications'),
    iconClass: 'bi bi-file-earmark-text',
    isVisible: true,
  },
  {
    key: 'programCompare',
    to: { name: 'ProgramCompare' },
    label: t('route.names.ProgramCompare'),
    iconClass: 'bi bi-columns-gap',
    isVisible: true,
  },
  {
    key: 'reviewQueue',
    to: { name: 'CoordinatorReviewQueue' },
    label: t('route.names.CoordinatorReviewQueue'),
    iconClass: 'bi bi-clipboard-check',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'workload',
    to: { name: 'CoordinatorWorkload' },
    label: t('dashboard.nav.workload'),
    iconClass: 'bi bi-graph-up-arrow',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'notificationRouting',
    to: { name: 'NotificationRouting' },
    label: t('dashboard.nav.notificationRouting'),
    iconClass: 'bi bi-diagram-3',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'exchangeAgreements',
    to: { name: 'StaffExchangeAgreements' },
    label: t('route.names.StaffExchangeAgreements'),
    iconClass: 'bi bi-file-earmark-richtext',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'documents',
    to: { name: 'Documents' },
    label: t('route.names.Documents'),
    iconClass: 'bi bi-folder',
    isVisible: true,
  },
  {
    key: 'deadlines',
    to: { name: 'DeadlinesCalendar' },
    label: t('dashboard.nav.deadlines'),
    iconClass: 'bi bi-calendar3',
    isVisible: true,
  },
  {
    key: 'notifications',
    to: { name: 'Notifications' },
    label: t('route.names.Notifications'),
    iconClass: 'bi bi-bell',
    isVisible: true,
  },
  {
    key: 'settings',
    to: { name: 'Settings' },
    label: t('route.names.Settings'),
    iconClass: 'bi bi-gear',
    isVisible: true,
  },
])

const primaryNavItemsVisible = computed(() => primaryNavItems.value.filter((item) => item.isVisible))

const adminNavItems = computed(() => [
  {
    key: 'adminPrograms',
    to: { name: 'AdminPrograms' },
    label: t('route.names.AdminPrograms'),
    iconClass: 'bi bi-mortarboard',
  },
  {
    key: 'adminForms',
    to: { name: 'AdminForms' },
    label: t('route.names.AdminForms'),
    iconClass: 'bi bi-ui-checks-grid',
  },
  {
    key: 'adminWorkflows',
    to: { name: 'AdminWorkflows' },
    label: t('route.names.AdminWorkflows'),
    iconClass: 'bi bi-diagram-3',
  },
])

function closeSidebarOffcanvas() {
  const el = document.getElementById('seimSidebarOffcanvas')
  if (!el) return
  const instance = Offcanvas.getInstance(el) || new Offcanvas(el)
  instance.hide()
}

async function toggleNavTheme() {
  const cur = readStoredUiPreferences() || {}
  const resolved = resolveTheme(cur.theme || 'auto')
  const nextTheme = resolved === 'dark' ? 'light' : 'dark'
  applyUiPreferences({
    ...cur,
    theme: nextTheme,
    font_size: cur.font_size || 'normal',
    high_contrast: Boolean(cur.high_contrast),
    reduce_motion: Boolean(cur.reduce_motion),
  })
  themeUiTick.value += 1
  try {
    await api.patch('/api/accounts/user-settings/', { theme: nextTheme })
  } catch {
    /* local preference already applied */
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.seim-app-shell {
  /* Space for fixed-top navbar (flow is removed from document) */
  padding-top: calc(3.75rem + env(safe-area-inset-top, 0px));
  min-height: 100vh;
  background-color: var(--seim-app-bg);
}

.navbar.seim-app-shell__navbar {
  /* Bootstrap fixed-top default; must stay below offcanvas/backdrop (see Bootstrap z-index stack) */
  z-index: 1030;
  padding-top: env(safe-area-inset-top, 0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.seim-app-shell__aside {
  align-self: flex-start;
}

.seim-theme-toggle {
  color: rgba(255, 255, 255, 0.92) !important;
  text-decoration: none;
}

.seim-theme-toggle:hover {
  color: #fff !important;
}

.list-group-item {
  border: none;
  border-radius: 0.5rem;
  margin-bottom: 0.25rem;
}

.list-group-item.active {
  background-color: var(--seim-brand-primary, #667eea);
  border-color: var(--seim-brand-primary, #667eea);
}
</style>

