"""
Storage configuration for SGII application.
"""

import os

# Base directories
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/app/media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.getenv('STATIC_ROOT', '/app/staticfiles')
STATIC_URL = '/static/'

# Storage backend selection
USE_S3 = os.getenv('USE_S3', 'False').lower() == 'true'

if USE_S3:
    # AWS S3 Storage settings
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    
    # AWS credentials
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    
    # S3 configuration
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_ENCRYPTION = True
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_VERIFY = True
    AWS_S3_USE_SSL = True
    
    # S3 URLs
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # S3 storage classes
    AWS_STORAGE_CLASSES = {
        'STANDARD': 'STANDARD',
        'REDUCED_REDUNDANCY': 'REDUCED_REDUNDANCY',
        'STANDARD_IA': 'STANDARD_IA',
        'ONEZONE_IA': 'ONEZONE_IA',
        'INTELLIGENT_TIERING': 'INTELLIGENT_TIERING',
        'GLACIER': 'GLACIER',
        'DEEP_ARCHIVE': 'DEEP_ARCHIVE',
    }
    AWS_S3_STORAGE_CLASS = 'STANDARD'
    
else:
    # Local file storage settings
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# File upload settings
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

# Directory structure for uploaded files
UPLOAD_DIRECTORIES = {
    'documents': 'exchanges/documents',
    'profile_pictures': 'users/profiles',
    'exports': 'exports',
    'imports': 'imports',
    'temp': 'temp',
}

# Backup storage settings
BACKUP_STORAGE_ENABLED = os.getenv('BACKUP_STORAGE_ENABLED', 'False').lower() == 'true'
BACKUP_STORAGE_LOCATION = os.getenv('BACKUP_STORAGE_LOCATION', '/app/backups')
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))

# Cache storage for static files
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Additional static file directories
STATICFILES_DIRS = [
    # Add any additional static file directories here
]

# WhiteNoise configuration
WHITENOISE_AUTOREFRESH = os.getenv('DJANGO_ENV', 'production') == 'development'
WHITENOISE_USE_FINDERS = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']
WHITENOISE_COMPRESS_OFFLINE = True
WHITENOISE_COMPRESSION_QUALITY = 80

# File validation settings
ALLOWED_FILE_EXTENSIONS = {
    'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.rtf', '.odt'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    'archives': ['.zip', '.tar', '.gz', '.7z', '.rar'],
}

MAX_FILE_SIZES = {
    'documents': 20 * 1024 * 1024,  # 20 MB
    'images': 5 * 1024 * 1024,      # 5 MB
    'archives': 50 * 1024 * 1024,   # 50 MB
    'default': 10 * 1024 * 1024,    # 10 MB
}

# Temporary file cleanup
FILE_UPLOAD_TEMP_DIR = os.path.join(MEDIA_ROOT, 'temp')
TEMP_FILE_EXPIRY_HOURS = 24

# CDN configuration (optional)
USE_CDN = os.getenv('USE_CDN', 'False').lower() == 'true'
CDN_URL = os.getenv('CDN_URL', '')
CDN_STATIC_URL = f'{CDN_URL}/static/' if USE_CDN else STATIC_URL
CDN_MEDIA_URL = f'{CDN_URL}/media/' if USE_CDN else MEDIA_URL
