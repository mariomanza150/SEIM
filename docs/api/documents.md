# Documents API

The Documents API handles file uploads, storage, and retrieval for exchange applications.

## Document Model

```json
{
  "id": 1,
  "exchange": 1,
  "document_type": "passport",
  "title": "Passport Scan",
  "description": "Scanned copy of passport",
  "file": "/media/documents/exchange_1/passport_abc123.pdf",
  "file_name": "passport.pdf",
  "file_size": 1048576,
  "file_hash": "sha256:abcd1234...",
  "uploaded_at": "2025-01-15T11:00:00Z",
  "uploaded_by": 1,
  "is_valid": true,
  "validation_errors": null
}
```

## Document Types

| Type | Description | Required |
|------|-------------|----------|
| `passport` | Passport or ID document | Yes |
| `transcript` | Academic transcript | Yes |
| `motivation_letter` | Letter of motivation | Yes |
| `recommendation` | Letter of recommendation | Yes |
| `language_certificate` | Language proficiency certificate | No |
| `medical_certificate` | Medical fitness certificate | No |
| `financial_statement` | Proof of financial support | No |
| `photo` | Passport photo | Yes |
| `acceptance_letter` | Generated acceptance letter | Auto |
| `progress_report` | Generated progress report | Auto |
| `grade_sheet` | Generated grade sheet | Auto |

## Endpoints

### List Documents

Get all documents for an exchange or user.

**Endpoint:** `GET /api/documents/`

**Query Parameters:**
- `exchange`: Filter by exchange ID
- `document_type`: Filter by document type
- `user`: Filter by user (managers only)
- `is_valid`: Filter by validation status

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "document_type": "passport",
      "title": "Passport Scan",
      // ... full document object
    }
  ]
}
```

### Upload Document

Upload a new document.

**Endpoint:** `POST /api/documents/`

**Request:** (multipart/form-data)
```
exchange: 1
document_type: passport
title: Passport Scan
description: Scanned copy of my passport (optional)
file: <binary file data>
```

**Response:**
```json
{
  "id": 1,
  "document_type": "passport",
  "title": "Passport Scan",
  "file_name": "passport.pdf",
  "file_size": 1048576,
  "file_hash": "sha256:abcd1234...",
  "uploaded_at": "2025-01-15T11:00:00Z",
  "is_valid": true
}
```

**Validation:**
- Maximum file size: 10MB (configurable)
- Allowed file types: PDF, JPG, PNG, DOC, DOCX
- File hash is automatically calculated
- Virus scanning (if configured)

### Retrieve Document

Get document details.

**Endpoint:** `GET /api/documents/{id}/`

**Response:**
```json
{
  "id": 1,
  "exchange": 1,
  "document_type": "passport",
  "title": "Passport Scan",
  // ... full document object
}
```

### Download Document

Download the actual file.

**Endpoint:** `GET /api/documents/{id}/download/`

**Response:** Binary file data with appropriate headers

**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="passport.pdf"
Content-Length: 1048576
```

### Delete Document

Delete a document.

**Endpoint:** `DELETE /api/documents/{id}/`

**Response:** `204 No Content`

**Restrictions:**
- Cannot delete generated documents
- Cannot delete if exchange is beyond "submitted" status
- Students can only delete their own documents

### Verify Integrity

Check if a document's file hash matches the stored hash.

**Endpoint:** `POST /api/documents/{id}/verify_integrity/`

**Response:**
```json
{
  "is_valid": true,
  "stored_hash": "sha256:abcd1234...",
  "current_hash": "sha256:abcd1234...",
  "match": true
}
```

## Document Generation

### Generate Document

Generate a PDF document for an exchange.

**Endpoint:** `POST /api/exchanges/{id}/generate_document/`

**Request:**
```json
{
  "document_type": "acceptance_letter"
}
```

**Response:**
```json
{
  "id": 10,
  "document_type": "acceptance_letter",
  "title": "Acceptance Letter - John Doe",
  "file_name": "acceptance_letter_2025_01_15.pdf",
  "generated_at": "2025-01-15T15:00:00Z"
}
```

**Available Types:**
- `acceptance_letter`: Generated when exchange is approved
- `progress_report`: Generated during exchange period
- `grade_sheet`: Generated at exchange completion

### Regenerate Document

Regenerate an existing generated document.

**Endpoint:** `POST /api/documents/{id}/regenerate/`

**Response:**
```json
{
  "id": 10,
  "document_type": "acceptance_letter",
  "title": "Acceptance Letter - John Doe",
  "regenerated_at": "2025-01-15T16:00:00Z",
  "previous_version": 9
}
```

## Bulk Operations

### Bulk Upload

Upload multiple documents at once.

**Endpoint:** `POST /api/documents/bulk_upload/`

**Request:** (multipart/form-data)
```
exchange: 1
files[0][type]: passport
files[0][title]: Passport Scan
files[0][file]: <binary data>
files[1][type]: transcript
files[1][title]: Academic Transcript
files[1][file]: <binary data>
```

**Response:**
```json
{
  "uploaded": [
    {
      "id": 1,
      "document_type": "passport",
      "title": "Passport Scan"
    }
  ],
  "failed": [
    {
      "type": "transcript",
      "error": "File size exceeds limit"
    }
  ]
}
```

### Bulk Download

Download multiple documents as a ZIP file.

**Endpoint:** `POST /api/documents/bulk_download/`

**Request:**
```json
{
  "document_ids": [1, 2, 3]
}
```

**Response:** ZIP file containing all requested documents

## Error Handling

### Upload Errors

```json
{
  "status": "error",
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds 10MB limit",
    "details": {
      "file_size": 15728640,
      "max_size": 10485760
    }
  }
}
```

### File Type Errors

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type not allowed",
    "details": {
      "file_type": "exe",
      "allowed_types": ["pdf", "jpg", "png", "doc", "docx"]
    }
  }
}
```

### Integrity Errors

```json
{
  "status": "error",
  "error": {
    "code": "INTEGRITY_CHECK_FAILED",
    "message": "File hash mismatch",
    "details": {
      "stored_hash": "sha256:abcd1234...",
      "current_hash": "sha256:efgh5678..."
    }
  }
}
```

## Examples

### Python File Upload

```python
import requests

# Upload a document
with open('passport.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/documents/',
        headers={'Authorization': f'Bearer {token}'},
        files={'file': ('passport.pdf', f, 'application/pdf')},
        data={
            'exchange': 1,
            'document_type': 'passport',
            'title': 'Passport Scan'
        }
    )
    
document = response.json()
print(f"Uploaded document ID: {document['id']}")
print(f"File hash: {document['file_hash']}")
```

### JavaScript File Upload with Progress

```javascript
async function uploadDocument(file, exchangeId, documentType) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('exchange', exchangeId);
  formData.append('document_type', documentType);
  formData.append('title', file.name);
  
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        console.log(`Upload progress: ${percentComplete}%`);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error('Upload failed'));
      }
    });
    
    xhr.open('POST', '/api/documents/');
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
}
```

### Verify Document Integrity

```python
import requests

# Verify document integrity
response = requests.post(
    f'http://localhost:8000/api/documents/{document_id}/verify_integrity/',
    headers={'Authorization': f'Bearer {token}'}
)

result = response.json()
if result['match']:
    print("Document integrity verified")
else:
    print("Document may have been tampered with!")
```

## Security Notes

1. **File Validation**: All uploads are validated for type and size
2. **Hash Verification**: SHA256 hashes ensure file integrity
3. **Access Control**: Users can only access their own documents
4. **Virus Scanning**: Optional integration with antivirus
5. **Secure Storage**: Files stored outside web root
6. **Encrypted Transport**: Use HTTPS in production
