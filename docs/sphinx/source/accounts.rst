Accounts Module
==============

The accounts module handles user management, authentication, and authorization in SEIM.

Overview
--------

The accounts module provides:

* Custom User model with email verification
* Role-based access control
* Account security features (lockout policy)
* Profile management
* Authentication workflows

Models
------

.. automodule:: accounts.models
   :members:
   :undoc-members:
   :show-inheritance:

User Model
---------

The custom User model extends Django's AbstractUser with SEIM-specific features:

.. autoclass:: accounts.models.User
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Email Verification**: Users must verify their email before accessing the system
* **Account Lockout**: Automatic lockout after 5 failed login attempts
* **Role Management**: Many-to-many relationship with roles
* **Profile Integration**: One-to-one relationship with Profile model

Example Usage:

.. code-block:: python

    from accounts.models import User, Profile, Role
    
    # Create a new user
    user = User.objects.create_user(
        username='john.doe',
        email='john.doe@university.edu',
        password='secure_password'
    )
    
    # Add roles
    student_role = Role.objects.get(name='student')
    user.roles.add(student_role)
    
    # Create profile
    profile = Profile.objects.create(
        user=user,
        gpa=3.5,
        language='English'
    )
    
    # Check if account is locked
    if user.is_locked_out():
        print("Account is locked")
    
    # Generate email verification token
    token = user.generate_email_verification_token()

Profile Model
------------

The Profile model stores additional user information:

.. autoclass:: accounts.models.Profile
   :members:
   :undoc-members:
   :show-inheritance:

Role and Permission Models
-------------------------

.. autoclass:: accounts.models.Role
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: accounts.models.Permission
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: accounts.services
   :members:
   :undoc-members:
   :show-inheritance:

AccountService
-------------

The AccountService handles user registration, verification, and account management:

.. autoclass:: accounts.services.AccountService
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage:

.. code-block:: python

    from accounts.services import AccountService
    
    # Register a new user
    user = AccountService.register_user(
        username='jane.smith',
        email='jane.smith@university.edu',
        password='secure_password',
        first_name='Jane',
        last_name='Smith'
    )
    
    # Verify email
    AccountService.verify_email(token)
    
    # Reset password
    AccountService.send_password_reset_email(email)

Views
-----

.. automodule:: accounts.views
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: accounts.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Admin Interface
--------------

.. automodule:: accounts.admin
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: accounts.urls
   :members:
   :undoc-members:
   :show-inheritance:

Authentication Workflow
----------------------

1. **Registration**: User registers with institutional email
2. **Email Verification**: User receives verification email
3. **Account Activation**: User clicks verification link
4. **Login**: User can now log in with email/password
5. **Role Assignment**: User is assigned appropriate roles
6. **Profile Creation**: User profile is created with additional info

Security Features
----------------

* **Email Verification**: Required before account activation
* **Account Lockout**: 5 failed attempts = 30-minute lockout
* **Password Requirements**: Enforced minimum security
* **Session Management**: Secure session handling
* **CSRF Protection**: Built-in Django CSRF protection

Business Rules
-------------

* Users must register with institutional email addresses
* Email addresses must be unique across the system
* Users must verify email before accessing the system
* Accounts are locked after 5 failed login attempts
* Password reset tokens expire after 1 hour
* Users can have multiple roles (student, coordinator, admin)

Related Documentation
--------------------

* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for user management
