Documents Module
===============

The documents module handles file upload, validation, and management in SEIM.

Overview
--------

The documents module provides:

* Secure file upload and storage
* Document type configuration
* File validation and virus scanning
* Document replacement workflow
* Resubmission request handling
* Document comments and validation

Models
------

.. automodule:: documents.models
   :members:
   :undoc-members:
   :show-inheritance:

Document Model
-------------

The Document model represents uploaded files associated with applications:

.. autoclass:: documents.models.Document
   :members:
   :undoc-members:
   :show-inheritance:

Key Features:

* **File Storage**: Secure file storage with path management
* **Validation Status**: Track document validation state
* **Resubmission Support**: Handle document replacement requests
* **Comments**: Coordinator comments on documents
* **Audit Trail**: Track document changes and updates

Example Usage:

.. code-block:: python

    from documents.models import Document, DocumentType
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    # Create document type
    doc_type = DocumentType.objects.create(
        name='Transcript',
        description='Official academic transcript',
        required=True,
        allowed_extensions=['pdf', 'jpg', 'png'],
        max_file_size=10485760  # 10MB
    )
    
    # Upload document
    file_content = b'fake file content'
    uploaded_file = SimpleUploadedFile(
        'transcript.pdf',
        file_content,
        content_type='application/pdf'
    )
    
    document = Document.objects.create(
        application=application,
        document_type=doc_type,
        file=uploaded_file,
        uploaded_by=student
    )

DocumentType Model
-----------------

.. autoclass:: documents.models.DocumentType
   :members:
   :undoc-members:
   :show-inheritance:

DocumentComment Model
--------------------

.. autoclass:: documents.models.DocumentComment
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: documents.services
   :members:
   :undoc-members:
   :show-inheritance:

DocumentService
--------------

The DocumentService handles all document-related operations:

.. autoclass:: documents.services.DocumentService
   :members:
   :undoc-members:
   :show-inheritance:

Key Methods:

* **upload_document()**: Upload and validate new document
* **replace_document()**: Replace existing document
* **validate_document()**: Mark document as validated
* **request_resubmission()**: Request document resubmission
* **add_comment()**: Add comment to document

Example Usage:

.. code-block:: python

    from documents.services import DocumentService
    
    # Upload document
    try:
        document = DocumentService.upload_document(
            application=application,
            document_type=doc_type,
            file=uploaded_file,
            uploaded_by=student
        )
        print("Document uploaded successfully")
    except ValueError as e:
        print(f"Upload failed: {e}")
    
    # Request resubmission
    DocumentService.request_resubmission(
        document=document,
        requested_by=coordinator,
        reason="Document is not clear enough"
    )
    
    # Validate document
    DocumentService.validate_document(
        document=document,
        validated_by=coordinator,
        notes="Document is valid and complete"
    )

Views
-----

.. automodule:: documents.views
   :members:
   :undoc-members:
   :show-inheritance:

Serializers
----------

.. automodule:: documents.serializers
   :members:
   :undoc-members:
   :show-inheritance:

Admin Interface
--------------

.. automodule:: documents.admin
   :members:
   :undoc-members:
   :show-inheritance:

URLs
----

.. automodule:: documents.urls
   :members:
   :undoc-members:
   :show-inheritance:

File Upload Workflow
-------------------

The document upload workflow follows these steps:

.. mermaid::

    flowchart TD
        A[Student Uploads File] --> B[File Validation]
        B --> C{Validation Pass?}
        C -->|Yes| D[Store File]
        C -->|No| E[Return Error]
        D --> F[Create Document Record]
        F --> G[Notify Coordinator]
        G --> H[Coordinator Reviews]
        H --> I{Document Valid?}
        I -->|Yes| J[Mark as Validated]
        I -->|No| K[Request Resubmission]
        K --> L[Student Replaces File]
        L --> B

File Validation
--------------

Documents undergo several validation checks:

1. **File Type**: Only allowed extensions are accepted
2. **File Size**: Maximum file size enforcement
3. **Virus Scan**: Basic virus scanning (stub implementation)
4. **Content Validation**: File integrity checks

Supported File Types:

* **PDF**: Documents, transcripts, certificates
* **Images**: JPG, PNG for scanned documents
* **Office Documents**: DOC, DOCX for additional documents

Example Validation Configuration:

.. code-block:: python

    # Document type configuration
    transcript_type = DocumentType.objects.create(
        name='Academic Transcript',
        description='Official university transcript',
        required=True,
        allowed_extensions=['pdf'],
        max_file_size=5242880,  # 5MB
        validation_rules={
            'min_pages': 1,
            'max_pages': 10,
            'require_text': True
        }
    )

Document Replacement Rules
-------------------------

Document replacement follows specific business rules:

* **Before Submission**: Students can freely replace documents
* **After Submission**: Only if resubmission is requested
* **Admin Override**: Admins can override restrictions
* **Maximum Resubmissions**: Limited to 3 requests per document

Example Replacement Workflow:

.. code-block:: python

    # Student replaces document before submission
    if application.status.name == 'draft':
        DocumentService.replace_document(
            document=document,
            new_file=new_uploaded_file,
            replaced_by=student
        )
    
    # Coordinator requests resubmission
    DocumentService.request_resubmission(
        document=document,
        requested_by=coordinator,
        reason="Document is not legible"
    )
    
    # Student replaces after resubmission request
    if document.resubmission_requested:
        DocumentService.replace_document(
            document=document,
            new_file=new_uploaded_file,
            replaced_by=student
        )

Security Features
----------------

* **File Type Validation**: Strict file type checking
* **Size Limits**: Enforced maximum file sizes
* **Path Sanitization**: Secure file path handling
* **Access Control**: Role-based document access
* **Audit Logging**: All document operations logged

Storage Configuration
--------------------

Documents are stored using Django's file storage system:

* **Development**: Local file system storage
* **Production**: AWS S3 or similar cloud storage
* **Backup**: Regular backup of document files
* **Retention**: Documents retained for audit purposes

Example Storage Configuration:

.. code-block:: python

    # settings.py
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
    # For production with S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = 'your-access-key'
    AWS_SECRET_ACCESS_KEY = 'your-secret-key'
    AWS_STORAGE_BUCKET_NAME = 'seim-documents'
    AWS_S3_REGION_NAME = 'us-east-1'

Business Rules
-------------

* Only verified users can upload documents
* Documents must be associated with specific applications
* File size limit: 10MB per document
* Allowed file types: PDF, DOC, DOCX, JPG, PNG
* Documents are scanned for viruses (stub implementation)
* Document types are configured by admins
* Each program can have different required document types
* Documents can only be replaced if resubmission is requested
* Maximum 3 resubmission requests per document
* All document operations are logged for audit purposes

Related Documentation
--------------------

* :doc:`business_rules` - Business logic and validation rules
* :doc:`architecture` - System architecture overview
* :doc:`api` - API endpoints for document management
* :doc:`exchange` - Application workflow integration 