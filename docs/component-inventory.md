# SEIM Component Inventory

**Generated:** 2025-01-27  
**Project Type:** Web Application

## UI Component Catalog

### Frontend JavaScript Modules

#### Core Application Modules

**Entry Points:**
- `main.js` - Main application initialization, core features setup
- `dashboard.js` - Dashboard functionality and widgets
- `applications.js` - Application management interface
- `programs.js` - Program browsing and filtering
- `documents.js` - Document upload and management
- `auth_entry.js` - Authentication entry point

#### API & Communication Modules

**API Clients:**
- `modules/api.js` - Basic API client utilities
- `modules/api-enhanced.js` - Enhanced API client with:
  - Request deduplication
  - Request queuing
  - Intelligent caching
  - Performance monitoring
  - Token refresh handling
  - Retry logic

**WebSocket:**
- `modules/websocket-client.js` - Real-time WebSocket communication for notifications

#### Authentication & Security Modules

**Authentication:**
- `modules/auth.js` - Legacy authentication handling
- `modules/auth-unified.js` - Unified authentication system
- `modules/security.js` - Security utilities (XSS prevention, input sanitization)

**Features:**
- JWT token management
- Automatic token refresh
- Session management
- CSRF protection

#### UI & Interaction Modules

**Core UI:**
- `modules/ui.js` - Core UI utilities (tooltips, modals, loading states)
- `modules/ui-enhanced.js` - Enhanced UI features:
  - Skeleton loading
  - Progressive loading
  - Error recovery
  - Loading overlays

**Bootstrap Helpers:**
- `modules/ui/bootstrap_helpers.js` - Bootstrap 5 component helpers
- `modules/ui/auth_ui.js` - Authentication UI components
- `modules/ui/loading.js` - Loading state management

#### Notification System

**Notifications:**
- `modules/notifications.js` - Basic notification utilities
- `modules/toast-notifications.js` - Toast notification system
- `modules/notification-center.js` - Notification center offcanvas:
  - Notification list with pagination
  - Mark as read/delete
  - Real-time updates via WebSocket
  - Filtering (all/unread)

#### Form & Data Modules

**Forms:**
- `modules/dynamic-forms.js` - Dynamic form handling
- `modules/dynamic-loader.js` - Lazy loading for dynamic forms
- `modules/file_upload.js` - File upload with drag-and-drop

**Data Management:**
- `modules/applications_list.js` - Applications list management
- `modules/applications_actions.js` - Application action handlers
- `modules/programs_list.js` - Programs list and filtering
- `modules/documents_list.js` - Documents list management

#### Feature Modules

**Search & Filtering:**
- `modules/advanced-search.js` - Advanced search functionality
- `modules/saved-searches.js` - Saved search management

**Calendar:**
- `modules/calendar.js` - Calendar view and event management

**Preferences:**
- `modules/preferences.js` - User preferences management

#### Utility Modules

**Core Utilities:**
- `modules/utils.js` - General utility functions
- `modules/logger.js` - Logging system
- `modules/error-handler.js` - Centralized error handling
- `modules/validators.js` - Form and input validation
- `modules/performance.js` - Performance monitoring and tracking

**Accessibility:**
- `modules/accessibility.js` - Accessibility features
- `modules/accessibility-tester.js` - Accessibility testing utilities

**Theme Management:**
- `theme-manager.js` - Dark/light theme switching

### CSS Components

#### Main Stylesheets

**Core Styles:**
- `main.css` - Main application styles
- `accessibility.css` - Accessibility enhancements (WCAG compliance)
- `dark-mode.css` - Dark mode theme support
- `critical.css` - Critical above-the-fold styles (performance)
- `uadec-styles.css` - UAdeC branding styles
- `wagtail_admin_custom.css` - Wagtail CMS admin customizations

#### Component Styles (`components/`)

**UI Components:**
- `buttons.css` - Button styles and variants
- `cards.css` - Card component styles
- `forms.css` - Form element styles
- `tables.css` - Data table styles

#### Layout Styles (`layouts/`)

**Layout Components:**
- `base.css` - Base layout styles
- `navigation.css` - Navigation bar and menu styles

#### Utility Styles (`utilities/`)

**Utility Classes:**
- `colors.css` - Color variables and utilities
- `spacing.css` - Spacing utilities (margins, padding)
- `typography.css` - Typography styles and utilities

#### Responsive Styles
- `mobile-optimizations.css` - Mobile-specific optimizations

### Django Templates

#### Base Templates

**Main Template:**
- `base.html` - Base template with:
  - Navigation bar
  - Footer
  - Theme switching
  - WebSocket connection
  - CSRF token
  - Bootstrap 5 integration
  - Critical CSS inline

#### Component Templates (`templates/components/`)

**Navigation:**
- `navigation/navbar.html` - Main navigation bar with:
  - Role-based menu items
  - Notification bell
  - Theme toggle
  - Language switcher
  - User dropdown menu

**UI Components:**
- `footer.html` - Footer component
- `messages.html` - Django messages display
- `notification-center.html` - Notification center offcanvas
- `language-switcher.html` - Language selection component

**Forms:**
- `forms/search_form.html` - Search form component

**Tables:**
- `tables/data_table.html` - Data table component with sorting/filtering

#### Frontend Page Templates (`templates/frontend/`)

**Authentication:**
- `auth/login.html` - Login page
- `auth/register.html` - Registration page
- `auth/password_reset.html` - Password reset page

**Dashboards:**
- `dashboard.html` - Main user dashboard
- `admin/dashboard.html` - Admin dashboard
- `coordinator/dashboard.html` - Coordinator dashboard

**Applications:**
- `applications/list.html` - Applications list page
- `applications/detail.html` - Application detail page
- `applications/form.html` - Application form page

**Programs:**
- `programs/list.html` - Programs browsing page
- `programs/form.html` - Program creation/edit page

**Documents:**
- `documents/list.html` - Documents list page
- `documents/detail.html` - Document detail page
- `documents/form.html` - Document upload page

**Profile & Settings:**
- `profile.html` - User profile page
- `sessions.html` - Active sessions management
- `settings.html` - User settings page
- `user-management.html` - User management (admin)

**Other Pages:**
- `home.html` - Landing/home page
- `calendar.html` - Calendar view page
- `preferences.html` - User preferences page

#### CMS Templates (`cms/templates/cms/`)

**Page Templates:**
- `home_page.html` - Wagtail CMS home page
- `standard_page.html` - Standard content page
- `program_page.html` - Program detail page (CMS)
- `program_index_page.html` - Program listing page (CMS)
- `blog_post_page.html` - Blog post page
- `blog_index_page.html` - Blog listing page
- `faq_page.html` - FAQ page
- `faq_index_page.html` - FAQ listing page
- `form_page.html` - Wagtail form page
- `international_home_page.html` - International relations home

**Content Blocks:**
- `blocks/hero_block.html` - Hero section block
- `blocks/card_grid_block.html` - Card grid layout
- `blocks/call_to_action_block.html` - CTA block
- `blocks/paragraph_block.html` - Rich text paragraph
- `blocks/heading_block.html` - Heading block
- `blocks/image_block.html` - Image block
- `blocks/form_block.html` - Form block
- `blocks/two_column_block.html` - Two-column layout
- `blocks/embed_block.html` - Embed block
- `blocks/embed_video_block.html` - Video embed block
- `blocks/document_download_block.html` - Document download block
- `blocks/testimonial_block.html` - Testimonial block
- `blocks/faq_block.html` - FAQ block
- `blocks/quote_block.html` - Quote block
- `blocks/rich_text_block.html` - Rich text editor block
- `blocks/process_steps_block.html` - Process steps visualization

### Reusable Components

#### JavaScript Components

**Data Tables:**
- Sortable, filterable data tables
- Pagination support
- Responsive design

**Forms:**
- Dynamic form builder integration
- Real-time validation
- File upload with drag-and-drop
- Progress indicators

**Modals:**
- Bootstrap 5 modals
- Confirmation dialogs
- Form modals

**Notifications:**
- Toast notifications (success, error, warning, info)
- Notification center (offcanvas)
- Real-time WebSocket updates

**Charts & Analytics:**
- Dashboard widgets
- Chart initialization placeholders
- Performance metrics display

#### CSS Component Classes

**Bootstrap 5 Components:**
- Cards, buttons, forms, tables
- Navigation (navbar, dropdowns)
- Modals, offcanvas
- Alerts, badges
- Spinners, progress bars

**Custom Components:**
- Theme-aware components
- Accessibility-enhanced components
- Dark mode support

### Design System

#### Color System
- Primary: `#0d6efd` (Bootstrap primary blue)
- Secondary: `#6c757d` (Gray)
- Success: `#198754` (Green)
- Danger: `#dc3545` (Red)
- Warning: `#ffc107` (Yellow)
- Info: `#0dcaf0` (Cyan)

**Theme Variables:**
- CSS custom properties for colors
- Light/dark mode variants
- High contrast support

#### Typography
- Font family: System fonts (-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, etc.)
- Responsive font sizes
- Accessibility considerations

#### Spacing System
- Bootstrap 5 spacing utilities
- Consistent margins and padding
- Responsive spacing

### State Management

#### Client-Side State
- JWT tokens in localStorage
- User preferences in localStorage
- Theme preference in localStorage
- Notification state
- API response caching

#### Server-Side State
- Django sessions
- Redis cache
- Database state

### Build System

#### Webpack Configuration
- Entry points: dashboard, applications, programs, documents, auth_entry
- Code splitting: vendor chunks, common chunks, module chunks
- Performance chunk optimization
- Production optimizations:
  - Minification (Terser)
  - CSS minification
  - Tree shaking
  - Source maps (dev only)
  - Compression (gzip)

#### Bundle Analysis
- Bundle analyzer plugin available
- Performance monitoring
- Load time tracking

### Accessibility Features

#### ARIA Support
- ARIA labels on interactive elements
- ARIA live regions for dynamic content
- Keyboard navigation support
- Screen reader compatibility

#### Accessibility Testing
- Automated accessibility testing module
- WCAG compliance checking
- High contrast mode
- Reduced motion support

### Performance Features

#### Optimization
- Code splitting
- Lazy loading
- Critical CSS inline
- Asset compression
- Caching strategies

#### Monitoring
- Performance tracking
- Bundle load monitoring
- API response time tracking
- Cache hit/miss statistics

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
