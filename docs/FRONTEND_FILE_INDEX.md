# SEIM Frontend - File Index

**Purpose:** Quick reference for locating and understanding frontend files  
**Last Updated:** 2026-01-29

---

## 📂 Core Application Files

### Django Frontend App

| File | Lines | Purpose | Notes |
|------|-------|---------|-------|
| `frontend/views.py` | 493 | View controllers for all frontend pages | Main routing logic |
| `frontend/urls.py` | 58 | URL patterns | Maps URLs to views |
| `frontend/forms.py` | - | Django form definitions | For server-side forms |
| `frontend/apps.py` | - | App configuration | Django app setup |

---

## 📄 Template Files

### Base Templates

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `templates/base.html` | 576 | Master template (all pages extend) | ⚠️ Too large, has inline JS |
| `templates/calendar.html` | - | Calendar page | ✅ Clean |
| `templates/preferences.html` | - | User preferences | ✅ Clean |

### Frontend Pages

| File | Lines | Purpose | Role Access |
|------|-------|---------|-------------|
| `templates/frontend/home.html` | - | Public landing page | All |
| `templates/frontend/dashboard.html` | 862 | Main user dashboard | ⚠️ Too large, All authenticated |
| `templates/frontend/profile.html` | - | User profile | All authenticated |
| `templates/frontend/settings.html` | - | User settings | All authenticated |
| `templates/frontend/sessions.html` | - | Session management | All authenticated |
| `templates/frontend/user-management.html` | - | User admin panel | Coordinator, Admin |

### Auth Templates

| File | Purpose | Access |
|------|---------|--------|
| `templates/frontend/auth/login.html` | Login page | Public |
| `templates/frontend/auth/register.html` | Registration page | Public |
| `templates/frontend/auth/password_reset.html` | Password reset | Public |

### Application Templates

| File | Purpose | Access |
|------|---------|--------|
| `templates/frontend/applications/list.html` | List applications | Authenticated |
| `templates/frontend/applications/detail.html` | View application | Owner, Staff |
| `templates/frontend/applications/form.html` | Create/edit application | Student |

### Program Templates

| File | Purpose | Access |
|------|---------|--------|
| `templates/frontend/programs/list.html` | Browse programs | Authenticated |
| `templates/frontend/programs/form.html` | Create/edit program | Admin |

### Document Templates

| File | Purpose | Access |
|------|---------|--------|
| `templates/frontend/documents/list.html` | List documents | Authenticated |
| `templates/frontend/documents/detail.html` | View document | Owner, Staff |
| `templates/frontend/documents/form.html` | Upload document | Authenticated |

### Admin Templates

| File | Purpose | Access |
|------|---------|--------|
| `templates/frontend/admin/dashboard.html` | Admin dashboard | Admin |
| `templates/frontend/admin/analytics.html` | Analytics page | Admin, Coordinator |

### Coordinator Templates

| File | Purpose | Access |
|------|---------|--------|
| `templates/frontend/coordinator/dashboard.html` | Coordinator dashboard | Coordinator, Admin |

### Component Templates

| File | Purpose | Reusable |
|------|---------|----------|
| `templates/components/navigation/navbar.html` | Main navigation | ✅ Yes |
| `templates/components/footer.html` | Page footer | ✅ Yes |
| `templates/components/messages.html` | Flash messages | ✅ Yes |
| `templates/components/notification-center.html` | Notification panel | ✅ Yes |
| `templates/components/language-switcher.html` | Language selector | ✅ Yes |
| `templates/components/forms/search_form.html` | Search form | ✅ Yes |
| `templates/components/tables/data_table.html` | Data table | ✅ Yes |

---

## 🎨 CSS Files

### Main CSS

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `static/css/main.css` | - | Entry point (imports all) | ✅ Good |
| `static/css/critical.css` | - | Critical inline styles | ✅ Good |
| `static/css/dark-mode.css` | - | Dark theme styles | ✅ Good |
| `static/css/accessibility.css` | - | A11y improvements | ✅ Good |
| `static/css/mobile-optimizations.css` | - | Mobile-specific styles | ✅ Good |
| `static/css/uadec-styles.css` | - | Institution branding | ✅ Good |

### Component CSS

| File | Purpose |
|------|---------|
| `static/css/components/buttons.css` | Button styles |
| `static/css/components/cards.css` | Card styles |
| `static/css/components/forms.css` | Form styles |
| `static/css/components/tables.css` | Table styles |

### Layout CSS

| File | Purpose |
|------|---------|
| `static/css/layouts/base.css` | Base layout |
| `static/css/layouts/navigation.css` | Navigation styles |

### Utility CSS

| File | Purpose |
|------|---------|
| `static/css/utilities/colors.css` | Color variables |
| `static/css/utilities/spacing.css` | Spacing utilities |
| `static/css/utilities/typography.css` | Typography styles |

---

## 📜 JavaScript Files

### Main JavaScript

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `static/js/main.js` | 745 | App initialization | ✅ Modular |
| `static/js/auth.js` | - | Auth utilities | ⚠️ Duplicate |
| `static/js/dashboard.js` | - | Dashboard logic | ✅ OK |
| `static/js/applications.js` | - | Application handling | ✅ OK |
| `static/js/documents.js` | - | Document management | ✅ OK |
| `static/js/programs.js` | - | Program listing | ✅ OK |
| `static/js/grades.js` | - | Grade management | ✅ OK |
| `static/js/theme-manager.js` | - | Dark mode toggle | ✅ Good |
| `static/js/sw.js` | - | Service worker | ✅ Good |

### Core Modules

| File | Purpose | Quality |
|------|---------|---------|
| `static/js/modules/api.js` | API client (basic) | ⚠️ Superseded |
| `static/js/modules/api-enhanced.js` | API client (enhanced) | ✅ Good |
| `static/js/modules/auth.js` | Auth service (old) | ⚠️ Duplicate |
| `static/js/modules/auth-unified.js` | Auth service (unified) | ⚠️ Duplicate |
| `static/js/modules/error-handler.js` | Error management | ✅ Excellent |
| `static/js/modules/logger.js` | Logging system | ✅ Excellent |
| `static/js/modules/performance.js` | Performance tracking | ✅ Good |
| `static/js/modules/security.js` | XSS/CSRF protection | ✅ Good |

### Feature Modules

| File | Purpose | Complexity |
|------|---------|------------|
| `static/js/modules/dynamic-forms.js` | Form builder | High |
| `static/js/modules/file_upload.js` | File handling | Medium |
| `static/js/modules/calendar.js` | Calendar widget | Medium |
| `static/js/modules/saved-searches.js` | Search persistence | Low |
| `static/js/modules/advanced-search.js` | Complex filtering | Medium |

### UI Modules

| File | Purpose |
|------|---------|
| `static/js/modules/ui.js` | UI utilities (basic) |
| `static/js/modules/ui-enhanced.js` | UI utilities (enhanced) |
| `static/js/modules/ui/auth_ui.js` | Auth UI components |
| `static/js/modules/ui/bootstrap_helpers.js` | Bootstrap utilities |
| `static/js/modules/ui/loading.js` | Loading states |

### Notification Modules

| File | Purpose |
|------|---------|
| `static/js/modules/notifications.js` | Notification utilities |
| `static/js/modules/toast-notifications.js` | Toast messages |
| `static/js/modules/notification-center.js` | Notification panel |
| `static/js/modules/websocket-client.js` | WebSocket handler |

### Data Modules

| File | Purpose |
|------|---------|
| `static/js/modules/applications_list.js` | Application listing |
| `static/js/modules/applications_actions.js` | Application actions |
| `static/js/modules/documents_list.js` | Document listing |
| `static/js/modules/programs_list.js` | Program listing |

### Quality Modules

| File | Purpose | Priority |
|------|---------|----------|
| `static/js/modules/accessibility.js` | A11y features | High |
| `static/js/modules/accessibility-tester.js` | A11y testing | Medium |
| `static/js/modules/validators.js` | Input validation | High |
| `static/js/modules/utils.js` | Utility functions | High |

### System Modules

| File | Purpose |
|------|---------|
| `static/js/modules/dynamic-loader.js` | Code splitting |
| `static/js/modules/preferences.js` | User preferences |

---

## 🔧 Build Configuration

| File | Purpose | Priority |
|------|---------|----------|
| `webpack.config.js` | Module bundling | Critical |
| `package.json` | Dependencies & scripts | Critical |
| `package-lock.json` | Dependency lock | Critical |
| `.eslintrc.js` | Linting rules | High |
| `.prettierrc` | Code formatting | Medium |
| `babel.config.js` | JS transpilation | High |

---

## 🧪 Test Files

### Current Frontend Test Coverage

```text
frontend-vue/src/
  ├── services/api.spec.js             # API client tests
  ├── services/websocket.spec.js       # WebSocket URL/service tests
  ├── stores/auth.spec.js              # Pinia auth store tests
  └── views/Login.spec.js              # Login view tests

tests/e2e_playwright/
  └── test_vue_ui.py                   # Vue SPA UI workflow coverage
```

---

## 📊 Analysis Files

### Code Quality Tools

| File | Purpose |
|------|---------|
| `scripts/code-quality-analyzer.js` | Code quality checks |
| `scripts/maintenance-automation.js` | Automated maintenance |
| `scripts/monitoring-system.js` | Performance monitoring |

---

## 🗂️ File Size Analysis

### Largest Files (Need Attention)

| File | Lines | Recommendation |
|------|-------|----------------|
| `templates/frontend/dashboard.html` | 862 | ⚠️ Split into components |
| `templates/base.html` | 576 | ⚠️ Extract inline JS, split |
| `static/js/main.js` | 745 | ⚠️ Split initialization logic |
| `frontend/views.py` | 493 | ✅ OK for now |

### Files with Inline JavaScript

| File | JS Lines | Action Required |
|------|----------|-----------------|
| `templates/base.html` | ~200 | 🔴 Extract to `base-init.js` |
| `templates/frontend/dashboard.html` | ~700 | 🔴 Extract to `dashboard-init.js` |

### Duplicate/Redundant Files

| Files | Issue | Resolution |
|-------|-------|------------|
| `auth.js`, `modules/auth.js`, `modules/auth-unified.js` | Multiple auth implementations | 🔴 Consolidate to single `AuthService` |
| `api.js`, `api-enhanced.js` | Two API clients | 🟡 Use enhanced version only |
| `ui.js`, `ui-enhanced.js` | Two UI utilities | 🟡 Merge or clarify purpose |

---

## 🔍 Quick Find

### "Where is the code for...?"

| Feature | File(s) |
|---------|---------|
| **Login page** | `templates/frontend/auth/login.html` |
| **Login logic** | `frontend/views.py` (login_view) |
| **Login API** | `accounts/views.py` (LoginView) |
| **Dashboard** | `templates/frontend/dashboard.html` |
| **Navigation** | `templates/components/navigation/navbar.html` |
| **Dark mode** | `static/js/theme-manager.js`, `static/css/dark-mode.css` |
| **Authentication** | `static/js/modules/auth-unified.js` |
| **API calls** | `static/js/modules/api-enhanced.js` |
| **Notifications** | `static/js/modules/notification-center.js` |
| **WebSockets** | `static/js/modules/websocket-client.js` |
| **Form validation** | `static/js/modules/validators.js` |
| **Error handling** | `static/js/modules/error-handler.js` |
| **File upload** | `static/js/modules/file_upload.js` |

---

## 📝 Notes

### Files to Create (High Priority)

- [ ] `static/js/init/base-init.js` - Extract from base.html
- [ ] `static/js/init/dashboard-init.js` - Extract from dashboard.html
- [ ] `static/js/modules/auth-service.js` - Consolidated auth
- [ ] `tests/frontend/unit/auth-service.test.js` - Auth tests
- [ ] `tests/frontend/integration/auth-flow.test.js` - Auth flow tests

### Files to Refactor

- [ ] `templates/base.html` - Split into smaller includes
- [ ] `templates/frontend/dashboard.html` - Split into components
- [ ] `static/js/main.js` - Extract some functions

### Files to Remove (After Migration)

- [ ] `static/js/auth.js` - After consolidation
- [ ] `static/js/modules/auth.js` - After consolidation
- [ ] `static/js/modules/api.js` - Use enhanced version only

---

## 🚀 New Developer Onboarding

**Most Important Files to Understand First:**

1. `templates/base.html` - Master template
2. `frontend/views.py` - View controllers
3. `frontend/urls.py` - URL routing
4. `static/js/main.js` - JS initialization
5. `static/js/modules/auth-unified.js` - Authentication
6. `static/js/modules/api-enhanced.js` - API client
7. `static/css/main.css` - CSS entry point

**Typical Development Flow:**

1. Create view in `frontend/views.py`
2. Add URL in `frontend/urls.py`
3. Create template in `templates/frontend/`
4. Add styles in `static/css/components/`
5. Add JS logic in `static/js/modules/`
6. Test in browser
7. Write tests in `tests/frontend/`

---

**Last Updated:** 2026-01-29  
**Maintained By:** SEIM Development Team  
**Version:** 1.0
