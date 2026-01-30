# SEIM Form Builder Guide

**Last Updated:** November 20, 2025  
**Version:** 1.0 - Enhanced django-dynforms Implementation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features & Capabilities](#features--capabilities)
- [User Guide - Administrators](#user-guide---administrators)
- [User Guide - End Users](#user-guide---end-users)
- [Implementation Details](#implementation-details)
- [Testing Guide](#testing-guide)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## Overview

The SEIM Form Builder is a custom-built dynamic form creation system that allows administrators to create and manage application forms for exchange programs. Built on top of `django-dynforms`, it provides a modern, intuitive interface for creating forms without writing code.

### Key Features

- **Drag-and-Drop Interface**: Visual form builder with intuitive drag-and-drop functionality
- **9 Field Types**: Support for text, textarea, email, number, date, select, checkbox, radio, and file fields
- **Real-time Preview**: See your form as you build it
- **JSON Schema Storage**: Standards-based form storage in PostgreSQL
- **Bootstrap 5 Compatible**: Matches the SEIM UI design system
- **No Breaking Changes**: Works alongside existing django-dynforms

### Technology Stack

- **Backend**: Django REST Framework with django-dynforms
- **Frontend**: Vanilla JavaScript (no React dependency)
- **Storage**: FormType model with JSON schema in PostgreSQL JSONField
- **Drag-and-Drop**: SortableJS library
- **Styling**: Bootstrap 5 compatible CSS

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Form Builder UI                         │
│  ┌───────────────┐ ┌────────────┐ ┌─────────────────────┐ │
│  │ Field Palette │ │  Canvas    │ │  Preview Panel      │ │
│  │ (Sidebar)     │ │ (Builder)  │ │  (Live Preview)     │ │
│  └───────────────┘ └────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
                  ┌─────────────────┐
                  │   Django API    │
                  │   (DRF Views)   │
                  └─────────────────┘
                            ↓
                  ┌─────────────────┐
                  │  FormType Model │
                  │  (JSON Schema)  │
                  └─────────────────┘
                            ↓
                  ┌─────────────────┐
                  │   PostgreSQL    │
                  │  (JSONField)    │
                  └─────────────────┘
```

### Data Flow

1. **Form Creation**: Admin uses drag-and-drop interface to build form
2. **Schema Generation**: JavaScript converts form to JSON Schema
3. **API Storage**: Form saved via REST API to FormType model
4. **Form Rendering**: django-dynforms renders form from JSON Schema
5. **Submission**: Form data validated and stored in FormSubmission model

### File Structure

```
application_forms/
├── static/
│   └── application_forms/
│       ├── css/
│       │   ├── form-builder.css      # Builder styles
│       │   └── form-renderer.css     # Form rendering styles
│       └── js/
│           ├── form-builder.js       # Main builder logic (750+ lines)
│           ├── field-palette.js      # Field types sidebar
│           ├── field-editor.js       # Field configuration
│           └── form-preview.js       # Real-time preview
├── templates/
│   └── application_forms/
│       ├── builder.html              # Form builder page
│       ├── field_palette.html        # Field types sidebar
│       └── field_editor.html         # Field config modal
├── models.py                         # FormType & FormSubmission
├── views.py                          # EnhancedFormBuilderView
└── urls.py                           # Builder routes
```

---

## Features & Capabilities

### Form Builder Interface

#### Three-Panel Layout

1. **Field Palette (Left Sidebar)**
   - Displays all available field types
   - Drag fields to canvas to add them
   - Visual icons for each field type

2. **Builder Canvas (Center)**
   - Main editing area
   - Shows added fields
   - Drag to reorder fields
   - Edit/delete buttons for each field

3. **Preview Panel (Right)**
   - Real-time form preview
   - Shows form as end users will see it
   - Updates automatically as you build

### Supported Field Types

| Field Type | Description | Configuration Options |
|------------|-------------|----------------------|
| **Text Input** | Single line text entry | Label, placeholder, required, help text |
| **Textarea** | Multi-line text entry | Label, placeholder, required, help text, rows |
| **Email** | Email with validation | Label, placeholder, required, help text |
| **Number** | Numeric input only | Label, placeholder, required, help text, min/max |
| **Date** | Date picker | Label, required, help text |
| **Select** | Dropdown menu | Label, required, help text, options |
| **Checkbox** | Single checkbox | Label, required, help text |
| **Radio** | Radio button group | Label, required, help text, options |
| **File Upload** | File attachment | Label, required, help text, accepted types |

### Field Configuration

Each field can be configured with:

- **Label**: Field label displayed to users
- **Name**: Internal field identifier (auto-generated)
- **Placeholder**: Hint text inside input field
- **Required**: Mark field as mandatory
- **Help Text**: Additional guidance below field
- **Options**: Choices for select/radio fields (add, edit, delete)

### Form Management

- **Create New Form**: Build forms from scratch
- **Edit Existing Form**: Load and modify saved forms
- **Save Forms**: Persist forms to database via API
- **JSON Schema Export**: Generate standard JSON Schema
- **UI Schema Support**: Enhanced rendering hints

### Advanced Features

- **Field Reordering**: Drag fields to reorder using SortableJS
- **Auto-save Draft**: Automatic draft saving (optional)
- **Form Validation**: Client-side and server-side validation
- **Responsive Design**: Works on desktop, tablet, and mobile

---

## User Guide - Administrators

### Accessing the Form Builder

1. Log in as an administrator
2. Navigate to: `/api/application-forms/builder/`
3. You'll see the three-panel builder interface

### Creating a New Form

#### Step 1: Add Fields

1. **Drag a field type** from the left sidebar to the canvas
2. The field configuration modal will open automatically
3. **Configure the field**:
   - Enter a descriptive label
   - Add placeholder text (optional)
   - Mark as required if needed
   - Add help text for guidance
   - For select/radio: Add options (one per line or use "Add Option" button)
4. Click **"Save"** to add the field

#### Step 2: Arrange Fields

- **Reorder fields**: Drag field headers up or down
- **Edit field**: Click the edit (pencil) icon
- **Delete field**: Click the delete (trash) icon

#### Step 3: Preview Form

- The preview panel on the right shows your form in real-time
- Click **"Preview"** button to see full-screen preview
- Test the form to ensure it works as expected

#### Step 4: Save Form

1. Click **"Save Form"** button (top right)
2. Enter a form name
3. Optionally add a description
4. Click **"Save"**
5. Form is saved to database

### Editing an Existing Form

1. Navigate to: `/api/application-forms/builder/<form-id>/`
2. Form loads automatically in the builder
3. Make your changes
4. Click **"Save Form"** to update

### Attaching Form to Program

1. Go to Django Admin: `/admin/`
2. Navigate to Exchange → Programs
3. Edit the desired program
4. Select your form from the "Application Form" dropdown
5. Save the program

### Best Practices

- **Use clear labels**: Make field labels descriptive and user-friendly
- **Add help text**: Provide guidance for complex fields
- **Required fields**: Only mark essential fields as required
- **Test thoroughly**: Preview and test forms before deploying
- **Logical order**: Arrange fields in a logical sequence
- **Group related fields**: Keep related information together

---

## User Guide - End Users

### Viewing and Completing Forms

End users (students) interact with forms when applying for exchange programs:

1. **View Program**: Navigate to an exchange program
2. **Start Application**: Click "Apply" button
3. **Complete Form**: Fill in all required fields
4. **Validation**: Required fields must be completed
5. **Submit**: Click "Submit Application"

### Form Features for End Users

- **Field Validation**: Required fields marked with asterisk (*)
- **Help Text**: Additional guidance shown below fields
- **Error Messages**: Clear messages for validation errors
- **Responsive Design**: Works on all devices
- **Progress Indication**: Shows completion status

---

## Implementation Details

### Technical Implementation

#### Backend (Django)

**Models** (`application_forms/models.py`):

```python
class FormType(models.Model):
    """Dynamic form definition"""
    name = models.CharField(max_length=200)
    schema = models.JSONField()  # JSON Schema format
    ui_schema = models.JSONField(default=dict)  # UI hints
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FormSubmission(models.Model):
    """Form submission data"""
    form_type = models.ForeignKey(FormType)
    application = models.ForeignKey('exchange.Application')
    data = models.JSONField()  # Submitted form data
    submitted_at = models.DateTimeField(auto_now_add=True)
```

**Views** (`application_forms/views.py`):

```python
class EnhancedFormBuilderView(TemplateView):
    """Enhanced form builder interface"""
    template_name = 'application_forms/builder.html'
    permission_required = 'application_forms.add_formtype'

class FormTypeViewSet(viewsets.ModelViewSet):
    """API for form CRUD operations"""
    serializer_class = FormTypeSerializer
    permission_classes = [IsAdminUser]
```

#### Frontend (JavaScript)

**Form Builder** (`form-builder.js`):

- Field palette with drag-and-drop
- Canvas for building forms
- Field configuration modal
- Real-time preview generation
- JSON Schema generation
- API integration for save/load

**Key Functions**:

```javascript
// Add field to canvas
function addFieldToCanvas(fieldType) { ... }

// Open field configuration modal
function editField(fieldIndex) { ... }

// Generate JSON Schema from form
function generateSchema() { ... }

// Save form via API
function saveForm() { ... }

// Load existing form
function loadForm(formId) { ... }
```

### JSON Schema Format

Forms are stored as JSON Schema:

```json
{
  "title": "Application Form",
  "type": "object",
  "required": ["fullName", "email"],
  "properties": {
    "fullName": {
      "type": "string",
      "title": "Full Name"
    },
    "email": {
      "type": "string",
      "format": "email",
      "title": "Email Address"
    },
    "country": {
      "type": "string",
      "title": "Country",
      "enum": ["USA", "Canada", "UK"]
    }
  }
}
```

### UI Schema Format

UI hints for enhanced rendering:

```json
{
  "fullName": {
    "ui:placeholder": "Enter your full name",
    "ui:help": "As shown on passport"
  },
  "email": {
    "ui:placeholder": "example@university.edu"
  }
}
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/application-forms/form-types/` | GET | List all forms |
| `/api/application-forms/form-types/` | POST | Create new form |
| `/api/application-forms/form-types/{id}/` | GET | Retrieve form |
| `/api/application-forms/form-types/{id}/` | PUT | Update form |
| `/api/application-forms/form-types/{id}/` | DELETE | Delete form |
| `/api/application-forms/builder/` | GET | Builder interface |
| `/api/application-forms/builder/{id}/` | GET | Edit form |

---

## Testing Guide

### Testing Checklist

#### Basic Functionality

- [ ] Access form builder at `/api/application-forms/builder/`
- [ ] Field palette displays all 9 field types
- [ ] Can drag fields from palette to canvas
- [ ] Field configuration modal opens when adding new field
- [ ] Can edit field properties (label, placeholder, required, help text)
- [ ] Can add/remove options for select/radio fields
- [ ] Can delete fields
- [ ] Can reorder fields by dragging
- [ ] Preview panel shows form preview
- [ ] Can save form successfully
- [ ] Can load existing form for editing

#### Field Types Testing

Test each field type:

- [ ] Text input field works
- [ ] Textarea field works
- [ ] Email field works (with validation)
- [ ] Number field works (numeric only)
- [ ] Date field works (date picker)
- [ ] Select dropdown with options works
- [ ] Checkbox field works
- [ ] Radio buttons with options work
- [ ] File upload field works

#### Form Operations

- [ ] Create new form
- [ ] Save form with name
- [ ] Load existing form
- [ ] Edit existing form
- [ ] Update form and save changes
- [ ] Delete form (via admin)

#### UI/UX Testing

- [ ] Responsive on desktop (1920x1080)
- [ ] Responsive on tablet (768x1024)
- [ ] Responsive on mobile (375x667)
- [ ] Dark mode works (if enabled)
- [ ] Error messages display correctly
- [ ] Success messages display correctly
- [ ] Loading states work

### Quick Start Testing

#### Test Case 1: Create Simple Form

1. Navigate to `/api/application-forms/builder/`
2. Drag "Text Input" field to canvas
3. Configure: Label "Full Name", Placeholder "Enter name", Required
4. Drag "Email" field
5. Configure: Label "Email", Required
6. Save form as "Test Form"
7. Verify form saved successfully

#### Test Case 2: Create Form with Options

1. Drag "Select" field
2. Configure: Label "Country"
3. Add options: USA, Canada, UK, France
4. Drag "Radio" field
5. Configure: Label "Experience Level"
6. Add options: Beginner, Intermediate, Advanced
7. Save and verify

#### Test Case 3: Edit Existing Form

1. Navigate to builder with form ID
2. Verify form loads correctly
3. Add new field
4. Modify existing field
5. Save changes
6. Reload and verify changes persisted

### Debugging

#### Common Issues

**Issue**: Fields not dragging
- **Solution**: Check if SortableJS library loaded
- **Check**: Browser console for errors

**Issue**: Modal not opening
- **Solution**: Verify Bootstrap JS loaded
- **Check**: Bootstrap version compatibility

**Issue**: Save failing
- **Solution**: Check CSRF token and authentication
- **Debug**: Check Network tab for API errors

**Issue**: Preview not updating
- **Solution**: Ensure renderPreview() function called
- **Debug**: Check JavaScript console

#### Browser Console Debugging

1. Open DevTools (F12)
2. Check Console tab for errors
3. Look for errors related to `form-builder.js`
4. Check Network tab for API request/response

#### Django Debugging

```bash
# Check Django logs
docker-compose logs web

# Check form types in database
docker-compose exec web python manage.py shell
>>> from application_forms.models import FormType
>>> FormType.objects.all()
```

---

## Troubleshooting

### Known Issues & Limitations

#### Current Limitations

- **Field Type Inference**: Loading forms with complex schemas may not perfectly infer field types
- **No Conditional Logic**: Show/hide fields based on other fields not yet implemented
- **No Validation Rules UI**: Only basic required/optional validation
- **No Form Templates**: Can't save form as template for reuse
- **Limited Mobile Optimization**: Builder works but not optimized for mobile editing

#### Workarounds

**Issue**: Can't add conditional logic
- **Workaround**: Use multiple forms or custom JavaScript in templates

**Issue**: Need custom field types
- **Workaround**: Extend form-builder.js to add new field types

**Issue**: Form builder slow on mobile
- **Workaround**: Use desktop for building, mobile only for preview

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Failed to save form" | API authentication issue | Verify logged in as admin |
| "Invalid schema" | Malformed JSON Schema | Check field configurations |
| "Field name conflict" | Duplicate field names | Ensure unique field names |
| "Missing required field" | Form missing required data | Complete all required fields |

### Getting Help

1. **Check Documentation**: Review this guide thoroughly
2. **Console Logs**: Check browser console for errors
3. **Django Admin**: Use admin interface as fallback
4. **Contact Support**: Reach out to SEIM development team

---

## Future Enhancements

### Planned Features

#### Phase 4: Advanced Features

- **Conditional Logic**: Show/hide fields based on answers
- **Field Validation Rules**: Custom validation patterns and rules
- **Field Grouping/Sections**: Organize fields into logical sections
- **Form Templates**: Save and reuse form templates
- **More Field Types**: Time, color, range, rating, location, etc.
- **Multi-page Forms**: Break long forms into multiple pages

#### Phase 5: UX Improvements

- **Better Mobile Optimization**: Touch-friendly builder for tablets
- **Keyboard Shortcuts**: Power user shortcuts
- **Undo/Redo**: Undo/redo form changes
- **Form Duplication**: Clone existing forms
- **Export/Import Forms**: JSON import/export
- **Form Analytics**: Track completion rates and drop-offs

#### Phase 6: Integration Enhancements

- **Email Notifications**: Custom notifications per form
- **Workflow Integration**: Tie form completion to workflow states
- **Document Generation**: Generate PDFs from submissions
- **Bulk Operations**: Bulk edit, delete, export forms

### Alternative Solutions

If more advanced features are needed, consider:

1. **React JSON Schema Form (RJSF)**: Modern React-based solution
2. **Form.io**: Enterprise-grade form builder
3. **SurveyJS**: Advanced survey/form platform

See `documentation/archive/form_builder_development/FORM_BUILDER_ANALYSIS_AND_PROPOSAL.md` for detailed analysis of alternatives.

---

## Appendix

### Related Documentation

- **Developer Guide**: `documentation/developer_guide.md`
- **API Documentation**: `documentation/api_documentation.md`
- **Architecture Overview**: `documentation/architecture.md`

### Related Code

- **Models**: `application_forms/models.py`
- **Views**: `application_forms/views.py`
- **Serializers**: `application_forms/serializers.py`
- **Builder JS**: `application_forms/static/application_forms/js/form-builder.js`
- **Builder CSS**: `application_forms/static/application_forms/css/form-builder.css`
- **Builder Template**: `application_forms/templates/application_forms/builder.html`

### Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-18 | 1.0 | Initial form builder implementation |
| 2025-11-20 | 1.0 | Documentation consolidated |

---

**Last Updated**: November 20, 2025  
**Maintained By**: SEIM Development Team  
**Status**: Production Ready ✅

