# Media Storage Quick Start Guide

## Overview

The SEIM media storage system provides secure file uploads with integrity tracking, virus scanning, and cloud storage support.

## Quick Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Start services**:
   ```bash
   # Start Django server
   python manage.py runserver
   
   # Start Celery worker (in another terminal)
   celery -A seim worker -l info
   
   # Start Celery beat (in another terminal)
   celery -A seim beat -l info
   ```

## Basic Usage

### Upload a document (API)

```python
import requests

# Get JWT token
response = requests.post('http://localhost:8000/api/auth/token/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['access']

# Upload file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/documents/',
        headers={'Authorization': f'Bearer {token}'},
        files={'file': f},
        data={
            'exchange': 1,
            'category': 'passport',
            'description': 'Passport copy'
        }
    )
```

### Download a document

```python
response = requests.get(
    'http://localhost:8000/api/documents/1/download/',
    headers={'Authorization': f'Bearer {token}'}
)

# Save file
with open('downloaded_file.pdf', 'wb') as f:
    f.write(response.content)
```

### Check file integrity

```bash
python manage.py check_file_integrity --verbose
```

### Scan for malware

```bash
python manage.py scan_documents --unscanned-only
```

## Configuration

### Local Storage (default)

No additional configuration needed.

### AWS S3

Add to environment:
```bash
FILE_STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
```

### Azure Blob Storage

Add to environment:
```bash
FILE_STORAGE_TYPE=azure
AZURE_ACCOUNT_NAME=your-account
AZURE_ACCOUNT_KEY=your-key
AZURE_CONTAINER=media
```

## Security Features

- File type validation (extensions and MIME types)
- File size limits (configurable)
- Malicious content detection
- SHA-256 checksum tracking
- Virus scanning (ClamAV integration)
- Access control and permissions

## Troubleshooting

### File upload fails
- Check file size limits
- Verify allowed file types
- Check user permissions

### Integrity check fails
- File may be corrupted
- Run `python manage.py check_file_integrity --fix`

### Virus scanner not available
- Install ClamAV: `sudo apt-get install clamav clamav-daemon`
- Start daemon: `sudo systemctl start clamav-daemon`

## API Endpoints

- `POST /api/documents/` - Upload document
- `GET /api/documents/` - List documents
- `GET /api/documents/{id}/` - Document details
- `GET /api/documents/{id}/download/` - Download file
- `POST /api/documents/{id}/verify/` - Verify document (staff)
- `POST /api/documents/{id}/check_integrity/` - Check integrity

## Admin Interface

Access at: `http://localhost:8000/admin/`

Features:
- View all documents
- Verify documents
- Scan for viruses
- Check integrity
- Manage exchanges

## Best Practices

1. Always validate files before storing
2. Run integrity checks regularly
3. Monitor virus scan results
4. Set appropriate file expiration dates
5. Use cloud storage for production
6. Enable SSL/TLS in production
7. Regularly backup file metadata

## Support

For issues or questions:
1. Check the logs in `logs/django.log`
2. Review Celery worker output
3. Verify environment configuration
4. Check database migrations are up to date

For detailed documentation, see the full implementation report.
