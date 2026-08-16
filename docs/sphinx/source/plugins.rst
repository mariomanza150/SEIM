Plugins Module
=============

The plugins module provides a modular plugin system for extending SEIM functionality.

Overview
--------

The plugins module provides:

* Plugin architecture and management
* Dynamic plugin loading and registration
* Plugin configuration and settings
* Plugin lifecycle management
* Extension points and hooks
* Plugin development framework

Models
------

.. automodule:: plugins.models
   :members:
   :undoc-members:
   :show-inheritance:

Plugin Model
-----------

The Plugin model represents installed plugins:

.. autoclass:: plugins.models.Plugin
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **Plugin Metadata**: Name, version, description, author
* **Configuration**: JSON-based plugin configuration
* **Status Management**: Active/inactive plugin states
* **Dependencies**: Plugin dependency management
* **Settings**: Plugin-specific settings storage

Example Usage:

.. code-block:: python

    from plugins.models import Plugin
    
    # Create a new plugin
    plugin = Plugin.objects.create(
        name='custom_notifications',
        version='1.0.0',
        description='Custom notification system',
        author='SEIM Team',
        is_active=True,
        config={
            'email_templates': True,
            'sms_notifications': False,
            'webhook_url': 'https://api.example.com/webhook'
        }
    )
    
    # Check plugin status
    if plugin.is_active:
        print(f"Plugin {plugin.name} is active")

PluginHook Model
---------------

.. autoclass:: plugins.models.PluginHook
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: plugins.services
   :members:
   :undoc-members:
   :show-inheritance:

PluginManager
------------

The PluginManager handles all plugin operations:

.. autoclass:: plugins.services.PluginManager
   :members:
   :undoc-members:
   :show-inheritance:

Key Methods:

* **load_plugins()**: Load and register all active plugins
* **install_plugin()**: Install a new plugin
* **uninstall_plugin()**: Remove a plugin
* **enable_plugin()**: Activate a plugin
* **disable_plugin()**: Deactivate a plugin
* **get_plugin()**: Get plugin by name
* **execute_hook()**: Execute plugin hooks

Example Usage:

.. code-block:: python

    from plugins.services import PluginManager
    
    # Initialize plugin manager
    plugin_manager = PluginManager()
    
    # Load all active plugins
    plugin_manager.load_plugins()
    
    # Install a new plugin
    plugin_manager.install_plugin('custom_notifications', {
        'version': '1.0.0',
        'description': 'Custom notification system',
        'author': 'SEIM Team'
    })
    
    # Execute a hook
    result = plugin_manager.execute_hook('application_submitted', {
        'application': application,
        'user': user
    })

Views
-----

.. automodule:: plugins.views
   :members:
   :undoc-members:
   :show-inheritance:

Admin Interface
--------------

.. automodule:: plugins.admin
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: plugins.urls
   :members:
   :undoc-members:
   :show-inheritance:

Plugin Architecture
------------------

SEIM uses a modular plugin architecture:

**Plugin Structure:**

.. code-block:: python

    # plugins/custom_notifications/__init__.py
    from .plugin import CustomNotificationsPlugin
    
    __version__ = '1.0.0'
    __author__ = 'SEIM Team'
    __description__ = 'Custom notification system'
    
    plugin = CustomNotificationsPlugin()

**Plugin Class:**

.. code-block:: python

    # plugins/custom_notifications/plugin.py
    from plugins.base import BasePlugin
    
    class CustomNotificationsPlugin(BasePlugin):
        name = 'custom_notifications'
        version = '1.0.0'
        description = 'Custom notification system'
        author = 'SEIM Team'
        
        def __init__(self):
            super().__init__()
            self.hooks = {
                'application_submitted': self.on_application_submitted,
                'document_uploaded': self.on_document_uploaded
            }
        
        def install(self):
            """Install the plugin."""
            # Create required models
            # Set up configurations
            # Register hooks
            pass
        
        def uninstall(self):
            """Uninstall the plugin."""
            # Clean up models
            # Remove configurations
            # Unregister hooks
            pass
        
        def on_application_submitted(self, context):
            """Handle application submission."""
            application = context['application']
            user = context['user']
            
            # Send custom notification
            self.send_custom_notification(application, user)
        
        def on_document_uploaded(self, context):
            """Handle document upload."""
            document = context['document']
            
            # Process document
            self.process_document(document)
        
        def send_custom_notification(self, application, user):
            """Send custom notification."""
            # Custom notification logic
            pass
        
        def process_document(self, document):
            """Process uploaded document."""
            # Custom document processing
            pass

Plugin Hooks
-----------

SEIM provides several extension points through hooks:

**Available Hooks:**

* **application_submitted**: When application is submitted
* **application_status_changed**: When application status changes
* **document_uploaded**: When document is uploaded
* **user_registered**: When new user registers
* **user_logged_in**: When user logs in
* **email_sent**: When email is sent
* **report_generated**: When report is generated

**Hook Implementation:**

.. code-block:: python

    # Example hook implementation
    def on_application_submitted(self, context):
        """Custom hook for application submission."""
        application = context['application']
        user = context['user']
        
        # Custom logic here
        if application.program.name == 'Erasmus+':
            self.send_erasmus_notification(application, user)
    
    def send_erasmus_notification(self, application, user):
        """Send Erasmus-specific notification."""
        # Custom notification logic
        pass

Plugin Configuration
-------------------

Plugins can be configured through the admin interface:

**Configuration Schema:**

.. code-block:: json

    {
        "email_templates": {
            "type": "boolean",
            "default": true,
            "description": "Enable custom email templates"
        },
        "sms_notifications": {
            "type": "boolean",
            "default": false,
            "description": "Enable SMS notifications"
        },
        "webhook_url": {
            "type": "string",
            "default": "",
            "description": "Webhook URL for notifications"
        },
        "notification_types": {
            "type": "array",
            "default": ["application_submitted", "status_changed"],
            "description": "Types of notifications to handle"
        }
    }

**Configuration Access:**

.. code-block:: python

    class CustomNotificationsPlugin(BasePlugin):
        def get_config(self, key, default=None):
            """Get plugin configuration."""
            return self.config.get(key, default)
        
        def set_config(self, key, value):
            """Set plugin configuration."""
            self.config[key] = value
            self.save()
        
        def is_feature_enabled(self, feature):
            """Check if feature is enabled."""
            return self.get_config(feature, False)

Plugin Development
-----------------

**Creating a New Plugin:**

1. **Create Plugin Directory:**

.. code-block:: bash

    mkdir -p plugins/my_plugin
    touch plugins/my_plugin/__init__.py
    touch plugins/my_plugin/plugin.py
    touch plugins/my_plugin/models.py
    touch plugins/my_plugin/views.py
    touch plugins/my_plugin/admin.py
    touch plugins/my_plugin/urls.py

2. **Define Plugin Class:**

.. code-block:: python

    # plugins/my_plugin/plugin.py
    from plugins.base import BasePlugin
    
    class MyPlugin(BasePlugin):
        name = 'my_plugin'
        version = '1.0.0'
        description = 'My custom plugin'
        author = 'Your Name'
        
        def install(self):
            """Install the plugin."""
            # Create models
            from .models import MyPluginModel
            # Set up configurations
            # Register hooks
            pass
        
        def uninstall(self):
            """Uninstall the plugin."""
            # Clean up
            pass

3. **Define Models:**

.. code-block:: python

    # plugins/my_plugin/models.py
    from django.db import models
    from core.models import TimeStampedModel, UUIDModel
    
    class MyPluginModel(UUIDModel, TimeStampedModel):
        name = models.CharField(max_length=100)
        description = models.TextField()
        
        class Meta:
            app_label = 'plugins'

4. **Define Views:**

.. code-block:: python

    # plugins/my_plugin/views.py
    from django.views.generic import ListView
    from .models import MyPluginModel
    
    class MyPluginListView(ListView):
        model = MyPluginModel
        template_name = 'plugins/my_plugin/list.html'
        context_object_name = 'items'

5. **Define URLs:**

.. code-block:: python

    # plugins/my_plugin/urls.py
    from django.urls import path
    from .views import MyPluginListView
    
    app_name = 'my_plugin'
    
    urlpatterns = [
        path('list/', MyPluginListView.as_view(), name='list'),
    ]

6. **Register Plugin:**

.. code-block:: python

    # plugins/my_plugin/__init__.py
    from .plugin import MyPlugin
    
    __version__ = '1.0.0'
    __author__ = 'Your Name'
    __description__ = 'My custom plugin'
    
    plugin = MyPlugin()

Plugin Testing
-------------

**Unit Testing:**

.. code-block:: python

    # plugins/my_plugin/tests.py
    from django.test import TestCase
    from plugins.services import PluginManager
    from .plugin import MyPlugin
    
    class MyPluginTestCase(TestCase):
        def setUp(self):
            self.plugin_manager = PluginManager()
            self.plugin = MyPlugin()
        
        def test_plugin_installation(self):
            """Test plugin installation."""
            self.plugin.install()
            self.assertTrue(self.plugin.is_installed())
        
        def test_plugin_uninstallation(self):
            """Test plugin uninstallation."""
            self.plugin.install()
            self.plugin.uninstall()
            self.assertFalse(self.plugin.is_installed())
        
        def test_hook_execution(self):
            """Test hook execution."""
            result = self.plugin.execute_hook('test_hook', {'data': 'test'})
            self.assertIsNotNone(result)

**Integration Testing:**

.. code-block:: python

    # plugins/my_plugin/test_integration.py
    from django.test import TestCase, Client
    from django.urls import reverse
    
    class MyPluginIntegrationTestCase(TestCase):
        def setUp(self):
            self.client = Client()
            self.user = User.objects.create_user(
                username='testuser',
                password='testpass123'
            )
        
        def test_plugin_view(self):
            """Test plugin view."""
            self.client.force_login(self.user)
            response = self.client.get(reverse('my_plugin:list'))
            self.assertEqual(response.status_code, 200)

Plugin Security
--------------

**Security Considerations:**

* **Input Validation**: All plugin inputs must be validated
* **Permission Checks**: Plugins must respect user permissions
* **Data Isolation**: Plugin data must be isolated
* **Error Handling**: Plugins must handle errors gracefully
* **Audit Logging**: Plugin actions must be logged

**Security Example:**

.. code-block:: python

    class SecurePlugin(BasePlugin):
        def execute_hook(self, hook_name, context):
            """Execute hook with security checks."""
            # Validate context
            if not self.validate_context(context):
                raise ValueError("Invalid context")
            
            # Check permissions
            if not self.check_permissions(context):
                raise PermissionError("Insufficient permissions")
            
            # Execute hook
            try:
                result = super().execute_hook(hook_name, context)
                self.log_action(hook_name, context, result)
                return result
            except Exception as e:
                self.log_error(hook_name, context, e)
                raise

Plugin Performance
-----------------

**Performance Optimization:**

* **Lazy Loading**: Load plugins only when needed
* **Caching**: Cache plugin configurations and results
* **Async Processing**: Use async for long-running operations
* **Resource Management**: Properly manage plugin resources

**Performance Example:**

.. code-block:: python

    from django.core.cache import cache
    
    class OptimizedPlugin(BasePlugin):
        def get_config(self, key, default=None):
            """Get cached configuration."""
            cache_key = f"plugin_config_{self.name}_{key}"
            result = cache.get(cache_key)
            
            if result is None:
                result = super().get_config(key, default)
                cache.set(cache_key, result, 300)  # Cache for 5 minutes
            
            return result
        
        async def async_hook(self, hook_name, context):
            """Execute hook asynchronously."""
            # Async hook execution
            pass

Business Rules
-------------

* Plugins must be compatible with SEIM version
* Plugin installation requires admin privileges
* Plugins must follow SEIM coding standards
* Plugin updates must be backward compatible
* Plugin uninstallation must clean up all data
* Plugin hooks must be documented
* Plugin configuration must be validated
* Plugin errors must not affect core system
* Plugin performance must be monitored
* Plugin security must be audited

Related Documentation
--------------------

* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for plugin management
* :doc:`business_rules` - Business logic and validation rules
* :doc:`development` - Plugin development guide
* :doc:`security` - Security best practices 