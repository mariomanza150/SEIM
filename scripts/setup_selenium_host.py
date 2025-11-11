#!/usr/bin/env python3
"""
Setup script for Selenium E2E testing on HOST OS.
This script helps configure the environment for running Selenium tests outside Docker.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_python_dependencies():
    """Install Python dependencies for Selenium testing."""
    print("📦 Installing Python dependencies...")

    dependencies = [
        "selenium==4.15.2",
        "webdriver-manager==4.0.1",
        "pytest-selenium==4.0.1",
        "requests==2.31.0",
    ]

    try:
        for dep in dependencies:
            print(f"  Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_chrome_installation():
    """Check if Chrome browser is installed."""
    system = platform.system().lower()

    print("🔍 Checking Chrome browser installation...")

    if system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    elif system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
        ]

    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            return True

    print("❌ Chrome browser not found")
    print("📋 Please install Chrome browser:")

    if system == "windows":
        print("  Download from: https://www.google.com/chrome/")
    elif system == "darwin":
        print("  Download from: https://www.google.com/chrome/")
        print("  Or install via Homebrew: brew install --cask google-chrome")
    else:
        print("  Ubuntu/Debian: sudo apt-get install google-chrome-stable")
        print("  CentOS/RHEL: sudo yum install google-chrome-stable")
        print("  Or download from: https://www.google.com/chrome/")

    return False


def test_selenium_setup():
    """Test if Selenium can be imported and configured."""
    print("🧪 Testing Selenium setup...")

    try:
        import selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        print("✅ Selenium imports successful")

        # Test ChromeDriver manager
        try:
            driver_path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver found at: {driver_path}")
        except Exception as e:
            print(f"⚠️  ChromeDriver setup issue: {e}")
            print("   This is normal if Chrome is not installed yet")

        return True

    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False


def create_test_script():
    """Create a simple test script to verify Selenium setup."""
    test_script = """#!/usr/bin/env python3
\"\"\"
Simple Selenium test to verify setup.
Run this script to test if Selenium is working correctly.
\"\"\"

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium():
    print("🧪 Testing Selenium setup...")

    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")  # Run in background

        # Create driver
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()

        print(f"✅ Selenium test successful! Page title: {title}")
        return True

    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_selenium()
    sys.exit(0 if success else 1)
"""

    script_path = Path("tests/selenium/test_setup_verification.py")
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with open(script_path, "w") as f:
        f.write(test_script)

    print(f"✅ Test script created: {script_path}")
    return script_path


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Selenium setup completed!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Install Chrome browser if not already installed")
    print("2. Start Django server: docker-compose up web")
    print("3. Test Selenium setup: python tests/selenium/test_setup_verification.py")
    print("4. Run Selenium tests: make test-selenium")
    print("\n🔧 Available commands:")
    print("  make test-selenium              # Run all Selenium tests")
    print("  make test-selenium-standalone   # Run standalone tests")
    print("  make test-selenium-setup        # Test setup")
    print("\n📚 Documentation:")
    print("  See documentation/testing.md for detailed instructions")
    print("\n⚠️  Important notes:")
    print("  - Selenium tests run from HOST OS, not Docker")
    print("  - Django server must be running in Docker")
    print("  - Chrome browser must be installed on host OS")


def main():
    """Main setup function."""
    print("🚀 SEIM Selenium Host OS Setup")
    print("="*40)
    print("This script sets up Selenium E2E testing on your host OS.")
    print("Selenium tests will run outside Docker containers.\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)

    # Test Selenium imports
    if not test_selenium_setup():
        sys.exit(1)

    # Check Chrome installation
    chrome_installed = check_chrome_installation()

    # Create test script
    create_test_script()

    # Print next steps
    print_next_steps()

    if not chrome_installed:
        print("\n⚠️  Setup incomplete: Chrome browser not installed")
        print("   Please install Chrome and run the test script again")
        sys.exit(1)

    print("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    main()
