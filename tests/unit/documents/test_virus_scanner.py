"""
Unit tests for virus scanner functionality.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from documents.virus_scanner import (
    BaseVirusScanner,
    ClamAVCommandLineScanner,
    ClamAVScanner,
    MockVirusScanner,
    VirusScannerError,
    VirusScannerFactory,
    get_virus_scanner,
    scan_file_for_viruses,
    test_virus_scanner_connection,
)


class TestBaseVirusScanner(TestCase):
    """Test base virus scanner class."""

    def test_base_scanner_is_abstract(self):
        """Test that BaseVirusScanner cannot be instantiated directly."""
        with self.assertRaises(NotImplementedError):
            scanner = BaseVirusScanner()
            scanner.scan_file("test.txt")


class TestMockVirusScanner(TestCase):
    """Test mock virus scanner implementation."""

    def test_mock_scanner_clean_file(self):
        """Test mock scanner with clean file."""
        scanner = MockVirusScanner(simulate_infected=False)

        is_clean, threat_name = scanner.scan_file("clean_file.txt")

        self.assertTrue(is_clean)
        self.assertIsNone(threat_name)

    def test_mock_scanner_infected_file(self):
        """Test mock scanner with infected file."""
        scanner = MockVirusScanner(simulate_infected=True, threat_name="TestVirus")

        is_clean, threat_name = scanner.scan_file("infected_file.txt")

        self.assertFalse(is_clean)
        self.assertEqual(threat_name, "TestVirus")

    def test_mock_scanner_virus_keyword_detection(self):
        """Test mock scanner detects virus keyword in filename."""
        scanner = MockVirusScanner(simulate_infected=True)

        is_clean, threat_name = scanner.scan_file("document_virus.pdf")

        self.assertFalse(is_clean)
        self.assertEqual(threat_name, "TestVirus")

    def test_mock_scanner_infected_keyword_detection(self):
        """Test mock scanner detects infected keyword in filename."""
        scanner = MockVirusScanner(simulate_infected=True)

        is_clean, threat_name = scanner.scan_file("infected_document.pdf")

        self.assertFalse(is_clean)
        self.assertEqual(threat_name, "TestVirus")


class TestClamAVCommandLineScanner(TestCase):
    """Test ClamAV command-line scanner."""

    @patch('subprocess.run')
    def test_clamav_cli_clean_file(self, mock_run):
        """Test ClamAV CLI scanner with clean file."""
        # Mock successful scan (return code 0)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )

        scanner = ClamAVCommandLineScanner()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Clean file content")
            temp_file_path = temp_file.name

        try:
            is_clean, threat_name = scanner.scan_file(temp_file_path)

            self.assertTrue(is_clean)
            self.assertIsNone(threat_name)
            mock_run.assert_called_once()
        finally:
            os.unlink(temp_file_path)

    @patch('subprocess.run')
    def test_clamav_cli_infected_file(self, mock_run):
        """Test ClamAV CLI scanner with infected file."""
        # Mock infected file detection (return code 1)
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="/path/to/file: EICAR-Test-File FOUND",
            stderr=""
        )

        scanner = ClamAVCommandLineScanner()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"EICAR test file")
            temp_file_path = temp_file.name

        try:
            is_clean, threat_name = scanner.scan_file(temp_file_path)

            self.assertFalse(is_clean)
            self.assertEqual(threat_name, "EICAR-Test-File")
        finally:
            os.unlink(temp_file_path)

    @patch('subprocess.run')
    def test_clamav_cli_scan_error(self, mock_run):
        """Test ClamAV CLI scanner with scan error."""
        # Mock scan error (return code 2)
        mock_run.return_value = MagicMock(
            returncode=2,
            stdout="",
            stderr="Scan error occurred"
        )

        scanner = ClamAVCommandLineScanner()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(VirusScannerError):
                scanner.scan_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_clamav_cli_file_not_found(self):
        """Test ClamAV CLI scanner with non-existent file."""
        scanner = ClamAVCommandLineScanner()

        with self.assertRaises(VirusScannerError):
            scanner.scan_file("non_existent_file.txt")

    @patch('subprocess.run')
    def test_clamav_cli_timeout(self, mock_run):
        """Test ClamAV CLI scanner timeout."""
        import subprocess

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("clamscan", 60)

        scanner = ClamAVCommandLineScanner()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(VirusScannerError):
                scanner.scan_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)


class TestVirusScannerFactory(TestCase):
    """Test virus scanner factory."""

    def test_create_mock_scanner(self):
        """Test creating mock scanner."""
        scanner = VirusScannerFactory.create_scanner("mock", simulate_infected=True)

        self.assertIsInstance(scanner, MockVirusScanner)
        self.assertTrue(scanner.simulate_infected)

    def test_create_clamav_cli_scanner(self):
        """Test creating ClamAV CLI scanner."""
        scanner = VirusScannerFactory.create_scanner(
            "clamav_cli",
            clamscan_path="/usr/bin/clamscan"
        )

        self.assertIsInstance(scanner, ClamAVCommandLineScanner)
        self.assertEqual(scanner.clamscan_path, "/usr/bin/clamscan")

    def test_create_clamav_scanner(self):
        """Test creating ClamAV daemon scanner."""
        scanner = VirusScannerFactory.create_scanner(
            "clamav",
            host="localhost",
            port=3310
        )

        self.assertIsInstance(scanner, ClamAVScanner)
        self.assertEqual(scanner.host, "localhost")
        self.assertEqual(scanner.port, 3310)

    def test_create_unknown_scanner(self):
        """Test creating unknown scanner type."""
        with self.assertRaises(ValueError):
            VirusScannerFactory.create_scanner("unknown_scanner")


class TestVirusScannerIntegration(TestCase):
    """Test virus scanner integration functions."""

    @patch('documents.virus_scanner.VirusScannerFactory.create_scanner')
    def test_get_virus_scanner(self, mock_create):
        """Test getting virus scanner instance."""
        mock_scanner = MockVirusScanner()
        mock_create.return_value = mock_scanner

        # Clear global scanner to test initialization
        import documents.virus_scanner
        documents.virus_scanner._virus_scanner = None

        scanner = get_virus_scanner()

        self.assertEqual(scanner, mock_scanner)
        mock_create.assert_called_once()

    @patch('documents.virus_scanner.get_virus_scanner')
    def test_scan_file_for_viruses_clean(self, mock_get_scanner):
        """Test scanning clean file."""
        mock_scanner = MockVirusScanner(simulate_infected=False)
        mock_get_scanner.return_value = mock_scanner

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Clean content")
            temp_file_path = temp_file.name

        try:
            is_clean, threat_name = scan_file_for_viruses(temp_file_path)

            self.assertTrue(is_clean)
            self.assertIsNone(threat_name)
        finally:
            os.unlink(temp_file_path)

    @patch('documents.virus_scanner.get_virus_scanner')
    def test_scan_file_for_viruses_infected(self, mock_get_scanner):
        """Test scanning infected file."""
        mock_scanner = MockVirusScanner(simulate_infected=True, threat_name="TestVirus")
        mock_get_scanner.return_value = mock_scanner

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Infected content")
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(ValidationError) as context:
                scan_file_for_viruses(temp_file_path)

            self.assertIn("TestVirus", str(context.exception))
        finally:
            os.unlink(temp_file_path)

    @patch('documents.virus_scanner.get_virus_scanner')
    def test_scan_file_for_viruses_scanner_error(self, mock_get_scanner):
        """Test handling scanner errors."""
        mock_scanner = MockVirusScanner()
        mock_scanner.scan_file = MagicMock(side_effect=VirusScannerError("Scanner failed"))
        mock_get_scanner.return_value = mock_scanner

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content")
            temp_file_path = temp_file.name

        try:
            with self.assertRaises(ValidationError) as context:
                scan_file_for_viruses(temp_file_path)

            self.assertIn("Virus scan failed", str(context.exception))
        finally:
            os.unlink(temp_file_path)

    @patch('documents.virus_scanner.get_virus_scanner')
    def test_test_virus_scanner_connection_success(self, mock_get_scanner):
        """Test virus scanner connection test success."""
        mock_scanner = MockVirusScanner()
        mock_get_scanner.return_value = mock_scanner

        result = test_virus_scanner_connection()

        self.assertTrue(result)

    @patch('documents.virus_scanner.get_virus_scanner')
    def test_test_virus_scanner_connection_failure(self, mock_get_scanner):
        """Test virus scanner connection test failure."""
        mock_scanner = MockVirusScanner()
        mock_scanner.scan_file = MagicMock(side_effect=Exception("Connection failed"))
        mock_get_scanner.return_value = mock_scanner

        result = test_virus_scanner_connection()

        self.assertFalse(result)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.security
class TestDocumentVirusScanning(TestCase):
    """Test document virus scanning integration."""

    def test_document_service_virus_scan_clean(self):
        """Test DocumentService virus scanning with clean file."""
        # Create a mock file
        from django.core.files.uploadedfile import SimpleUploadedFile

        from documents.services import DocumentService

        file_content = b"Clean document content"
        file_obj = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")

        with patch('documents.virus_scanner.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)

            result = DocumentService.virus_scan(file_obj)

            self.assertTrue(result)
            mock_scan.assert_called_once()

    def test_document_service_virus_scan_infected(self):
        """Test DocumentService virus scanning with infected file."""
        # Create a mock file
        from django.core.files.uploadedfile import SimpleUploadedFile

        from documents.services import DocumentService

        file_content = b"Infected document content"
        file_obj = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")

        with patch('documents.virus_scanner.scan_file_for_viruses') as mock_scan:
            mock_scan.side_effect = ValidationError("File contains virus: TestVirus")

            result = DocumentService.virus_scan(file_obj)

            self.assertFalse(result)

    def test_document_service_virus_scan_error(self):
        """Test DocumentService virus scanning with scan error."""
        # Create a mock file
        from django.core.files.uploadedfile import SimpleUploadedFile

        from documents.services import DocumentService

        file_content = b"Test document content"
        file_obj = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")

        with patch('documents.virus_scanner.scan_file_for_viruses') as mock_scan:
            mock_scan.side_effect = Exception("Scanner error")

            # Should not raise exception, but return False
            result = DocumentService.virus_scan(file_obj)

            self.assertFalse(result)
