"""
Test Virus Scanner Services

Comprehensive tests for virus scanning functionality.
"""

import os
import pytest
import tempfile
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from unittest.mock import MagicMock, patch

from documents.virus_scanner import (
    BaseVirusScanner,
    ClamAVScanner,
    ClamAVCommandLineScanner,
    MockVirusScanner,
    VirusScannerError,
    VirusScannerFactory,
    get_virus_scanner,
    scan_file_for_viruses,
    test_virus_scanner_connection
)


@pytest.mark.django_db
class TestMockVirusScanner(TestCase):
    """Test mock virus scanner."""

    def test_mock_scanner_clean_file(self):
        """Test mock scanner returns clean for normal operation."""
        scanner = MockVirusScanner(simulate_infected=False)
        
        is_clean, threat = scanner.scan_file('/fake/path.txt')
        
        self.assertTrue(is_clean)
        self.assertIsNone(threat)

    def test_mock_scanner_infected_file(self):
        """Test mock scanner can simulate infected files."""
        scanner = MockVirusScanner(simulate_infected=True, threat_name="TestVirus")
        
        is_clean, threat = scanner.scan_file('/fake/path.txt')
        
        self.assertFalse(is_clean)
        self.assertEqual(threat, "TestVirus")

    def test_mock_scanner_custom_threat_name(self):
        """Test mock scanner uses custom threat name."""
        scanner = MockVirusScanner(simulate_infected=True, threat_name="CustomThreat")
        
        is_clean, threat = scanner.scan_file('/any/path')
        
        self.assertEqual(threat, "CustomThreat")

    def test_mock_scanner_default_threat_name(self):
        """Test mock scanner has default threat name."""
        scanner = MockVirusScanner(simulate_infected=True)
        
        is_clean, threat = scanner.scan_file('/path')
        
        self.assertEqual(threat, "TestVirus")


@pytest.mark.django_db
class TestClamAVScanner(TestCase):
    """Test ClamAV scanner."""

    def test_clamav_scanner_initialization(self):
        """Test ClamAV scanner initialization."""
        scanner = ClamAVScanner(
            socket_path='/var/run/clamav/clamd.sock',
            host='localhost',
            port=3310,
            timeout=30
        )
        
        self.assertEqual(scanner.socket_path, '/var/run/clamav/clamd.sock')
        self.assertEqual(scanner.host, 'localhost')
        self.assertEqual(scanner.port, 3310)
        self.assertEqual(scanner.timeout, 30)

    def test_clamav_scanner_default_values(self):
        """Test ClamAV scanner has default values."""
        scanner = ClamAVScanner()
        
        self.assertEqual(scanner.host, 'localhost')
        self.assertEqual(scanner.port, 3310)
        self.assertEqual(scanner.timeout, 30)

    def test_clamav_scanner_file_not_found(self):
        """Test scanning non-existent file raises error."""
        scanner = ClamAVScanner()
        
        with self.assertRaises(VirusScannerError) as context:
            scanner.scan_file('/nonexistent/file.txt')
        
        self.assertIn('File not found', str(context.exception))

    @patch('documents.virus_scanner.socket.socket')
    def test_clamav_scanner_connection_refused(self, mock_socket):
        """Test handling connection refused."""
        mock_socket_instance = MagicMock()
        mock_socket_instance.connect.side_effect = ConnectionRefusedError("Connection refused")
        mock_socket.return_value = mock_socket_instance
        
        scanner = ClamAVScanner()
        
        # Create temp file for testing
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'test content')
            test_file = f.name
        
        try:
            with self.assertRaises(VirusScannerError) as context:
                scanner.scan_file(test_file)
            
            self.assertIn('Failed to connect', str(context.exception))
        finally:
            os.unlink(test_file)


@pytest.mark.django_db
class TestClamAVCommandLineScanner(TestCase):
    """Test ClamAV command-line scanner."""

    def test_clamav_cli_scanner_initialization(self):
        """Test command-line scanner initialization."""
        scanner = ClamAVCommandLineScanner(clamscan_path='/usr/bin/clamscan')
        
        self.assertEqual(scanner.clamscan_path, '/usr/bin/clamscan')

    def test_clamav_cli_scanner_default_path(self):
        """Test command-line scanner has default path."""
        scanner = ClamAVCommandLineScanner()
        
        self.assertEqual(scanner.clamscan_path, 'clamscan')

    def test_clamav_cli_scanner_file_not_found(self):
        """Test scanning non-existent file raises error."""
        scanner = ClamAVCommandLineScanner()
        
        with self.assertRaises(VirusScannerError) as context:
            scanner.scan_file('/nonexistent/file.txt')
        
        self.assertIn('File not found', str(context.exception))

    @patch('documents.virus_scanner.subprocess.run')
    def test_clamav_cli_scanner_clean_file(self, mock_run):
        """Test scanning clean file with CLI."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        scanner = ClamAVCommandLineScanner()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'clean content')
            test_file = f.name
        
        try:
            is_clean, threat = scanner.scan_file(test_file)
            
            self.assertTrue(is_clean)
            self.assertIsNone(threat)
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.subprocess.run')
    def test_clamav_cli_scanner_infected_file(self, mock_run):
        """Test scanning infected file with CLI."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='/path/to/file: Eicar-Test-Signature FOUND',
            stderr=''
        )
        
        scanner = ClamAVCommandLineScanner()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'infected content')
            test_file = f.name
        
        try:
            is_clean, threat = scanner.scan_file(test_file)
            
            self.assertFalse(is_clean)
            self.assertEqual(threat, 'Eicar-Test-Signature')
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.subprocess.run')
    def test_clamav_cli_scanner_timeout(self, mock_run):
        """Test handling scan timeout."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired('clamscan', 60)
        
        scanner = ClamAVCommandLineScanner()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            with self.assertRaises(VirusScannerError) as context:
                scanner.scan_file(test_file)
            
            self.assertIn('timed out', str(context.exception))
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.subprocess.run')
    def test_clamav_cli_scanner_executable_not_found(self, mock_run):
        """Test handling missing clamscan executable."""
        mock_run.side_effect = FileNotFoundError()
        
        scanner = ClamAVCommandLineScanner()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            with self.assertRaises(VirusScannerError) as context:
                scanner.scan_file(test_file)
            
            self.assertIn('executable not found', str(context.exception))
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.subprocess.run')
    def test_clamav_cli_scanner_scan_error(self, mock_run):
        """Test handling scan error."""
        mock_run.return_value = MagicMock(
            returncode=2,
            stdout='',
            stderr='Scan error'
        )
        
        scanner = ClamAVCommandLineScanner()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            with self.assertRaises(VirusScannerError) as context:
                scanner.scan_file(test_file)
            
            self.assertIn('scan failed', str(context.exception))
        finally:
            os.unlink(test_file)


@pytest.mark.django_db
class TestVirusScannerFactory(TestCase):
    """Test virus scanner factory."""

    def test_factory_creates_clamav_scanner(self):
        """Test factory creates ClamAV scanner."""
        scanner = VirusScannerFactory.create_scanner('clamav')
        
        self.assertIsInstance(scanner, ClamAVScanner)

    def test_factory_creates_clamav_cli_scanner(self):
        """Test factory creates ClamAV CLI scanner."""
        scanner = VirusScannerFactory.create_scanner('clamav_cli')
        
        self.assertIsInstance(scanner, ClamAVCommandLineScanner)

    def test_factory_creates_mock_scanner(self):
        """Test factory creates mock scanner."""
        scanner = VirusScannerFactory.create_scanner('mock')
        
        self.assertIsInstance(scanner, MockVirusScanner)

    def test_factory_creates_clamav_with_config(self):
        """Test factory passes configuration to scanner."""
        scanner = VirusScannerFactory.create_scanner(
            'clamav',
            host='example.com',
            port=1234,
            timeout=60
        )
        
        self.assertEqual(scanner.host, 'example.com')
        self.assertEqual(scanner.port, 1234)
        self.assertEqual(scanner.timeout, 60)

    def test_factory_creates_mock_with_config(self):
        """Test factory passes configuration to mock scanner."""
        scanner = VirusScannerFactory.create_scanner(
            'mock',
            simulate_infected=True,
            threat_name='CustomVirus'
        )
        
        self.assertTrue(scanner.simulate_infected)
        self.assertEqual(scanner.threat_name, 'CustomVirus')

    def test_factory_invalid_scanner_type(self):
        """Test factory raises error for invalid type."""
        with self.assertRaises(ValueError) as context:
            VirusScannerFactory.create_scanner('invalid_scanner')
        
        self.assertIn('Unknown virus scanner type', str(context.exception))

    @override_settings(VIRUS_SCANNER_TYPE='mock')
    def test_factory_uses_settings_default(self):
        """Test factory uses default from settings."""
        scanner = VirusScannerFactory.create_scanner()
        
        self.assertIsInstance(scanner, MockVirusScanner)


@pytest.mark.django_db
class TestGetVirusScanner(TestCase):
    """Test get_virus_scanner function."""

    def setUp(self):
        """Clear global scanner before each test."""
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

    def tearDown(self):
        """Clear global scanner after each test."""
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

    @override_settings(VIRUS_SCANNER_TYPE='mock')
    def test_get_virus_scanner_returns_scanner(self):
        """Test get_virus_scanner returns a scanner instance."""
        scanner = get_virus_scanner()
        
        self.assertIsNotNone(scanner)
        self.assertIsInstance(scanner, BaseVirusScanner)

    @override_settings(VIRUS_SCANNER_TYPE='mock')
    def test_get_virus_scanner_caches_instance(self):
        """Test get_virus_scanner returns same instance."""
        scanner1 = get_virus_scanner()
        scanner2 = get_virus_scanner()
        
        self.assertIs(scanner1, scanner2)

    @override_settings(VIRUS_SCANNER_TYPE='mock', VIRUS_SCANNER_CONFIG={'simulate_infected': True})
    def test_get_virus_scanner_uses_config(self):
        """Test get_virus_scanner uses settings config."""
        scanner = get_virus_scanner()
        
        self.assertIsInstance(scanner, MockVirusScanner)
        self.assertTrue(scanner.simulate_infected)

    @patch('documents.virus_scanner.VirusScannerFactory.create_scanner')
    def test_get_virus_scanner_fallback_on_error(self, mock_factory):
        """Test get_virus_scanner falls back to mock on error."""
        mock_factory.side_effect = Exception("Configuration error")
        
        scanner = get_virus_scanner()
        
        # Should fallback to mock scanner
        self.assertIsInstance(scanner, MockVirusScanner)
        self.assertFalse(scanner.simulate_infected)


@pytest.mark.django_db
class TestScanFileForViruses(TestCase):
    """Test scan_file_for_viruses function."""

    def setUp(self):
        """Clear global scanner before each test."""
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

    def tearDown(self):
        """Clear global scanner after each test."""
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

    @override_settings(VIRUS_SCANNER_TYPE='mock')
    def test_scan_file_clean(self):
        """Test scanning clean file succeeds."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'clean content')
            test_file = f.name
        
        try:
            is_clean, threat = scan_file_for_viruses(test_file)
            
            self.assertTrue(is_clean)
            self.assertIsNone(threat)
        finally:
            os.unlink(test_file)

    @override_settings(VIRUS_SCANNER_TYPE='mock', VIRUS_SCANNER_CONFIG={'simulate_infected': True, 'threat_name': 'Eicar'})
    def test_scan_file_infected_raises_validation_error(self):
        """Test scanning infected file raises ValidationError."""
        # Reset global scanner to pick up new settings
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'infected content')
            test_file = f.name
        
        try:
            with self.assertRaises(ValidationError) as context:
                scan_file_for_viruses(test_file)
            
            self.assertIn('virus', str(context.exception).lower())
            self.assertIn('Eicar', str(context.exception))
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.get_virus_scanner')
    @override_settings(VIRUS_SCAN_FAIL_SECURE=True)
    def test_scan_file_scanner_error_fail_secure(self, mock_get_scanner):
        """Test scanner error with fail-secure mode."""
        mock_scanner = MagicMock()
        mock_scanner.scan_file.side_effect = VirusScannerError("Scanner failed")
        mock_get_scanner.return_value = mock_scanner
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            with self.assertRaises(ValidationError) as context:
                scan_file_for_viruses(test_file)
            
            self.assertIn('scan failed', str(context.exception).lower())
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.get_virus_scanner')
    @override_settings(VIRUS_SCAN_FAIL_SECURE=False)
    def test_scan_file_scanner_error_allow_through(self, mock_get_scanner):
        """Test scanner error with allow-through mode."""
        mock_scanner = MagicMock()
        mock_scanner.scan_file.side_effect = VirusScannerError("Scanner failed")
        mock_get_scanner.return_value = mock_scanner
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            # Should not raise error, allow file through
            is_clean, threat = scan_file_for_viruses(test_file)
            
            self.assertTrue(is_clean)
            self.assertIsNone(threat)
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.get_virus_scanner')
    @override_settings(VIRUS_SCAN_FAIL_SECURE=True)
    def test_scan_file_unexpected_error_fail_secure(self, mock_get_scanner):
        """Test unexpected error with fail-secure mode."""
        mock_scanner = MagicMock()
        mock_scanner.scan_file.side_effect = Exception("Unexpected error")
        mock_get_scanner.return_value = mock_scanner
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            with self.assertRaises(ValidationError) as context:
                scan_file_for_viruses(test_file)
            
            self.assertIn('scan failed', str(context.exception).lower())
        finally:
            os.unlink(test_file)

    @patch('documents.virus_scanner.get_virus_scanner')
    @override_settings(VIRUS_SCAN_FAIL_SECURE=False)
    def test_scan_file_unexpected_error_allow_through(self, mock_get_scanner):
        """Test unexpected error with allow-through mode."""
        mock_scanner = MagicMock()
        mock_scanner.scan_file.side_effect = Exception("Unexpected error")
        mock_get_scanner.return_value = mock_scanner
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'content')
            test_file = f.name
        
        try:
            # Should not raise error, allow file through
            is_clean, threat = scan_file_for_viruses(test_file)
            
            self.assertTrue(is_clean)
            self.assertIsNone(threat)
        finally:
            os.unlink(test_file)


@pytest.mark.django_db
class TestVirusScannerConnection(TestCase):
    """Test virus scanner connection testing."""

    def setUp(self):
        """Clear global scanner before each test."""
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

    def tearDown(self):
        """Clear global scanner after each test."""
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

    @override_settings(VIRUS_SCANNER_TYPE='mock')
    def test_connection_test_success(self):
        """Test connection test succeeds with working scanner."""
        result = test_virus_scanner_connection()
        
        self.assertTrue(result)

    @patch('documents.virus_scanner.get_virus_scanner')
    def test_connection_test_failure(self, mock_get_scanner):
        """Test connection test fails gracefully."""
        mock_scanner = MagicMock()
        mock_scanner.scan_file.side_effect = Exception("Scanner not available")
        mock_get_scanner.return_value = mock_scanner
        
        result = test_virus_scanner_connection()
        
        self.assertFalse(result)

    @override_settings(VIRUS_SCANNER_TYPE='mock', VIRUS_SCANNER_CONFIG={'simulate_infected': True})
    def test_connection_test_with_infected_simulation(self):
        """Test connection test works even with infected simulation."""
        # Reset global scanner to pick up new settings
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None
        
        # Should still succeed - it's just testing connectivity
        result = test_virus_scanner_connection()
        
        # Returns True because scan completes successfully
        # (even though it detects a "virus", the scanner is working)
        self.assertTrue(result)


@pytest.mark.django_db
class TestBaseVirusScanner(TestCase):
    """Test base virus scanner class."""

    def test_base_scanner_not_implemented(self):
        """Test base scanner raises NotImplementedError."""
        scanner = BaseVirusScanner()
        
        with self.assertRaises(NotImplementedError):
            scanner.scan_file('/any/path')

