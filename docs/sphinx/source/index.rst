SEIM Documentation
==================

Welcome to the SEIM (Student Exchange Information Manager) documentation. This documentation provides comprehensive information about the SEIM system, including API reference, development guides, and user documentation.

About SEIM
----------

SEIM is a comprehensive Django-based web application for managing student exchange programs, applications, and workflows. The system features a modern, responsive Django frontend with Bootstrap 5, JWT authentication, and role-based dashboards.

Key Features:

* **User Management**: Role-based authentication (Student, Coordinator, Admin)
* **Program Management**: Exchange program creation and management
* **Application Workflow**: Complete application lifecycle management
* **Document Management**: Secure file upload and validation
* **Notifications**: Email and in-app notification system
* **Analytics**: Dashboard and reporting capabilities
* **API**: RESTful API with comprehensive documentation

Quick Start
-----------

For developers getting started with SEIM:

1. **Installation**: See :doc:`installation` for setup instructions
2. **Development**: See :doc:`developer_guide` for development workflow
3. **API**: See :doc:`api` for API documentation
4. **Architecture**: See :doc:`architecture` for system design

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   developer_guide
   architecture
   architectural_decisions

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   admin_guide
   frontend_guide
   business_rules
   deployment

.. toctree::
   :maxdepth: 2
   :caption: Technical Reference

   api_documentation
   testing
   troubleshooting
   environment_variables
   caching
   dark_mode_implementation

.. toctree::
   :maxdepth: 2
   :caption: Project Planning

   roadmap
   backlog
   user_stories
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

