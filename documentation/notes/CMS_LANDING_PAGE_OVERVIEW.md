# CMS Landing Page Overview - UAdeC Exchange Department

## 🎯 Purpose
The CMS serves as the **public-facing landing page** for UAdeC's (Universidad Autónoma de Coahuila) Exchange Department. It provides comprehensive information for:
- **Students**: Discover programs, apply, read experiences, and get answers
- **Teachers/Faculty**: View program details, guide students, and stay informed
- **Prospective Partners**: Learn about UAdeC's exchange capabilities

---

## 📊 Current Content Structure

### 🏠 Homepage (`/`)
**URL**: `http://localhost:8000/`

The enhanced landing page now includes:

#### Hero Section
- **Title**: "Bienvenido a la Dirección de Intercambio Académico"
- **Subtitle**: "Universidad Autónoma de Coahuila - Transformando vidas a través de experiencias internacionales"
- **CTA Button**: Links to programs page

#### Content Blocks (7 total):
1. **Hero Banner**: "Vive una Experiencia Internacional"
2. **Feature Cards**: 6 benefits of exchange programs
   - International Experience
   - Revalidable Credits
   - Comprehensive Support
   - Available Scholarships
   - Language Development
   - Competitive Advantage
3. **Call-to-Action**: Current call for Spring 2026 applications
4. **Process Steps**: 6-step application guide
5. **Student Testimonial**: Real experience from Salamanca exchange
6. **FAQ Section**: Quick answers to common questions
7. **Final CTA**: Contact invitation

---

## 📄 Available Pages

### For Students

#### 1. **Programs** (`/programas/`)
Browse all available exchange programs:
- **Universidad de Salamanca** (Spain) - 1 semester
- **Texas A&M University** (USA) - 1 semester
- **Università di Bologna** (Italy) - 1 semester

Each program page includes:
- Location and duration
- Academic details
- Language requirements
- Application process

#### 2. **Blog/News** (`/blog/`)
Stay updated with:
- **Student Experiences**: "Mi Semestre en la Universidad de Salamanca"
- **Announcements**: "Convocatoria Abierta: Intercambio Primavera 2026"
- **Tips & Advice**: "10 Consejos para Preparar tu Intercambio"

Categories: Experiencias, Convocatorias, Consejos, Noticias

#### 3. **FAQs** (`/preguntas-frecuentes/`)
Quick answers to 5+ common questions:
- Application requirements
- Costs and scholarships
- Credit validation
- Working abroad
- Emergency procedures

#### 4. **Application Process** (`/proceso-aplicacion/`)
Detailed step-by-step guide including:
- Required documents
- Timeline
- Evaluation process
- Preparation tips

#### 5. **Contact** (`/contacto/`)
Complete contact information:
- Physical address
- Office hours
- Phone and email
- Social media links

### For Staff/Faculty

#### 6. **About Us** (`/sobre-nosotros/`)
Department information:
- Mission statement
- Vision
- History since 1995
- Network of 80+ institutions in 25 countries

---

## 🎨 Available Content Blocks

The Wagtail CMS provides flexible content blocks that can be added to any page:

### Content Blocks
- **Rich Text**: Formatted text with headings, lists, links
- **Image**: Images with captions and alignment options
- **Call to Action**: Prominent CTAs with buttons
- **Card Grid**: Feature cards (2, 3, or 4 columns)
- **Hero Banner**: Large banner sections
- **Testimonial**: Quotes from students
- **FAQ Section**: Collapsible Q&A
- **Process Steps**: Numbered step-by-step guides
- **Video**: Embedded YouTube/Vimeo videos
- **Document Download**: PDF downloads
- **Two Columns**: Side-by-side layouts
- **Embedded Form**: Contact/application forms

---

## 🔧 Managing Content

### Accessing the CMS
**Admin Interface**: `http://localhost:8000/cms/`

**Who Can Access**:
- Staff users (`is_staff=True`)
- Coordinators
- Administrators

### Two Admin Interfaces

1. **Wagtail CMS** (`/cms/`)
   - Content management
   - Pages, blog posts, programs
   - Dynamic forms
   - SEO settings

2. **Django Admin** (`/seim/admin/`)
   - System configuration
   - User management
   - Exchange workflows
   - Data management

### Editing the Landing Page

To modify the homepage content:

```bash
# Access the container
docker-compose exec web python manage.py shell

# Or use the CMS admin interface at /cms/
```

Or use the Wagtail admin:
1. Navigate to `http://localhost:8000/cms/`
2. Click "Pages" in the sidebar
3. Find "UAdeC - Dirección de Intercambio Académico"
4. Click "Edit"
5. Modify content blocks using the StreamField interface
6. Click "Publish" to make changes live

---

## 📋 Key Features

### For Students
✅ Browse exchange programs by country
✅ Read real student experiences
✅ Get answers to common questions
✅ Learn the application process
✅ Access online application portal (SEIM integration)
✅ Track application status (when logged in)

### For Teachers/Faculty
✅ View all available programs and requirements
✅ Guide students with comprehensive information
✅ Access contact information for coordination
✅ Stay updated with news and announcements

### For Administrators
✅ Easy content editing with visual interface
✅ No coding required for updates
✅ SEO optimization built-in
✅ Responsive design (mobile-friendly)
✅ Integration with SEIM application system

---

## 🚀 Management Commands

Useful commands for CMS management:

```bash
# Populate/refresh UAdeC content
docker-compose exec web python manage.py populate_uadec_content

# Show current CMS content overview
docker-compose exec web python manage.py show_cms_content

# Enhance homepage with content blocks
docker-compose exec web python manage.py enhance_homepage

# Initialize Wagtail (first-time setup)
docker-compose exec web python manage.py initialize_wagtail
```

---

## 🌐 Navigation Structure

The main navigation includes:
- **Inicio** (Home)
- **Programas** (Programs)
- **Noticias** (Blog/News)
- **FAQ** (Preguntas Frecuentes)
- **Contacto** (Contact)
- **SEIM** dropdown (for authenticated users)
  - Dashboard
  - My Applications
  - My Profile
  - Admin interfaces (staff only)

---

## 📱 Responsive Design

The landing page is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

Built with **Bootstrap 5** for consistent, mobile-first design.

---

## 🔍 SEO Features

Each page includes:
- Meta titles and descriptions
- Open Graph tags
- Twitter Card support
- Sitemap generation
- Search-friendly URLs

Powered by `wagtailseo` for comprehensive SEO optimization.

---

## 📊 Current Statistics

**Pages**: 17 published pages
- 1 Homepage
- 3 Exchange Programs
- 3 Blog Posts
- 5 FAQs
- 3 Standard Pages (About, Contact, Application)
- 3 Index Pages (Blog, Programs, FAQs)

**Content Blocks on Homepage**: 7 blocks
- Hero Banner
- Feature Cards (6 cards)
- Call-to-Action (2)
- Process Steps (6 steps)
- Testimonial
- FAQ Section
- Final CTA

---

## 🎯 Future Enhancements

Potential additions:
- [ ] Photo gallery from past exchanges
- [ ] Video testimonials
- [ ] Interactive program comparison tool
- [ ] Live chat support
- [ ] Newsletter subscription
- [ ] Event calendar
- [ ] Partner institution showcase
- [ ] Alumni network section
- [ ] Scholarship calculator

---

## 🔗 Integration with SEIM

The CMS landing page integrates with the SEIM application system:

- **Public Content**: CMS handles all public-facing information
- **Applications**: SEIM manages the application workflow
- **User Dashboard**: Students can log in from the CMS to access their SEIM dashboard
- **Seamless Experience**: Users navigate between CMS and SEIM transparently

---

## 📞 Support & Documentation

For more information:
- **CMS Guide**: See `documentation/cms_guide.md`
- **Wagtail Docs**: https://docs.wagtail.org/
- **Technical Support**: Contact system administrator

---

**Last Updated**: November 20, 2025
**System**: SEIM v1.0 with Wagtail CMS
**Status**: ✅ Fully operational and populated with UAdeC content

