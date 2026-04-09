# Quick Fix Guide: Complete E2E Test Setup

## 🎯 Goal
Get the first E2E test running successfully.

## 🔧 The Problem
Django's test database setup conflicts with Playwright's async execution model.

## ✅ Solution Options

### Option 1: Simple HTTP-Only Tests (RECOMMENDED)
Remove Django test fixtures and use pure HTTP requests.

**Steps:**
1. Remove `@pytest.mark.django_db` from tests
2. Use HTTP requests instead of Django ORM
3. Set up test data via API calls

**Implementation:**
```python
# In conftest.py, remove Django setup
# Remove: django.setup()

# In tests, use HTTP only:
async def test_homepage(page, base_url):
    await page.goto(f"{base_url}/")
    await expect(page.locator("h1")).to_contain_text("Welcome")
```

### Option 2: Disable Django Test Database
Configure pytest to skip database creation for E2E tests.

**Add to pytest.ini:**
```ini
[pytest]
django_db = false  # Disable test database
```

**Or add to conftest.py:**
```python
import pytest

@pytest.fixture(scope="session")
def django_db_setup():
    """Override to skip test database creation."""
    pass

@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Override to use production database."""
    pass
```

### Option 3: Use Development Database Directly
Point Django settings to use the E2E database without creating test database.

**Update docker-compose.e2e.yml:**
```yaml
environment:
  - DJANGO_SETTINGS_MODULE=seim.settings.development  # Already done
  - TESTING=false  # Don't trigger test mode
```

## 🚀 Quick Win: Run a Simple Test

**Create a minimal test file:**

```python
# tests/e2e_playwright/test_simple.py
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e_playwright
def test_homepage_loads(page: Page):
    """Test that homepage loads successfully."""
    page.goto("http://web:8000/")
    expect(page).to_have_title(/.+/)  # Any title
    print("✅ Homepage loaded successfully!")
```

**Run it:**
```bash
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright \
  pytest tests/e2e_playwright/test_simple.py -v \
  --browser chromium
```

## 📋 Checklist

- [ ] Web service is running and healthy
- [ ] Database is seeded with test users
- [ ] Remove Django test database setup
- [ ] Update tests to use HTTP/API only
- [ ] Run simple homepage test
- [ ] Add `data-testid` attributes to templates
- [ ] Update Page Objects with correct selectors
- [ ] Run full test suite
- [ ] Review and fix failures
- [ ] Document results

## 🎓 Best Practices

1. **Start Simple**: Get one test working before fixing all tests
2. **Use data-testid**: Add these to templates for reliable selectors
3. **Test Data**: Create fixtures via Django management commands
4. **Parallel Safe**: Ensure tests can run in parallel
5. **Screenshots**: Review failure screenshots in `playwright-results/`

## 📊 Success Metrics

- ✅ Web service responds to requests
- ✅ At least 1 test passes
- ✅ Screenshots captured on failure
- ✅ Test reports generated
- ✅ Can run tests in Docker

## 🆘 Common Issues

**"Connection refused"**
- Check web service is healthy: `docker-compose -f docker-compose.e2e.yml ps`
- Verify ports: `docker-compose -f docker-compose.e2e.yml logs web`

**"Element not found"**
- Add `data-testid` attributes
- Use `page.pause()` to inspect page
- Check selector in browser DevTools

**"Test database creation failed"**
- Remove `@pytest.mark.django_db`
- Disable Django test database (see Option 2 above)

## 🎉 When Complete

You'll have:
- ✅ Working E2E test infrastructure
- ✅ Automated browser testing
- ✅ CI/CD integration
- ✅ Visual regression capability
- ✅ Accessibility testing
- ✅ Production-ready test suite

## Next Steps After First Test Passes

1. Seed test database with users
2. Add more navigation tests
3. Test authentication flows
4. Test form submissions
5. Test document uploads
6. Enable visual regression
7. Run accessibility audits
8. Enable parallel execution
9. Integrate with CI/CD
10. Document test results

---

**Time Estimate**: 30-60 minutes to first passing test  
**Difficulty**: Medium  
**Impact**: High - Enables confident deployments

