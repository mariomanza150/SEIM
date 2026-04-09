# CMS Quick Start Guide

> Keep this as the short operational reference for day-to-day CMS usage. For full restore/export workflows, use `docs/CMS_RESTORE_GUIDE.md`. For broader CMS architecture and content guidance, use `documentation/cms_guide.md`.

## 🚀 Accessing the Landing Page

### View the Public Site
```
URL: http://localhost:8001/
```

### Access the CMS Admin
```
URL: http://localhost:8001/cms/
Login with your staff account
```

### Access Django Admin
```
URL: http://localhost:8001/seim/admin/
For system configuration and data management
```

---

## ✅ Current Status

- CMS restore/export/import workflow is available and documented.
- Public CMS pages are served from the root site.
- Wagtail admin remains the primary editing interface for CMS content.
- Use `show_cms_content` for the current page and content counts instead of relying on static numbers in this file.

---

## 🎯 What You Can Do Right Now

### 1. View the Landing Page
```bash
# Make sure Docker is running
docker-compose up -d

# Open browser to:
http://localhost:8001/
```

### 2. Edit Content via CMS Admin
1. Navigate to `http://localhost:8000/cms/`
2. Login with staff credentials
3. Click "Pages" in sidebar
4. Find "UAdeC - Dirección de Intercambio Académico"
5. Click "Edit"
6. Modify content blocks using drag-and-drop interface
7. Click "Publish" to make changes live

### 3. View All Content
```bash
docker-compose exec web python manage.py show_cms_content
```

### 4. Restore/Refresh CMS Content

**✨ NEW: Simple One-Command Restore** (Recommended)
```bash
docker-compose exec web python manage.py restore_cms
```

This single command restores the entire CMS in one go!

**Alternative: Individual Commands**
```bash
# If you need to run steps separately:
docker-compose exec web python manage.py setup_wagtail_site
docker-compose exec web python manage.py populate_uadec_content
docker-compose exec web python manage.py enhance_homepage
```

**💡 See [CMS_RESTORE_GUIDE.md](CMS_RESTORE_GUIDE.md) for the complete workflow guide including export/import functionality.**

---

## 📋 Content Overview

### Public Pages (No Login Required)

| Page | URL | Purpose |
|------|-----|---------|
| **Homepage** | `/` | Landing page for students/teachers |
| **Programs** | `/programas/` | Browse exchange programs |
| **Blog/News** | `/blog/` | Read experiences & announcements |
| **FAQs** | `/preguntas-frecuentes/` | Get quick answers |
| **Contact** | `/contacto/` | Contact information |
| **About** | `/sobre-nosotros/` | Department info |
| **Application Guide** | CMS-managed page | Application guide content |

### Notes
- Exact program, blog, and FAQ slugs may change over time as content editors update the CMS.
- Use the CMS page tree or `show_cms_content` for the current published structure.

---

## 🎨 Homepage Content Blocks

1. **Hero Banner**: "Vive una Experiencia Internacional"
2. **Feature Cards**: 6 benefits (3x2 grid)
3. **Call-to-Action**: Spring 2026 application call
4. **Process Steps**: 6-step application guide
5. **Testimonial**: Student quote from Salamanca
6. **FAQ Section**: 4 quick Q&A items
7. **Final CTA**: Contact invitation

---

## 🔧 Common Tasks

### Add a New Blog Post

**Via CMS Admin:**
1. Go to `/cms/` → Pages
2. Navigate to "Noticias y Experiencias"
3. Click "Add child page"
4. Select "Blog Post Page"
5. Fill in title, excerpt, content
6. Add categories and tags
7. Publish

**Via Management Command:**
Create a new command in `cms/management/commands/`

### Add a New Exchange Program

**Via CMS Admin:**
1. Go to `/cms/` → Pages
2. Navigate to "Programas de Intercambio"
3. Click "Add child page"
4. Select "Program Page"
5. Fill in details (location, duration, requirements)
6. Add content blocks
7. Publish

### Update Homepage Content

**Via CMS Admin:**
1. Go to `/cms/` → Pages
2. Find "UAdeC - Dirección de Intercambio Académico"
3. Click "Edit"
4. Modify hero section or body blocks
5. Add/remove/reorder blocks as needed
6. Save and publish

### Add a New FAQ

**Via CMS Admin:**
1. Go to `/cms/` → Pages
2. Navigate to "Preguntas Frecuentes"
3. Click "Add child page"
4. Select "FAQ Page"
5. Enter question as title
6. Add answer in body
7. Publish

---

## 📊 Management Commands

### **Primary Commands (Use These)**

```bash
# 🎯 RESTORE ENTIRE CMS (One command does it all!)
docker-compose exec web python manage.py restore_cms

# Export your customized CMS content
docker-compose exec web python manage.py export_cms

# Import previously exported CMS content
docker-compose exec web python manage.py import_cms --clear

# Show all CMS content
docker-compose exec web python manage.py show_cms_content

# Create superuser (if needed)
docker-compose exec web python manage.py createsuperuser
```

### **Legacy Commands (For Individual Steps)**

```bash
# Set up Wagtail site structure
docker-compose exec web python manage.py setup_wagtail_site

# Populate UAdeC content
docker-compose exec web python manage.py populate_uadec_content

# Enhance homepage with blocks
docker-compose exec web python manage.py enhance_homepage
```

**📖 For detailed workflow instructions, see [CMS_RESTORE_GUIDE.md](CMS_RESTORE_GUIDE.md)**

---

## 🎓 For Students (User Perspective)

### What Students See
1. **Landing Page**: Welcoming hero, program benefits, testimonials
2. **Programs**: Detailed info on each exchange opportunity
3. **Blog**: Real experiences from past exchange students
4. **FAQs**: Answers to common concerns
5. **Application Process**: Clear step-by-step guide
6. **Login Portal**: Access to SEIM application system

### Student Journey
```
Visit Landing Page
    ↓
Browse Programs
    ↓
Read Student Experiences
    ↓
Check FAQs
    ↓
Review Application Process
    ↓
Create Account / Login
    ↓
Submit Application via SEIM
```

---

## 👨‍🏫 For Teachers (User Perspective)

### What Teachers Can Access
1. **Program Details**: Full requirements and curricula
2. **Student Resources**: Materials to share with advisees
3. **Contact Info**: Direct communication with exchange office
4. **News/Updates**: Latest announcements and deadlines
5. **Admin Tools**: (if staff) Content management and system access

### Teacher Use Cases
- Guide students on program selection
- Review requirements with advisees
- Stay informed on deadlines
- Coordinate with exchange office
- Approve student applications

---

## 🔐 Permissions

| Role | CMS Access | Can Edit | Can Publish | SEIM Admin |
|------|------------|----------|-------------|------------|
| **Anonymous** | View only | ❌ | ❌ | ❌ |
| **Student** | View only | ❌ | ❌ | Limited |
| **Teacher** | View only | ❌ | ❌ | Limited |
| **Coordinator** | Yes | ✅ | ✅ | Yes |
| **Admin** | Yes | ✅ | ✅ | Full |

---

## 🚨 Troubleshooting

### Problem: Can't access CMS admin
**Solution**: Ensure you're logged in with a staff account
```bash
# Check user status
docker-compose exec web python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='your_username')
>>> user.is_staff = True
>>> user.save()
```

### Problem: Content not showing
**Solution**: Check if page is published
1. Go to CMS admin
2. Find the page
3. Check status (Draft vs Live)
4. Click "Publish" if needed

### Problem: 404 on homepage
**Solution**: Verify site root page
```bash
docker-compose exec web python manage.py shell
>>> from wagtail.models import Site
>>> site = Site.objects.get(is_default_site=True)
>>> print(site.root_page)
```

### Problem: Changes not visible
**Solution**: Clear cache and hard refresh
- Browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear Django cache if enabled

---

## 📚 Documentation References

- **Full CMS Guide**: `documentation/cms_guide.md`
- **CMS Restore Workflow**: `docs/CMS_RESTORE_GUIDE.md`
- **Full CMS Guide**: `documentation/cms_guide.md`
- **Architecture**: `documentation/architecture.md`
- **Wagtail Docs**: https://docs.wagtail.org/

---

## 🎯 Next Steps

### Immediate Actions
- [ ] Visit http://localhost:8001/ to view landing page
- [ ] Login to /cms/ to explore admin interface
- [ ] Review all published pages
- [ ] Test navigation and links
- [ ] Verify mobile responsiveness

### Content Improvements
- [ ] Add real UAdeC campus photos
- [ ] Replace placeholder images
- [ ] Add more student testimonials
- [ ] Create video content
- [ ] Update program details with current info

### System Configuration
- [ ] Configure email settings for notifications
- [ ] Set up Google Analytics (if needed)
- [ ] Configure SSL/HTTPS for production
- [ ] Set up automated backups
- [ ] Configure CDN for static files

---

## 📞 Getting Help

### Resources
1. **Documentation**: Check `/docs` and `/documentation` folders
2. **Management Commands**: Run `--help` on any command
3. **Wagtail Community**: https://wagtail.org/community/
4. **Django Docs**: https://docs.djangoproject.com/

### Common Commands
```bash
# List all management commands
docker-compose exec web python manage.py --help

# Get help on specific command
docker-compose exec web python manage.py show_cms_content --help
```

---

**Quick Reference Created**: November 20, 2025
**System Version**: SEIM v1.0 + Wagtail 6.x
**Status**: ✅ Ready for use

