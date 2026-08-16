# PDF Forms & Partner Logos Implementation Plan

**Date**: November 20, 2025  
**Purpose**: Add the 2 missing features identified in CMS assessment  
**Estimated Time**: 3 hours total

---

## 📋 Overview

### Gap 1: Downloadable PDF Forms
**Current State**: UAdeC reference sites have downloadable forms  
**Goal**: Add official application forms as downloadable PDFs  
**Location**: `/internacional/movilidad-estudiantil/documentacion/`

### Gap 2: Partner Institution Logos
**Current State**: No logos displayed for partner institutions  
**Goal**: Add logos to Convenio (agreement) pages  
**Location**: Convenio pages under `/internacional/institucional/convenios/`

---

## 🎯 Implementation Strategy

### Phase 1: PDF Forms (1.5 hours)

#### Step 1.1: Identify Required Forms
Based on UAdeC reference content, create these forms:

1. **Participation Application** (`Solicitud_Participacion.pdf`)
   - Student information
   - Program selection
   - Academic record

2. **Commitment Letter** (`Carta_Compromiso.pdf`)
   - Student commitment to program rules
   - Return guarantee

3. **Nomination Letter Template** (`Carta_Postulacion_Template.pdf`)
   - For faculty director to nominate student
   - Pre-formatted template

4. **Course Equivalency Form** (`Formulario_Equivalencias.pdf`)
   - Map courses at host institution to UAdeC courses
   - Credit validation

5. **Guidelines and Provisions** (`Lineamientos_Disposiciones.pdf`)
   - Program rules and regulations
   - Student responsibilities

6. **Return Program Form** (`Programa_Retorno.pdf`)
   - Post-exchange reporting
   - Credit transfer finalization

#### Step 1.2: Create PDF Generation Script
- Use ReportLab or WeasyPrint to generate professional PDFs
- Include UAdeC branding (logo, colors)
- Create fillable forms where possible

#### Step 1.3: Upload to Documents App
- Store in Django Documents app
- Organize with tags/categories
- Link to Wagtail for CMS access

#### Step 1.4: Update Documentation Page
- Add DocumentDownloadBlock to `/documentacion/` page
- Group forms by category:
  - General Application Forms
  - Academic Forms
  - Administrative Forms
- Include descriptions for each form

### Phase 2: Partner Logos (1.5 hours)

#### Step 2.1: Identify Top Partner Institutions
Create logos for these institutions (from UAdeC reference):

**Top 10 Partners**:
1. Universidad de Salamanca (España)
2. Texas A&M University (USA)
3. Università di Bologna (Italia)
4. UNAM - Universidad Nacional Autónoma de México
5. Universidad de Guadalajara (México)
6. Tecnológico de Monterrey (México)
7. University of Texas System (USA)
8. McGill University (Canada)
9. Sorbonne Université (France)
10. Freie Universität Berlin (Germany)

#### Step 2.2: Source/Create Logos
**Options**:
- Download official logos from institution websites
- Use placeholder images with institution names
- Create simple text-based logos for now

#### Step 2.3: Upload to Wagtail Images
- Store in Wagtail Images app
- Tag with "partner-logo"
- Standardize sizes (400x200px recommended)

#### Step 2.4: Create/Update Convenio Pages
- Create ConvenioPage for each top partner
- Add institution logo
- Include basic partnership information
- Link to related Program pages if available

---

## 🛠️ Technical Implementation

### Directory Structure

```
media/
├── documents/
│   └── forms/
│       ├── Solicitud_Participacion.pdf
│       ├── Carta_Compromiso.pdf
│       ├── Carta_Postulacion_Template.pdf
│       ├── Formulario_Equivalencias.pdf
│       ├── Lineamientos_Disposiciones.pdf
│       └── Programa_Retorno.pdf
│
└── images/
    └── partner_logos/
        ├── universidad-salamanca.png
        ├── texas-am.png
        ├── bologna.png
        ├── unam.png
        ├── guadalajara.png
        ├── tec-monterrey.png
        ├── ut-system.png
        ├── mcgill.png
        ├── sorbonne.png
        └── fu-berlin.png
```

### Management Commands

#### `populate_pdf_forms.py`
```python
"""Create and upload standard PDF forms for mobility program."""

from django.core.management.base import BaseCommand
from documents.models import Document
from cms.models import StandardPage
# Generate PDFs and upload to Documents app
# Update Documentation page with download blocks
```

#### `add_partner_logos.py`
```python
"""Add partner institution logos to Convenio pages."""

from django.core.management.base import BaseCommand
from cms.models import ConvenioPage, ConvenioIndexPage
from wagtail.images.models import Image
# Upload logos to Wagtail Images
# Create/update ConvenioPage instances with logos
```

---

## 📝 Detailed Steps

### Phase 1: PDF Forms Implementation

#### Step 1: Create PDF Generator Utility

**File**: `cms/utils/pdf_generator.py`

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.conf import settings
import os

def generate_participation_form():
    """Generate Participation Application PDF."""
    # Create professional PDF form with UAdeC branding
    pass

def generate_commitment_letter():
    """Generate Commitment Letter PDF."""
    pass

# ... other form generators
```

#### Step 2: Create Management Command

**File**: `cms/management/commands/populate_pdf_forms.py`

Features:
- Generate 6 standard PDF forms
- Upload to Documents app
- Update Documentation page with download blocks
- Add proper metadata (title, description)

#### Step 3: Update Documentation Page

Add StreamField blocks:
```python
# In Wagtail admin or via script
documentation_page.body.append({
    'type': 'document',
    'value': {
        'document': document_id,
        'title': 'Solicitud de Participación',
        'description': 'Formulario oficial para aplicar al programa de movilidad'
    }
})
```

### Phase 2: Partner Logos Implementation

#### Step 1: Create Logo Placeholder Generator

**File**: `cms/utils/logo_generator.py`

```python
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_logo(institution_name, output_path):
    """Create simple text-based logo for institution."""
    # Generate 400x200px image with institution name
    # Use UAdeC color scheme
    pass
```

#### Step 2: Create Management Command

**File**: `cms/management/commands/add_partner_logos.py`

Features:
- Create/download logos for top 10 partners
- Upload to Wagtail Images
- Create ConvenioPage instances if they don't exist
- Link logos to pages
- Add basic partnership information

#### Step 3: Verify Convenio Index Page

Ensure `/internacional/institucional/convenios/` displays:
- Partner logos
- Institution names
- Countries
- Agreement types
- Links to detail pages

---

## 🎨 Design Specifications

### PDF Forms Design
- **Header**: UAdeC logo + "CGRI - Movilidad Internacional"
- **Footer**: Contact info + page numbers
- **Colors**: UAdeC official colors
- **Font**: Professional (Helvetica/Arial)
- **Layout**: Clean, scannable, fillable

### Partner Logos
- **Size**: 400x200px (2:1 ratio)
- **Format**: PNG with transparency
- **Background**: White or transparent
- **Quality**: High-res for retina displays
- **Naming**: lowercase-with-hyphens.png

---

## ✅ Acceptance Criteria

### PDF Forms
- [ ] 6 PDF forms generated and available
- [ ] All forms include UAdeC branding
- [ ] Forms are downloadable from Documentation page
- [ ] Each form has clear title and description
- [ ] PDFs are well-formatted and professional
- [ ] File sizes are reasonable (<500KB each)

### Partner Logos
- [ ] Logos for top 10 partners added
- [ ] All logos display correctly on Convenio pages
- [ ] Logos are consistent size and quality
- [ ] ConvenioIndexPage shows all partners with logos
- [ ] Detail pages include logo + institution info
- [ ] Mobile display is responsive

---

## 📊 Testing Plan

### PDF Forms Testing
1. Navigate to `/internacional/movilidad-estudiantil/documentacion/`
2. Verify all 6 forms are listed
3. Click each download link
4. Verify PDF opens and displays correctly
5. Check branding and formatting
6. Test on mobile devices

### Partner Logos Testing
1. Navigate to `/internacional/institucional/convenios/`
2. Verify all 10 logos display
3. Click on each convenio to view detail page
4. Verify logo appears on detail page
5. Check responsive display on mobile
6. Verify links work correctly

---

## 🚀 Rollout Plan

### Day 1: Development (3 hours)
- Hour 1: Create PDF generator utility + forms
- Hour 1.5: Create populate_pdf_forms command
- Hour 0.5: Test and verify PDFs

### Day 1: Development (1.5 hours)  
- Hour 0.5: Source/create partner logos
- Hour 0.5: Create add_partner_logos command
- Hour 0.5: Test and verify logos

### Day 1: Deployment (0.5 hours)
- Run management commands in Docker container
- Verify all content displays correctly
- Update documentation
- Mark todos as complete

**Total Time**: 3-4 hours

---

## 📋 Commands to Run

```bash
# Generate and upload PDF forms
docker-compose exec web python manage.py populate_pdf_forms

# Add partner institution logos
docker-compose exec web python manage.py add_partner_logos

# Verify CMS content
docker-compose exec web python manage.py show_cms_content

# Check forms in Documents app
docker-compose exec web python manage.py shell
>>> from documents.models import Document
>>> Document.objects.filter(tags__name='mobility-form').count()

# Check logos in Wagtail Images
>>> from wagtail.images.models import Image
>>> Image.objects.filter(tags__name='partner-logo').count()
```

---

## 🎯 Success Metrics

After implementation:
- ✅ 6 downloadable PDF forms available
- ✅ 10 partner logos displayed
- ✅ Documentation page enhanced
- ✅ Convenio pages populated
- ✅ 100% feature parity with UAdeC reference sites
- ✅ Professional presentation
- ✅ Ready for production deployment

---

## 📚 Next Steps After Implementation

1. **Content Enrichment**:
   - Add more partner institutions (60+ total)
   - Create detailed convenio pages for each
   - Add partnership history and details

2. **Form Enhancement**:
   - Make PDFs fillable (interactive fields)
   - Add digital signature capability
   - Create online form versions

3. **Logo Gallery**:
   - Create interactive partner map
   - Add filters by country/region
   - Show partnership statistics

---

**Status**: Ready to implement 🚀  
**Priority**: High (closes feature gaps)  
**Risk**: Low (straightforward implementation)

