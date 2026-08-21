# URL Structure - SEIM with Wagtail CMS

## Overview

The application has been restructured so that Wagtail CMS serves the public-facing content at the root (`/`), while the SEIM application management system is accessible under the `/seim/` prefix.

## URL Structure

### Public CMS Content (Wagtail)
All public-facing content is managed through Wagtail CMS:

- `/` - Homepage (UAdeC Exchange Department)
- `/programas/` - Exchange programs listing
- `/blog/` - News and experiences
- `/preguntas-frecuentes/` - FAQ pages
- `/sobre-nosotros/` - About page
- `/contacto/` - Contact information
- `/proceso-aplicacion/` - Application process guide
- `/internacional/` - Relaciones Internacionales (CGRI + movilidad)
- `/internacional/institucional/` - CGRI: misión, equipo, organigrama, acreditaciones, idiomas, asesoría consular, asociaciones, contacto, convenios
- `/internacional/movilidad-estudiantil/` - Movilidad: programas, requisitos, documentación, entrante, saliente, beneficios, calendario, FAQ
- Any other CMS-created pages

Legacy aliases `/cgri/` and `/movilidad/` (and selected subpaths) redirect into `/internacional/`.

### SEIM Application
All SEIM application features are under `/seim/`:

#### Authentication
- `/seim/` - SEIM landing/redirect
- `/seim/login/` - User login
- `/seim/register/` - User registration
- `/logout/` - Session logout (not a Vue route; CMS uses this)
- `/seim/password-reset/` - Password reset

#### Student Dashboard
- `/seim/dashboard/` - Main dashboard
- `/seim/profile/` - User profile
- `/seim/settings/` - User settings in the Vue SPA
- `/seim/preferences/` and `/seim/sessions/` - SPA aliases that redirect to `/seim/settings/` (staff session console is `/seim/admin/sessions`)
- `/seim/calendar/` - Deadlines and milestones (Vue; uses `/api/calendar/events/`)

#### Applications
- `/seim/applications/` - List user's applications
- `/seim/programs/compare` - Vue SPA: compare up to four active programs side by side; optional query `?ids=<uuid>,<uuid>` to preselect and share
- `/seim/applications/new` - Create new application in the Vue SPA
- `/seim/applications/<uuid>/` - View application details
- `/seim/applications/<uuid>/edit/` - Edit application
- `/seim/programs/` - SPA alias that redirects to program compare
- `/seim/review-queue/` - Staff application review queue (Vue)
- `/seim/coordinator-workload/` - Staff workload / queue metrics (Vue)
- `/seim/workload/` - SPA alias that redirects to coordinator-workload
- `/seim/coordinator-dashboard/` - SPA alias that redirects to `/seim/dashboard/`

Root leftovers (`/applications/`, `/applications/create/`, `/profile/`, `/calendar/`, `/documents/`, `/notifications/`, and related) redirect into these `/seim/` routes. See `docs/notes/SPA_VS_LEGACY.md`.

#### Exchange Management
- `/seim/exchange/` - SPA alias that redirects to exchange agreements
- `/seim/grades/` - SPA alias that redirects to profile (student grade scale lives on the profile)
- `/seim/admin/grades` - Vue admin console for grade scales, values, and translations
- `/seim/analytics/` - SPA alias that redirects to `/seim/analytics-forecasts/`

#### Administrative
- `/seim/django-admin/` - Django admin (`/admin/` redirects here)
- `/seim/admin` - SPA alias that redirects to `/seim/admin/programs`
- `/seim/admin-dashboard/` - SPA alias that redirects to `/seim/dashboard/`
- `/admin-dashboard/` - leftover root alias that redirects to `/seim/dashboard/` (must not 404 via Wagtail)
- `/coordinator-dashboard/` - leftover root alias that redirects to `/seim/dashboard/`
- `/sessions/` - leftover root alias that redirects to `/seim/settings/`
- `/dashboard/analytics/` - leftover SSR analytics URL that redirects to `/seim/analytics-forecasts/`
- `/seim/admin/programs|catalogs|grades|users|sessions|workflow-catalogs|forms|dynforms|data-management|workflows|documents` - Vue admin console
- `/seim/admin/dynforms` - Vue visual form builder (admin only; `/dynforms/` redirects here)
- `/seim/admin/data-management` - Vue data-management console (`/data-management/` redirects here)

### Admin Interfaces

#### Wagtail CMS Admin
- `/cms/` - Wagtail admin interface
  - Accessible to all staff users
  - Manage pages, blog posts, programs, FAQs
  - Upload images and documents
  - Workflow and publishing controls

#### Django Admin
- `/seim/django-admin/` - Django admin interface
  - Accessible to superusers and admin users
  - Manage users, permissions, applications
  - System configuration
  - `/admin/` and `/django/admin/` redirect here so they do not collide with `/seim/admin/*` SPA routes

### API Endpoints
API endpoints remain at the root for consistency:

- `/api/` - Main API routes
- `/api/accounts/` - Account management API
- `/api/token/` - JWT token obtain
- `/api/token/refresh/` - JWT token refresh
- `/api/schema/` - API schema
- `/api/docs/` - API documentation (Swagger UI)
- `/api/application-forms/` - Application forms API
- `/api-auth/` - REST framework auth

### Static Resources
- `/cms-documents/` - Wagtail documents
- `/documents/` - Redirects to the SPA document list (`/seim/documents/`)
- `/media/` - Media files (development)
- `/static/` - Static files (development)

## Navigation Flow

### For Public Users (Not Logged In)
1. Visit `/` → See UAdeC exchange department homepage
2. Browse `/programas/` → View available programs
3. Read `/blog/` → Read news and student experiences
4. Check `/preguntas-frecuentes/` → Find answers
5. Click **Ir a SEIM** (navbar, banner, or footer) → `/seim/login/`
6. After login → Access `/seim/dashboard/`

### For Authenticated Students
1. Login at `/seim/login/`
2. Access dashboard at `/seim/dashboard/`
3. Apply to programs at `/seim/applications/new`
4. Manage account settings at `/seim/settings/`
5. Can still browse CMS content at `/`, `/programas/`, etc.
6. **Ir a SEIM** in the CMS chrome goes to `/seim/dashboard/`; the account dropdown still lists dashboard, applications, compare, profile, settings, and calendar

### For Staff/Administrators
1. Login at `/seim/login/` or `/cms/` (Wagtail login)
2. Access Wagtail CMS at `/cms/` to manage content
3. Access Django Admin at `/seim/django-admin/` for system management
4. Access the Vue admin console at `/seim/admin/programs` (catalogs, grades, forms, dynforms, data management, workflows, documents)
5. Full navigation includes both CMS and SEIM admin links

## Benefits of This Structure

1. **Clear Separation**: Public content (CMS) vs Application logic (SEIM)
2. **SEO Friendly**: CMS content at root for better search engine visibility
3. **Logical Grouping**: All app features under `/seim/` namespace
4. **Future Scalability**: Easy to add new CMS pages without URL conflicts
5. **Consistent APIs**: API routes remain stable at `/api/`

## Migration Notes

### URL Changes
All previous root-level SEIM URLs have moved:
- `/dashboard/` → `/seim/dashboard/`
- `/login/` → `/seim/login/`
- `/applications/` → `/seim/applications/`
- `/admin/` → `/seim/django-admin/`
- etc.

### Template Updates
Templates have been updated to use the new URL structure:
- CMS templates link to `/seim/` for application features
- Spanish labels used in CMS navigation
- Login/logout links point to `/seim/login/` and `/logout/`
- Public CMS chrome always includes **Ir a SEIM** (navbar button, integration banner, footer, homepage CTAs)
- Guests land on `/seim/login/`; authenticated users land on `/seim/dashboard/`
- CMS account navigation points to the SPA dashboard, applications, program comparison (`/seim/programs/compare`), profile, settings, and calendar (`/seim/calendar/`)
- Wagtail admin (`/cms/`) includes an **Ir a SEIM** menu item to `/seim/`
- The Vue app user menu includes **Public site** / **Sitio público** back to `/`
- Public program index and program detail pages link to the SPA comparison tool (signed-in users directly; others via `/seim/login?redirect=…` including optional `?ids=` preselection)

### Reverse URL Lookup
When using `{% url %}` tags or `reverse()` in code:
- Prefix app names appropriately
- The Django `frontend` URL namespace is gone; link to `/seim/...` paths or Vue route names
- Example: `{% url 'core:contact_form' %}` → `/contact/`

## Testing Checklist

- [ ] Root `/` loads Wagtail homepage
- [ ] `/seim/login/` works correctly
- [ ] `/seim/dashboard/` accessible after login
- [ ] `/cms/` opens Wagtail admin
- [ ] `/seim/django-admin/` opens Django admin
- [ ] `/seim/admin/programs` opens the Vue admin console
- [ ] Navigation links work in CMS pages
- [ ] Application creation flow works
- [ ] API endpoints still functional
- [ ] Static and media files load correctly

