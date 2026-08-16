# CGRI & Movilidad Internacional Integration Analysis

## Current State Analysis

### UAdeC Website Structure

#### 1. **CGRI Page** (`/cgri/`)
**Purpose**: Coordinación General de Relaciones Internacionales
- Promotes international mobility for academics and students
- Manages collaboration agreements
- Handles international accreditation of academic programs
- Serves as the administrative/institutional face of international relations

#### 2. **Movilidad Page** (`/movilidad/`)
**Purpose**: Student-facing mobility information
- Incoming and outgoing mobility calls (convocatorias)
- Required documentation
- Benefits and requirements
- International agreements
- Student resources

### Overlap & Issues Identified
- **Content Duplication**: Both pages contain similar information about mobility programs
- **Navigation Confusion**: Students may not know which page to visit
- **Inconsistent Updates**: Risk of information being out of sync between pages

## SIEM Integration Options

### **Option 1: Link Integration (Quick & Simple)** ⚡
**Approach**: Add prominent SIEM links to existing UAdeC pages

**Implementation**:
```html
<!-- Add to /cgri/ page -->
<div class="cta-box">
    <h3>Gestión de Movilidad Estudiantil</h3>
    <p>Accede al Sistema Integral de Estudiantes en Movilidad</p>
    <a href="https://seim.uadec.mx" class="btn-primary">Ir a SEIM</a>
</div>

<!-- Add to /movilidad/ page -->
<section class="application-portal">
    <h2>Portal de Aplicaciones</h2>
    <p>Aplica a programas de intercambio a través de SEIM</p>
    <a href="https://seim.uadec.mx" class="btn-large">Aplicar Ahora</a>
</section>
```

**Pros**:
- ✅ Quick to implement (1 day)
- ✅ No disruption to existing UAdeC site
- ✅ Maintains current information flow
- ✅ Easy rollback if needed

**Cons**:
- ❌ Doesn't solve content duplication
- ❌ Creates another destination for users
- ❌ Requires maintaining two separate systems

**Best For**: Pilot phase or if UAdeC IT has limited capacity for integration

---

### **Option 2: Wagtail Replacement (Comprehensive)** 🏆 **RECOMMENDED**
**Approach**: Recreate CGRI and Movilidad pages in Wagtail CMS, integrate SEIM functionality

**Implementation Strategy**:

#### Phase 1: Content Migration
1. **Create Wagtail page structure**:
   ```
   /cgri/                    (HomePage for CGRI section)
   ├── /sobre-nosotros/      (About CGRI)
   ├── /convenios/           (International agreements)
   ├── /acreditacion/        (Accreditation)
   └── /contacto/            (Contact)
   
   /movilidad/               (ProgramIndexPage)
   ├── /programas/           (Program listings - links to SEIM)
   ├── /convocatorias/       (Active calls)
   ├── /como-aplicar/        (How to apply - redirects to SEIM)
   ├── /requisitos/          (Requirements)
   ├── /documentacion/       (Documentation guide)
   ├── /preguntas-frecuentes/ (FAQ)
   └── /testimonios/         (Student testimonials)
   ```

2. **Unify the two pages**:
   ```
   /relaciones-internacionales/     (Main landing page)
   ├── /institucional/              (CGRI institutional info)
   │   ├── /mision-vision/
   │   ├── /convenios/
   │   └── /acreditaciones/
   └── /movilidad-estudiantil/      (Student mobility)
       ├── /programas/
       ├── /proceso-aplicacion/     (Links to SEIM)
       └── /recursos/
   ```

#### Phase 2: SEIM Integration Points

**A. Authentication Bridge**
```python
# In seim/settings/base.py
WAGTAIL_FRONTEND_LOGIN_URL = '/seim/login/'
LOGIN_REDIRECT_URL = '/movilidad/mi-panel/'

# Create seamless login experience
# User navigates: /movilidad/ → "Aplicar" → /seim/login/ → Dashboard
```

**B. Embedded Application Portal**
```django
<!-- In cms/templates/cms/movilidad_landing.html -->
{% if user.is_authenticated %}
    <div class="seim-dashboard-widget">
        <h3>Mis Aplicaciones</h3>
        {% include 'seim/widgets/my_applications.html' %}
    </div>
{% else %}
    <div class="cta-register">
        <a href="/seim/register/">Crear Cuenta en SEIM</a>
    </div>
{% endif %}
```

**C. Content Blocks for Dynamic Info**
```python
# In cms/blocks.py
class ProgramListBlock(blocks.StructBlock):
    """Dynamically pull programs from SEIM database"""
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        from exchange.models import Program
        context['programs'] = Program.objects.filter(
            is_active=True
        ).order_by('-application_deadline')
        return context
```

#### Phase 3: URL Strategy

**Option A: Subdomain (Clean Separation)**
```
https://internacional.uadec.mx/          → Wagtail CMS (informational)
https://internacional.uadec.mx/seim/     → SEIM application system
```

**Option B: Path-based (Current Structure)**
```
https://www.uadec.mx/cgri/               → Wagtail CMS (CGRI info)
https://www.uadec.mx/movilidad/          → Wagtail CMS (Student info)
https://www.uadec.mx/seim/               → SEIM application system
```

**Option C: Unified (Seamless Integration)** ⭐
```
https://www.uadec.mx/internacional/                    → Landing
https://www.uadec.mx/internacional/institucional/      → CGRI info
https://www.uadec.mx/internacional/movilidad/          → Programs & info
https://www.uadec.mx/internacional/aplicar/            → SEIM application
https://www.uadec.mx/internacional/mi-cuenta/          → SEIM dashboard
```

**Pros**:
- ✅ Single source of truth for all international mobility info
- ✅ Eliminates content duplication
- ✅ Consistent UAdeC branding throughout
- ✅ Better user experience (no multiple destinations)
- ✅ SEO benefits (consolidated content)
- ✅ Easier to maintain long-term
- ✅ Can leverage Wagtail's content management for non-technical staff

**Cons**:
- ❌ Requires coordination with UAdeC IT/Web team
- ❌ Longer implementation time (2-4 weeks)
- ❌ Need to migrate existing content
- ❌ Requires DNS/server configuration changes

**Best For**: Long-term solution with institutional buy-in

---

### **Option 3: Hybrid Approach (Pragmatic)** 🎯
**Approach**: Replace `/movilidad/` with Wagtail+SEIM, keep `/cgri/` as-is with link

**Implementation**:

1. **Phase 1** (Week 1):
   - Replace `/movilidad/` with Wagtail CMS
   - Integrate SEIM application flow
   - Add prominent link from `/cgri/` to new `/movilidad/`

2. **Phase 2** (Week 2-3):
   - Migrate all student-facing content to Wagtail
   - Create application CTAs throughout
   - Add program catalog (pulling from SEIM database)

3. **Phase 3** (Week 4):
   - Migrate `/cgri/` content if desired
   - Unify under `/relaciones-internacionales/`

**Pros**:
- ✅ Phased approach reduces risk
- ✅ Student-facing pages improved quickly
- ✅ Can demonstrate value before full migration
- ✅ Flexible timeline

**Cons**:
- ❌ Temporary inconsistency between pages
- ❌ Requires two-phase effort

**Best For**: Organizations that need to show value incrementally

---

## Detailed Recommendation: **Option 2 (Comprehensive Integration)**

### Why This is the Best Approach

1. **User Experience**: Students get a single, unified destination for all international mobility needs
2. **Content Management**: Non-technical CGRI staff can update content via Wagtail admin
3. **Brand Consistency**: Entire international section matches UAdeC's official styling
4. **Future-Proof**: Easier to add new features (blogs, events, news)
5. **SEO & Discoverability**: Better search engine optimization with consolidated content

### Implementation Roadmap

#### **Week 1: Planning & Content Audit**
- [ ] Audit current `/cgri/` and `/movilidad/` content
- [ ] Create content migration spreadsheet
- [ ] Design new information architecture
- [ ] Get stakeholder approval

#### **Week 2: Wagtail Page Structure**
- [ ] Create page models for CGRI content
- [ ] Create page models for Movilidad content
- [ ] Design templates with UAdeC branding
- [ ] Set up navigation menus

#### **Week 3: Content Migration**
- [ ] Migrate CGRI content to Wagtail
- [ ] Migrate Movilidad content to Wagtail
- [ ] Create SEIM integration points
- [ ] Add application CTAs throughout

#### **Week 4: Integration & Testing**
- [ ] Integrate SEIM authentication
- [ ] Create application flow from CMS to SEIM
- [ ] Test all user journeys
- [ ] UAT with CGRI staff

#### **Week 5: Launch & Training**
- [ ] Configure DNS/URLs
- [ ] Deploy to production
- [ ] Train CGRI staff on Wagtail admin
- [ ] Monitor and fix issues

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    www.uadec.mx                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         /internacional/ (Wagtail CMS)                 │  │
│  │                                                        │  │
│  │  ├─ /institucional/     (CGRI Info - Static Pages)    │  │
│  │  │                                                     │  │
│  │  └─ /movilidad/        (Student Portal - Dynamic)     │  │
│  │       │                                                │  │
│  │       ├─ Programs List   ──┐                          │  │
│  │       ├─ How to Apply    ──┼─► Links to SIEM         │  │
│  │       └─ Documentation   ──┘                          │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │    /seim/ (SEIM Application System)             │ │  │
│  │  │                                                   │ │  │
│  │  │  • User Authentication                           │ │  │
│  │  │  • Application Forms                             │ │  │
│  │  │  • Document Upload                               │ │  │
│  │  │  • Application Tracking                          │ │  │
│  │  │  • Admin Workflow                                │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Shared: Database, Auth, Static Files, Email                │
└─────────────────────────────────────────────────────────────┘
```

### Content Structure Proposal

```
/internacional/                                 [HomePage]
├── index                                       "Bienvenido a Relaciones Internacionales"
│
├── /institucional/                             [StandardPage]
│   ├── sobre-cgri                              About CGRI
│   ├── mision-vision                           Mission & Vision
│   ├── equipo                                  Team
│   ├── convenios-internacionales               International Agreements (list)
│   ├── acreditaciones                          Accreditations
│   └── contacto                                Contact
│
├── /movilidad-estudiantil/                     [ProgramIndexPage]
│   ├── index                                   "Tu Aventura Internacional Comienza Aquí"
│   ├── programas                               Active Programs (from SEIM DB)
│   │   ├── [program-slug-1]                    Individual program pages
│   │   └── [program-slug-2]
│   │
│   ├── como-aplicar                            Application Guide → Links to SEIM
│   │   ├── paso-1-registro                     Register account
│   │   ├── paso-2-aplicacion                   Submit application
│   │   ├── paso-3-documentos                   Upload documents
│   │   └── paso-4-seguimiento                  Track application
│   │
│   ├── requisitos                              Requirements by program type
│   ├── documentacion                           Required documents guide
│   ├── beneficios                              Benefits & scholarships
│   ├── calendario                              Important dates
│   ├── preguntas-frecuentes                    FAQ
│   └── testimonios                             Student testimonials
│
├── /noticias/                                  [BlogIndexPage]
│   └── [blog-posts]                            News & announcements
│
└── /aplicar/                                   → Redirects to /seim/register/
```

### User Journeys

#### Journey 1: New Student Discovers Program
```
1. Student visits www.uadec.mx
2. Clicks "Movilidad Internacional" in main menu
3. Lands on /internacional/movilidad-estudiantil/
4. Browses available programs
5. Clicks "¿Cómo Aplicar?"
6. Reads application guide
7. Clicks "Crear Cuenta" → /seim/register/
8. Completes registration → /seim/dashboard/
9. Starts application
```

#### Journey 2: Returning Student Applies
```
1. Student goes directly to www.uadec.mx/seim/
2. Logs in
3. Views dashboard with available programs
4. Starts new application
5. Submits application
6. Uploads documents
```

#### Journey 3: CGRI Staff Updates Content
```
1. Staff logs into /admin/ (Wagtail admin)
2. Navigates to "Internacional" → "Movilidad"
3. Edits program page
4. Adds new announcement
5. Publishes changes
6. Changes appear immediately on public site
```

### Next Steps

**Immediate Actions** (You can do now):
1. Create new Wagtail page models for CGRI content
2. Design page templates matching UAdeC style
3. Set up URL structure in Django

**Coordination Required** (Need UAdeC approval):
1. Get content from existing `/cgri/` and `/movilidad/` pages
2. Coordinate URL strategy with UAdeC IT
3. Plan deployment timeline
4. Arrange training for CGRI staff

Would you like me to start implementing Option 2 (or another option)?

