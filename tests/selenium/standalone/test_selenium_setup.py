#!/usr/bin/env python3
"""
Test script to verify Selenium setup for E2E tests on Windows.
"""

import os
import sys
from pathlib import Path

import django

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings.test")
django.setup()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def test_selenium_setup():
    """Test that Selenium can start Chrome and navigate to a page."""
    print("Testing Selenium setup...")

    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Set up ChromeDriver
        service = Service(ChromeDriverManager().install())

        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Test navigation
        driver.get("https://www.google.com")
        title = driver.title
        print(f"Successfully navigated to Google. Page title: {title}")

        # Clean up
        driver.quit()
        print("✅ Selenium setup is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Selenium setup failed: {e}")
        return False


if __name__ == "__main__":
    success = test_selenium_setup()
    sys.exit(0 if success else 1)
