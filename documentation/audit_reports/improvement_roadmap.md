# SEIM Codebase Improvement Roadmap

**Date:** October 15, 2025  
**Based On:** Comprehensive code audit of backend, frontend, and documentation  
**Version:** 1.0.0

---

## Executive Summary

This roadmap consolidates findings from three comprehensive audits:
- **Backend Audit:** 3.7/5.0 ⭐⭐⭐⭐
- **Frontend Audit:** 4.0/5.0 ⭐⭐⭐⭐
- **Documentation Audit:** 3.5/5.0 ⭐⭐⭐⭐

**Overall Project Health: 3.7/5.0** ⭐⭐⭐⭐

The SEIM codebase is **production-ready** with a solid architectural foundation, modern tooling, and comprehensive features. The main areas for improvement are query optimization, testing coverage, and documentation accuracy.

---

## Priority Classification

- 🔴 **Critical** - Security issues, data integrity risks, production blockers
- 🟠 **High** - Performance issues, significant technical debt
- 🟡 **Medium** - Code quality, maintainability improvements
- 🟢 **Low** - Nice-to-have enhancements, cosmetic issues

---

## Phase 1: Critical Issues (Week 1)

### 🔴 Critical Priority

#### 1. Add Missing Permissions to DocumentViewSet
**Category:** Security  
**Affected File:** `documents/views.py`  
**Issue:** DocumentViewSet has no permission classes, allowing unauthenticated access  
**Impact:** Critical security vulnerability  
**Effort:** 1 hour  

**Solution:**
```python
from rest_framework import permissions
from core.permissions import IsOwnerOrAdmin

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
```

#### 2. Fix CORS Configuration for Production
**Category:** Security  
**Affected File:** `seim/settings/production.py`  
**Issue:** `CORS_ALLOW_ALL_ORIGINS = True` in production  
**Impact:** Security risk - allows any domain  
**Effort:** 30 minutes  

**Solution:**
```python
# settings/production.py
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
```

**Estimated Total Time:** 1.5 hours  
**Sprint:** Week 1, Day 1-2

---

### 🟠 High Priority - Performance

#### 3. Fix N+1 Queries in ViewSets
**Category:** Performance  
**Affected Files:** `exchange/views.py`, `documents/views.py`, `notifications/views.py`  
**Issue:** Missing select_related/prefetch_related causing N+1 queries  
**Impact:** Poor performance with large datasets  
**Effort:** 4 hours  

**Solution for ApplicationViewSet:**
```python
class ApplicationViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related(
            'program', 
            'student', 
            'status'
        ).prefetch_related(
            'student__roles',
            'comment_set',
            'timelineevent_set'
        )
        
        if user.has_role("coordinator") or user.has_role("admin"):
            return qs
        else:
            return qs.filter(student=user)
```

**Files to Update:**
- `exchange/views.py`: ApplicationViewSet, CommentViewSet, TimelineEventViewSet
- `documents/views.py`: DocumentViewSet
- `notifications/views.py`: NotificationViewSet (if exists)

**Estimated Total Time:** 4 hours  
**Sprint:** Week 1, Day 3-4

---

### 🟡 Medium Priority - Code Quality

#### 4. Fix Documentation Accuracy Issues
**Category:** Documentation  
**Affected Files:** `README.md`, `documentation/architecture.md`  
**Issue:** Outdated architecture diagrams showing React/Vue instead of actual stack  
**Impact:** Developer confusion, onboarding difficulty  
**Effort:** 2 hours  

**Changes:**
1. Update architecture diagram in README.md (lines 437-454)
2. Update architecture.md frontend section (lines 10-28)
3. Correct environment_variables.md Redis DB number

**Estimated Total Time:** 2 hours  
**Sprint:** Week 1, Day 5

---

## Phase 2: High-Priority Improvements (Month 1)

### 🟠 High Priority - Architecture

#### 5. Move Business Logic from Models to Services
**Category:** Architecture, Maintainability  
**Affected Files:** `accounts/models.py`, `accounts/serializers.py`  
**Issue:** Business logic in User model and LoginSerializer  
**Impact:** Violates Single Responsibility Principle  
**Effort:** 8 hours  

**Create:** `accounts/services.py`
```python
from django.db import transaction
from django.utils import timezone

class AccountService:
    """Service for account-related business logic."""
    
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    @staticmethod
    @transaction.atomic
    def increment_failed_login_attempts(user):
        """Increment failed login attempts and lock account if threshold reached."""
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= AccountService.MAX_LOGIN_ATTEMPTS:
            user.lockout_until = timezone.now() + timezone.timedelta(
                minutes=AccountService.LOCKOUT_DURATION_MINUTES
            )
            user.failed_login_attempts = 0
        user.save()
        return user
    
    @staticmethod
    def is_locked_out(user):
        """Check if account is currently locked out."""
        return (user.lockout_until is not None and 
                user.lockout_until > timezone.now())
    
    @staticmethod
    @transaction.atomic
    def unlock_account(user):
        """Unlock a locked account."""
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.save()
        return user
    
    @staticmethod
    @transaction.atomic
    def verify_email(user, token):
        """Verify user email with token."""
        if user.email_verification_token != token:
            raise ValueError("Invalid verification token")
        if user.is_email_verified:
            raise ValueError("Email already verified")
        
        user.is_email_verified = True
        user.is_active = True
        user.email_verification_token = None
        user.save()
        return user
```

**Refactor:**
- Remove methods from User model
- Update LoginSerializer to use AccountService
- Update RegistrationSerializer to use AccountService

**Estimated Total Time:** 8 hours  
**Sprint:** Month 1, Week 2

---

#### 6. Add Database Indexes
**Category:** Performance  
**Affected Files:** `exchange/models.py`, `documents/models.py`, `notifications/models.py`  
**Issue:** Missing indexes on frequently queried fields  
**Impact:** Slow queries as data grows  
**Effort:** 2 hours + migration  

**Solution for Application model:**
```python
class Application(UUIDModel, TimeStampedModel):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['student', 'status'], name='app_student_status_idx'),
            models.Index(fields=['program', 'status'], name='app_program_status_idx'),
            models.Index(fields=['submitted_at'], name='app_submitted_idx'),
            models.Index(fields=['student', 'withdrawn'], name='app_student_withdrawn_idx'),
        ]
        ordering = ['-created_at']
```

**Models to Update:**
- `Application`: student+status, program+status, submitted_at
- `Document`: application+type, uploaded_by, validated_at
- `Notification`: recipient+is_read, sent_at

**Estimated Total Time:** 2 hours  
**Sprint:** Month 1, Week 2

---

#### 7. Create Custom Permission Classes
**Category:** Architecture, Consistency  
**Affected File:** `exchange/views.py`  
**Issue:** Inline permission checks instead of permission classes  
**Impact:** Code duplication, harder to test  
**Effort:** 3 hours  

**Create:** `core/permissions.py` additions
```python
class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow admins to write, others to read."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_role('admin')

class IsStudentOrReadOnly(permissions.BasePermission):
    """Allow students to write their own data, others to read."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_role('student')
```

**Update:** `exchange/views.py`
```python
class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    # Remove inline permission checks
```

**Estimated Total Time:** 3 hours  
**Sprint:** Month 1, Week 3

---

#### 8. Add API Rate Limiting
**Category:** Security, Performance  
**Affected File:** `seim/settings/base.py`  
**Issue:** No rate limiting on API endpoints  
**Impact:** Vulnerable to abuse  
**Effort:** 1 hour  

**Solution:**
```python
# settings/base.py
REST_FRAMEWORK = {
    # ... existing settings ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '10/minute'  # For login/register
    }
}
```

**Add Custom Throttle:**
```python
# core/throttling.py
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'
```

**Update Login/Register Views:**
```python
class LoginView(generics.GenericAPIView):
    throttle_classes = [BurstRateThrottle]
    # ...
```

**Estimated Total Time:** 1 hour  
**Sprint:** Month 1, Week 3

---

### 🟡 Medium Priority - Frontend

#### 9. Fix Duplicate Code in auth.js
**Category:** Code Quality  
**Affected File:** `static/js/modules/auth.js`  
**Issue:** handleLogin and login functions have duplicate logic  
**Impact:** Code maintenance difficulty  
**Effort:** 2 hours  

**Solution:** Consolidate into single function

**Estimated Total Time:** 2 hours  
**Sprint:** Month 1, Week 3

---

#### 10. Implement Token Expiry Handling
**Category:** Security, UX  
**Affected File:** `static/js/modules/auth.js`  
**Issue:** tokenExpiry set but never used  
**Impact:** Tokens expire without auto-refresh  
**Effort:** 3 hours  

**Solution:**
```javascript
// Check token expiry and refresh if needed
async function ensureValidToken() {
    const tokenExpiry = localStorage.getItem('seim_token_expiry');
    if (!tokenExpiry) return true;
    
    const expiryTime = new Date(tokenExpiry);
    const now = new Date();
    const fiveMinutes = 5 * 60 * 1000;
    
    // Refresh if expiring within 5 minutes
    if (expiryTime - now < fiveMinutes) {
        return await refreshToken();
    }
    return true;
}

// Update storeTokens to save expiry
function storeTokens(access, refresh) {
    localStorage.setItem('seim_access_token', access);
    localStorage.setItem('seim_refresh_token', refresh);
    
    // Decode JWT to get expiry (simple base64 decode)
    const payload = JSON.parse(atob(access.split('.')[1]));
    const expiryDate = new Date(payload.exp * 1000);
    localStorage.setItem('seim_token_expiry', expiryDate.toISOString());
}
```

**Estimated Total Time:** 3 hours  
**Sprint:** Month 1, Week 4

---

#### 11. Add Cross-Platform Build Scripts
**Category:** Developer Experience  
**Affected File:** `package.json`  
**Issue:** Build scripts use Windows-specific `set` command  
**Impact:** Won't work on Unix systems  
**Effort:** 1 hour  

**Solution:**
```bash
npm install --save-dev cross-env
```

```json
{
  "scripts": {
    "build": "cross-env LOG_LEVEL=ERROR webpack --mode production",
    "dev": "cross-env LOG_LEVEL=DEBUG webpack --mode development --watch",
  }
}
```

**Estimated Total Time:** 1 hour  
**Sprint:** Month 1, Week 4

---

## Phase 3: Medium-Priority Improvements (Quarter 1)

### 🟡 Medium Priority - Testing

#### 12. Implement Backend Unit Tests
**Category:** Testing, Quality Assurance  
**Affected Files:** Create new test files  
**Issue:** Minimal test coverage  
**Impact:** Regression risk  
**Effort:** 20 hours  

**Test Structure:**
```
tests/
├── unit/
│   ├── test_account_service.py
│   ├── test_application_service.py
│   ├── test_document_service.py
│   ├── test_analytics_service.py
│   ├── test_notification_service.py
│   ├── test_permissions.py
│   └── test_serializers.py
├── integration/
│   ├── test_api_authentication.py
│   ├── test_api_programs.py
│   ├── test_api_applications.py
│   └── test_workflow.py
└── fixtures/
    └── factories.py
```

**Priority Tests:**
1. Service layer methods (critical business logic)
2. Permission classes
3. Serializer validation
4. Model methods with business logic
5. API endpoints

**Coverage Goal:** 80%+

**Estimated Total Time:** 20 hours  
**Sprint:** Q1, Weeks 5-7

---

#### 13. Implement Frontend Unit Tests
**Category:** Testing  
**Affected Files:** Create new test files  
**Issue:** Test structure exists but implementation needed  
**Impact:** No frontend regression detection  
**Effort:** 15 hours  

**Test Structure:**
```
tests/frontend/
├── unit/
│   ├── api.test.js
│   ├── auth.test.js
│   ├── validators.test.js
│   ├── ui-loading.test.js
│   └── ui-auth.test.js
├── integration/
│   ├── auth-flow.test.js
│   ├── form-submission.test.js
│   └── error-handling.test.js
└── e2e/
    ├── user-registration.spec.js
    ├── application-workflow.spec.js
    └── document-upload.spec.js
```

**Priority Tests:**
1. API client (caching, error handling)
2. Authentication flow
3. Form validation
4. UI state management

**Estimated Total Time:** 15 hours  
**Sprint:** Q1, Weeks 7-9

---

### 🟡 Medium Priority - Code Quality

#### 14. Add Type Hints to Backend
**Category:** Code Quality, IDE Support  
**Affected Files:** All Python files  
**Issue:** Limited type hint coverage (~5%)  
**Impact:** Harder to maintain, less IDE support  
**Effort:** 20 hours  

**Priority Areas:**
1. Service layer public methods
2. Serializers
3. ViewSet methods
4. Utility functions

**Example:**
```python
from typing import List, Optional, Dict, Any
from accounts.models import User
from exchange.models import Application

class ApplicationService:
    @staticmethod
    @transaction.atomic
    def submit_application(
        application: Application, 
        user: User
    ) -> Application:
        """Submit an application."""
        # ...
        return application
    
    @staticmethod
    def check_eligibility(
        student: User, 
        program: Program
    ) -> bool:
        """Check eligibility."""
        # ...
        return True
```

**Estimated Total Time:** 20 hours  
**Sprint:** Q1, Weeks 8-10 (incremental)

---

#### 15. Add JSDoc to Frontend Modules
**Category:** Documentation, Code Quality  
**Affected Files:** All JS modules  
**Issue:** ~10% JSDoc coverage  
**Impact:** Poor IDE support, unclear APIs  
**Effort:** 10 hours  

**Priority:**
1. Public exported functions
2. Complex async functions
3. API client methods
4. Authentication functions

**Example:**
```javascript
/**
 * Make an authenticated API request with automatic token refresh.
 * 
 * @param {string} url - The API endpoint URL
 * @param {Object} [options={}] - Fetch options
 * @param {string} [options.method='GET'] - HTTP method
 * @param {Object} [options.headers] - Custom headers
 * @param {string} [options.body] - Request body (JSON string)
 * @returns {Promise<Object>} API response data
 * @throws {Error} When request fails or network error occurs
 * 
 * @example
 * const data = await apiRequest('/api/programs/', { method: 'GET' });
 * console.log(data);
 */
export async function apiRequest(url, options = {}) {
    // ...
}
```

**Estimated Total Time:** 10 hours  
**Sprint:** Q1, Weeks 10-11

---

#### 16. Create Custom Exception Hierarchy
**Category:** Code Quality, Error Handling  
**Affected Files:** Create `core/exceptions.py`, update services  
**Issue:** Using generic ValueError/Exception  
**Impact:** Less specific error handling  
**Effort:** 2 hours  

**Solution:**
```python
# core/exceptions.py
class SEIMException(Exception):
    """Base exception for SEIM application."""
    pass

class ValidationException(SEIMException):
    """Raised when validation fails."""
    pass

class AuthenticationException(SEIMException):
    """Raised when authentication fails."""
    pass

class PermissionDeniedException(SEIMException):
    """Raised when permission is denied."""
    pass

class DocumentException(SEIMException):
    """Base exception for document operations."""
    pass

class InvalidFileTypeError(DocumentException):
    """Raised when file type is not allowed."""
    pass

class FileSizeExceededError(DocumentException):
    """Raised when file size exceeds limit."""
    pass

class VirusScanFailedError(DocumentException):
    """Raised when virus scan fails."""
    pass
```

**Update Services:**
```python
from core.exceptions import InvalidFileTypeError, FileSizeExceededError

class DocumentService:
    @staticmethod
    def validate_file_type_and_size(file):
        if mime_type not in DocumentService.ALLOWED_FILE_TYPES:
            raise InvalidFileTypeError(f"File type {mime_type} not allowed")
        if file.size > DocumentService.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise FileSizeExceededError(f"File size exceeds {DocumentService.MAX_FILE_SIZE_MB}MB")
        return True
```

**Estimated Total Time:** 2 hours  
**Sprint:** Q1, Week 11

---

### 🟡 Medium Priority - Documentation

#### 17. Add Comprehensive Cache Documentation
**Category:** Documentation  
**Affected Files:** Create `documentation/caching_guide.md`  
**Issue:** Caching system underdocumented  
**Impact:** Developers don't know how to use cache  
**Effort:** 4 hours  

**Contents:**
1. Cache architecture overview
2. Cache decorator usage
3. Cache invalidation strategies
4. Performance monitoring
5. Configuration options
6. Best practices

**Estimated Total Time:** 4 hours  
**Sprint:** Q1, Week 12

---

## Phase 4: Low-Priority Enhancements (Ongoing)

### 🟢 Low Priority

#### 18. Move Magic Numbers to Settings (2 hours)
- Extract hard-coded values to configuration
- Files: Services, models

#### 19. Explicit Serializer Fields (1 hour)
- Replace `fields = "__all__"` with explicit lists
- Files: All serializers

#### 20. Add Admin Filters (2 hours)
- Add list_filter and date_hierarchy to admin classes
- Files: All admin.py files

#### 21. Add CSS Linting (2 hours)
- Install and configure stylelint
- File: Create `.stylelintrc.json`

#### 22. Accessibility Audit (8 hours)
- Manual WCAG audit
- Add automated testing (axe-core)
- Fix identified issues

#### 23. Template Linting (2 hours)
- Install djlint
- Configure and fix issues

#### 24. Consolidate CSS Approach (6 hours)
- Standardize on utility-first or component-based
- Refactor existing styles

---

## Summary by Effort

### Quick Wins (< 2 hours each)
1. Add permissions to DocumentViewSet (1h)
2. Fix CORS configuration (0.5h)
3. Fix documentation inaccuracies (2h)
4. Add API rate limiting (1h)
5. Cross-platform build scripts (1h)

**Total:** 5.5 hours

### Medium Effort (2-8 hours each)
6. Fix N+1 queries (4h)
7. Move business logic to services (8h)
8. Add database indexes (2h)
9. Create custom permission classes (3h)
10. Fix duplicate auth.js code (2h)
11. Implement token expiry handling (3h)
12. Create custom exceptions (2h)
13. Cache documentation (4h)

**Total:** 28 hours

### Large Effort (> 8 hours each)
14. Backend unit tests (20h)
15. Frontend unit tests (15h)
16. Add type hints (20h)
17. Add JSDoc (10h)

**Total:** 65 hours

---

## Timeline Estimate

| Phase | Duration | Effort | Key Deliverables |
|-------|----------|--------|------------------|
| **Phase 1** | Week 1 | 7.5h | Security fixes, N+1 queries fixed |
| **Phase 2** | Weeks 2-4 | 20h | Services refactored, permissions standardized |
| **Phase 3** | Weeks 5-12 | 65h | Tests implemented, type hints added |
| **Phase 4** | Ongoing | 23h | Polish and enhancements |

**Total Estimated Effort:** ~115 hours (14-15 working days)

---

## Success Metrics

### Code Quality
- [ ] Backend test coverage: 80%+
- [ ] Frontend test coverage: 70%+
- [ ] Type hint coverage: 60%+
- [ ] JSDoc coverage: 70%+
- [ ] All critical security issues resolved
- [ ] All N+1 queries fixed

### Documentation
- [ ] All architecture diagrams accurate
- [ ] API documentation complete
- [ ] Cache system documented
- [ ] All setup instructions verified

### Performance
- [ ] Database queries optimized
- [ ] API response times < 200ms (p95)
- [ ] Bundle sizes under 50KB (gzipped)

---

## Prioritization Matrix

```
   Impact
   High  │  3, 5, 12, 13  │  1, 2, 6, 8
         │                │
   Medium│  7, 9, 14, 17  │  10, 11, 15, 16
         │                │
   Low   │  18, 19, 22    │  20, 21, 23, 24
         └────────────────┴────────────────
           Low              High
                Urgency
```

---

## Conclusion

The SEIM codebase is in **excellent shape** for a production application. The architecture is solid, the code is clean, and modern best practices are followed. The improvements outlined in this roadmap will:

1. **Close critical security gaps** (Phase 1)
2. **Optimize performance** (Phases 1-2)
3. **Improve maintainability** (Phases 2-3)
4. **Ensure quality** (Phase 3)
5. **Polish the application** (Phase 4)

With these improvements implemented, SEIM will be a **4.5/5.0 quality codebase** suitable for enterprise production use.

---

**Document Version:** 1.0.0  
**Last Updated:** October 15, 2025  
**Next Review:** January 15, 2026

