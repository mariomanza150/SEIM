# Form Builder Testing Guide

**Date:** November 18, 2025  
**Version:** Enhanced django-dynforms Form Builder

---

## 🧪 Testing Checklist

### Basic Functionality
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

### Field Types
- [ ] Text input field works
- [ ] Textarea field works
- [ ] Email field works
- [ ] Number field works
- [ ] Date field works
- [ ] Select dropdown with options works
- [ ] Checkbox field works
- [ ] Radio buttons with options work
- [ ] File upload field works

### Form Operations
- [ ] Create new form
- [ ] Save form with name
- [ ] Load existing form
- [ ] Edit existing form
- [ ] Update form and save changes

### UI/UX
- [ ] Responsive on desktop
- [ ] Responsive on tablet
- [ ] Responsive on mobile
- [ ] Dark mode works (if enabled)
- [ ] Error messages display correctly
- [ ] Success messages display correctly
- [ ] Loading states work

---

## 🚀 Quick Start Testing

### 1. Access the Builder
```
Navigate to: http://localhost:8000/api/application-forms/builder/
Login as admin user
```

### 2. Create a Test Form
1. Drag "Text Input" from left sidebar
2. Configure field (modal should open automatically)
3. Set label: "Full Name"
4. Set placeholder: "Enter your full name"
5. Mark as required
6. Save field config

### 3. Add More Fields
1. Drag "Email" field
2. Configure: Label "Email Address", Required
3. Drag "Select" field
4. Configure: Label "Country", Add options (USA, Canada, UK)
5. Drag "Date" field
6. Configure: Label "Birth Date"

### 4. Test Reordering
- Drag field headers to reorder fields
- Verify order persists

### 5. Test Preview
- Click "Preview" button
- Verify form preview shows correctly
- Check all field types render properly

### 6. Save Form
- Click "Save Form"
- Enter form name: "Test Application Form"
- Verify success message
- Check form saved in database

### 7. Load Form
- Navigate to edit URL with form ID
- Verify form loads correctly
- Make changes and save

---

## 🐛 Known Issues / Limitations

### Current Limitations
- Field type inference from schema could be improved
- No conditional logic yet
- No field validation rules UI
- No form templates
- Limited mobile optimization

### Future Enhancements
- Conditional logic (show/hide fields)
- More field types
- Field grouping/sections
- Form templates
- Better mobile experience

---

## 📊 Test Results Template

```
Date: ___________
Tester: ___________

Basic Functionality: [ ] Pass [ ] Fail
Field Types: [ ] Pass [ ] Fail
Form Operations: [ ] Pass [ ] Fail
UI/UX: [ ] Pass [ ] Fail

Issues Found:
1. 
2. 
3. 

Notes:
```

---

## 🔍 Debugging

### Console Errors
Check browser console for JavaScript errors:
- Open DevTools (F12)
- Check Console tab
- Look for errors related to form-builder.js

### Network Errors
Check Network tab for API errors:
- Failed requests to `/api/application-forms/form-types/`
- Check response status codes
- Verify authentication

### Common Issues
1. **Fields not dragging**: Check if SortableJS loaded
2. **Modal not opening**: Check Bootstrap JS loaded
3. **Save failing**: Check CSRF token and authentication
4. **Preview not updating**: Check renderPreview() called

---

## ✅ Success Criteria

Form builder is ready when:
- ✅ All field types can be added and configured
- ✅ Forms can be saved and loaded
- ✅ Preview works correctly
- ✅ No console errors
- ✅ Responsive on all screen sizes
- ✅ Works with existing FormType model

---

**Status**: Ready for comprehensive testing! 🧪

