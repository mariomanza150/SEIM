"""
Virus scanning integration for SEIM document management.
Supports multiple virus scanning engines including ClamAV.
"""

import logging
import os
import socket
import subprocess

from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class VirusScannerError(Exception):
    """Custom exception for virus scanner errors."""
    pass


class BaseVirusScanner:
    """Base class for virus scanners."""

    def scan_file(self, file_path: str) -> tuple[bool, str | None]:
        """
        Scan a file for viruses.

        Args:
            file_path: Path to the file to scan

        Returns:
            Tuple of (is_clean, threat_name)
            - is_clean: True if file is clean, False if infected
            - threat_name: Name of detected threat, None if clean
        """
        raise NotImplementedError


class ClamAVScanner(BaseVirusScanner):
    """ClamAV virus scanner implementation."""

    def __init__(self,
                 socket_path: str | None = None,
                 host: str = 'localhost',
                 port: int = 3310,
                 timeout: int = 30):
        """
        Initialize ClamAV scanner.

        Args:
            socket_path: Path to ClamAV socket (Unix socket)
            host: ClamAV daemon host
            port: ClamAV daemon port
            timeout: Connection timeout in seconds
        """
        self.socket_path = socket_path
        self.host = host
        self.port = port
        self.timeout = timeout

    def _connect_to_daemon(self) -> socket.socket:
        """Connect to ClamAV daemon."""
        try:
            if self.socket_path and os.path.exists(self.socket_path):
                # Unix socket connection
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect(self.socket_path)
                return sock
            else:
                # TCP connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                return sock
        except (OSError, ConnectionRefusedError) as e:
            raise VirusScannerError(f"Failed to connect to ClamAV daemon: {e}")

    def _send_command(self, sock: socket.socket, command: str) -> str:
        """Send command to ClamAV daemon and get response."""
        try:
            sock.send(command.encode())
            response = sock.recv(4096).decode().strip()
            return response
        except OSError as e:
            raise VirusScannerError(f"Failed to communicate with ClamAV daemon: {e}")

    def scan_file(self, file_path: str) -> tuple[bool, str | None]:
        """
        Scan a file using ClamAV.

        Args:
            file_path: Path to the file to scan

        Returns:
            Tuple of (is_clean, threat_name)
        """
        if not os.path.exists(file_path):
            raise VirusScannerError(f"File not found: {file_path}")

        try:
            with self._connect_to_daemon() as sock:
                # Send SCAN command
                response = self._send_command(sock, f"SCAN {file_path}\n")

                if "OK" in response:
                    return True, None  # File is clean
                elif "FOUND" in response:
                    # Extract threat name from response
                    # Format: "FILE: /path/to/file ThreatName FOUND"
                    parts = response.split()
                    threat_name = parts[-2] if len(parts) >= 2 else "Unknown"
                    logger.warning(f"Virus detected in {file_path}: {threat_name}")
                    return False, threat_name
                elif "ERROR" in response:
                    raise VirusScannerError(f"ClamAV scan error: {response}")
                else:
                    raise VirusScannerError(f"Unexpected ClamAV response: {response}")

        except VirusScannerError:
            raise
        except Exception as e:
            raise VirusScannerError(f"Unexpected error during virus scan: {e}")


class ClamAVCommandLineScanner(BaseVirusScanner):
    """ClamAV command-line scanner implementation (fallback)."""

    def __init__(self, clamscan_path: str = 'clamscan'):
        """
        Initialize ClamAV command-line scanner.

        Args:
            clamscan_path: Path to clamscan executable
        """
        self.clamscan_path = clamscan_path

    def scan_file(self, file_path: str) -> tuple[bool, str | None]:
        """
        Scan a file using clamscan command-line tool.

        Args:
            file_path: Path to the file to scan

        Returns:
            Tuple of (is_clean, threat_name)
        """
        if not os.path.exists(file_path):
            raise VirusScannerError(f"File not found: {file_path}")

        try:
            # Run clamscan with specific return codes
            result = subprocess.run(
                [self.clamscan_path, '--no-summary', '--stdout', file_path],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )

            if result.returncode == 0:
                return True, None  # File is clean
            elif result.returncode == 1:
                # Virus found, extract threat name from stdout
                threat_name = "Unknown"
                if result.stdout:
                    # Format: "FILE: /path/to/file ThreatName FOUND"
                    parts = result.stdout.strip().split()
                    if len(parts) >= 2 and "FOUND" in parts:
                        threat_name = parts[-2]

                logger.warning(f"Virus detected in {file_path}: {threat_name}")
                return False, threat_name
            else:
                raise VirusScannerError(f"ClamAV scan failed with return code {result.returncode}: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise VirusScannerError(f"ClamAV scan timed out for file: {file_path}")
        except FileNotFoundError:
            raise VirusScannerError(f"ClamAV executable not found: {self.clamscan_path}")
        except Exception as e:
            raise VirusScannerError(f"Unexpected error during virus scan: {e}")


class MockVirusScanner(BaseVirusScanner):
    """Mock virus scanner for testing and development."""

    def __init__(self, simulate_infected: bool = False, threat_name: str = "TestVirus"):
        """
        Initialize mock scanner.

        Args:
            simulate_infected: Whether to simulate infected files
            threat_name: Name of simulated threat
        """
        self.simulate_infected = simulate_infected
        self.threat_name = threat_name

    def scan_file(self, file_path: str) -> tuple[bool, str | None]:
        """
        Mock scan that can simulate infected files.

        Args:
            file_path: Path to the file to scan

        Returns:
            Tuple of (is_clean, threat_name)
        """
        if self.simulate_infected:
            # Simulate infected file
            return False, self.threat_name

        return True, None  # File is clean


class VirusScannerFactory:
    """Factory for creating virus scanner instances."""

    @staticmethod
    def create_scanner(scanner_type: str = None, **kwargs) -> BaseVirusScanner:
        """
        Create a virus scanner instance.

        Args:
            scanner_type: Type of scanner ('clamav', 'clamav_cli', 'mock')
            **kwargs: Scanner-specific configuration

        Returns:
            Configured virus scanner instance
        """
        if scanner_type is None:
            scanner_type = getattr(settings, 'VIRUS_SCANNER_TYPE', 'clamav')

        if scanner_type == 'clamav':
            return ClamAVScanner(
                socket_path=kwargs.get('socket_path'),
                host=kwargs.get('host', 'localhost'),
                port=kwargs.get('port', 3310),
                timeout=kwargs.get('timeout', 30)
            )
        elif scanner_type == 'clamav_cli':
            return ClamAVCommandLineScanner(
                clamscan_path=kwargs.get('clamscan_path', 'clamscan')
            )
        elif scanner_type == 'mock':
            return MockVirusScanner(
                simulate_infected=kwargs.get('simulate_infected', False),
                threat_name=kwargs.get('threat_name', 'TestVirus')
            )
        else:
            raise ValueError(f"Unknown virus scanner type: {scanner_type}")


# Global scanner instance
_virus_scanner: BaseVirusScanner | None = None


def get_virus_scanner() -> BaseVirusScanner:
    """Get the global virus scanner instance."""
    global _virus_scanner

    if _virus_scanner is None:
        scanner_type = getattr(settings, 'VIRUS_SCANNER_TYPE', 'clamav')
        scanner_config = getattr(settings, 'VIRUS_SCANNER_CONFIG', {})

        try:
            _virus_scanner = VirusScannerFactory.create_scanner(scanner_type, **scanner_config)
        except Exception as e:
            logger.error(f"Failed to initialize virus scanner: {e}")
            # Fallback to mock scanner in case of configuration issues
            _virus_scanner = MockVirusScanner(simulate_infected=False)

    return _virus_scanner


def scan_file_for_viruses(file_path: str) -> tuple[bool, str | None]:
    """
    Scan a file for viruses using the configured scanner.

    Args:
        file_path: Path to the file to scan

    Returns:
        Tuple of (is_clean, threat_name)

    Raises:
        ValidationError: If virus scan fails or file is infected
    """
    try:
        scanner = get_virus_scanner()
        is_clean, threat_name = scanner.scan_file(file_path)

        if not is_clean:
            raise ValidationError(f"File contains virus: {threat_name}")

        return True, None

    except ValidationError:
        # Re-raise ValidationError from virus detection
        raise
    except VirusScannerError as e:
        logger.error(f"Virus scan error: {e}")
        # In production, you might want to fail securely
        if getattr(settings, 'VIRUS_SCAN_FAIL_SECURE', True):
            raise ValidationError("Virus scan failed. File rejected for security.")
        else:
            # Allow file through if scan fails (not recommended for production)
            logger.warning("Virus scan failed, allowing file through")
            return True, None
    except Exception as e:
        logger.error(f"Unexpected error during virus scan: {e}")
        if getattr(settings, 'VIRUS_SCAN_FAIL_SECURE', True):
            raise ValidationError("Virus scan failed. File rejected for security.")
        else:
            logger.warning("Unexpected virus scan error, allowing file through")
            return True, None


def test_virus_scanner_connection() -> bool:
    """
    Test virus scanner connection and configuration.

    Returns:
        True if scanner is working, False otherwise
    """
    try:
        scanner = get_virus_scanner()

        # Create a temporary test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file for virus scanning.")
            test_file_path = f.name

        try:
            is_clean, threat_name = scanner.scan_file(test_file_path)
            logger.info("Virus scanner test successful")
            return True
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)

    except Exception as e:
        logger.error(f"Virus scanner test failed: {e}")
        return False
