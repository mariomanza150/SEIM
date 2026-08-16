Exchange Module
==============

The exchange module handles exchange programs, applications, and workflow management in SEIM.

Overview
--------

The exchange module provides:

* Exchange program management
* Application workflow and state management
* Dynamic form system using django-dynforms
* Application comments and audit logging
* Timeline event tracking

Models
------

.. automodule:: exchange.models
   :members:
   :undoc-members:
   :show-inheritance:

Program Model
------------

The Program model represents exchange programs available to students:

.. autoclass:: exchange.models.Program
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Program Information**: Name, description, dates, institution
* **Eligibility Criteria**: Minimum GPA, language requirements
* **Recurring Programs**: Support for annual/semester programs
* **Status Management**: Active/inactive program states

Example Usage:

.. code-block:: python

    from exchange.models import Program
    
    # Create a new exchange program
    program = Program.objects.create(
        name='Erasmus+ Exchange Program',
        description='European exchange program for students',
        start_date='2024-09-01',
        end_date='2025-01-31',
        min_gpa=3.0,
        required_language='English',
        recurring=True,
        is_active=True
    )
    
    # Check program eligibility
    if program.min_gpa and student.profile.gpa < program.min_gpa:
        print("Student does not meet GPA requirement")

Application Model
----------------

The Application model represents student applications for exchange programs:

.. autoclass:: exchange.models.Application
   :members:
   :undoc-members:
   :show-inheritance:

Application Workflow States:

* **draft**: Initial state, student can edit
* **submitted**: Application submitted for review
* **under_review**: Coordinator is reviewing
* **approved**: Application approved
* **rejected**: Application rejected
* **completed**: Program completed
* **cancelled**: Application cancelled/withdrawn

Example Usage:

.. code-block:: python

    from exchange.models import Application, ApplicationStatus
    
    # Create a new application
    application = Application.objects.create(
        program=program,
        student=student,
        status=ApplicationStatus.objects.get(name='draft')
    )
    
    # Submit application
    ApplicationService.submit_application(application, student)
    
    # Check application status
    if application.status.name == 'approved':
        print("Application approved!")

ApplicationStatus Model
----------------------

.. autoclass:: exchange.models.ApplicationStatus
   :members:
   :undoc-members:
   :show-inheritance:

Comment Model
------------

.. autoclass:: exchange.models.Comment
   :members:
   :undoc-members:
   :show-inheritance:

TimelineEvent Model
------------------

.. autoclass:: exchange.models.TimelineEvent
   :members:
   :undoc-members:
   :show-inheritance:

DynamicForm Model
----------------

.. autoclass:: exchange.models.DynamicForm
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: exchange.services
   :members:
   :undoc-members:
   :show-inheritance:

ApplicationService
-----------------

The ApplicationService handles all application workflow operations:

.. autoclass:: exchange.services.ApplicationService
   :members:
   :undoc-members:
   :show-inheritance:

Key Methods:

* **check_eligibility()**: Validates student eligibility for program
* **submit_application()**: Submits draft application
* **transition_status()**: Changes application status
* **withdraw_application()**: Withdraws draft application
* **add_comment()**: Adds comments to application

Example Usage:

.. code-block:: python

    from exchange.services import ApplicationService
    
    # Check if student is eligible
    try:
        ApplicationService.check_eligibility(student, program)
        print("Student is eligible")
    except ValueError as e:
        print(f"Eligibility check failed: {e}")
    
    # Submit application
    try:
        ApplicationService.submit_application(application, student)
        print("Application submitted successfully")
    except ValueError as e:
        print(f"Submission failed: {e}")
    
    # Add coordinator comment
    comment = ApplicationService.add_comment(
        application=application,
        author=coordinator,
        text="Please provide additional documentation",
        is_private=False
    )

WorkflowService
--------------

.. automodule:: exchange.services.WorkflowService
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: exchange.views
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: exchange.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Admin Interface
--------------

.. automodule:: exchange.admin
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: exchange.urls
   :members:
   :undoc-members:
   :show-inheritance:

Application Workflow
-------------------

The application workflow follows a state machine pattern:

.. mermaid::

    flowchart TD
        A[draft] --> B[submitted]
        B --> C[under_review]
        C --> D[approved]
        C --> E[rejected]
        D --> F[completed]
        E --> G[cancelled]
        A --> G[cancelled]

State Transitions:

1. **draft → submitted**: Student submits application
2. **submitted → under_review**: Automatic transition
3. **under_review → approved/rejected**: Coordinator decision
4. **approved → completed**: Automatic when program ends
5. **rejected → cancelled**: Automatic when rejected
6. **draft → cancelled**: Student withdrawal

Business Rules
-------------

* Students can only have one active application per program
* Only draft applications can be submitted
* Only coordinators/admins can approve/reject applications
* Applications cannot be reactivated after withdrawal
* All status changes are logged in timeline events
* Comments can be private (internal) or public (visible to students)

Dynamic Forms
------------

The exchange module integrates with django-dynforms for dynamic application forms:

* **Form Builder**: Admin interface for creating forms
* **Validation Rules**: Configurable field validation
* **Conditional Logic**: Show/hide fields based on answers
* **Schema Storage**: JSON-based form schema storage

Example Form Schema:

.. code-block:: json

    {
        "fields": [
            {
                "name": "motivation",
                "type": "textarea",
                "label": "Motivation Statement",
                "required": true,
                "validation": {
                    "min_length": 100,
                    "max_length": 1000
                }
            },
            {
                "name": "previous_experience",
                "type": "checkbox",
                "label": "Previous Exchange Experience",
                "required": false
            }
        ]
    }

Related Documentation
--------------------

* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for exchange management
* :doc:`documents` - Document upload and validation 