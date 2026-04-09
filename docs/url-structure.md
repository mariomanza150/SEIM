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
- Any other CMS-created pages

### SEIM Application
All SEIM application features are under `/seim/`:

#### Authentication
- `/seim/` - SEIM landing/redirect
- `/seim/login/` - User login
- `/seim/register/` - User registration
- `/seim/logout/` - User logout
- `/seim/password-reset/` - Password reset

#### Student Dashboard
- `/seim/dashboard/` - Main dashboard
- `/seim/profile/` - User profile
- `/seim/settings/` - User settings in the Vue SPA
- `/seim/preferences/` - Legacy compatibility path that now redirects to `/seim/settings/` inside the SPA
- `/seim/calendar/` - Legacy server-rendered calendar page

#### Applications
- `/seim/applications/` - List user's applications
- `/seim/programs/compare` - Vue SPA: compare up to four active programs side by side; optional query `?ids=<uuid>,<uuid>` to preselect and share
- `/seim/applications/new` - Create new application in the Vue SPA
- `/seim/applications/<uuid>/` - View application details
- `/seim/applications/<uuid>/edit/` - Edit application
- `/seim/programs/` - SEIM programs management (admin)

Legacy server-rendered application creation also remains available at `/applications/create/`.

#### Exchange Management
- `/seim/exchange/` - Exchange module URLs
- `/seim/grades/` - Grades management
- `/seim/analytics/` - Analytics dashboard

#### Administrative
- `/seim/admin/` - Django Admin interface
- `/seim/admin-dashboard/` - Admin dashboard view
- `/seim/dynforms/` - Dynamic forms builder (admin only)

### Admin Interfaces

#### Wagtail CMS Admin
- `/cms/` - Wagtail admin interface
  - Accessible to all staff users
  - Manage pages, blog posts, programs, FAQs
  - Upload images and documents
  - Workflow and publishing controls

#### Django Admin
- `/seim/admin/` - Django admin interface
  - Accessible to superusers and admin users
  - Manage users, permissions, applications
  - System configuration

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
- `/documents/` - Wagtail documents
- `/media/` - Media files (development)
- `/static/` - Static files (development)

## Navigation Flow

### For Public Users (Not Logged In)
1. Visit `/` → See UAdeC exchange department homepage
2. Browse `/programas/` → View available programs
3. Read `/blog/` → Read news and student experiences
4. Check `/preguntas-frecuentes/` → Find answers
5. Click "Iniciar Sesión" → Redirected to `/seim/login/`
6. After login → Access `/seim/dashboard/`

### For Authenticated Students
1. Login at `/seim/login/`
2. Access dashboard at `/seim/dashboard/`
3. Apply to programs at `/seim/applications/new`
4. Manage account settings at `/seim/settings/`
5. Can still browse CMS content at `/`, `/programas/`, etc.
6. Navigation includes dropdown to access SEIM features

### For Staff/Administrators
1. Login at `/seim/login/` or `/cms/` (Wagtail login)
2. Access Wagtail CMS at `/cms/` to manage content
3. Access Django Admin at `/seim/admin/` for system management
4. Access admin dashboard at `/seim/admin-dashboard/`
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
- `/admin/` → `/seim/admin/`
- etc.

### Template Updates
Templates have been updated to use the new URL structure:
- CMS templates link to `/seim/` for application features
- Spanish labels used in CMS navigation
- Login/logout links point to `/seim/login/` and `/seim/logout/`
- CMS account navigation now points to the SPA dashboard, applications, profile, and settings routes, while the calendar link remains on the legacy Django page

### Reverse URL Lookup
When using `{% url %}` tags or `reverse()` in code:
- Prefix app names appropriately
- Example: `{% url 'frontend:dashboard' %}` → `/seim/dashboard/`
- Example: `{% url 'core:contact_form' %}` → `/seim/contact/`

## Testing Checklist

- [ ] Root `/` loads Wagtail homepage
- [ ] `/seim/login/` works correctly
- [ ] `/seim/dashboard/` accessible after login
- [ ] `/cms/` opens Wagtail admin
- [ ] `/seim/admin/` opens Django admin
- [ ] Navigation links work in CMS pages
- [ ] Application creation flow works
- [ ] API endpoints still functional
- [ ] Static and media files load correctly

