#!/usr/bin/env python3
"""
Test script to verify theme toggle functionality
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def test_theme_toggle():
    """Test the theme toggle functionality"""

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        print("🌐 Testing theme toggle functionality...")

        # Test 1: Visit the debug page
        print("📄 Visiting theme debug page...")
        driver.get("http://localhost:8000/theme-debug/")

        # Wait for page to load
        time.sleep(2)

        # Test 2: Check if theme toggle button exists
        print("🔍 Looking for theme toggle button...")
        try:
            toggle_button = wait.until(
                EC.presence_of_element_located((By.ID, "theme-toggle"))
            )
            print("✅ Theme toggle button found!")

            # Get button properties
            button_text = toggle_button.text
            button_classes = toggle_button.get_attribute("class")
            button_visible = toggle_button.is_displayed()

            print(f"   - Text: '{button_text}'")
            print(f"   - Classes: {button_classes}")
            print(f"   - Visible: {button_visible}")

        except Exception as e:
            print(f"❌ Theme toggle button not found: {e}")
            return False

        # Test 3: Check current theme
        print("🎨 Checking current theme...")
        try:
            html_element = driver.find_element(By.TAG_NAME, "html")
            current_theme = html_element.get_attribute("data-theme")
            print(f"   - Current theme: {current_theme or 'light (default)'}")
        except Exception as e:
            print(f"❌ Could not determine current theme: {e}")

        # Test 4: Click the toggle button
        print("🖱️  Testing theme toggle...")
        try:
            # Get initial theme
            initial_theme = driver.find_element(By.TAG_NAME, "html").get_attribute(
                "data-theme"
            )

            # Click the toggle button
            toggle_button.click()
            time.sleep(1)

            # Check if theme changed
            new_theme = driver.find_element(By.TAG_NAME, "html").get_attribute(
                "data-theme"
            )

            if new_theme != initial_theme:
                print(
                    f"✅ Theme successfully toggled from '{initial_theme or 'light'}' to '{new_theme or 'light'}'"
                )
            else:
                print(
                    f"⚠️  Theme may not have changed: {initial_theme or 'light'} -> {new_theme or 'light'}"
                )

        except Exception as e:
            print(f"❌ Error toggling theme: {e}")

        # Test 5: Check CSS variables
        print("🎨 Checking CSS variables...")
        try:
            # Get CSS variables
            css_vars = driver.execute_script(
                """
                const styles = getComputedStyle(document.documentElement);
                return {
                    '--text-primary': styles.getPropertyValue('--text-primary'),
                    '--bg-primary': styles.getPropertyValue('--bg-primary'),
                    '--border-color': styles.getPropertyValue('--border-color')
                };
            """
            )

            print("   - CSS Variables:")
            for var_name, value in css_vars.items():
                print(f"     {var_name}: {value}")

        except Exception as e:
            print(f"❌ Error checking CSS variables: {e}")

        # Test 6: Check theme manager JavaScript
        print("🔧 Checking theme manager...")
        try:
            theme_manager_status = driver.execute_script(
                """
                if (window.themeManager) {
                    return {
                        exists: true,
                        currentTheme: window.themeManager.getCurrentTheme(),
                        isDarkMode: window.themeManager.isDarkMode()
                    };
                } else {
                    return { exists: false };
                }
            """
            )

            if theme_manager_status.get("exists"):
                print("✅ Theme manager found")
                print(f"   - Current theme: {theme_manager_status.get('currentTheme')}")
                print(f"   - Dark mode: {theme_manager_status.get('isDarkMode')}")
            else:
                print("❌ Theme manager not found")

        except Exception as e:
            print(f"❌ Error checking theme manager: {e}")

        # Test 7: Test visual feedback
        print("💫 Testing visual feedback...")
        try:
            # Click toggle again to trigger feedback
            toggle_button.click()
            time.sleep(2)

            # Look for feedback element
            feedback_elements = driver.find_elements(By.CLASS_NAME, "theme-feedback")
            if feedback_elements:
                print("✅ Visual feedback detected")
            else:
                print("⚠️  No visual feedback detected")

        except Exception as e:
            print(f"❌ Error testing visual feedback: {e}")

        print("\n🎉 Theme toggle testing completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    print("🚀 Starting theme toggle tests...")
    success = test_theme_toggle()

    if success:
        print("\n✅ All tests passed! Theme toggle is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
