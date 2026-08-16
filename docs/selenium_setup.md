# Selenium Setup Guide for Windows

This guide covers setting up Selenium WebDriver with Google Chrome and ChromeDriver on Windows for running browser-based tests in the SEIM project.

## Prerequisites

- Windows 10/11
- Python 3.8+ (already installed in the project)
- Selenium Python package (already installed: version 4.15.2)

## Step 1: Install Google Chrome

### Option A: Download from Official Site
1. Visit [Google Chrome Download Page](https://www.google.com/chrome/)
2. Click "Download Chrome"
3. Run the installer and follow the setup wizard
4. Chrome will be installed to: `C:\Program Files\Google\Chrome\Application\chrome.exe`

### Option B: Using Chocolatey (if installed)
```powershell
choco install googlechrome
```

### Option C: Using Winget (Windows 10/11)
```powershell
winget install Google.Chrome
```

## Step 2: Verify Chrome Installation

After installation, verify Chrome is accessible:

```powershell
# Check if Chrome is in PATH
Get-Command chrome -ErrorAction SilentlyContinue

# Or check the default installation path
Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Get Chrome version
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

## Step 3: Download ChromeDriver

### Find Your Chrome Version
1. Open Chrome
2. Go to `chrome://settings/help`
3. Note the version number (e.g., 124.0.6367.91)

### Download ChromeDriver
1. Visit [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/)
2. Download the version that matches your Chrome version
3. Extract the `chromedriver.exe` file

### Alternative: Use WebDriver Manager
The project can use `webdriver-manager` to automatically download and manage ChromeDriver:

```powershell
pip install webdriver-manager
```

## Step 4: Install ChromeDriver

### Option A: Add to System PATH
1. Create a directory for ChromeDriver (e.g., `C:\WebDriver`)
2. Copy `chromedriver.exe` to this directory
3. Add the directory to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Edit the "Path" variable
   - Add `C:\WebDriver` to the list
   - Click OK to save

### Option B: Place in Project Directory
1. Create a `drivers` directory in your project root
2. Copy `chromedriver.exe` to `SEIM/drivers/`
3. Update test configuration to use the local path

### Option C: Use WebDriver Manager (Recommended)
This automatically handles ChromeDriver installation and version matching.

## Step 5: Verify ChromeDriver Installation

```powershell
# Check if ChromeDriver is in PATH
Get-Command chromedriver -ErrorAction SilentlyContinue

# Test ChromeDriver
chromedriver --version
```

## Step 6: Configure Selenium Tests

### Update Test Configuration
The project's Selenium tests should be configured to use the local Chrome installation:

```python
# In test files, use:
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# For local Chrome installation
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Use WebDriver Manager (recommended)
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

### Environment Variables
Set these environment variables for consistent test execution:

```powershell
# Set Chrome binary path
$env:CHROME_BIN = "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Set ChromeDriver path (if not using WebDriver Manager)
$env:CHROMEDRIVER_PATH = "C:\WebDriver\chromedriver.exe"
```

## Step 7: Test the Setup

### Run a Simple Test
Create a test script to verify the setup:

```python
# test_chrome_setup.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_chrome_setup():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://www.google.com")
        print(f"Chrome setup successful! Page title: {driver.title}")
        return True
    except Exception as e:
        print(f"Chrome setup failed: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    test_chrome_setup()
```

### Run the Test
```powershell
python test_chrome_setup.py
```

## Step 8: Run SEIM Selenium Tests

### Ensure Django App is Running
```powershell
# Start the Django app in Docker
docker-compose up -d

# Verify the app is accessible
curl http://localhost:8000
```

### Run Selenium Tests
```powershell
# Run all Selenium tests
python -m pytest tests/selenium/ -v

# Run specific test file
python -m pytest tests/selenium/test_core_functionality.py -v

# Run with coverage
python -m pytest tests/selenium/ --cov=frontend --cov-report=html
```

## Troubleshooting

### Common Issues

1. **ChromeDriver version mismatch**
   - Ensure ChromeDriver version matches Chrome version
   - Use WebDriver Manager for automatic version management

2. **Chrome not found**
   - Verify Chrome installation path
   - Check if Chrome is in system PATH

3. **Permission errors**
   - Run PowerShell as Administrator
   - Check file permissions for ChromeDriver

4. **Network connectivity issues**
   - Ensure Django app is accessible from host
   - Check Docker port mappings

5. **Chrome crashes or hangs**
   - Add `--no-sandbox` and `--disable-dev-shm-usage` options
   - Use headless mode for CI/CD environments

### Debug Commands

```powershell
# Check Chrome installation
Get-ChildItem "C:\Program Files\Google\Chrome\Application\" -Name "chrome.exe"

# Check ChromeDriver installation
Get-ChildItem "C:\WebDriver\" -Name "chromedriver.exe"

# Test network connectivity to Django app
Test-NetConnection -ComputerName localhost -Port 8000

# Check environment variables
Get-ChildItem Env: | Where-Object { $_.Name -like "*CHROME*" }
```

## Integration with CI/CD

For continuous integration, consider:

1. **Using WebDriver Manager** for automatic driver management
2. **Headless mode** for server environments
3. **Docker-based Selenium** for consistent environments
4. **Screenshot capture** for debugging failed tests

## References

- [Selenium Python Documentation](https://selenium-python.readthedocs.io/)
- [ChromeDriver Downloads](https://sites.google.com/chromium.org/driver/)
- [WebDriver Manager Documentation](https://github.com/SergeyPirogov/webdriver_manager)
- [Chrome Command Line Switches](https://peter.sh/experiments/chromium-command-line-switches/)

## Project-Specific Notes

- The SEIM project uses Django with Docker for the backend
- Selenium tests should target `localhost:8000` (Django app)
- Tests are located in `tests/selenium/` directory
- Coverage target: 80% for both backend and frontend
- Tests should run on Windows host, not inside Docker containers 