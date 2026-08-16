# Vue.js Migration – Test Checklist

Use this checklist to verify the app end‑to‑end.  
**Prerequisites:** Docker running, `docker-compose up -d`, Vue deps installed (`cd frontend-vue && npm install`).

---

## 1. Environment

- [ ] **1.1** Docker: `docker-compose ps` – web, db, redis (and celery if used) are Up/healthy.
- [ ] **1.2** Django: Open http://localhost:8001/api/docs/ – Swagger loads.
- [ ] **1.3** Vue: In `frontend-vue`, run `npm run dev` – dev server starts (e.g. http://localhost:5173).
- [ ] **1.4** No console errors on blank Vue app load (before login).

---

## 2. Authentication

- [ ] **2.1** Open http://localhost:5173 – redirects to `/login` (or shows login).
- [ ] **2.2** Wrong credentials (e.g. wrong@test.com / wrong) – error message, no redirect.
- [ ] **2.3** Login: `student@test.com` / `student123` – success toast, redirect to `/dashboard`.
- [ ] **2.4** Dashboard shows “Welcome, Student User!” (or similar) and stats.
- [ ] **2.5** Refresh page – still logged in (tokens in localStorage).
- [ ] **2.6** Logout (user menu → Logout) – redirect to `/login`, tokens cleared; visiting `/dashboard` redirects to login.

---

## 3. Dashboard

- [ ] **3.1** Four stat cards: Applications, Documents, Notifications, Pending (numbers may be 0).
- [ ] **3.2** Click “Applications” card – goes to `/applications`.
- [ ] **3.3** Click “Documents” card – goes to `/documents`.
- [ ] **3.4** Click “Notifications” card – goes to `/notifications`.
- [ ] **3.5** Sidebar: Dashboard, Applications, Documents, Notifications, Settings – links work (Settings can 404 for now).
- [ ] **3.6** Navbar: bell icon visible; if test notifications exist, unread count shown; dropdown opens and shows recent items + “View all”.

---

## 4. Applications

- [ ] **4.1** `/applications` – list loads (empty or with data); no console errors.
- [ ] **4.2** Filters: Status, Sort – change and see list update (or stay empty).
- [ ] **4.3** “New Application” – goes to `/applications/new`.
- [ ] **4.4** Create: Select a program, optional statement, “Create Application” – success, redirect to application detail.
- [ ] **4.5** Application detail – program info, timeline, sidebar with “Edit”, “Delete”, “Back to List”.
- [ ] **4.6** Edit draft: “Edit” → form with same program (disabled), change statement, save – detail updates or list reflects change.
- [ ] **4.7** Delete draft: “Delete” → confirm – application removed, back to list.
- [ ] **4.8** Breadcrumbs: Dashboard → Applications → [Program name] – correct.

---

## 5. Documents

- [ ] **5.1** `/documents` – list loads; filters (Application, Type, Status) work.
- [ ] **5.2** From application detail (draft or submitted): “Upload Document” – type dropdown and file input visible.
- [ ] **5.3** Upload: Select type, choose file (e.g. PDF), Submit – success toast; document appears in sidebar list and/or on `/documents`.
- [ ] **5.4** Document detail: Click a document – title, type, application, status, “Download” (link works or shows expected behavior).
- [ ] **5.5** Dashboard “Documents” card and sidebar “Documents” – both go to `/documents`.

---

## 6. Notifications

- [ ] **6.1** Seed data: `docker-compose exec web python manage.py create_test_notifications --count 5`
- [ ] **6.2** `/notifications` – list shows items; read/unread and category filters work.
- [ ] **6.3** “Mark as Read” on one – item becomes read, count updates if shown.
- [ ] **6.4** “Mark All as Read” – all become read; count 0.
- [ ] **6.5** Navbar bell – unread count; dropdown shows recent; “View all” goes to `/notifications`.
- [ ] **6.6** Action link on a notification (if present) – navigates or opens correct URL.

---

## 7. Navigation & Guards

- [ ] **7.1** Direct URL while logged out: http://localhost:5173/dashboard – redirects to login (with redirect back after login if implemented).
- [ ] **7.2** Direct URL while logged in: http://localhost:5173/login – redirects to dashboard.
- [ ] **7.3** Unknown route: http://localhost:5173/unknown – 404 (NotFound) page.
- [ ] **7.4** Breadcrumbs and “Back” links – consistent and correct.

---

## 8. Build & Production Readiness

- [ ] **8.1** In `frontend-vue`: `npm run build` – completes without errors.
- [ ] **8.2** `frontend-vue/dist` – contains `index.html` and `assets/` (JS/CSS).
- [ ] **8.3** (Optional) Serve `dist` with a static server and point API to 8001 – login and main flows work.

---

## 9. Optional / Edge Cases

- [ ] **9.1** Token expiry: wait or force 401 – refresh runs and request retries, or logout and redirect to login.
- [ ] **9.2** Coordinator login: `coordinator@test.com` / `coordinator123` – dashboard and list views work.
- [ ] **9.3** Admin login: `admin@test.com` / `admin123` – same; admin features (if any) work.

---

## How to use this checklist

1. Run through sections 1–3 first (env, auth, dashboard).
2. Then 4–6 (applications, documents, notifications).
3. Then 7–8 (guards, build).
4. Mark items pass/fail; note any failures (screen, console, URL) for fixing.

If something fails, note:
- Step number
- What you did
- What you expected
- What happened (message, redirect, console error)
- Browser and OS if relevant

This supports the “review and test what’s been built” goal in a repeatable way.
