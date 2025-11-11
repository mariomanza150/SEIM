# SEIM Frontend Development Guide

## Overview
SEIM uses a modern Django-based frontend with Bootstrap 5, JavaScript ES6+, and responsive design principles. The frontend is production-ready with comprehensive features and optimizations.

---

## 🏗️ Frontend Architecture

### **Technology Stack**
- **Django Templates** - Server-side rendering with template inheritance
- **Bootstrap 5** - CSS framework for responsive design
- **JavaScript ES6+** - Modern client-side functionality
- **CSS3** - Custom styling with CSS custom properties
- **JWT Authentication** - Token-based authentication with automatic refresh

### **Directory Structure**
```
static/
├── css/
│   ├── main.css (modular entry point)
│   ├── utilities/
│   │   ├── colors.css (comprehensive color system)
│   │   ├── spacing.css (spacing utilities)
│   │   └── typography.css (typography system)
│   ├── layouts/
│   │   ├── base.css (grid system & fundamentals)
│   │   └── navigation.css (navbar & sidebar)
│   └── components/
│       ├── buttons.css (button variants & states)
│       ├── cards.css (card components & variants)
│       ├── forms.css (form controls & validation)
│       └── tables.css (table styles & responsive)
├── js/
│   ├── main.js (core utilities and initialization)
│   ├── auth.js (authentication logic)
│   ├── dashboard.js (dashboard functionality)
│   └── modules/
│       ├── api.js (API interaction utilities)
│       ├── auth-unified.js (unified authentication)
│       ├── notifications.js (notification system)
│       ├── validators.js (form validation)
│       ├── utils.js (utility functions)
│       ├── logger.js (logging system)
│       ├── error-handler.js (error handling)
│       └── ui/
│           ├── auth_ui.js (authentication UI)
│           ├── bootstrap_helpers.js (Bootstrap utilities)
│           └── loading.js (loading states)
└── img/ (images and icons)

templates/
├── base.html (modular base template)
├── components/
│   ├── navigation/
│   │   └── navbar.html (accessible navigation)
│   ├── forms/
│   │   └── search_form.html (reusable search)
│   ├── tables/
│   │   └── data_table.html (responsive data table)
│   ├── messages.html (enhanced message display)
│   └── footer.html (modular footer)
└── frontend/
    ├── dashboard.html
    ├── auth/
    ├── applications/
    ├── programs/
    └── documents/
```

---

## 🎨 CSS Architecture

### **Design System**
- **Color System**: Comprehensive palette with light/dark mode support
- **Typography**: Consistent font hierarchy and spacing
- **Spacing**: Systematic spacing scale using CSS custom properties
- **Components**: Reusable component library with variants

### **Key Features**
- ✅ **Responsive Design** - Mobile-first approach with Bootstrap 5
- ✅ **Accessibility** - WCAG 2.1 AA compliance with ARIA support
- ✅ **Performance** - Optimized CSS with critical path loading
- ✅ **Maintainability** - Modular architecture with clear separation
- ✅ **Dark Mode** - Built-in dark theme support
- ✅ **High Contrast** - Accessibility-focused contrast ratios

### **CSS Custom Properties**
```css
:root {
  /* Colors */
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 3rem;
  
  /* Typography */
  --font-family-base: 'Segoe UI', system-ui, sans-serif;
  --font-size-base: 1rem;
  --line-height-base: 1.5;
}
```

---

## ⚡ JavaScript Architecture

### **Module System**
- **ES6 Modules** - Modern import/export syntax
- **Modular Design** - Clear separation of concerns
- **Dependency Management** - Explicit module dependencies
- **Error Handling** - Comprehensive error management

### **Core Modules**

#### **API Module** (`modules/api.js`)
```javascript
// Centralized API interaction
const API = {
  async request(endpoint, options = {}) {
    // JWT token handling
    // Error handling
    // Request/response logging
  },
  
  // CRUD operations
  get: (endpoint) => API.request(endpoint),
  post: (endpoint, data) => API.request(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => API.request(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint) => API.request(endpoint, { method: 'DELETE' })
};
```

#### **Authentication Module** (`modules/auth-unified.js`)
```javascript
// Unified authentication system
const Auth = {
  // JWT token management
  getToken: () => localStorage.getItem('access_token'),
  setToken: (token) => localStorage.setItem('access_token', token),
  removeToken: () => localStorage.removeItem('access_token'),
  
  // Authentication state
  isAuthenticated: () => !!Auth.getToken(),
  
  // Login/logout
  login: async (credentials) => { /* implementation */ },
  logout: () => { /* implementation */ },
  
  // Token refresh
  refreshToken: async () => { /* implementation */ }
};
```

#### **Notification System** (`modules/notifications.js`)
```javascript
// Toast notification system
const Notifications = {
  success: (message) => { /* implementation */ },
  error: (message) => { /* implementation */ },
  warning: (message) => { /* implementation */ },
  info: (message) => { /* implementation */ }
};
```

### **Performance Optimizations**
- **Code Splitting** - Dynamic imports for non-critical features
- **Request Deduplication** - Prevent duplicate API calls
- **Intelligent Caching** - Cache warming and versioning
- **Bundle Optimization** - Reduced bundle sizes by 30%

---

## 📱 Responsive Design

### **Breakpoints**
```css
/* Bootstrap 5 breakpoints */
--bs-breakpoint-xs: 0;
--bs-breakpoint-sm: 576px;
--bs-breakpoint-md: 768px;
--bs-breakpoint-lg: 992px;
--bs-breakpoint-xl: 1200px;
--bs-breakpoint-xxl: 1400px;
```

### **Mobile-First Approach**
- All styles start with mobile design
- Progressive enhancement for larger screens
- Touch-friendly interface elements
- Optimized loading for mobile networks

### **Component Responsiveness**
- **Navigation** - Collapsible mobile menu
- **Tables** - Horizontal scrolling on mobile
- **Forms** - Stacked layout on small screens
- **Cards** - Single column on mobile

---

## 🔧 Development Workflow

### **Frontend Development Commands**
```bash
# Run frontend tests
npx jest --config=jest.config.js

# View test coverage
npx jest --config=jest.config.js --coverage

# Code quality checks
make quality-check

# Pre-commit hooks
make pre-commit-run
```

### **Testing Strategy**
- **Unit Tests** - Individual component testing
- **Integration Tests** - Module interaction testing
- **E2E Tests** - Complete user workflow testing
- **Accessibility Tests** - WCAG compliance verification

### **Code Quality Standards**
- **ESLint** - JavaScript linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking (optional)
- **Pre-commit Hooks** - Automated quality checks

---

## 🎯 Key Features

### **Authentication System**
- JWT token-based authentication
- Automatic token refresh
- Role-based access control
- Secure logout with token invalidation

### **Form Handling**
- Real-time validation
- Error message display
- File upload with progress
- Form state management

### **Data Management**
- API integration with error handling
- Optimistic updates
- Data caching strategies
- Real-time updates

### **User Experience**
- Loading states and indicators
- Toast notifications
- Modal dialogs
- Responsive navigation

---

## 🚀 Performance Metrics

### **Current Performance**
- **Initial Load Time**: < 2 seconds
- **Time to Interactive**: < 3 seconds
- **Lighthouse Score**: > 90
- **Bundle Size**: Optimized and compressed

### **Optimization Techniques**
- **Critical CSS** - Above-the-fold styles inlined
- **Lazy Loading** - Non-critical resources deferred
- **Image Optimization** - WebP format with fallbacks
- **Caching Strategy** - Intelligent cache invalidation

---

## 🔒 Security Features

### **Frontend Security**
- **XSS Prevention** - Content Security Policy
- **CSRF Protection** - Django CSRF tokens
- **Input Validation** - Client and server-side validation
- **Secure Headers** - Security-focused HTTP headers

### **Authentication Security**
- **JWT Token Storage** - Secure localStorage usage
- **Token Expiration** - Automatic refresh handling
- **Logout Security** - Complete token cleanup
- **Session Management** - Proper session handling

---

## 📚 Additional Resources

- **[Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)**
- **[Django Template Language](https://docs.djangoproject.com/en/stable/topics/templates/)**
- **[JavaScript ES6+ Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript)**
- **[Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)**

---

## 🔧 Dynamic Forms Integration

### **django-dynforms Integration**
SEIM uses django-dynforms for dynamic form creation and management. The frontend integration follows these principles:

#### **Template Usage**
- **Official Templates**: Always use official dynforms templates from the package
- **Base Template Extension**: Dynforms templates extend the main base template
- **Block Name Adjustments**: Template blocks are adjusted to match the main base template structure

#### **JavaScript Integration**
- **Official JS Files**: Use `dynforms.min.js` and `df-toasts.min.js` from the official package
- **No Custom Overrides**: Avoid custom JavaScript that overrides official dynforms functionality
- **Loading Order**: Ensure dynforms JS loads after Bootstrap and other dependencies

#### **CSS Customization**
- **Dark Mode**: Implemented via CSS-only customizations in `static/css/dynforms-dark-mode.css`
- **Theme Variables**: Use CSS custom properties for consistent theming
- **No Template Modifications**: All styling is handled via CSS, not template changes

#### **Best Practices**
- Always test form builder functionality after any dynforms-related changes
- Use official dynforms documentation for form building features
- Customize appearance via CSS only, never modify dynforms templates or JavaScript
- Ensure proper authentication is in place for form builder access

---

For frontend-specific issues or questions, see the [Support & Contact](../README.md#support--contact) section. 