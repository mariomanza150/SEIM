"""
End-to-end tests for user workflows.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.mark.usefixtures('live_server', 'driver')
class TestUserWorkflows:
    def test_registration_workflow(self, driver, live_server):
        driver.get(f'{live_server.url}/auth/register')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'registration-form'))
        )
        driver.find_element(By.ID, 'username').send_keys('newuser')
        driver.find_element(By.ID, 'email').send_keys('newuser@example.com')
        driver.find_element(By.ID, 'password').send_keys('SecurePass123!')
        driver.find_element(By.ID, 'confirm-password').send_keys('SecurePass123!')
        driver.find_element(By.ID, 'registration-form').submit()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        assert 'auth_token' in driver.get_cookies() or driver.execute_script('return localStorage.getItem("auth_token")')

    def test_registration_validation_error(self, driver, live_server):
        driver.get(f'{live_server.url}/auth/register')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'registration-form'))
        )
        driver.find_element(By.ID, 'username').send_keys('existinguser')
        driver.find_element(By.ID, 'registration-form').submit()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger'))
        )
        error_message = driver.find_element(By.CLASS_NAME, 'alert-danger').text
        assert 'Username already exists' in error_message

    def test_login_workflow(self, driver, live_server):
        driver.get(f'{live_server.url}/auth/login')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login-form'))
        )
        driver.find_element(By.ID, 'username').send_keys('testuser')
        driver.find_element(By.ID, 'password').send_keys('password123')
        driver.find_element(By.ID, 'login-form').submit()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'dashboard'))
        )
        assert 'auth_token' in driver.get_cookies() or driver.execute_script('return localStorage.getItem("auth_token")')

    def test_logout_workflow(self, driver, live_server):
        driver.get(f'{live_server.url}/dashboard')
        # Simulate user already logged in
        driver.add_cookie({'name': 'auth_token', 'value': 'test-token'})
        driver.refresh()
        # Assume there is a logout button with id 'logout-btn'
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'logout-btn'))
        )
        driver.find_element(By.ID, 'logout-btn').click()
        WebDriverWait(driver, 10).until(
            EC.url_contains('/login'))
        assert not driver.get_cookie('auth_token') and not driver.execute_script('return localStorage.getItem("auth_token")')

    def test_application_submission_workflow(self, driver, live_server):
        driver.get(f'{live_server.url}/applications/create/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'application-form'))
        )
        driver.find_element(By.ID, 'program').send_keys('test-program-id')
        driver.find_element(By.ID, 'personal_statement').send_keys('Test personal statement')
        driver.find_element(By.ID, 'application-form').submit()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        assert driver.find_element(By.CLASS_NAME, 'alert-success')
