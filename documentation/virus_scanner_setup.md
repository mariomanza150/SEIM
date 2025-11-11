# Virus Scanner Setup Guide

This guide explains how to set up and configure virus scanning for the SEIM document management system.

## Overview

SEIM supports multiple virus scanning engines to ensure uploaded documents are safe:

- **ClamAV Daemon** (Recommended for production)
- **ClamAV Command Line** (Fallback option)
- **Mock Scanner** (Development/testing only)

## ClamAV Installation

### Ubuntu/Debian

```bash
# Install ClamAV
sudo apt-get update
sudo apt-get install clamav clamav-daemon clamav-clamdscan

# Update virus definitions
sudo freshclam

# Start and enable the daemon
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon

# Check daemon status
sudo systemctl status clamav-daemon
```

### CentOS/RHEL

```bash
# Install EPEL repository
sudo yum install epel-release

# Install ClamAV
sudo yum install clamav clamav-update

# Update virus definitions
sudo freshclam

# Start and enable the daemon
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon
```

### Docker Setup

Add ClamAV to your `docker-compose.yml`:

```yaml
services:
  clamav:
    image: clamav/clamav:stable
    container_name: seim-clamav
    ports:
      - "3310:3310"
    volumes:
      - clamav_data:/var/lib/clamav
    environment:
      - CLAMAV_NO_FRESHCLAMD=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "clamdscan", "--ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  clamav_data:
```

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Virus Scanner Configuration
VIRUS_SCANNER_TYPE=clamav                    # Options: clamav, clamav_cli, mock
VIRUS_SCANNER_HOST=localhost                 # ClamAV daemon host
VIRUS_SCANNER_PORT=3310                      # ClamAV daemon port
VIRUS_SCANNER_SOCKET_PATH=/var/run/clamav/clamd.ctl  # Unix socket path (optional)
VIRUS_SCANNER_TIMEOUT=30                     # Connection timeout in seconds
VIRUS_SCANNER_CLAMSCAN_PATH=clamscan         # Path to clamscan executable
VIRUS_SCAN_FAIL_SECURE=true                  # Fail securely if scan fails

# For Docker setup
VIRUS_SCANNER_HOST=clamav
VIRUS_SCANNER_PORT=3310
```

### Django Settings

The virus scanner configuration is automatically loaded from environment variables in `seim/settings/base.py`:

```python
# Virus Scanner Configuration
VIRUS_SCANNER_TYPE = env("VIRUS_SCANNER_TYPE", default="mock")
VIRUS_SCANNER_CONFIG = {
    "socket_path": env("VIRUS_SCANNER_SOCKET_PATH", default=None),
    "host": env("VIRUS_SCANNER_HOST", default="localhost"),
    "port": env.int("VIRUS_SCANNER_PORT", default=3310),
    "timeout": env.int("VIRUS_SCANNER_TIMEOUT", default=30),
    "clamscan_path": env("VIRUS_SCANNER_CLAMSCAN_PATH", default="clamscan"),
}
VIRUS_SCAN_FAIL_SECURE = env.bool("VIRUS_SCAN_FAIL_SECURE", default=True)
```

## Testing

### Test Scanner Connection

```bash
# Test from Django shell
python manage.py shell
>>> from documents.virus_scanner import test_virus_scanner_connection
>>> test_virus_scanner_connection()
True
```

### Test File Upload

```bash
# Create a test file
echo "X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*" > eicar.txt

# Try uploading through the web interface
# The file should be rejected as infected
```

### Run Unit Tests

```bash
# Run virus scanner tests
python manage.py test tests.unit.documents.test_virus_scanner -v

# Run all document tests
python manage.py test tests.unit.documents -v
```

## Production Deployment

### Security Considerations

1. **Fail Secure**: Set `VIRUS_SCAN_FAIL_SECURE=true` to reject files when scanning fails
2. **Regular Updates**: Ensure virus definitions are updated regularly
3. **Monitoring**: Monitor scan logs for failures and performance issues
4. **Backup**: Keep ClamAV daemon running and healthy

### Performance Optimization

1. **Async Scanning**: Use Celery tasks for large file scanning
2. **Caching**: Cache scan results for identical files
3. **Timeout**: Set appropriate timeout values for your environment
4. **Resource Limits**: Monitor ClamAV daemon resource usage

### Monitoring

```bash
# Check ClamAV daemon status
sudo systemctl status clamav-daemon

# Check daemon logs
sudo journalctl -u clamav-daemon -f

# Test daemon connectivity
clamdscan --ping

# Check virus definition freshness
sudo freshclam --verbose
```

## Troubleshooting

### Common Issues

#### Daemon Connection Failed

```
VirusScannerError: Failed to connect to ClamAV daemon: [Errno 111] Connection refused
```

**Solutions:**
1. Check if ClamAV daemon is running: `sudo systemctl status clamav-daemon`
2. Verify port configuration: `netstat -tlnp | grep 3310`
3. Check firewall settings
4. For Docker: Ensure containers are on the same network

#### Socket Permission Denied

```
VirusScannerError: Failed to connect to ClamAV daemon: [Errno 13] Permission denied
```

**Solutions:**
1. Check socket permissions: `ls -la /var/run/clamav/clamd.ctl`
2. Add user to clamav group: `sudo usermod -a -G clamav $USER`
3. Restart ClamAV daemon: `sudo systemctl restart clamav-daemon`

#### Scan Timeout

```
VirusScannerError: ClamAV scan timed out for file: /path/to/file
```

**Solutions:**
1. Increase timeout: `VIRUS_SCANNER_TIMEOUT=60`
2. Check file size limits
3. Monitor ClamAV daemon performance
4. Consider using async scanning for large files

### Logging

Enable detailed logging for troubleshooting:

```python
# In Django settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'virus_scanner.log',
        },
    },
    'loggers': {
        'documents.virus_scanner': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Development Setup

For development and testing, use the mock scanner:

```bash
# .env file for development
VIRUS_SCANNER_TYPE=mock
VIRUS_SCANNER_SIMULATE_INFECTED=false
```

This allows development without requiring ClamAV installation while still testing the integration code.

## API Integration

The virus scanner is automatically integrated into the document upload workflow:

1. **File Upload**: Document is uploaded via API
2. **Validation**: File type and size are validated
3. **Virus Scan**: File is scanned for viruses
4. **Storage**: Clean files are stored, infected files are rejected
5. **Notification**: Users are notified of scan results

### Manual Scanning

You can also scan files programmatically:

```python
from documents.virus_scanner import scan_file_for_viruses

try:
    is_clean, threat_name = scan_file_for_viruses("/path/to/file.pdf")
    if is_clean:
        print("File is clean")
    else:
        print(f"File is infected: {threat_name}")
except ValidationError as e:
    print(f"Scan failed: {e}")
```
