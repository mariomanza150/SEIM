# SEIM Frontend - Quick Reference Guide

**Last Updated:** 2026-01-29

---

## 📁 Project Structure at a Glance

```
SEIM Frontend
│
├── 🎨 Templates (Django)
│   ├── base.html                    # Master template (576 lines) ⚠️
│   ├── frontend/
│   │   ├── dashboard.html           # Main dashboard (862 lines) ⚠️
│   │   ├── auth/                    # Login, register, password reset
│   │   ├── applications/            # Application CRUD
│   │   ├── programs/                # Program listing
│   │   └── documents/               # Document management
│   └── components/                  # Reusable components ✅
│
├── 🎨 Static Assets
│   ├── css/
│   │   ├── main.css                 # Modular entry point ✅
│   │   ├── dark-mode.css            # Theme support ✅
│   │   ├── accessibility.css        # WCAG compliance ✅
│   │   └── components/              # Component styles ✅
│   │
│   └── js/
│       ├── main.js                  # App initialization (745 lines)
│       ├── auth.js                  # Auth utilities ⚠️ (duplicate)
│       ├── dashboard.js             # Dashboard logic
│       └── modules/                 # Feature modules ✅
│           ├── auth-unified.js      # Auth service ⚠️ (duplicate)
│           ├── api-enhanced.js      # API client ✅
│           ├── websocket-client.js  # Real-time updates ✅
│           └── notification-center.js # Notifications ✅
│
├── 🏗️ Frontend App (Django)
│   ├── views.py                     # View controllers (493 lines)
│   ├── urls.py                      # URL routing
│   └── forms.py                     # Django forms
│
└── 📦 Build System
    ├── webpack.config.js            # Module bundling
    └── package.json                 # Dependencies
```

---

## 🎯 Current Status Summary

### ✅ What's Working Well

| Feature | Status | Notes |
|---------|--------|-------|
| **Dark Mode** | ✅ Excellent | Full theme support, persisted |
| **Accessibility** | ✅ Good | WCAG 2.1 AA compliant (85%) |
| **Real-time Updates** | ✅ Good | WebSocket notifications |
| **Modular CSS** | ✅ Excellent | Clean architecture |
| **API Client** | ✅ Good | Enhanced error handling |
| **Performance** | ✅ Decent | Code splitting, lazy loading |
| **Internationalization** | ✅ Good | Multi-language support |
| **Mobile Support** | ✅ Good | Responsive design |

### ⚠️ What Needs Attention

| Issue | Severity | Impact |
|-------|----------|--------|
| **Inline JavaScript** | 🔴 Critical | 900+ lines in templates |
| **Dual Auth System** | 🔴 Critical | JWT + Session confusion |
| **Test Coverage** | 🔴 Critical | Only ~20% |
| **jQuery Dependency** | 🟡 Medium | Legacy, 90KB overhead |
| **Large Templates** | 🟡 Medium | Hard to maintain |
| **Code Duplication** | 🟡 Medium | Multiple auth/API modules |

---

## 🚀 Quick Start Commands

### Development
```bash
# Start Django server
python manage.py runserver

# Watch JS/CSS changes
npm run dev

# Run tests
npm run test

# Lint code
npm run lint
```

### Build
```bash
# Production build
npm run build

# Analyze bundle
npm run build:analyze
```

### Quality
```bash
# All quality checks
npm run quality:all

# Fix linting issues
npm run lint:fix
```

---

## 📊 Key Metrics

### Performance
- **Bundle Size:** 250KB (target: <150KB)
- **Initial Load:** 2.5s (target: <1.5s)
- **Time to Interactive:** 3.5s (target: <2s)

### Quality
- **Test Coverage:** 20% (target: >80%)
- **Lighthouse Score:** 75 (target: >90)
- **Accessibility:** 85 (target: >95)

---

## 🔧 Common Tasks

### Adding a New Page

1. **Create Django view** in `frontend/views.py`
```python
def my_new_view(request):
    return render(request, 'frontend/my_page.html')
```

2. **Add URL route** in `frontend/urls.py`
```python
path('my-page/', views.my_new_view, name='my_page'),
```

3. **Create template** at `templates/frontend/my_page.html`
```django
{% extends 'base.html' %}
{% block content %}
  <!-- Your content -->
{% endblock %}
```

4. **Add navigation link** in `templates/components/navigation/navbar.html`

---

### Adding a New JavaScript Module

1. **Create module** at `static/js/modules/my-module.js`
```javascript
export class MyModule {
    constructor() {
        // Initialize
    }
    
    doSomething() {
        // Logic
    }
}
```

2. **Import in main.js**
```javascript
import { MyModule } from './modules/my-module.js';
```

3. **Use in application**
```javascript
const myModule = new MyModule();
myModule.doSomething();
```

---

### Adding a New CSS Component

1. **Create component file** at `static/css/components/my-component.css`
```css
.my-component {
    /* Styles */
}
```

2. **Import in main.css**
```css
@import url('./components/my-component.css');
```

---

## 🐛 Common Issues and Solutions

### Issue: JWT Token Expired
**Symptom:** API calls return 401 Unauthorized

**Solution:**
```javascript
// Token refresh happens automatically
// If it fails, user is redirected to login
// Check browser console for details
```

### Issue: WebSocket Not Connecting
**Symptom:** Real-time notifications not working

**Solution:**
1. Check if Redis is running
2. Check WebSocket URL in browser console
3. Verify ASGI server is running (not just WSGI)

### Issue: Dark Mode Not Persisting
**Symptom:** Theme resets on page reload

**Solution:**
```javascript
// Check localStorage
localStorage.getItem('seim-theme'); // Should return 'dark' or 'light'

// Manually set if needed
localStorage.setItem('seim-theme', 'dark');
```

### Issue: Module Not Found Error
**Symptom:** Webpack build fails with module error

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

---

## 📚 Important Files Reference

### Configuration
- `webpack.config.js` - Build configuration
- `package.json` - Dependencies and scripts
- `.eslintrc.js` - Linting rules
- `pytest.ini` - Test configuration

### Templates
- `base.html` - Master template (all pages extend this)
- `components/navigation/navbar.html` - Main navigation
- `components/messages.html` - Flash messages
- `components/footer.html` - Page footer

### JavaScript
- `main.js` - Application entry point
- `modules/auth-unified.js` - Authentication service
- `modules/api-enhanced.js` - API client
- `modules/websocket-client.js` - WebSocket handler

### CSS
- `main.css` - Style entry point
- `dark-mode.css` - Dark theme styles
- `accessibility.css` - A11y improvements

---

## 🔒 Security Considerations

### Authentication
- JWT tokens stored in localStorage
- Refresh tokens for long sessions
- Session fallback for compatibility

### XSS Prevention
- Input sanitization in `modules/security.js`
- CSP headers configured (when inline JS removed)
- All user input escaped

### CSRF Protection
- Django CSRF tokens
- Meta tag in base.html
- Automatically included in AJAX requests

---

## 🎨 Design System

### Colors
```css
--primary-color: #0d6efd;
--success-color: #198754;
--danger-color: #dc3545;
--warning-color: #ffc107;
--info-color: #0dcaf0;
```

### Spacing
```css
--spacing-xs: 0.25rem;  /* 4px */
--spacing-sm: 0.5rem;   /* 8px */
--spacing-md: 1rem;     /* 16px */
--spacing-lg: 1.5rem;   /* 24px */
--spacing-xl: 2rem;     /* 32px */
```

### Typography
```css
--font-size-xs: 0.75rem;   /* 12px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-base: 1rem;    /* 16px */
--font-size-lg: 1.125rem;  /* 18px */
--font-size-xl: 1.25rem;   /* 20px */
```

---

## 📞 Getting Help

### Documentation
- **Main Docs:** `/documentation/`
- **API Docs:** `/documentation/api_documentation.md`
- **Architecture:** `/documentation/architecture.md`
- **Frontend Report:** `/docs/FRONTEND_STATE_REPORT.md`

### Resources
- **Bootstrap 5 Docs:** https://getbootstrap.com/docs/5.3/
- **Django Templates:** https://docs.djangoproject.com/en/5.0/topics/templates/
- **Webpack:** https://webpack.js.org/

### Team Contacts
- **Frontend Lead:** [Contact Info]
- **Backend Lead:** [Contact Info]
- **DevOps:** [Contact Info]

---

## 🗺️ Roadmap

### Q1 2026 (Current Quarter)
- ✅ Extract inline JavaScript
- ✅ Consolidate authentication
- ✅ Split large templates
- ⏳ Remove jQuery dependency
- ⏳ Increase test coverage to 80%

### Q2 2026
- Component library with Storybook
- Performance optimization (Lighthouse >90)
- Advanced accessibility features
- Progressive Web App features

### Q3 2026
- Evaluate modern framework (React/Vue)
- GraphQL consideration
- Advanced state management
- Micro-frontends exploration

---

**Quick Tip:** Always check the browser console for errors and warnings during development!

**Document Version:** 1.0  
**Last Updated:** 2026-01-29
