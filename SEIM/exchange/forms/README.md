# Exchange Forms Module

This directory contains the refactored forms module for the SEIM application. The forms have been organized into logical submodules to improve maintainability and code organization.

## Directory Structure

```
forms/
├── __init__.py                 # Main module exports and backward compatibility
├── authentication_forms.py    # Login and registration forms
├── profile_forms.py           # User profile management forms
├── exchange_forms.py          # Exchange application forms
├── form_choices.py            # Reusable choice constants
├── form_widgets.py            # Bootstrap-styled widget configurations
├── form_utils.py              # Utility functions for forms
└── README.md                  # This documentation file
```

## Module Overview

### authentication_forms.py
Contains forms related to user authentication:
- `LoginForm`: Custom login form with Bootstrap styling
- `RegistrationForm`: User registration with profile creation

### profile_forms.py
Contains forms for user profile management:
- `UserProfileForm`: Form for updating user profile information

### exchange_forms.py
Contains forms for exchange applications:
- `ExchangeForm`: Comprehensive form for creating/editing exchange applications

### form_choices.py
Provides reusable choice constants:
- `ACADEMIC_LEVEL_CHOICES`: Academic level options
- `COUNTRY_CHOICES`: Country selection options
- `CURRENT_YEAR_CHOICES`: Academic year options

### form_widgets.py
Provides Bootstrap-styled widget configurations:
- `BootstrapWidgets`: Collection of pre-configured widgets
- `COMMON_WIDGETS`: Dictionary of commonly used widgets

### form_utils.py
Provides utility functions:
- `update_if_not_empty()`: Update model attributes conditionally
- `apply_bootstrap_styling()`: Apply Bootstrap classes to form fields
- `validate_word_count()`: Validate text word count requirements
- `validate_date_range()`: Validate date range logic
- `populate_user_fields()`: Pre-populate form fields with user data

## Usage Examples

### Basic Import (Backward Compatible)
```python
from exchange.forms import LoginForm, RegistrationForm, UserProfileForm, ExchangeForm
```

### Advanced Usage with Helpers
```python
from exchange.forms import ExchangeForm
from exchange.forms.form_choices import COUNTRY_CHOICES
from exchange.forms.form_widgets import BootstrapWidgets
from exchange.forms.form_utils import validate_word_count
```

### Creating Custom Forms
```python
from django import forms
from exchange.forms.form_widgets import BootstrapWidgets
from exchange.forms.form_choices import ACADEMIC_LEVEL_CHOICES

class CustomForm(forms.Form):
    name = forms.CharField(widget=BootstrapWidgets.text_input(placeholder='Name'))
    level = forms.ChoiceField(choices=ACADEMIC_LEVEL_CHOICES)
```

## Design Principles

1. **Modularity**: Forms are organized by their primary purpose
2. **Reusability**: Common widgets, choices, and utilities are shared
3. **Consistency**: All forms use Bootstrap styling through helper classes
4. **Backward Compatibility**: Existing imports continue to work
5. **Documentation**: Each module is well-documented with clear docstrings

## Migration Notes

This refactor maintains 100% backward compatibility. All existing imports of:
```python
from exchange.forms import LoginForm, RegistrationForm, UserProfileForm, ExchangeForm
```

Will continue to work without any changes to existing code.

## Testing

After refactoring, ensure all forms work correctly by:
1. Testing all form imports in existing code
2. Verifying form rendering in templates
3. Testing form validation and saving
4. Checking that Bootstrap styling is applied correctly

## Future Enhancements

Consider adding these helper modules in the future:
- `form_mixins.py`: Common form mixin classes
- `form_validators.py`: Custom field validators
- `form_fields.py`: Custom form field types
