# Vue.js Migration Review – What’s Been Built

**Branch:** `feature/vue-migration`  
**Days completed:** 1–7  
**Last commit:** Day 7 – Notifications module  

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (http://localhost:5173 – dev / served by Django)   │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  Vue 3 SPA (Vite)                                           │
│  • Vue Router (history mode)                                │
│  • Pinia (auth store)                                        │
│  • Axios + JWT interceptors                                │
│  • Bootstrap 5 + Bootstrap Icons                          │
└─────────────────────────────┬───────────────────────────────┘
                              │ Proxy / API base URL
┌─────────────────────────────▼───────────────────────────────┐
│  Django Backend (http://localhost:8001 – dev)               │
│  • REST API (/api/)                                         │
│  • JWT auth (simplejwt)                                     │
│  • Admin: /seim/admin/, Wagtail: /cms/                      │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  PostgreSQL (5434) | Redis (6379) | Celery                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. What Was Built (by Day)

### Day 1 – Django configuration
- **CORS:** `seim/settings/development.py` – origins for `localhost:5173`, methods, headers.
- **Templates:** `base.py` – `frontend-vue/dist` in `TEMPLATES['DIRS']`.
- **Static:** `base.py` – `frontend-vue/dist/assets` in `STATICFILES_DIRS` (commented until build).
- **URLs:** `seim/urls.py` – catch‑all for SPA; admin/API routes unchanged; backup in `urls_OLD_BACKUP.py`.
- **.gitignore:** Vue/frontend‑vue entries.

### Day 2 – Vue project setup
- **Project:** `frontend-vue/` – Vite + Vue 3.
- **Stack:** Vue Router 4, Pinia, Axios, Bootstrap 5, Bootstrap Icons.
- **Config:** `vite.config.js` – proxy to Django (8001), `@` alias, env prefix `VITE_`.
- **Env:** `.env`, `.env.development`, `.env.production` (API/WS URLs, app name/version).
- **Structure:** `src/services/api.js`, `src/stores/auth.js`, `src/router/index.js`, `src/views/`, `src/components/`, `src/composables/`, `src/utils/`.
- **Dockerfile:** Multi‑stage build – Node stage builds Vue, Python stage copies `frontend-vue/dist`.

### Day 3 – Auth & dashboard
- **Backend:** `create_vue_test_users` (admin, coordinator, student, test@example.com), `accounts/views_dashboard.py` – `/api/accounts/dashboard/stats/`.
- **Auth store:** Login, logout, refresh token, profile fetch, `localStorage` tokens.
- **API service:** JWT in headers, 401 → refresh then retry.
- **Views:** Login, Dashboard (stats cards, sidebar), NotFound.
- **Router:** Guards for protected routes and login redirect.
- **Toasts:** `useToast` composable + `ToastContainer`; used on login/logout/dashboard errors.
- **Ports:** Docker web → 8001, db → 5434 (avoid conflicts).

### Day 4 – Applications module
- **Views:** `Applications.vue` (list, filters, search, pagination), `ApplicationDetail.vue` (timeline, quick actions).
- **Routes:** `/applications`, `/applications/:id`.
- **Dashboard:** Applications card and sidebar link to list.

### Day 5 – Application form & programs
- **Backend:** `create_test_programs` – 6 exchange programs.
- **View:** `ApplicationForm.vue` – create/edit, program select, optional statement, program info sidebar.
- **Routes:** `/applications/new`, `/applications/:id/edit`.
- **List/Detail:** Links to “New Application” and “Edit” for drafts.

### Day 6 – Documents module
- **Views:** `Documents.vue` (list, filters by application/type/valid), `DocumentDetail.vue` (metadata, download).
- **Component:** `DocumentUpload.vue` – type + file, multipart POST to `/api/documents/`.
- **Integration:** Application detail sidebar – upload + list of application documents; `resolveFileUrl()` in `src/utils/apiUrl.js` for download links.
- **Routes:** `/documents`, `/documents/:id`.
- **Dashboard:** Documents card and sidebar link.

### Day 7 – Notifications module
- **Backend:** `create_test_notifications` – `--user`, `--count`.
- **Views:** `Notifications.vue` – list, filters (read/category), mark one / mark all read.
- **Component:** `NotificationDropdown.vue` – bell + count, 5 recent, “View all”.
- **Route:** `/notifications`.
- **Dashboard:** Notifications card, sidebar link, navbar dropdown.

---

## 3. Routes Summary

| Route | View | Auth | Purpose |
|-------|------|------|---------|
| `/login` | Login | No | Sign in |
| `/` | redirect | Yes | → `/dashboard` |
| `/dashboard` | Dashboard | Yes | Home, stats, nav |
| `/applications` | Applications | Yes | List applications |
| `/applications/new` | ApplicationForm | Yes | Create application |
| `/applications/:id/edit` | ApplicationForm | Yes | Edit draft |
| `/applications/:id` | ApplicationDetail | Yes | View application, upload docs |
| `/documents` | Documents | Yes | List documents |
| `/documents/:id` | DocumentDetail | Yes | View document, download |
| `/notifications` | Notifications | Yes | List, mark read |
| `*` | NotFound | No | 404 |

---

## 4. API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/token/` | Login (email, password) |
| POST | `/api/token/refresh/` | Refresh JWT |
| GET | `/api/accounts/profile/` | Current user profile |
| GET | `/api/accounts/dashboard/stats/` | Dashboard counts |
| GET/POST | `/api/applications/` | List, create |
| GET/PATCH/DELETE | `/api/applications/:id/` | Detail, update, delete |
| GET | `/api/programs/` | List programs (for form) |
| GET | `/api/documents/` | List documents |
| GET | `/api/documents/:id/` | Document detail |
| POST | `/api/documents/` | Upload (multipart) |
| GET | `/api/document-types/` | Types for upload |
| GET | `/api/notifications/` | List notifications |
| POST | `/api/notifications/:id/mark_read/` | Mark one read |
| POST | `/api/notifications/mark_all_read/` | Mark all read |

---

## 5. Test Data (Django)

- **Users:** `create_vue_test_users`  
  - admin@test.com / admin123  
  - coordinator@test.com / coordinator123  
  - student@test.com / student123  
  - test@example.com / testpass123  

- **Programs:** `create_test_programs`  
  - 6 exchange programs (e.g. Erasmus+ Barcelona, DAAD Munich, Fulbright Harvard).  

- **Notifications:** `create_test_notifications`  
  - e.g. `--user student@test.com --count 5`.  

---

## 6. Key Files (Frontend)

```
frontend-vue/
├── src/
│   ├── main.js              # App entry, Pinia, Router, Bootstrap
│   ├── App.vue               # Router view + ToastContainer
│   ├── router/index.js       # Routes + auth guards
│   ├── stores/auth.js        # User, tokens, login, logout, profile
│   ├── services/api.js       # Axios + JWT interceptors
│   ├── composables/useToast.js
│   ├── utils/apiUrl.js       # resolveFileUrl for downloads
│   ├── components/
│   │   ├── DocumentUpload.vue
│   │   ├── NotificationDropdown.vue
│   │   └── ToastContainer.vue
│   └── views/
│       ├── Login.vue
│       ├── Dashboard.vue
│       ├── Applications.vue
│       ├── ApplicationForm.vue
│       ├── ApplicationDetail.vue
│       ├── Documents.vue
│       ├── DocumentDetail.vue
│       ├── Notifications.vue
│       └── NotFound.vue
├── vite.config.js
├── index.html
└── .env.development          # VITE_API_BASE_URL=http://localhost:8001
```

---

## 7. Known Gaps / Not Done Yet

- **Shared layout:** Navbar (with notification bell) only on Dashboard; Applications/Documents/Notifications are full‑page without top nav.
- **Profile/Settings:** Nav links exist in dropdown but no Vue pages yet.
- **Application submit:** Detail “Submit” is placeholder (no real submit endpoint wired).
- **WebSockets:** No live notification push; list/dropdown are polling on load.
- **Documents API filter:** Backend may not support `?application=uuid`; list may be all user docs.
- **Media auth:** Download links use `resolveFileUrl`; if Django requires auth for `/media/`, downloads may need a different endpoint.

---

## 8. Quick Commands

```powershell
# Backend (Docker)
docker-compose up -d
docker-compose exec web python manage.py create_vue_test_users
docker-compose exec web python manage.py create_test_programs
docker-compose exec web python manage.py create_test_notifications --count 5

# Frontend
cd frontend-vue
npm install
npm run dev          # http://localhost:5173

# Build (for production / Django serving SPA)
npm run build        # → frontend-vue/dist
```

---

## 9. Success Criteria for “Review and Test”

- [ ] Django runs on 8001; Vue dev runs on 5173.
- [ ] Login with student@test.com / student123 works; redirect to dashboard.
- [ ] Dashboard shows stats (applications, documents, notifications, pending).
- [ ] Applications: list, create (program select), view detail, edit draft.
- [ ] Documents: list, view detail, download; from application detail: upload, list of docs.
- [ ] Notifications: list, filter, mark one read, mark all read; navbar bell shows count and recent.
- [ ] Logout clears tokens and redirects to login.
- [ ] Protected routes redirect to login when not authenticated.
- [ ] `npm run build` completes and `frontend-vue/dist` is populated.

This document is the single place to “review” what’s been built; use the testing checklist next to verify behavior.
