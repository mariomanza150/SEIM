# Implementation Plan: Add Permissions to DocumentViewSet

**Priority:** 🔴 Critical Security Issue  
**Effort:** 1 hour  
**Risk:** High - Currently allows unauthenticated access to documents  
**Dependencies:** None  

---

## Problem Statement

The `DocumentViewSet` in `documents/views.py` has no permission classes defined, allowing unauthenticated users to access, create, update, and delete documents. This is a critical security vulnerability.

### Current Code

**File:** `documents/views.py` (Lines 38-48)

```python
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    # ❌ NO PERMISSION CLASSES!

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

### Security Risks

1. **Unauthenticated Access:** Anyone can view all documents
2. **Unauthorized Modifications:** Anyone can create/update/delete documents
3. **Data Leakage:** Sensitive student documents exposed
4. **Compliance Issues:** Violates data privacy requirements

---

## Proposed Solution

### Step 1: Add Permission Classes

**File:** `documents/views.py`

```python
from django.shortcuts import render
from rest_framework import permissions, viewsets
from django.db.models import Q

from core.cache import cache_api_response
from core.permissions import IsOwnerOrAdmin

from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
)
from .serializers import (
    DocumentCommentSerializer,
    DocumentResubmissionRequestSerializer,
    DocumentSerializer,
    DocumentTypeSerializer,
    DocumentValidationSerializer,
)


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ Add this

    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]  # ✅ Add this

    def get_queryset(self):  # ✅ Add filtering
        """
        Filter documents based on user permissions.
        - Students: Only their own documents
        - Coordinators/Admins: All documents
        """
        user = self.request.user
        
        # Coordinators and admins can see all documents
        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return Document.objects.select_related(
                'application__student',
                'application__program',
                'type',
                'uploaded_by'
            )
        
        # Students can only see their own documents
        return Document.objects.filter(
            Q(uploaded_by=user) | Q(application__student=user)
        ).select_related(
            'application__student',
            'application__program',
            'type',
            'uploaded_by'
        )

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def perform_create(self, serializer):  # ✅ Add this
        """Set uploaded_by to current user on creation."""
        serializer.save(uploaded_by=self.request.user)


class DocumentValidationViewSet(viewsets.ModelViewSet):
    queryset = DocumentValidation.objects.all()
    serializer_class = DocumentValidationSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ Add this
    
    def get_queryset(self):  # ✅ Add filtering
        """Filter validations based on user permissions."""
        user = self.request.user
        
        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return DocumentValidation.objects.select_related(
                'document',
                'validator'
            )
        
        # Students can only see validations for their documents
        return DocumentValidation.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            'document',
            'validator'
        )

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentResubmissionRequestViewSet(viewsets.ModelViewSet):
    queryset = DocumentResubmissionRequest.objects.all()
    serializer_class = DocumentResubmissionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ Add this
    
    def get_queryset(self):  # ✅ Add filtering
        """Filter resubmission requests based on user permissions."""
        user = self.request.user
        
        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return DocumentResubmissionRequest.objects.select_related(
                'document',
                'requested_by'
            )
        
        # Students can only see requests for their documents
        return DocumentResubmissionRequest.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            'document',
            'requested_by'
        )

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentCommentViewSet(viewsets.ModelViewSet):
    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]  # ✅ Add this
    
    def get_queryset(self):  # ✅ Add filtering
        """Filter comments based on user permissions."""
        user = self.request.user
        
        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return DocumentComment.objects.select_related(
                'document',
                'author'
            )
        
        # Students can only see public comments on their documents
        return DocumentComment.objects.filter(
            Q(author=user) | 
            Q(document__application__student=user, is_private=False)
        ).select_related(
            'document',
            'author'
        )
    
    def perform_create(self, serializer):  # ✅ Add this
        """Set author to current user on creation."""
        serializer.save(author=self.request.user)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

---

## Implementation Steps

### Step 1: Update documents/views.py (10 minutes)

1. Add imports at the top of the file
2. Add `permission_classes` to all ViewSets
3. Add `get_queryset()` methods for filtering
4. Add `perform_create()` methods where needed

### Step 2: Verify IsOwnerOrAdmin Permission Exists (5 minutes)

**File:** `core/permissions.py`

Verify this permission class exists:

```python
class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access if user is admin/staff or is the object's owner (student)."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or getattr(obj, "student", None) == request.user
```

**If it doesn't exist**, add it to `core/permissions.py`.

### Step 3: Update DocumentSerializer (5 minutes)

**File:** `documents/serializers.py`

Ensure uploaded_by is read-only:

```python
class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)  # ✅ Add read_only
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'validated_at']  # ✅ Add this
```

### Step 4: Test the Changes (30 minutes)

#### Manual Testing

1. **Test Unauthenticated Access (Should Fail)**
   ```bash
   curl -X GET http://localhost:8000/api/documents/
   # Expected: 401 Unauthorized
   ```

2. **Test Student Access (Should See Only Own Documents)**
   ```bash
   # Login as student
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"login":"student","password":"student123"}'
   
   # Get documents with token
   curl -X GET http://localhost:8000/api/documents/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   # Expected: Only student's own documents
   ```

3. **Test Coordinator Access (Should See All)**
   ```bash
   # Login as coordinator
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"login":"coordinator","password":"coordinator123"}'
   
   # Get documents with token
   curl -X GET http://localhost:8000/api/documents/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   # Expected: All documents
   ```

#### Automated Tests

**Create:** `documents/tests/test_permissions.py`

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Role
from exchange.models import Application, Program, ApplicationStatus
from documents.models import Document, DocumentType


class DocumentPermissionTests(TestCase):
    def setUp(self):
        # Create roles
        self.student_role = Role.objects.create(name='student')
        self.coordinator_role = Role.objects.create(name='coordinator')
        
        # Create users
        self.student1 = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='test123'
        )
        self.student1.roles.add(self.student_role)
        
        self.student2 = User.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='test123'
        )
        self.student2.roles.add(self.student_role)
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='test123'
        )
        self.coordinator.roles.add(self.coordinator_role)
        
        # Create program and applications
        self.program = Program.objects.create(
            name='Test Program',
            description='Test',
            start_date='2025-01-01',
            end_date='2025-12-31'
        )
        
        status_draft = ApplicationStatus.objects.create(name='draft', order=1)
        
        self.app1 = Application.objects.create(
            program=self.program,
            student=self.student1,
            status=status_draft
        )
        
        self.app2 = Application.objects.create(
            program=self.program,
            student=self.student2,
            status=status_draft
        )
        
        # Create document type
        self.doc_type = DocumentType.objects.create(
            name='Transcript',
            description='Academic transcript'
        )
        
        # Create documents
        self.doc1 = Document.objects.create(
            application=self.app1,
            type=self.doc_type,
            file='test1.pdf',
            uploaded_by=self.student1
        )
        
        self.doc2 = Document.objects.create(
            application=self.app2,
            type=self.doc_type,
            file='test2.pdf',
            uploaded_by=self.student2
        )
        
        self.client = APIClient()
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access documents."""
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_student_sees_only_own_documents(self):
        """Test that students can only see their own documents."""
        self.client.force_authenticate(user=self.student1)
        response = self.client.get('/api/documents/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see doc1, not doc2
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(self.doc1.id))
    
    def test_coordinator_sees_all_documents(self):
        """Test that coordinators can see all documents."""
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.get('/api/documents/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see both documents
        self.assertEqual(len(response.data['results']), 2)
    
    def test_student_cannot_access_other_student_document(self):
        """Test that students cannot access other students' documents."""
        self.client.force_authenticate(user=self.student1)
        response = self.client.get(f'/api/documents/{self.doc2.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_document_creation_sets_uploaded_by(self):
        """Test that uploaded_by is automatically set to current user."""
        self.client.force_authenticate(user=self.student1)
        
        data = {
            'application': str(self.app1.id),
            'type': self.doc_type.id,
            'file': 'test3.pdf'
        }
        
        response = self.client.post('/api/documents/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify uploaded_by was set correctly
        new_doc = Document.objects.get(id=response.data['id'])
        self.assertEqual(new_doc.uploaded_by, self.student1)
```

Run tests:
```bash
docker-compose exec web python manage.py test documents.tests.test_permissions
```

### Step 5: Update API Documentation (10 minutes)

**File:** `documentation/api_documentation.md`

Add permission requirements:

```markdown
## Documents Endpoints

### List Documents
**GET** `/api/documents/`

**Authentication:** Required  
**Permissions:** 
- Students: Can only see their own documents
- Coordinators/Admins: Can see all documents

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "application": "uuid",
      "type": 1,
      "file": "url",
      "uploaded_by": "username",
      "is_valid": false
    }
  ]
}
```
```

---

## Verification Checklist

Before deploying:

- [ ] Permission classes added to all ViewSets in documents/views.py
- [ ] `get_queryset()` methods filter by user role
- [ ] `perform_create()` sets uploaded_by automatically
- [ ] IsOwnerOrAdmin permission exists in core/permissions.py
- [ ] DocumentSerializer has uploaded_by as read_only
- [ ] Manual testing completed (unauthenticated, student, coordinator)
- [ ] Automated tests pass
- [ ] API documentation updated
- [ ] Cache invalidation still works
- [ ] No regression in existing functionality

---

## Rollback Plan

If issues occur:

1. **Immediate:** Comment out permission_classes:
   ```python
   # permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
   ```

2. **Deploy Fix:** Revert the changes:
   ```bash
   git revert <commit-hash>
   ```

3. **Investigate:** Review error logs and test failures

---

## Post-Deployment Monitoring

Monitor for:

1. **401 Errors:** Increase in unauthorized access attempts (expected, good!)
2. **403 Errors:** Users getting forbidden when they should have access (bad!)
3. **Performance:** Check if get_queryset() filtering impacts performance
4. **User Reports:** Students unable to see their documents

**Monitoring Queries:**
```python
# Check recent 401/403 errors
from django.contrib.admin.models import LogEntry
LogEntry.objects.filter(
    action_time__gte=timezone.now() - timedelta(hours=24)
).count()
```

---

## Estimated Time Breakdown

| Task | Time |
|------|------|
| Update views.py | 10 min |
| Verify/create permissions | 5 min |
| Update serializer | 5 min |
| Manual testing | 15 min |
| Write automated tests | 20 min |
| Run tests | 5 min |
| Update documentation | 10 min |

**Total:** ~70 minutes (1 hour 10 minutes with buffer)

---

## Success Criteria

✅ **Security Fixed:** Unauthenticated users cannot access documents  
✅ **Privacy Maintained:** Students can only see their own documents  
✅ **Admin Access:** Coordinators and admins can see all documents  
✅ **Tests Pass:** All automated tests pass  
✅ **No Regression:** Existing functionality still works  
✅ **Performance:** No significant performance degradation  

---

## Next Steps

After this fix:
1. ✅ Monitor for 24 hours
2. ✅ Review error logs
3. ✅ Gather user feedback
4. ✅ Document any edge cases
5. ✅ Move to next critical fix (CORS configuration)

