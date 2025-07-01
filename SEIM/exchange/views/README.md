# Exchange Views Package

This package contains the modular view files for the SEIM exchange application.

## Structure

The views have been split into logical groups for better maintainability:

### `dashboard_views.py`
- `dashboard()` - Main dashboard view with statistics and overview

### `exchange_views.py`
- `exchange_list()` - List exchanges with filtering and searching
- `exchange_detail()` - Show detailed exchange information
- `create_exchange()` - Create new exchange applications
- `edit_exchange()` - Edit existing exchange applications
- `exchange_list_api()` - JSON API endpoint for exchange data

### `workflow_views.py`
- `submit_exchange()` - Submit an exchange application
- `review_exchange()` - Mark exchange as under review
- `approve_exchange()` - Approve an exchange application
- `reject_exchange()` - Reject an exchange application  
- `complete_exchange()` - Mark exchange as completed

### `admin_views.py`
- `pending_approvals()` - Administrative view for pending applications

### `notification_views.py`
- `notification_list()` - List user notifications
- `notification_settings()` - Manage notification preferences

## Backward Compatibility

The main `views.py` file imports all functions from this package, maintaining full backward compatibility with existing code that imports from `exchange.views`.

## Benefits of This Structure

1. **Separation of Concerns** - Each file has a focused responsibility
2. **Easier Maintenance** - Smaller files are easier to understand and modify
3. **Better Testing** - Individual view groups can be tested independently
4. **Team Development** - Multiple developers can work on different view files
5. **Code Reusability** - Related views are grouped together logically

## Import Usage

You can import views in these ways:

```python
# Import from the package (recommended for new code)
from exchange.views.dashboard_views import dashboard
from exchange.views.exchange_views import exchange_list

# Import from main views module (backward compatibility)
from exchange.views import dashboard, exchange_list

# Import everything (legacy compatibility)
from exchange.views import *
```
