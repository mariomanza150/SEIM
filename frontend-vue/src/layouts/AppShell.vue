<template>
  <div class="seim-app-shell" data-testid="app-shell">
    <nav
      class="navbar navbar-dark bg-primary fixed-top seim-app-shell__navbar"
      data-bs-theme="dark"
      :aria-label="t('dashboard.mainNavAria')"
    >
      <div class="container-fluid seim-app-shell__navbar-inner">
        <div class="d-flex align-items-center flex-shrink-0">
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
          <router-link class="navbar-brand mb-0" :to="{ name: 'Dashboard' }">SEIM</router-link>
        </div>

        <ul class="navbar-nav flex-row align-items-center flex-nowrap ms-auto seim-app-shell__utilities">
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

          <li v-if="authStore.isAdmin" class="nav-item dropdown" ref="adminMenuRoot">
            <button
              type="button"
              class="nav-link dropdown-toggle seim-nav-text-btn"
              id="spaAdminNavDropdown"
              data-testid="admin-menu"
              :class="{ show: adminMenuOpen }"
              :aria-expanded="adminMenuOpen ? 'true' : 'false'"
              aria-haspopup="menu"
              @click="toggleAdminMenu"
            >
              <i class="bi bi-sliders me-1" aria-hidden="true"></i>
              <span class="d-none d-md-inline">{{ t('adminNav.consoleMenu') }}</span>
            </button>
            <ul
              class="dropdown-menu dropdown-menu-end"
              :class="{ show: adminMenuOpen }"
              aria-labelledby="spaAdminNavDropdown"
            >
              <li>
                <router-link class="dropdown-item" :to="{ name: 'AdminPrograms' }" @click="closeAdminMenu">
                  {{ t('route.names.AdminPrograms') }}
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" :to="{ name: 'AdminForms' }" @click="closeAdminMenu">
                  {{ t('route.names.AdminForms') }}
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" :to="{ name: 'AdminDynforms' }" @click="closeAdminMenu">
                  {{ t('route.names.AdminDynforms') }}
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" :to="{ name: 'AdminDataManagement' }" @click="closeAdminMenu">
                  {{ t('route.names.AdminDataManagement') }}
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" :to="{ name: 'AdminWorkflows' }" @click="closeAdminMenu">
                  {{ t('route.names.AdminWorkflows') }}
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" :to="{ name: 'AdminDocuments' }" @click="closeAdminMenu">
                  {{ t('route.names.AdminDocuments') }}
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" :to="{ name: 'EligibilityRulesets' }" @click="closeAdminMenu">
                  {{ t('route.names.EligibilityRulesets') }}
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <a class="dropdown-item" href="/seim/django-admin/" target="_blank" rel="noopener noreferrer">
                  <i class="bi bi-gear-wide-connected me-1" aria-hidden="true"></i>{{ t('dashboard.djangoAdmin') }}
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="/cms/" target="_blank" rel="noopener noreferrer">
                  <i class="bi bi-layout-wtf me-1" aria-hidden="true"></i>{{ t('dashboard.cmsAdmin') }}
                </a>
              </li>
            </ul>
          </li>

          <li class="nav-item dropdown" ref="userMenuRoot">
            <button
              type="button"
              class="nav-link dropdown-toggle d-flex align-items-center seim-nav-text-btn"
              id="userDropdown"
              data-testid="user-menu"
              :class="{ show: userMenuOpen }"
              :aria-expanded="userMenuOpen ? 'true' : 'false'"
              aria-haspopup="menu"
              :aria-label="t('dashboard.userMenuAria', { name: userName })"
              @click="toggleUserMenu"
            >
              <i class="bi bi-person-circle me-1" aria-hidden="true"></i>
              <span class="d-none d-sm-inline text-truncate seim-user-name">{{ userName }}</span>
            </button>
            <ul
              class="dropdown-menu dropdown-menu-end"
              :class="{ show: userMenuOpen }"
              aria-labelledby="userDropdown"
            >
              <li>
                <a class="dropdown-item" href="/" data-testid="public-site-link" @click="closeUserMenu">
                  <i class="bi bi-house me-1" aria-hidden="true"></i>{{ t('dashboard.publicSite') }}
                </a>
              </li>
              <li>
                <router-link :to="{ name: 'Profile' }" class="dropdown-item" @click="closeUserMenu">
                  {{ t('route.names.Profile') }}
                </router-link>
              </li>
              <li>
                <router-link :to="{ name: 'Settings' }" class="dropdown-item" @click="closeUserMenu">
                  {{ t('route.names.Settings') }}
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <button class="dropdown-item" type="button" data-testid="logout-link" @click="handleLogout">
                  {{ t('dashboard.logout') }}
                </button>
              </li>
            </ul>
          </li>
        </ul>
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
import { useNavDropdown } from '@/composables/useNavDropdown'
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

const {
  open: userMenuOpen,
  rootEl: userMenuRoot,
  toggle: toggleUserMenu,
  close: closeUserMenu,
} = useNavDropdown()
const {
  open: adminMenuOpen,
  rootEl: adminMenuRoot,
  toggle: toggleAdminMenu,
  close: closeAdminMenu,
} = useNavDropdown()

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
    isVisible: !authStore.canUsePartnerPortal,
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
    key: 'eligibilityRulesets',
    to: { name: 'EligibilityRulesets' },
    label: t('route.names.EligibilityRulesets'),
    iconClass: 'bi bi-funnel',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'nominations',
    to: { name: 'Nominations' },
    label: t('route.names.Nominations'),
    iconClass: 'bi bi-trophy',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'analyticsForecasts',
    to: { name: 'AnalyticsForecasts' },
    label: t('route.names.AnalyticsForecasts'),
    iconClass: 'bi bi-graph-up',
    isVisible: authStore.canUseStaffReviewQueue,
  },
  {
    key: 'partnerPortal',
    to: { name: 'PartnerPortal' },
    label: t('route.names.PartnerPortal'),
    iconClass: 'bi bi-building',
    isVisible: authStore.canUsePartnerPortal,
  },
  {
    key: 'documents',
    to: { name: 'Documents' },
    label: t('route.names.Documents'),
    iconClass: 'bi bi-folder',
    isVisible: !authStore.canUsePartnerPortal,
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
    key: 'adminDynforms',
    to: { name: 'AdminDynforms' },
    label: t('route.names.AdminDynforms'),
    iconClass: 'bi bi-window-sidebar',
  },
  {
    key: 'adminDataManagement',
    to: { name: 'AdminDataManagement' },
    label: t('route.names.AdminDataManagement'),
    iconClass: 'bi bi-database-gear',
  },
  {
    key: 'adminWorkflows',
    to: { name: 'AdminWorkflows' },
    label: t('route.names.AdminWorkflows'),
    iconClass: 'bi bi-diagram-3',
  },
  {
    key: 'adminDocuments',
    to: { name: 'AdminDocuments' },
    label: t('route.names.AdminDocuments'),
    iconClass: 'bi bi-file-earmark-text',
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
  closeUserMenu()
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
  overflow: visible;
}

.seim-app-shell__navbar-inner {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 0.5rem;
}

.seim-app-shell__utilities {
  gap: 0.15rem;
}

.seim-app-shell__navbar :deep(.nav-link),
.seim-app-shell__navbar :deep(.navbar-brand) {
  color: rgba(255, 255, 255, 0.92);
}

.seim-app-shell__navbar :deep(.nav-link:hover),
.seim-app-shell__navbar :deep(.nav-link:focus-visible),
.seim-app-shell__navbar :deep(.navbar-brand:hover) {
  color: #fff;
}

.seim-nav-text-btn {
  background: transparent;
  border: 0;
}

.seim-user-name {
  max-width: min(12rem, 30vw);
  vertical-align: middle;
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

