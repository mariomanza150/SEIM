# Quick Start Guide - UAdeC Exchange & SEIM

## 🌐 Access Points

### Public Website (CMS)
**URL:** `http://localhost:8000/`

The main public-facing website powered by Wagtail CMS featuring:
- UAdeC Exchange Department information
- Available programs
- News and student experiences
- FAQs and contact information

### SEIM Application
**URL:** `http://localhost:8000/seim/`

The Student Exchange Information Management system for:
- Student applications
- Dashboard and profile management
- Application tracking
- Administrative functions

### Admin Interfaces

#### Wagtail CMS Admin
**URL:** `http://localhost:8000/cms/`
- **Access:** Staff users
- **Purpose:** Manage website content, pages, blog posts, programs
- **Features:**
  - Drag-and-drop page editor
  - Media library
  - Publishing workflow
  - SEO management

#### Django Admin
**URL:** `http://localhost:8000/seim/admin/`
- **Access:** Superusers and admins
- **Purpose:** System administration, user management, data management
- **Features:**
  - User and permission management
  - Application data management
  - System configuration

## 🚀 Quick Navigation

### For Students

1. **Browse Programs**
   - Visit `/` for homepage
   - Click "Programas" or go to `/programas/`
   - Select a program to view details

2. **Apply to a Program**
   - Click "Iniciar Sesión" (Login)
   - Login at `/seim/login/`
   - Go to `/seim/applications/create/`
   - Or click "Aplicar Ahora" on any program page

3. **Track Applications**
   - Login to SEIM
   - Visit `/seim/dashboard/` or `/seim/applications/`

### For Staff/Coordinators

1. **Manage Content**
   - Login to Wagtail at `/cms/`
   - Create/edit pages, blog posts, programs
   - Publish content

2. **Manage Applications**
   - Login to Django admin at `/seim/admin/`
   - Or use SEIM dashboard at `/seim/admin-dashboard/`
   - Review and process applications

3. **Manage Users**
   - Use Django admin at `/seim/admin/`
   - User management section

## 📱 Navigation Guide

### CMS Navigation Bar
Located at the top of all CMS pages:
- **Inicio** → Homepage
- **Programas** → Exchange programs
- **Noticias** → Blog/news
- **FAQ** → Frequently asked questions
- **Contacto** → Contact information
- **SEIM Dropdown** (when logged in):
  - Dashboard
  - Mis Solicitudes (My Applications)
  - Mi Perfil (My Profile)
  - CMS Admin (staff only)
  - Django Admin (staff only)

### SEIM Application
Once logged in to SEIM, use the dashboard to access:
- Applications management
- Profile settings
- Calendar
- Analytics (admins)

## 🔧 Common Tasks

### Add a New Exchange Program (CMS)
1. Login to `/cms/`
2. Go to Pages → Programas de Intercambio
3. Click "Add child page"
4. Select "Program Page"
5. Fill in details and publish

### Create a Blog Post
1. Login to `/cms/`
2. Go to Pages → Noticias y Experiencias
3. Click "Add child page"
4. Select "Blog Post Page"
5. Write content and publish

### Update Homepage Content
1. Login to `/cms/`
2. Go to Pages → UAdeC - Dirección de Intercambio Académico
3. Click "Edit"
4. Update content in the StreamField blocks
5. Save and publish

### Manage Student Applications (SEIM)
1. Login to `/seim/admin/`
2. Go to Exchange → Applications
3. Review, approve, or reject applications

## 🔑 Default Credentials

### Admin User
Create a superuser if you haven't already:
```bash
docker-compose exec web python manage.py createsuperuser
```

This user can access both:
- Django Admin (`/seim/admin/`)
- Wagtail CMS (`/cms/`)

## 📊 Content Management

### Adding Images
1. Login to `/cms/`
2. Go to Images in the sidebar
3. Upload images
4. Use in pages via the media chooser

### Adding Documents
1. Login to `/cms/`
2. Go to Documents in the sidebar
3. Upload PDFs, Word docs, etc.
4. Link from pages

### Managing Menus
Navigation is automatically generated from:
- Pages marked as "Show in menus"
- Edit in Wagtail admin → Pages → (page) → Promote tab

## 🐛 Troubleshooting

### Can't Access CMS
- Ensure you're a staff user: `/seim/admin/` → Users → Check "Staff status"
- Run: `docker-compose exec web python manage.py setup_wagtail_permissions`

### Pages Not Showing
- Check page is published (not draft)
- Check page is set to "Show in menus" if needed
- Verify parent page is published

### Login Redirects Wrong
- CMS login: Use `/cms/` directly
- SEIM login: Use `/seim/login/`
- They use separate authentication contexts

## 📚 Additional Resources

- **URL Structure Guide:** `docs/url-structure.md`
- **Architecture Documentation:** `docs/architecture.md`
- **API Documentation:** `http://localhost:8000/api/docs/`

## 🎯 Next Steps

1. ✅ URLs restructured - CMS at root, SEIM at `/seim/`
2. ✅ Content populated for UAdeC
3. ✅ Navigation updated
4. 📝 Add images to programs and blog posts
5. 📝 Customize homepage hero image
6. 📝 Create additional FAQ entries
7. 📝 Test application workflow end-to-end

## 💡 Tips

- **Drafts:** Save as draft in Wagtail to preview before publishing
- **Revisions:** Wagtail keeps all revisions - you can revert anytime
- **Workflow:** Set up approval workflows in Wagtail for content review
- **Search:** Wagtail has built-in search across all content
- **Bulk Actions:** Use Django admin for bulk operations on data

