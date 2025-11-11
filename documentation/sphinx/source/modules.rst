SEIM Modules
============

This section provides detailed documentation for all SEIM modules and their components.

.. toctree::
   :maxdepth: 4
   :caption: Core Modules

   accounts
   exchange
   documents
   notifications
   analytics
   core

.. toctree::
   :maxdepth: 4
   :caption: Supporting Modules

   api
   dashboard
   frontend
   plugins

Module Overview
--------------

SEIM is organized into several Django applications, each responsible for specific functionality:

**Core Applications:**

* :doc:`accounts` - User management and authentication
* :doc:`exchange` - Exchange program and application management
* :doc:`documents` - Document upload and validation
* :doc:`notifications` - Email and in-app notifications
* :doc:`analytics` - Dashboard and reporting
* :doc:`core` - Shared utilities and base classes

**Supporting Applications:**

* :doc:`api` - RESTful API endpoints
* :doc:`dashboard` - Admin and user dashboards
* :doc:`frontend` - Django-based frontend
* :doc:`plugins` - Modular plugin system

Architecture
-----------

Each module follows Django's app-based architecture with clear separation of concerns:

* **Models**: Data structure and business logic
* **Views**: Request handling and response generation
* **Services**: Business logic and external integrations
* **Serializers**: Data transformation for API
* **Admin**: Django admin interface customization
* **Tests**: Unit and integration tests

For detailed architecture information, see :doc:`architecture`.
