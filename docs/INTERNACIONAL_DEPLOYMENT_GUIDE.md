# International Section Deployment Guide

## Overview

This document provides a comprehensive guide for deploying the new **International Relations section** (`/internacional/`) as a drop-in replacement for UAdeC's existing `/cgri/` and `/movilidad/` pages.

## Architecture

### Old Structure (UAdeC Website)
```
https://www.uadec.mx/
├── /cgri/                          # CGRI institutional info
│   ├── About CGRI
│   ├── International agreements
│   └── Contact information
│
└── /movilidad/                     # Student mobility info
    ├── Programs
    ├── Requirements
    ├── Documentation
    └── Application process
```

### New Structure (SEIM/Wagtail CMS)
```
https://www.uadec.mx/internacional/   # or https://internacional.uadec.mx/
├── /institucional/                   # CGRI content (replaces /cgri/)
│   ├── /mision-vision/
│   ├── /equipo/
│   ├── /acreditaciones/
│   ├── /contacto/
│   └── /convenios/                   # International agreements
│       └── /[institution-name]/
│
└── /movilidad-estudiantil/           # Student portal (replaces /movilidad/)
    ├── /programas/                   # Program listings
    │   └── /[program-name]/
    ├── /como-aplicar/                # How to apply (links to SEIM)
    ├── /requisitos/                  # Requirements
    ├── /documentacion/               # Documentation guide
    ├── /beneficios/                  # Benefits & scholarships
    ├── /calendario/                  # Important dates
    ├── /preguntas-frecuentes/        # FAQ
    └── /testimonios/                 # Student testimonials
        └── /[student-name]/
```

## URL Mapping

### CGRI Replacement Mapping
| Old URL (uadec.mx)          | New URL (SEIM)                                    | Status |
|-----------------------------|---------------------------------------------------|--------|
| `/cgri/`                    | `/internacional/institucional/`                   | ✅     |
| `/cgri/about/`              | `/internacional/institucional/mision-vision/`     | ✅     |
| `/cgri/team/`               | `/internacional/institucional/equipo/`            | ✅     |
| `/cgri/agreements/`         | `/internacional/institucional/convenios/`         | ✅     |
| `/cgri/accreditations/`     | `/internacional/institucional/acreditaciones/`    | ✅     |
| `/cgri/contact/`            | `/internacional/institucional/contacto/`          | ✅     |

### Movilidad Replacement Mapping
| Old URL (uadec.mx)          | New URL (SEIM)                                         | Status |
|-----------------------------|--------------------------------------------------------|--------|
| `/movilidad/`               | `/internacional/movilidad-estudiantil/`                | ✅     |
| `/movilidad/programs/`      | `/internacional/movilidad-estudiantil/programas/`      | ✅     |
| `/movilidad/apply/`         | `/internacional/movilidad-estudiantil/como-aplicar/`   | ✅     |
| `/movilidad/requirements/`  | `/internacional/movilidad-estudiantil/requisitos/`     | ✅     |
| `/movilidad/documents/`     | `/internacional/movilidad-estudiantil/documentacion/`  | ✅     |
| `/movilidad/benefits/`      | `/internacional/movilidad-estudiantil/beneficios/`     | ✅     |
| `/movilidad/calendar/`      | `/internacional/movilidad-estudiantil/calendario/`     | ✅     |
| `/movilidad/faq/`           | `/internacional/movilidad-estudiantil/preguntas-frecuentes/` | ✅ |

## Deployment Options

### Option 1: Subdomain Deployment (Recommended)
**URL**: `https://internacional.uadec.mx/`

**Advantages**:
- Clean separation from main UAdeC site
- Independent deployment and updates
- Easier maintenance
- Clear branding for international programs

**DNS Configuration**:
```
internacional.uadec.mx  A     [SEIM-SERVER-IP]
internacional.uadec.mx  AAAA  [SEIM-SERVER-IPv6]
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name internacional.uadec.mx;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name internacional.uadec.mx;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/internacional.uadec.mx/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/internacional.uadec.mx/privkey.pem;
    
    # Proxy to Django/SEIM
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

### Option 2: Path-Based Deployment
**URL**: `https://www.uadec.mx/internacional/`

**Advantages**:
- Single domain
- Consistent user experience
- No DNS changes required

**Nginx Configuration (on UAdeC main server)**:
```nginx
# Add to existing www.uadec.mx server block

location /internacional/ {
    # Proxy to SEIM server
    proxy_pass http://[SEIM-SERVER-IP]:8000/internacional/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /internacional;
}

# Redirect old URLs
location /cgri/ {
    return 301 https://www.uadec.mx/internacional/institucional/;
}

location /movilidad/ {
    return 301 https://www.uadec.mx/internacional/movilidad-estudiantil/;
}
```

## SEIM Integration Points

### 1. User Authentication
Users can seamlessly move between CMS and SEIM application:

```python
# In cms/templates/cms/movilidad_landing_page.html
{% if user.is_authenticated %}
    <a href="/seim/applications/" class="btn btn-primary">Mi Panel</a>
{% else %}
    <a href="/seim/register/" class="btn btn-primary">Crear Cuenta</a>
{% endif %}
```

### 2. Program Listings
Programs from the Exchange app are dynamically displayed in CMS:

```python
# In cms/models.py - MovilidadLandingPage.get_context()
from exchange.models import Program
context['active_programs'] = Program.objects.filter(
    is_active=True
).select_related('destination_university', 'destination_country')[:6]
```

### 3. Application Flow
```
CMS Page (/movilidad-estudiantil/) 
    ↓
User clicks "Aplicar" button
    ↓
Redirects to /seim/register/ or /seim/login/
    ↓
User authenticates
    ↓
Redirects to /seim/applications/new
    ↓
User completes application in SEIM system
    ↓
Application managed through SEIM workflow
```

## Content Migration Plan

### Phase 1: Content Audit (Week 1)
1. **Export existing content** from `/cgri/` and `/movilidad/`
2. **Create content spreadsheet** mapping old content to new pages
3. **Identify missing content** or outdated information
4. **Get stakeholder approval** on content structure

### Phase 2: Content Migration (Week 2)
1. **Migrate CGRI content** to `/institucional/` pages via Wagtail admin
2. **Migrate Movilidad content** to `/movilidad-estudiantil/` pages
3. **Add convenio pages** for each international agreement
4. **Create initial program pages** (or link to existing Exchange programs)

### Phase 3: Enhancement (Week 3)
1. **Add testimonials** from past exchange students
2. **Create FAQ pages** with common questions
3. **Upload images** and media assets
4. **Set up email notifications** for new content

### Phase 4: Testing & Launch (Week 4)
1. **UAT testing** with CGRI staff
2. **Student testing** with current applicants
3. **Performance testing**
4. **Soft launch** to limited audience
5. **Full deployment**

## Wagtail Admin Setup

### 1. Access Wagtail Admin
```
https://internacional.uadec.mx/admin/
or
https://www.uadec.mx/admin/
```

### 2. Edit Pages
1. Navigate to **Pages** in left sidebar
2. Expand tree to find **Relaciones Internacionales**
3. Click on any page to edit
4. Use StreamField blocks for flexible content
5. Click **Publish** to make changes live

### 3. Add Programs
1. Go to **Relaciones Internacionales → Movilidad Estudiantil → Programas**
2. Click **Add child page**
3. Select **Program Page**
4. Fill in details:
   - Title
   - Link to Exchange Program (optional)
   - Location, Duration, Language
   - Featured Image
   - Body content using blocks
5. Publish

### 4. Add Convenios
1. Go to **Relaciones Internacionales → Institucional → Convenios**
2. Click **Add child page**
3. Select **Convenio**
4. Fill in:
   - Institution name and logo
   - Country and city
   - Agreement type
   - Start/end dates
   - Body content
   - Related programs
5. Publish

### 5. Add Testimonials
1. Go to **Relaciones Internacionales → Movilidad Estudiantil → Testimonios**
2. Click **Add child page**
3. Select **Testimonial**
4. Fill in student information and story
5. Publish

## URL Redirects Setup

### Django URLs Configuration
Create redirects in `seim/urls.py` or create a new `internacional/urls.py`:

```python
# seim/urls.py or internacional/urls.py
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect old /cgri/ URLs
    path('cgri/', RedirectView.as_view(
        url='/internacional/institucional/', permanent=True
    )),
    path('cgri/about/', RedirectView.as_view(
        url='/internacional/institucional/mision-vision/', permanent=True
    )),
    path('cgri/contact/', RedirectView.as_view(
        url='/internacional/institucional/contacto/', permanent=True
    )),
    
    # Redirect old /movilidad/ URLs
    path('movilidad/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/', permanent=True
    )),
    path('movilidad/programs/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/programas/', permanent=True
    )),
    path('movilidad/apply/', RedirectView.as_view(
        url='/internacional/movilidad-estudiantil/como-aplicar/', permanent=True
    )),
]
```

## SEO & Analytics

### 1. Meta Tags
All pages include SEO-optimized meta tags via `wagtailseo`:
- Title tags
- Meta descriptions
- Open Graph tags
- Twitter Card tags

### 2. Google Analytics
Add tracking code in `cms/templates/cms/base.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXXX-X"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'UA-XXXXXX-X');
</script>
```

### 3. Sitemap
Wagtail automatically generates sitemap at `/sitemap.xml`

## Security Considerations

### 1. HTTPS Only
Ensure all pages use HTTPS:
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. CORS Configuration
If using subdomain:
```python
# settings/production.py
CORS_ALLOWED_ORIGINS = [
    'https://www.uadec.mx',
    'https://internacional.uadec.mx',
]
```

### 3. Content Security Policy
Add CSP headers in nginx or Django middleware

## Monitoring & Maintenance

### 1. Health Checks
Create a health check endpoint:
```python
# core/views.py
def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### 2. Error Monitoring
Use Sentry or similar:
```python
# settings/production.py
import sentry_sdk
sentry_sdk.init(dsn='...')
```

### 3. Regular Backups
- Database backups (daily)
- Media files backups (weekly)
- Wagtail page revisions (automatic)

## Training Materials

### For CGRI Staff
1. **Wagtail Admin Introduction** (30 min video)
2. **Adding/Editing Pages** (tutorial doc)
3. **Using StreamField Blocks** (interactive guide)
4. **Publishing Workflow** (quick reference)

### For Students
1. **How to Apply** (step-by-step guide)
2. **SEIM Registration** (video tutorial)
3. **Application Tracking** (user guide)

## Rollback Plan

If issues arise after deployment:

### 1. Immediate Rollback (< 5 minutes)
```bash
# Restore nginx config
sudo cp /etc/nginx/sites-available/uadec.mx.backup /etc/nginx/sites-available/uadec.mx
sudo nginx -t && sudo systemctl reload nginx
```

### 2. Database Rollback (< 15 minutes)
```bash
# Restore database backup
docker-compose down
docker-compose exec db psql -U postgres -d seim < backup_YYYYMMDD.sql
docker-compose up -d
```

### 3. Communication Plan
- Notify CGRI staff
- Post notice on main page
- Email active applicants
- Update social media

## Success Metrics

### Key Performance Indicators
- **Page Load Time**: < 2 seconds
- **Mobile Responsiveness**: 100% on Google PageSpeed
- **SEO Score**: > 90
- **Uptime**: 99.9%
- **User Satisfaction**: > 4.5/5

### Analytics Tracking
- Page views per section
- Time on page
- Bounce rate
- Conversion rate (views → applications)
- Search terms used

## Support & Contacts

### Technical Support
- **SEIM Development Team**: [email]
- **UAdeC IT Department**: [email]
- **Server/Infrastructure**: [email]

### Content Management
- **CGRI Staff**: cgri@uadec.mx
- **Wagtail Admin Issues**: [support email]

## Appendix

### A. Complete URL Reference
See `URL Mapping` section above

### B. StreamField Block Types Available
- Hero Block
- Call to Action Block
- Process Steps Block
- Card Grid Block
- FAQ Block
- Rich Text Block
- Image Block
- Embed Block
- Document Download Block

### C. Color Scheme Reference
See `docs/CMS_COLOR_SCHEME_UPDATE.md`

### D. Custom Page Types
- `InternationalHomePage` - Main landing page
- `CGRIPage` - Institutional pages
- `MovilidadLandingPage` - Student portal landing
- `ConvenioPage` - International agreement details
- `ConvenioIndexPage` - Agreement listings
- `TestimonialPage` - Student testimonials
- `TestimonialIndexPage` - Testimonial listings
- `ProgramPage` - Individual programs
- `StandardPage` - General content pages

