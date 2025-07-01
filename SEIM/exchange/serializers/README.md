# Exchange Serializers Module

This directory contains Django REST Framework serializers for the SEIM exchange application, organized into logical modules for better maintainability and code organization.

## Structure

### document_serializers.py
Contains serializers related to document handling:
- `DocumentSerializer`: Handles file uploads, validation, and metadata
- `DocumentVerificationSerializer`: Manages document approval/rejection workflow

### exchange_serializers.py
Contains serializers for exchange applications:
- `ExchangeSerializer`: Main serializer for student exchange applications
- `ExchangeSubmitSerializer`: Handles application submission workflow

### user_serializers.py
Contains user-related serializers:
- `UserSerializer`: Basic user account information
- `UserProfileSerializer`: Extended user profile with institutional details

## Usage

All serializers can be imported either from their specific modules or from the main serializers module:

```python
# Import from specific modules
from exchange.serializers.document_serializers import DocumentSerializer
from exchange.serializers.exchange_serializers import ExchangeSerializer

# Import from main module (backward compatibility)
from exchange.serializers import DocumentSerializer, ExchangeSerializer
```

## Key Features

- **File Validation**: Comprehensive file upload validation with security checks
- **Nested Serialization**: Exchange applications include nested document data
- **Computed Fields**: Dynamic fields for submission status and requirements
- **Workflow Support**: Specialized serializers for approval workflows
- **User Safety**: Phone number validation and role-based field restrictions

## Validation

Each serializer includes appropriate validation:
- File uploads are validated for security and integrity
- Required fields are enforced based on application status
- Role-based permissions are respected
- Phone numbers and contact information are format-validated

## Documentation

All serializers include comprehensive docstrings with:
- Purpose and usage description
- Parameter and return value documentation
- Exception information
- Example usage where appropriate
