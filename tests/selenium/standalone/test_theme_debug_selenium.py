#!/usr/bin/env python3
"""
Comprehensive Selenium test to debug theme switching issues
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def test_theme_debug():
    """Comprehensive theme debugging test"""

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        print("🔍 Starting comprehensive theme debugging...")

        # Test 1: Visit the theme debug page
        print("\n📄 Loading theme debug page...")
        driver.get("http://localhost:8000/theme-debug/")
        time.sleep(3)

        # Test 2: Check initial state
        print("\n🎨 Checking initial theme state...")
        initial_theme = driver.execute_script(
            """
            return {
                htmlDataTheme: document.documentElement.getAttribute('data-theme'),
                localStorageTheme: localStorage.getItem('seim-theme'),
                themeManagerExists: !!window.themeManager,
                themeManagerTheme: window.themeManager ? window.themeManager.getCurrentTheme() : null,
                cssVariables: {
                    '--bg-primary': getComputedStyle(document.documentElement).getPropertyValue('--bg-primary'),
                    '--text-primary': getComputedStyle(document.documentElement).getPropertyValue('--text-primary'),
                    '--primary-color': getComputedStyle(document.documentElement).getPropertyValue('--primary-color')
                }
            }
        """
        )

        print(f"   HTML data-theme: {initial_theme['htmlDataTheme']}")
        print(f"   localStorage theme: {initial_theme['localStorageTheme']}")
        print(f"   ThemeManager exists: {initial_theme['themeManagerExists']}")
        print(f"   ThemeManager current theme: {initial_theme['themeManagerTheme']}")
        print("   CSS Variables:")
        for var, value in initial_theme["cssVariables"].items():
            print(f"     {var}: {value}")

        # Test 3: Find and click theme toggle
        print("\n🖱️  Testing theme toggle functionality...")
        toggle_button = wait.until(EC.element_to_be_clickable((By.ID, "theme-toggle")))

        # Get initial button state
        initial_button_icon = toggle_button.find_element(
            By.TAG_NAME, "i"
        ).get_attribute("class")
        print(f"   Initial button icon: {initial_button_icon}")

        # Click the toggle
        print("   Clicking theme toggle...")
        toggle_button.click()
        time.sleep(2)

        # Test 4: Check state after toggle
        print("\n🔄 Checking state after toggle...")
        after_toggle_state = driver.execute_script(
            """
            return {
                htmlDataTheme: document.documentElement.getAttribute('data-theme'),
                localStorageTheme: localStorage.getItem('seim-theme'),
                themeManagerTheme: window.themeManager ? window.themeManager.getCurrentTheme() : null,
                cssVariables: {
                    '--bg-primary': getComputedStyle(document.documentElement).getPropertyValue('--bg-primary'),
                    '--text-primary': getComputedStyle(document.documentElement).getPropertyValue('--text-primary'),
                    '--primary-color': getComputedStyle(document.documentElement).getPropertyValue('--primary-color')
                },
                bodyBackground: getComputedStyle(document.body).backgroundColor,
                bodyColor: getComputedStyle(document.body).color
            }
        """
        )

        print(f"   HTML data-theme: {after_toggle_state['htmlDataTheme']}")
        print(f"   localStorage theme: {after_toggle_state['localStorageTheme']}")
        print(
            f"   ThemeManager current theme: {after_toggle_state['themeManagerTheme']}"
        )
        print(f"   Body background: {after_toggle_state['bodyBackground']}")
        print(f"   Body color: {after_toggle_state['bodyColor']}")
        print("   CSS Variables after toggle:")
        for var, value in after_toggle_state["cssVariables"].items():
            print(f"     {var}: {value}")

        # Test 5: Check button state after toggle
        new_button_icon = toggle_button.find_element(By.TAG_NAME, "i").get_attribute(
            "class"
        )
        print(f"   New button icon: {new_button_icon}")

        # Test 6: Force light mode via console
        print("\n☀️  Testing force light mode...")
        driver.execute_script(
            """
            if (window.themeManager) {
                window.themeManager.forceLight();
            }
        """
        )
        time.sleep(2)

        force_light_state = driver.execute_script(
            """
            return {
                htmlDataTheme: document.documentElement.getAttribute('data-theme'),
                localStorageTheme: localStorage.getItem('seim-theme'),
                themeManagerTheme: window.themeManager ? window.themeManager.getCurrentTheme() : null,
                cssVariables: {
                    '--bg-primary': getComputedStyle(document.documentElement).getPropertyValue('--bg-primary'),
                    '--text-primary': getComputedStyle(document.documentElement).getPropertyValue('--text-primary')
                },
                bodyBackground: getComputedStyle(document.body).backgroundColor,
                bodyColor: getComputedStyle(document.body).color
            }
        """
        )

        print("   After force light:")
        print(f"     HTML data-theme: {force_light_state['htmlDataTheme']}")
        print(f"     localStorage theme: {force_light_state['localStorageTheme']}")
        print(f"     ThemeManager theme: {force_light_state['themeManagerTheme']}")
        print(f"     Body background: {force_light_state['bodyBackground']}")
        print(f"     Body color: {force_light_state['bodyColor']}")

        # Test 7: Check for CSS conflicts
        print("\n🎨 Checking for CSS conflicts...")
        css_conflicts = driver.execute_script(
            """
            const styles = document.styleSheets;
            const conflicts = [];

            for (let sheet of styles) {
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('[data-theme="dark"]')) {
                            conflicts.push({
                                selector: rule.selectorText,
                                cssText: rule.cssText.substring(0, 100) + '...'
                            });
                        }
                    }
                } catch (e) {
                    // Cross-origin stylesheets
                }
            }
            return conflicts;
        """
        )

        print(f"   Found {len(css_conflicts)} dark theme CSS rules:")
        for conflict in css_conflicts[:5]:  # Show first 5
            print(f"     {conflict['selector']}")

        # Test 8: Check Bootstrap utility classes
        print("\n🎯 Testing Bootstrap utility classes...")
        utility_test = driver.execute_script(
            """
            // Create test elements
            const testDiv = document.createElement('div');
            testDiv.className = 'bg-primary text-primary p-3';
            testDiv.textContent = 'Test Element';
            testDiv.style.position = 'absolute';
            testDiv.style.top = '10px';
            testDiv.style.left = '10px';
            testDiv.style.zIndex = '9999';
            document.body.appendChild(testDiv);

            const computedStyle = getComputedStyle(testDiv);
            return {
                backgroundColor: computedStyle.backgroundColor,
                color: computedStyle.color,
                classes: testDiv.className
            }
        """
        )

        print("   Test element with .bg-primary.text-primary:")
        print(f"     Background: {utility_test['backgroundColor']}")
        print(f"     Color: {utility_test['color']}")
        print(f"     Classes: {utility_test['classes']}")

        # Clean up test element
        driver.execute_script(
            """
            const testDiv = document.querySelector('div[style*="position: absolute"]');
            if (testDiv) testDiv.remove();
        """
        )

        # Test 9: Check if dark mode is being forced by system preference
        print("\n💻 Checking system preference...")
        system_pref = driver.execute_script(
            """
            return {
                prefersDark: window.matchMedia('(prefers-color-scheme: dark)').matches,
                prefersLight: window.matchMedia('(prefers-color-scheme: light)').matches,
                noPreference: window.matchMedia('(prefers-color-scheme: no-preference)').matches
            }
        """
        )

        print(f"   System prefers dark: {system_pref['prefersDark']}")
        print(f"   System prefers light: {system_pref['prefersLight']}")
        print(f"   System no preference: {system_pref['noPreference']}")

        # Test 10: Final diagnosis
        print("\n🔍 Final Diagnosis:")

        if after_toggle_state["htmlDataTheme"] == "dark":
            print("   ❌ ISSUE: HTML still has data-theme='dark' after toggle")
        else:
            print("   ✅ HTML data-theme correctly removed")

        if after_toggle_state["localStorageTheme"] == "light":
            print("   ✅ localStorage correctly set to 'light'")
        else:
            print("   ❌ ISSUE: localStorage not set to 'light'")

        if after_toggle_state["themeManagerTheme"] == "light":
            print("   ✅ ThemeManager correctly set to 'light'")
        else:
            print("   ❌ ISSUE: ThemeManager not set to 'light'")

        # Check if body is actually light colored
        if (
            "rgb(255, 255, 255)" in after_toggle_state["bodyBackground"]
            or "#ffffff" in after_toggle_state["bodyBackground"]
        ):
            print("   ✅ Body background is light colored")
        else:
            print("   ❌ ISSUE: Body background is not light colored")

        if (
            "rgb(33, 37, 41)" in after_toggle_state["bodyColor"]
            or "#212529" in after_toggle_state["bodyColor"]
        ):
            print("   ✅ Body text is dark colored")
        else:
            print("   ❌ ISSUE: Body text is not dark colored")

        print("\n🎉 Theme debugging test completed!")
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
    print("🚀 Starting comprehensive theme debugging test...")
    success = test_theme_debug()

    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed. Check the output above for details.")
