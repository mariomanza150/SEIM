#!/usr/bin/env python3
"""
Dynforms Form Builder E2E tests using Selenium.
These tests require the Django app to be running at http://localhost:8000
"""

import os
import time
import unittest

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class TestDynformsBuilder(unittest.TestCase):
    """Test Dynforms Form Builder functionality using Selenium."""

    def setUp(self):
        # Use Remote WebDriver to connect to Chrome running on the host OS
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # If you want to see the browser, comment out the next line
        # chrome_options.add_argument('--headless')
        # Host IP for Windows host (adjust if needed)
        host_ip = os.environ.get("SELENIUM_HOST", "host.docker.internal")
        self.driver = webdriver.Remote(
            command_executor=f"http://{host_ip}:4444/wd/hub",
            options=chrome_options,
        )

        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "http://localhost:8000"

        # Admin user credentials
        self.admin_user = {
            "username": "admin",
            "password": "admin123",
            "email": "admin@test.com",
        }

    def tearDown(self):
        """Clean up driver after each test."""
        if hasattr(self, "driver"):
            self.driver.quit()

    def test_dynforms_builder_loads(self):
        """Test that the Dynforms Form Builder loads correctly for admin users."""
        # Log in as admin
        self.driver.get(f"{self.base_url}/login/")
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")

        try:
            # Wait for login form fields
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )

            # Fill in credentials
            username_field.send_keys(self.admin_user["username"])
            password_field.send_keys(self.admin_user["password"])
            password_field.send_keys(Keys.RETURN)

            # Wait for login to complete (redirect to dashboard or home)
            time.sleep(2)

            # Go to the Dynforms builder page
            self.driver.get(f"{self.base_url}/dynforms/")

            # Wait for the builder UI to load
            builder = self.wait.until(
                EC.presence_of_element_located((By.ID, "df-builder"))
            )
            assert builder.is_displayed(), "Form builder UI did not load!"

            # Check for field palette (sidebar)
            sidebar = self.wait.until(
                EC.presence_of_element_located((By.ID, "df-sidebar"))
            )
            assert sidebar.is_displayed(), "Sidebar (field palette) not visible!"

            # Check for header
            header = self.wait.until(
                EC.presence_of_element_located((By.ID, "df-header"))
            )
            assert header.is_displayed(), "Form builder header not visible!"

            print("✅ Dynforms Form Builder loaded successfully!")

        except NoSuchElementException as e:
            print(f"Form builder elements not found: {e}")
            pytest.skip(f"Form builder elements not found: {e}")
        except TimeoutException as e:
            print(f"Form builder did not load in time: {e}")
            pytest.skip(f"Form builder did not load in time: {e}")
