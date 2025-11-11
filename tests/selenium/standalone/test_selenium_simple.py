#!/usr/bin/env python3
"""
Simple test script to verify Selenium setup for E2E tests on Windows.
This version doesn't require Django setup.
"""


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
        chrome_options.add_argument("--remote-debugging-port=9222")

        # Set up ChromeDriver with explicit path
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver path: {driver_path}")

        # Ensure the path points to the executable
        if driver_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
            driver_path = driver_path.replace(
                "THIRD_PARTY_NOTICES.chromedriver", "chromedriver.exe"
            )

        print(f"Using ChromeDriver: {driver_path}")
        service = Service(driver_path)

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
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_selenium_setup()
    exit(0 if success else 1)
