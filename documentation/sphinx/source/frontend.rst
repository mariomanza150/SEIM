Frontend Module
==============

The frontend module provides the user interface and client-side functionality for SEIM.

Overview
--------

The frontend module provides:

* Django-based frontend with Bootstrap 5
* Responsive design and mobile support
* JavaScript interactions and AJAX
* CSS styling and theming
* Template system and components
* Service worker for offline support

Views
-----

.. automodule:: frontend.views
   :members:
   :undoc-members:
   :show-inheritance:

Frontend Views
-------------

The frontend module provides several key views:

**Home View:**

.. code-block:: python

    class HomeView(TemplateView):
        template_name = 'frontend/home.html'
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Get featured programs
            featured_programs = Program.objects.filter(
                is_active=True, 
                is_featured=True
            )[:3]
            
            # Get system statistics
            stats = AnalyticsService.get_public_metrics()
            
            context.update({
                'featured_programs': featured_programs,
                'stats': stats
            })
            return context

**Application Views:**

.. code-block:: python

    class ApplicationListView(LoginRequiredMixin, ListView):
        model = Application
        template_name = 'frontend/applications/list.html'
        context_object_name = 'applications'
        
        def get_queryset(self):
            if self.request.user.has_role('admin'):
                return Application.objects.all()
            elif self.request.user.has_role('coordinator'):
                return Application.objects.filter(
                    status__name__in=['submitted', 'under_review']
                )
            else:
                return Application.objects.filter(student=self.request.user)

URLs
----

.. automodule:: frontend.urls
   :members:
   :undoc-members:
   :show-inheritance:

Templates
---------

The frontend uses Django templates with Bootstrap 5:

**Base Template:**

.. code-block:: html

    <!-- templates/base.html -->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}SEIM - Student Exchange Information Manager{% endblock %}</title>
        
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- Custom CSS -->
        <link href="{% static 'css/main.css' %}" rel="stylesheet">
        <!-- Font Awesome -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        
        {% block extra_css %}{% endblock %}
    </head>
    <body>
        <!-- Navigation -->
        {% include 'frontend/includes/navbar.html' %}
        
        <!-- Main Content -->
        <main class="main-content">
            {% if messages %}
                {% include 'frontend/includes/messages.html' %}
            {% endif %}
            
            {% block content %}{% endblock %}
        </main>
        
        <!-- Footer -->
        {% include 'frontend/includes/footer.html' %}
        
        <!-- Bootstrap JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <!-- Custom JS -->
        <script src="{% static 'js/main.js' %}"></script>
        <!-- SweetAlert2 -->
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
        
        {% block extra_js %}{% endblock %}
    </body>
    </html>

**Navigation Template:**

.. code-block:: html

    <!-- templates/frontend/includes/navbar.html -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">
                <i class="fas fa-globe"></i> SEIM
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'home' %}">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'programs:list' %}">Programs</a>
                    </li>
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'applications:list' %}">Applications</a>
                        </li>
                        {% if user.has_role('coordinator') or user.has_role('admin') %}
                            <li class="nav-item">
                                <a class="nav-link" href="{% url 'dashboard' %}">Dashboard</a>
                            </li>
                        {% endif %}
                    {% endif %}
                </ul>
                
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-user"></i> {{ user.get_full_name }}
                            </a>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="{% url 'profile' %}">Profile</a></li>
                                <li><a class="dropdown-item" href="{% url 'notifications:list' %}">Notifications</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{% url 'logout' %}">Logout</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'login' %}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'register' %}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

**Application Form Template:**

.. code-block:: html

    <!-- templates/frontend/applications/form.html -->
    {% extends 'base.html' %}
    
    {% block title %}Application Form - {{ program.name }}{% endblock %}
    
    {% block content %}
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card">
                    <div class="card-header">
                        <h4 class="card-title mb-0">Application for {{ program.name }}</h4>
                    </div>
                    <div class="card-body">
                        <form method="post" enctype="multipart/form-data" id="applicationForm">
                            {% csrf_token %}
                            
                            <!-- Program Information -->
                            <div class="mb-4">
                                <h5>Program Information</h5>
                                <div class="row">
                                    <div class="col-md-6">
                                        <p><strong>Institution:</strong> {{ program.institution }}</p>
                                        <p><strong>Country:</strong> {{ program.country }}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <p><strong>Start Date:</strong> {{ program.start_date }}</p>
                                        <p><strong>End Date:</strong> {{ program.end_date }}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Application Form -->
                            <div class="mb-4">
                                <h5>Application Details</h5>
                                {{ form.as_p }}
                            </div>
                            
                            <!-- Document Upload -->
                            <div class="mb-4">
                                <h5>Required Documents</h5>
                                <div id="documentUpload">
                                    {% for doc_type in required_documents %}
                                    <div class="mb-3">
                                        <label class="form-label">{{ doc_type.name }}</label>
                                        <input type="file" class="form-control" 
                                               name="document_{{ doc_type.id }}"
                                               accept=".pdf,.doc,.docx,.jpg,.png"
                                               data-required="true">
                                        <div class="form-text">{{ doc_type.description }}</div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                            
                            <!-- Submit Buttons -->
                            <div class="d-flex justify-content-between">
                                <button type="submit" name="action" value="save_draft" class="btn btn-secondary">
                                    <i class="fas fa-save"></i> Save as Draft
                                </button>
                                <button type="submit" name="action" value="submit" class="btn btn-primary">
                                    <i class="fas fa-paper-plane"></i> Submit Application
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    
    {% block extra_js %}
    <script src="{% static 'js/application-form.js' %}"></script>
    {% endblock %}

JavaScript
----------

The frontend includes comprehensive JavaScript functionality:

**Main JavaScript File:**

.. code-block:: javascript

    // static/js/main.js
    
    // Global variables
    const API_BASE_URL = '/api/';
    const CSRF_TOKEN = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // Utility functions
    const utils = {
        // Show notification
        showNotification: function(message, type = 'success') {
            Swal.fire({
                title: type === 'success' ? 'Success!' : 'Error!',
                text: message,
                icon: type,
                timer: type === 'success' ? 3000 : null,
                timerProgressBar: type === 'success'
            });
        },
        
        // Make API request
        apiRequest: async function(endpoint, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN
                }
            };
            
            const config = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(API_BASE_URL + endpoint, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API request failed:', error);
                throw error;
            }
        },
        
        // Format date
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },
        
        // Validate form
        validateForm: function(formElement) {
            const requiredFields = formElement.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            return isValid;
        }
    };
    
    // Authentication functions
    const auth = {
        // Login
        login: async function(username, password) {
            try {
                const response = await utils.apiRequest('token/', {
                    method: 'POST',
                    body: JSON.stringify({ username, password })
                });
                
                // Store tokens
                localStorage.setItem('access_token', response.access);
                localStorage.setItem('refresh_token', response.refresh);
                
                return response;
            } catch (error) {
                throw error;
            }
        },
        
        // Logout
        logout: function() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
        },
        
        // Check if user is authenticated
        isAuthenticated: function() {
            return !!localStorage.getItem('access_token');
        },
        
        // Get access token
        getAccessToken: function() {
            return localStorage.getItem('access_token');
        }
    };
    
    // Document upload functions
    const documentUpload = {
        // Upload document
        upload: async function(file, applicationId, documentType) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('application', applicationId);
            formData.append('document_type', documentType);
            
            try {
                const response = await fetch(API_BASE_URL + 'documents/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${auth.getAccessToken()}`
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`Upload failed: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                throw error;
            }
        },
        
        // Validate file
        validateFile: function(file, allowedTypes, maxSize) {
            const allowedExtensions = allowedTypes.map(type => type.toLowerCase());
            const fileExtension = file.name.split('.').pop().toLowerCase();
            
            if (!allowedExtensions.includes(fileExtension)) {
                throw new Error(`File type not allowed. Allowed types: ${allowedTypes.join(', ')}`);
            }
            
            if (file.size > maxSize) {
                throw new Error(`File too large. Maximum size: ${maxSize / 1024 / 1024}MB`);
            }
            
            return true;
        }
    };
    
    // Application form handling
    const applicationForm = {
        // Initialize form
        init: function() {
            const form = document.getElementById('applicationForm');
            if (form) {
                this.setupFormValidation(form);
                this.setupDocumentUpload(form);
                this.setupAutoSave(form);
            }
        },
        
        // Setup form validation
        setupFormValidation: function(form) {
            form.addEventListener('submit', function(e) {
                if (!utils.validateForm(form)) {
                    e.preventDefault();
                    utils.showNotification('Please fill in all required fields.', 'error');
                }
            });
        },
        
        // Setup document upload
        setupDocumentUpload: function(form) {
            const fileInputs = form.querySelectorAll('input[type="file"]');
            
            fileInputs.forEach(input => {
                input.addEventListener('change', function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        try {
                            documentUpload.validateFile(file, ['pdf', 'doc', 'docx', 'jpg', 'png'], 10 * 1024 * 1024);
                            utils.showNotification('File selected successfully.');
                        } catch (error) {
                            utils.showNotification(error.message, 'error');
                            e.target.value = '';
                        }
                    }
                });
            });
        },
        
        // Setup auto-save
        setupAutoSave: function(form) {
            let autoSaveTimer;
            
            form.addEventListener('input', function() {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    applicationForm.autoSave(form);
                }, 2000);
            });
        },
        
        // Auto-save form
        autoSave: async function(form) {
            try {
                const formData = new FormData(form);
                formData.append('action', 'save_draft');
                
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    console.log('Form auto-saved');
                }
            } catch (error) {
                console.error('Auto-save failed:', error);
            }
        }
    };
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        applicationForm.init();
        
        // Setup global event listeners
        setupGlobalEventListeners();
    });
    
    // Setup global event listeners
    function setupGlobalEventListeners() {
        // Handle logout
        const logoutButtons = document.querySelectorAll('[data-action="logout"]');
        logoutButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                auth.logout();
            });
        });
        
        // Handle notifications
        const notificationButtons = document.querySelectorAll('[data-action="mark-read"]');
        notificationButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const notificationId = this.dataset.notificationId;
                markNotificationAsRead(notificationId);
            });
        });
    }

CSS Styling
-----------

The frontend uses Bootstrap 5 with custom CSS:

**Main CSS File:**

.. code-block:: css

    /* static/css/main.css */
    
    /* Custom CSS variables */
    :root {
        --primary-color: #0d6efd;
        --secondary-color: #6c757d;
        --success-color: #198754;
        --danger-color: #dc3545;
        --warning-color: #ffc107;
        --info-color: #0dcaf0;
        --light-color: #f8f9fa;
        --dark-color: #212529;
        
        --border-radius: 0.375rem;
        --box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        --transition: all 0.15s ease-in-out;
    }
    
    /* Global styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: var(--dark-color);
        background-color: var(--light-color);
    }
    
    /* Navigation styles */
    .navbar-brand {
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    .navbar-nav .nav-link {
        font-weight: 500;
        transition: var(--transition);
    }
    
    .navbar-nav .nav-link:hover {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Card styles */
    .card {
        border: none;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        transition: var(--transition);
    }
    
    .card:hover {
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }
    
    .card-header {
        background-color: rgba(0, 0, 0, 0.03);
        border-bottom: 1px solid rgba(0, 0, 0, 0.125);
        font-weight: 600;
    }
    
    /* Button styles */
    .btn {
        border-radius: var(--border-radius);
        font-weight: 500;
        transition: var(--transition);
    }
    
    .btn-primary {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
    }
    
    .btn-primary:hover {
        background-color: #0b5ed7;
        border-color: #0a58ca;
    }
    
    /* Form styles */
    .form-control {
        border-radius: var(--border-radius);
        border: 1px solid #ced4da;
        transition: var(--transition);
    }
    
    .form-control:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
    }
    
    .form-control.is-invalid {
        border-color: var(--danger-color);
    }
    
    .form-control.is-valid {
        border-color: var(--success-color);
    }
    
    /* Table styles */
    .table {
        border-radius: var(--border-radius);
        overflow: hidden;
    }
    
    .table thead th {
        background-color: rgba(0, 0, 0, 0.03);
        border-bottom: 2px solid #dee2e6;
        font-weight: 600;
    }
    
    /* Badge styles */
    .badge {
        font-size: 0.75em;
        padding: 0.375em 0.75em;
        border-radius: 0.375rem;
    }
    
    /* Alert styles */
    .alert {
        border: none;
        border-radius: var(--border-radius);
    }
    
    /* Progress bar styles */
    .progress {
        border-radius: var(--border-radius);
        height: 0.5rem;
    }
    
    /* Modal styles */
    .modal-content {
        border: none;
        border-radius: var(--border-radius);
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }
    
    .modal-header {
        border-bottom: 1px solid #dee2e6;
        background-color: rgba(0, 0, 0, 0.03);
    }
    
    /* Utility classes */
    .text-primary { color: var(--primary-color) !important; }
    .text-secondary { color: var(--secondary-color) !important; }
    .text-success { color: var(--success-color) !important; }
    .text-danger { color: var(--danger-color) !important; }
    .text-warning { color: var(--warning-color) !important; }
    .text-info { color: var(--info-color) !important; }
    
    .bg-primary { background-color: var(--primary-color) !important; }
    .bg-secondary { background-color: var(--secondary-color) !important; }
    .bg-success { background-color: var(--success-color) !important; }
    .bg-danger { background-color: var(--danger-color) !important; }
    .bg-warning { background-color: var(--warning-color) !important; }
    .bg-info { background-color: var(--info-color) !important; }
    
    /* Responsive utilities */
    @media (max-width: 768px) {
        .container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .card-body {
            padding: 1rem;
        }
        
        .btn {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        .btn-group .btn {
            width: auto;
            margin-bottom: 0;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --light-color: #212529;
            --dark-color: #f8f9fa;
        }
        
        body {
            background-color: var(--light-color);
            color: var(--dark-color);
        }
        
        .card {
            background-color: #343a40;
            color: var(--dark-color);
        }
        
        .navbar {
            background-color: #495057 !important;
        }
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }

Service Worker
-------------

The frontend includes a service worker for offline support:

.. code-block:: javascript

    // static/js/sw.js
    
    const CACHE_NAME = 'seim-v1.0.0';
    const STATIC_CACHE = 'seim-static-v1.0.0';
    const API_CACHE = 'seim-api-v1.0.0';
    
    // Files to cache
    const STATIC_FILES = [
        '/',
        '/static/css/main.css',
        '/static/js/main.js',
        '/static/js/auth.js',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
        'https://cdn.jsdelivr.net/npm/sweetalert2@11'
    ];
    
    // Install event
    self.addEventListener('install', event => {
        event.waitUntil(
            caches.open(STATIC_CACHE)
                .then(cache => cache.addAll(STATIC_FILES))
                .then(() => self.skipWaiting())
        );
    });
    
    // Activate event
    self.addEventListener('activate', event => {
        event.waitUntil(
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
                            return caches.delete(cacheName);
                        }
                    })
                );
            }).then(() => self.clients.claim())
        );
    });
    
    // Fetch event
    self.addEventListener('fetch', event => {
        const { request } = event;
        const url = new URL(request.url);
        
        // Handle static files
        if (request.method === 'GET' && isStaticFile(url.pathname)) {
            event.respondWith(cacheFirst(request, STATIC_CACHE));
            return;
        }
        
        // Handle API requests
        if (request.method === 'GET' && url.pathname.startsWith('/api/')) {
            event.respondWith(networkFirst(request, API_CACHE));
            return;
        }
        
        // Handle other requests
        event.respondWith(networkFirst(request));
    });
    
    // Cache first strategy
    async function cacheFirst(request, cacheName) {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        try {
            const networkResponse = await fetch(request);
            if (networkResponse.ok) {
                cache.put(request, networkResponse.clone());
            }
            return networkResponse;
        } catch (error) {
            return new Response('Offline content not available', {
                status: 503,
                statusText: 'Service Unavailable'
            });
        }
    }
    
    // Network first strategy
    async function networkFirst(request, cacheName = null) {
        try {
            const networkResponse = await fetch(request);
            if (cacheName && networkResponse.ok) {
                const cache = await caches.open(cacheName);
                cache.put(request, networkResponse.clone());
            }
            return networkResponse;
        } catch (error) {
            if (cacheName) {
                const cache = await caches.open(cacheName);
                const cachedResponse = await cache.match(request);
                if (cachedResponse) {
                    return cachedResponse;
                }
            }
            throw error;
        }
    }
    
    // Check if file is static
    function isStaticFile(pathname) {
        return pathname.startsWith('/static/') ||
               pathname.startsWith('/media/') ||
               pathname.endsWith('.css') ||
               pathname.endsWith('.js') ||
               pathname.endsWith('.png') ||
               pathname.endsWith('.jpg') ||
               pathname.endsWith('.ico');
    }

Business Rules
-------------

* Frontend must be responsive and mobile-friendly
* All forms must have client-side validation
* JavaScript must be progressive enhancement
* Service worker provides offline support
* Bootstrap 5 is the primary CSS framework
* Custom CSS follows BEM methodology
* All interactive elements must be accessible
* Dark mode support is optional but recommended
* Performance optimization is required
* Cross-browser compatibility is essential

Related Documentation
--------------------

* :doc:`dashboard` - Dashboard interfaces and components
* :doc:`api` - API integration and endpoints
* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`deployment` - Frontend deployment configuration 