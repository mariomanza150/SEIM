Dashboard Module
===============

The dashboard module provides role-based dashboards and user interfaces for SEIM.

Overview
--------

The dashboard module provides:

* Role-based dashboard interfaces
* User dashboard customization
* Admin dashboard with analytics
* Coordinator dashboard for application review
* Student dashboard for application management
* Real-time data updates

Views
-----

.. automodule:: dashboard.views
   :members:
   :undoc-members:
   :show-inheritance:

Dashboard Views
--------------

The dashboard module provides several key views:

**Student Dashboard:**

.. code-block:: python

    class StudentDashboardView(LoginRequiredMixin, TemplateView):
        template_name = 'frontend/dashboard.html'
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user = self.request.user
            
            # Get user's applications
            applications = Application.objects.filter(student=user)
            
            # Get available programs
            programs = Program.objects.filter(is_active=True)
            
            context.update({
                'applications': applications,
                'programs': programs,
                'user_role': 'student'
            })
            return context

**Coordinator Dashboard:**

.. code-block:: python

    class CoordinatorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
        template_name = 'frontend/dashboard.html'
        
        def test_func(self):
            return self.request.user.has_role('coordinator')
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Get applications to review
            applications = Application.objects.filter(
                status__name__in=['submitted', 'under_review']
            )
            
            # Get program statistics
            program_stats = self.get_program_statistics()
            
            context.update({
                'applications': applications,
                'program_stats': program_stats,
                'user_role': 'coordinator'
            })
            return context

**Admin Dashboard:**

.. code-block:: python

    class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
        template_name = 'frontend/dashboard.html'
        
        def test_func(self):
            return self.request.user.has_role('admin')
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            
            # Get system-wide statistics
            stats = AnalyticsService.get_dashboard_metrics()
            
            # Get recent activity
            recent_activity = self.get_recent_activity()
            
            context.update({
                'stats': stats,
                'recent_activity': recent_activity,
                'user_role': 'admin'
            })
            return context

Models
------

.. automodule:: dashboard.models
   :members:
   :undoc-members:
   :show-inheritance:

DashboardWidget Model
--------------------

The DashboardWidget model allows customization of dashboard layouts:

.. autoclass:: dashboard.models.DashboardWidget
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Widget Configuration**: JSON-based widget configuration
* **User Customization**: Users can customize their dashboard
* **Role-based Widgets**: Different widgets for different roles
* **Position Management**: Widget positioning and layout

Example Usage:

.. code-block:: python

    from dashboard.models import DashboardWidget
    
    # Create a widget for applications
    widget = DashboardWidget.objects.create(
        user=user,
        widget_type='applications_list',
        title='My Applications',
        position=1,
        config={
            'show_status': True,
            'limit': 5,
            'refresh_interval': 300
        }
    )

URLs
----

.. automodule:: dashboard.urls
   :members:
   :undoc-members:
   :show-inheritance:

Templates
---------

The dashboard uses Django templates with Bootstrap 5:

**Base Dashboard Template:**

.. code-block:: html

    <!-- templates/frontend/dashboard.html -->
    {% extends 'base.html' %}
    
    {% block content %}
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar">
                {% include 'frontend/includes/sidebar.html' %}
            </nav>
            
            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                <!-- Dashboard header -->
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Dashboard</h1>
                    <div class="btn-toolbar mb-2 mb-md-0">
                        <div class="btn-group me-2">
                            <button type="button" class="btn btn-sm btn-outline-secondary">Export</button>
                        </div>
                    </div>
                </div>
                
                <!-- Dashboard content -->
                {% if user_role == 'student' %}
                    {% include 'frontend/dashboard/student.html' %}
                {% elif user_role == 'coordinator' %}
                    {% include 'frontend/dashboard/coordinator.html' %}
                {% elif user_role == 'admin' %}
                    {% include 'frontend/dashboard/admin.html' %}
                {% endif %}
            </main>
        </div>
    </div>
    {% endblock %}

**Student Dashboard Content:**

.. code-block:: html

    <!-- templates/frontend/dashboard/student.html -->
    <div class="row">
        <!-- Applications Summary -->
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">My Applications</h5>
                    <p class="card-text display-4">{{ applications.count }}</p>
                    <a href="{% url 'applications:list' %}" class="btn btn-primary">View All</a>
                </div>
            </div>
        </div>
        
        <!-- Available Programs -->
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Available Programs</h5>
                    <p class="card-text display-4">{{ programs.count }}</p>
                    <a href="{% url 'programs:list' %}" class="btn btn-primary">Browse Programs</a>
                </div>
            </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Recent Activity</h5>
                    <div class="list-group list-group-flush">
                        {% for application in applications|slice:":3" %}
                        <div class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">{{ application.program.name }}</h6>
                                <small class="text-muted">{{ application.updated_at|timesince }} ago</small>
                            </div>
                            <p class="mb-1">Status: {{ application.status.name|title }}</p>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

**Coordinator Dashboard Content:**

.. code-block:: html

    <!-- templates/frontend/dashboard/coordinator.html -->
    <div class="row">
        <!-- Applications to Review -->
        <div class="col-md-8 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title mb-0">Applications to Review</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Student</th>
                                    <th>Program</th>
                                    <th>Status</th>
                                    <th>Submitted</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for application in applications %}
                                <tr>
                                    <td>{{ application.student.get_full_name }}</td>
                                    <td>{{ application.program.name }}</td>
                                    <td>
                                        <span class="badge bg-{{ application.status.color }}">
                                            {{ application.status.name|title }}
                                        </span>
                                    </td>
                                    <td>{{ application.submitted_at|date:"M j, Y" }}</td>
                                    <td>
                                        <a href="{% url 'applications:detail' application.id %}" 
                                           class="btn btn-sm btn-primary">Review</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Program Statistics -->
        <div class="col-md-4 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title mb-0">Program Statistics</h5>
                </div>
                <div class="card-body">
                    {% for stat in program_stats %}
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>{{ stat.program_name }}</span>
                        <span class="badge bg-primary">{{ stat.application_count }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

**Admin Dashboard Content:**

.. code-block:: html

    <!-- templates/frontend/dashboard/admin.html -->
    <div class="row">
        <!-- System Statistics -->
        <div class="col-md-3 mb-4">
            <div class="card text-white bg-primary">
                <div class="card-body">
                    <h5 class="card-title">Total Users</h5>
                    <p class="card-text display-4">{{ stats.total_users }}</p>
                </div>
            </div>
        </div>
        
        <div class="col-md-3 mb-4">
            <div class="card text-white bg-success">
                <div class="card-body">
                    <h5 class="card-title">Active Applications</h5>
                    <p class="card-text display-4">{{ stats.active_applications }}</p>
                </div>
            </div>
        </div>
        
        <div class="col-md-3 mb-4">
            <div class="card text-white bg-info">
                <div class="card-body">
                    <h5 class="card-title">Approved</h5>
                    <p class="card-text display-4">{{ stats.approved_applications }}</p>
                </div>
            </div>
        </div>
        
        <div class="col-md-3 mb-4">
            <div class="card text-white bg-warning">
                <div class="card-body">
                    <h5 class="card-title">Pending Review</h5>
                    <p class="card-text display-4">{{ stats.pending_applications }}</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Charts and Analytics -->
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title mb-0">Applications Over Time</h5>
                </div>
                <div class="card-body">
                    <canvas id="applicationsChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="col-md-6 mb-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title mb-0">Status Distribution</h5>
                </div>
                <div class="card-body">
                    <canvas id="statusChart"></canvas>
                </div>
            </div>
        </div>
    </div>

JavaScript Integration
---------------------

The dashboard includes JavaScript for interactive features:

.. code-block:: javascript

    // static/js/dashboard.js
    
    // Dashboard initialization
    document.addEventListener('DOMContentLoaded', function() {
        initializeDashboard();
        setupRealTimeUpdates();
        initializeCharts();
    });
    
    // Initialize dashboard components
    function initializeDashboard() {
        // Setup tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Setup dropdowns
        var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }
    
    // Setup real-time updates
    function setupRealTimeUpdates() {
        // Update dashboard every 30 seconds
        setInterval(function() {
            updateDashboardData();
        }, 30000);
    }
    
    // Update dashboard data
    async function updateDashboardData() {
        try {
            const response = await fetch('/api/analytics/dashboard/');
            const data = await response.json();
            
            // Update statistics
            updateStatistics(data);
            
            // Update charts
            updateCharts(data);
        } catch (error) {
            console.error('Failed to update dashboard:', error);
        }
    }
    
    // Initialize charts
    function initializeCharts() {
        // Applications over time chart
        const applicationsCtx = document.getElementById('applicationsChart');
        if (applicationsCtx) {
            new Chart(applicationsCtx, {
                type: 'line',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Applications',
                        data: chartData.applications,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Status distribution chart
        const statusCtx = document.getElementById('statusChart');
        if (statusCtx) {
            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: statusData.labels,
                    datasets: [{
                        data: statusData.values,
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#dc3545',
                            '#17a2b8'
                        ]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
    }

CSS Styling
-----------

The dashboard uses Bootstrap 5 with custom styling:

.. code-block:: css

    /* static/css/dashboard.css */
    
    /* Dashboard layout */
    .dashboard-container {
        min-height: 100vh;
        background-color: #f8f9fa;
    }
    
    /* Sidebar styling */
    .sidebar {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        z-index: 100;
        padding: 48px 0 0;
        box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);
    }
    
    .sidebar-sticky {
        position: relative;
        top: 0;
        height: calc(100vh - 48px);
        padding-top: .5rem;
        overflow-x: hidden;
        overflow-y: auto;
    }
    
    /* Card styling */
    .dashboard-card {
        border: none;
        border-radius: 10px;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        transition: box-shadow 0.15s ease-in-out;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }
    
    /* Statistics cards */
    .stat-card {
        text-align: center;
        padding: 1.5rem;
    }
    
    .stat-card .display-4 {
        font-weight: 300;
        line-height: 1.2;
    }
    
    /* Table styling */
    .dashboard-table {
        margin-bottom: 0;
    }
    
    .dashboard-table th {
        border-top: none;
        font-weight: 600;
        color: #495057;
    }
    
    /* Badge styling */
    .badge {
        font-size: 0.75em;
        padding: 0.375em 0.75em;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .sidebar {
            position: static;
            height: auto;
            padding-top: 0;
        }
        
        .sidebar-sticky {
            height: auto;
        }
    }

Business Rules
-------------

* Dashboard access is role-based (student, coordinator, admin)
* Students can only see their own applications and available programs
* Coordinators can see applications assigned to them for review
* Admins have access to system-wide statistics and analytics
* Dashboard data is cached for performance
* Real-time updates are available for critical data
* Dashboard layout is customizable per user
* Mobile-responsive design is required
* Charts and graphs are interactive
* Export functionality is available for reports

Related Documentation
--------------------

* :doc:`frontend` - Frontend architecture and components
* :doc:`analytics` - Analytics and reporting functionality
* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for dashboard data 