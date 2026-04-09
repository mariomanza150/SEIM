# Vue + Wagtail Content & Path Alignment Revision Prompt

## System Role
You are a Senior Full Stack Engineer responsible for ensuring perfect alignment between Vue 3 frontend application and Wagtail 5 CMS backend for the SEIM Student Exchange Information Manager system.

## Context
This project currently operates with a dual frontend architecture:
- ✅ New Vue 3 SPA with Vue Router at `/seim/` base path
- ✅ Existing Wagtail CMS with public pages, content, and form builder
- ✅ Django template-based legacy frontend being migrated to Vue
- ✅ Both systems share authentication, API, and user sessions

---

## PRIMARY OBJECTIVE
**Audit and revise ALL content, links, buttons, navigation paths, and routing between Vue and Wagtail systems. Ensure 100% consistency, no broken links, proper context preservation, and seamless user experience across both systems.**

---

## 📋 VALIDATION CHECKLIST - EXECUTE IN ORDER

### 1. 🔍 PATH BASE CONTEXT
```
✅ Vue Router base path: "/seim/" (defined in router/index.js createWebHistory('/seim/'))
✅ Wagtail CMS root path: "/"
✅ Django legacy pages: "/"
✅ API base: "/api/"
✅ Admin paths: "/seim/admin/", "/cms/"
```

> **CRITICAL RULE:** ALL links from Vue to CMS/Django pages MUST EXCLUDE the `/seim/` prefix. ALL internal Vue links MUST use relative paths or named routes without leading slash.

---

### 2. 🗺️ ROUTING CROSS-REFERENCE MATRIX

| Purpose | Vue Path (SPA) | Django/Wagtail Path | Cross-link Requirements |
|---------|----------------|----------------------|------------------------|
| Login | `/login` | `/login/` | Auto-detect auth state, preserve redirect target |
| Dashboard | `/dashboard` | `/dashboard/` | Vue is primary, legacy path should redirect |
| Applications | `/applications` | `/applications/` | All links must point to Vue implementation |
| Documents | `/documents` | `/documents/` | All links must point to Vue implementation |
| Notifications | `/notifications` | N/A | Exclusive to Vue |
| Profile | `/profile` | `/profile/` | Sync both implementations |
| Programs | N/A | `/programs/` | Links from Vue should open Wagtail program pages |
| CMS Admin | N/A | `/cms/` | Open in new tab from Vue navigation |
| Django Admin | N/A | `/seim/admin/` | Open in new tab from Vue navigation |

---

### 3. 🔗 LINK VALIDATION RULES

#### FOR VUE COMPONENTS:
✅ **Use named routes for internal navigation:**
```vue
<router-link :to="{ name: 'ApplicationDetail', params: { id: app.id } }">
```

✅ **For external links to CMS/Django:**
```vue
<a href="/programs/" target="_blank" rel="noopener noreferrer">
```

✅ **For API calls:** Always use relative paths without `/seim/` prefix
```javascript
api.get('/api/accounts/dashboard/stats/')
```

❌ **NEVER DO THIS:**
```vue
<router-link to="/seim/applications"> ❌ WRONG - duplicates base path
<a href="/seim/programs/"> ❌ WRONG - CMS is at root
```

---

### 4. 🎯 BUTTON & ACTION INTEGRITY CHECK

For EVERY button, link, and navigation element:

1. **Verify target path matches intended destination system**
2. **Check for proper `target="_blank"` on external/admin links**
3. **Validate `rel="noopener noreferrer"` on new tab links**
4. **Ensure no trailing slash inconsistencies**
5. **Confirm proper authentication state awareness**
6. **Verify user role visibility matches permissions**
7. **Check that CTA buttons point to correct implementation (Vue vs CMS)**

---

### 5. 📄 WAGTAIL CONTENT INTEGRATION

For ALL Wagtail page types:
- ✅ **ProgramPage**: Links to `/applications/new` in Vue with program parameter
- ✅ **MovilidadLandingPage**: "Apply Now" CTA points to correct Vue application flow
- ✅ **ConvenioPage**: Application buttons preserve program context
- ✅ **FormPage**: Form submissions properly integrate with Vue application state
- ✅ **BlogPostPage**: Internal links maintain consistent navigation context
- ✅ **FAQPage**: Action links point to appropriate system

---

### 6. 🔄 NAVIGATION SYNCHRONIZATION

Both systems MUST show identical navigation structure:

| Navigation Item | Visibility | Target |
|-----------------|------------|--------|
| Dashboard | Authenticated | `/dashboard` (Vue) |
| Programs | All users | `/programs/` (Wagtail) |
| Applications | Authenticated | `/applications` (Vue) |
| Calendar | Authenticated | `/calendar/` (Django) |
| Admin Dashboard | Admin | `/seim/admin/` (new tab) |
| CMS Admin | Admin | `/cms/` (new tab) |

✅ Verify active state highlighting works correctly
✅ Verify role-based visibility matches in both systems
✅ Verify logout flow clears tokens in both systems
✅ Verify theme preferences sync between Vue and Django templates

---

### 7. 🚦 ERROR & REDIRECT HANDLING

1. **404 Pages:** Both systems must maintain consistent styling
2. **Authentication Redirects:** Preserve original target URL across systems
3. **Session Expiry:** Seamless transition between login forms
4. **Permission Denied:** Consistent error pages with proper navigation

---

### 8. ✅ FINAL VALIDATION STEPS

Before completing revision:

- [ ] Test every navigation link end-to-end
- [ ] Verify no mixed content warnings
- [ ] Confirm authentication state persists across system boundaries
- [ ] Check all CTA buttons from CMS landing pages
- [ ] Validate form submission flows between Wagtail forms and Vue applications
- [ ] Confirm deep linking works correctly
- [ ] Verify back button behavior is consistent
- [ ] Test in both authenticated and anonymous states
- [ ] Validate all user role views
- [ ] Check mobile responsive navigation

---

## 🎯 IMPLEMENTATION PRIORITIES

1. **Fix broken cross-system links first**
2. **Standardize navigation behavior**
3. **Ensure CTA buttons direct users to correct implementation**
4. **Resolve path prefix inconsistencies**
5. **Add proper security attributes on external links**
6. **Synchronize role-based visibility**
7. **Validate error handling flows**

---

## ACCEPTANCE CRITERIA

✅ No broken links between Vue and Wagtail
✅ No 404 errors from navigation actions
✅ Seamless user experience across both systems
✅ Consistent navigation structure everywhere
✅ Proper security attributes on all external links
✅ Authentication state preserved when moving between systems
✅ All CTA buttons point to correct application flow
✅ No duplicate base path in URLs
✅ Consistent error handling across the entire application

---

> **REMEMBER:** This is NOT a rewrite. This is an alignment and consistency audit. Preserve all existing functionality while fixing path, link, and navigation inconsistencies between the two systems.

**Execute this prompt systematically and document all changes made.**