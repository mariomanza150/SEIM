Analytics Module
===============

The analytics module handles dashboard metrics, reporting, and data analysis in SEIM.

Overview
--------

The analytics module provides:

* Dashboard metrics calculation
* Program-specific analytics
* User activity tracking
* Exportable reports
* Real-time data visualization
* Performance monitoring

Models
------

.. automodule:: analytics.models
   :members:
   :undoc-members:
   :show-inheritance:

AnalyticsEvent Model
-------------------

The AnalyticsEvent model tracks user activities and system events:

.. autoclass:: analytics.models.AnalyticsEvent
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Event Tracking**: Track user actions and system events
* **User Context**: Associate events with specific users
* **Event Types**: Categorize different types of events
* **Metadata Storage**: Store additional event data
* **Timestamp Tracking**: Precise event timing

Example Usage:

.. code-block:: python

    from analytics.models import AnalyticsEvent
    
    # Track user login
    AnalyticsEvent.objects.create(
        user=user,
        event_type='user_login',
        event_data={
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0...',
            'success': True
        }
    )
    
    # Track application submission
    AnalyticsEvent.objects.create(
        user=student,
        event_type='application_submitted',
        event_data={
            'application_id': application.id,
            'program_id': application.program.id,
            'submission_time': application.submitted_at.isoformat()
        }
    )

DashboardMetric Model
--------------------

.. autoclass:: analytics.models.DashboardMetric
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: analytics.services
   :members:
   :undoc-members:
   :show-inheritance:

AnalyticsService
---------------

The AnalyticsService handles all analytics and reporting operations:

.. autoclass:: analytics.services.AnalyticsService
   :members:
   :undoc-members:
   :show-inheritance:

Key Methods:

* **get_dashboard_metrics()**: Calculate dashboard metrics
* **get_program_analytics()**: Get program-specific analytics
* **track_event()**: Track user or system events
* **generate_report()**: Generate exportable reports
* **get_user_activity()**: Get user activity data

Example Usage:

.. code-block:: python

    from analytics.services import AnalyticsService
    
    # Get dashboard metrics
    metrics = AnalyticsService.get_dashboard_metrics()
    print(f"Total Users: {metrics['total_users']}")
    print(f"Active Applications: {metrics['active_applications']}")
    print(f"Approved Applications: {metrics['approved_applications']}")
    
    # Get program analytics
    program_analytics = AnalyticsService.get_program_analytics(program_id)
    print(f"Applications: {program_analytics['total_applications']}")
    print(f"Approval Rate: {program_analytics['approval_rate']}%")
    
    # Track custom event
    AnalyticsService.track_event(
        user=user,
        event_type='document_uploaded',
        event_data={'document_type': 'transcript'}
    )

Views
-----

.. automodule:: analytics.views
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: analytics.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Admin Interface
--------------

.. automodule:: analytics.admin
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: analytics.urls
   :members:
   :undoc-members:
   :show-inheritance:

Tasks
-----

.. automodule:: analytics.tasks
   :members:
   :undoc-members:
   :show-inheritance:

Dashboard Metrics
----------------

SEIM provides comprehensive dashboard metrics:

**System Overview Metrics:**

* **Total Users**: Number of registered users
* **Active Users**: Users active in last 30 days
* **Total Applications**: All applications created
* **Active Applications**: Applications in progress
* **Approved Applications**: Successfully approved applications
* **Rejected Applications**: Rejected applications
* **Completion Rate**: Percentage of completed applications

**Program-Specific Metrics:**

* **Applications per Program**: Number of applications for each program
* **Approval Rate**: Percentage of approved applications
* **Average Processing Time**: Time from submission to decision
* **Popular Programs**: Most applied-to programs
* **Success Rate**: Program completion success rate

**User Activity Metrics:**

* **Login Frequency**: How often users log in
* **Feature Usage**: Which features are most used
* **Session Duration**: Average session length
* **User Engagement**: User interaction patterns

Example Metrics Calculation:

.. code-block:: python

    from analytics.services import AnalyticsService
    from django.utils import timezone
    from datetime import timedelta
    
    # Calculate dashboard metrics
    def calculate_dashboard_metrics():
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        metrics = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(
                last_login__gte=thirty_days_ago
            ).count(),
            'total_applications': Application.objects.count(),
            'active_applications': Application.objects.filter(
                status__name__in=['submitted', 'under_review']
            ).count(),
            'approved_applications': Application.objects.filter(
                status__name='approved'
            ).count(),
            'rejected_applications': Application.objects.filter(
                status__name='rejected'
            ).count(),
        }
        
        # Calculate completion rate
        total_completed = Application.objects.filter(
            status__name__in=['approved', 'rejected', 'completed']
        ).count()
        if metrics['total_applications'] > 0:
            metrics['completion_rate'] = (
                total_completed / metrics['total_applications']
            ) * 100
        else:
            metrics['completion_rate'] = 0
            
        return metrics

Reporting System
---------------

SEIM includes a comprehensive reporting system:

**Report Types:**

* **Application Summary**: Overview of all applications
* **Program Performance**: Program-specific performance metrics
* **User Activity**: User engagement and activity reports
* **Document Statistics**: Document upload and validation stats
* **Timeline Analysis**: Application processing timeline analysis

**Export Formats:**

* **CSV**: Comma-separated values for spreadsheet analysis
* **JSON**: Structured data for API consumption
* **PDF**: Formatted reports for printing/sharing
* **Excel**: Advanced spreadsheet format with formatting

Example Report Generation:

.. code-block:: python

    from analytics.services import AnalyticsService
    import csv
    from io import StringIO
    
    def generate_application_report(start_date, end_date, format='csv'):
        """Generate application report for date range."""
        
        # Get application data
        applications = Application.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('student', 'program', 'status')
        
        if format == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Application ID', 'Student', 'Program', 'Status',
                'Submitted Date', 'Processing Time (days)'
            ])
            
            # Write data
            for app in applications:
                processing_time = None
                if app.submitted_at and app.status.name in ['approved', 'rejected']:
                    processing_time = (app.updated_at - app.submitted_at).days
                
                writer.writerow([
                    app.id, app.student.username, app.program.name,
                    app.status.name, app.submitted_at, processing_time
                ])
            
            return output.getvalue()
        
        return applications

Real-time Analytics
------------------

SEIM provides real-time analytics capabilities:

**Live Dashboard Updates:**

* **WebSocket Integration**: Real-time data updates
* **Auto-refresh**: Automatic dashboard refresh
* **Live Metrics**: Current system status
* **Alert System**: Notifications for important events

**Performance Monitoring:**

* **Response Times**: API and page load times
* **Error Rates**: System error tracking
* **Resource Usage**: Server resource monitoring
* **User Experience**: Frontend performance metrics

Example Real-time Analytics:

.. code-block:: python

    from analytics.services import AnalyticsService
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    def update_dashboard_realtime():
        """Update dashboard with real-time data."""
        channel_layer = get_channel_layer()
        
        # Get current metrics
        metrics = AnalyticsService.get_dashboard_metrics()
        
        # Send to WebSocket
        async_to_sync(channel_layer.group_send)(
            'dashboard_updates',
            {
                'type': 'dashboard.update',
                'metrics': metrics
            }
        )

Data Visualization
-----------------

SEIM supports various data visualization options:

**Chart Types:**

* **Line Charts**: Time-series data (applications over time)
* **Bar Charts**: Categorical data (program popularity)
* **Pie Charts**: Proportional data (status distribution)
* **Heatmaps**: User activity patterns
* **Gauges**: Key performance indicators

**Interactive Features:**

* **Drill-down**: Click to see detailed data
* **Filtering**: Filter by date, program, status
* **Sorting**: Sort by various metrics
* **Export**: Export chart data

Example Chart Configuration:

.. code-block:: python

    def get_application_status_chart():
        """Generate application status distribution chart."""
        from django.db.models import Count
        
        status_data = Application.objects.values('status__name').annotate(
            count=Count('id')
        ).order_by('status__name')
        
        chart_data = {
            'type': 'pie',
            'data': {
                'labels': [item['status__name'] for item in status_data],
                'datasets': [{
                    'data': [item['count'] for item in status_data],
                    'backgroundColor': [
                        '#28a745', '#ffc107', '#dc3545',
                        '#17a2b8', '#6c757d', '#fd7e14'
                    ]
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Application Status Distribution'
                    }
                }
            }
        }
        
        return chart_data

Business Rules
-------------

* Analytics data is calculated in real-time
* Admin dashboard shows system-wide statistics
* Program-specific metrics available for coordinators
* User activity is tracked for audit purposes
* Personal information is anonymized in reports
* Access to analytics is role-based
* Historical data is preserved for compliance
* Reports can be scheduled and automated
* Data retention policies apply to analytics data

Related Documentation
--------------------

* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for analytics
* :doc:`exchange` - Application data integration
* :doc:`caching` - Performance optimization 