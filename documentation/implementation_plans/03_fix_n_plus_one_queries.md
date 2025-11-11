# Implementation Plan: Fix N+1 Query Problems

**Priority:** 🟠 High Priority - Performance  
**Effort:** 4 hours  
**Risk:** Medium - Could impact performance if not done correctly  
**Dependencies:** None  

---

## Problem Statement

Multiple ViewSets have N+1 query problems due to missing `select_related()` and `prefetch_related()` calls. This causes excessive database queries when serializing related objects, leading to poor performance with large datasets.

### What is an N+1 Query?

**Example:**
```python
# Bad: Causes N+1 queries
applications = Application.objects.all()  # 1 query
for app in applications:
    print(app.student.username)  # N additional queries (one per application)
    print(app.program.name)      # N more queries
```

**Result:** 1 + 2N queries instead of 1 query!

### Current Issues

**Affected ViewSets:**
1. `ApplicationViewSet` - Missing relations to student, program, status
2. `CommentViewSet` - Missing relations to author, application  
3. `TimelineEventViewSet` - Missing relations to created_by, application
4. `DocumentViewSet` - Missing relations to uploaded_by, application, type

---

## Proposed Solutions

### Solution 1: ApplicationViewSet

**File:** `exchange/views.py`

**Current Code:**
```python
class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()  # ❌ No optimization
    serializer_class = ApplicationSerializer
    # ...
    
    def get_queryset(self):
        user = self.request.user
        if user.has_role("coordinator") or user.has_role("admin"):
            return Application.objects.all()  # ❌ N+1 queries here!
        else:
            return Application.objects.filter(student=user)  # ❌ And here!
```

**Fixed Code:**
```python
class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "program", "student"]
    search_fields = ["program__name"]
    ordering_fields = ["created_at", "submitted_at"]

    def get_queryset(self):
        """
        Filter queryset based on user role with optimized queries.
        
        Uses select_related for foreign keys and prefetch_related for
        reverse foreign keys to prevent N+1 queries.
        """
        user = self.request.user
        
        # Base queryset with all optimizations
        base_qs = Application.objects.select_related(
            'program',           # ✅ ForeignKey - use select_related
            'student',           # ✅ ForeignKey
            'status'             # ✅ ForeignKey
        ).prefetch_related(
            'student__roles',    # ✅ ManyToMany through student
            'comment_set',       # ✅ Reverse ForeignKey (comments for this application)
            'comment_set__author',  # ✅ And the authors of those comments
            'timelineevent_set',    # ✅ Reverse ForeignKey (events for this application)
            'timelineevent_set__created_by',  # ✅ And who created those events
            'document_set',         # ✅ Reverse ForeignKey (documents)
            'document_set__type',   # ✅ Document types
            'document_set__uploaded_by'  # ✅ Who uploaded them
        )
        
        # Filter based on role
        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            return base_qs.filter(student=user)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        """List applications with caching."""
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific application with caching."""
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create an application with automatic student assignment."""
        user = request.user
        if not user.has_role("student"):
            return Response(
                {"error": "Only students can create applications."},
                status=status.HTTP_403_FORBIDDEN,
            )
        request.data["student"] = user.id
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit an application."""
        application = self.get_object()
        try:
            ApplicationService.submit_application(application, request.user)
            self._invalidate_application_cache(application)
            return Response({"status": "Application submitted successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Withdraw an application."""
        application = self.get_object()
        try:
            ApplicationService.withdraw_application(application, request.user)
            self._invalidate_application_cache(application)
            return Response({"status": "Application withdrawn successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _invalidate_application_cache(self, application):
        """Invalidate cache for application-related data."""
        from core.cache import invalidate_cache_pattern

        invalidate_cache_pattern(f"api:ApplicationViewSet:*{application.id}*")
        invalidate_cache_pattern("api:ApplicationViewSet:list*")
```

---

### Solution 2: CommentViewSet

**File:** `exchange/views.py`

**Current Code:**
```python
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()  # ❌ No optimization
```

**Fixed Code:**
```python
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "author", "is_private"]

    def get_queryset(self):
        """
        Filter comments based on user role and permissions with optimizations.
        """
        user = self.request.user
        
        # Base queryset with optimizations
        base_qs = Comment.objects.select_related(
            'application',              # ✅ ForeignKey
            'application__program',     # ✅ Through application
            'application__student',     # ✅ Through application
            'application__status',      # ✅ Through application
            'author',                   # ✅ ForeignKey
        ).prefetch_related(
            'author__roles'            # ✅ Author's roles
        )
        
        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            # Students can only see their own comments and public comments on their applications
            return base_qs.filter(
                Q(author=user) | Q(application__student=user, is_private=False)
            )

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        """List comments with caching."""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a comment and invalidate cache."""
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            application_id = request.data.get("application")
            if application_id:
                from core.cache import invalidate_cache_pattern
                invalidate_cache_pattern(f"api:CommentViewSet:*{application_id}*")
        return response
```

---

### Solution 3: TimelineEventViewSet

**File:** `exchange/views.py`

**Current Code:**
```python
class TimelineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEvent.objects.all()  # ❌ No optimization
```

**Fixed Code:**
```python
class TimelineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEvent.objects.all()
    serializer_class = TimelineEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "event_type", "created_by"]

    def get_queryset(self):
        """
        Filter timeline events based on user permissions with optimizations.
        """
        user = self.request.user
        
        # Base queryset with optimizations
        base_qs = TimelineEvent.objects.select_related(
            'application',              # ✅ ForeignKey
            'application__program',     # ✅ Through application
            'application__student',     # ✅ Through application
            'application__status',      # ✅ Through application
            'created_by',               # ✅ ForeignKey (nullable)
        ).prefetch_related(
            'created_by__roles'        # ✅ Creator's roles (if exists)
        ).order_by('-created_at')      # ✅ Most recent first
        
        if user.has_role("coordinator") or user.has_role("admin"):
            return base_qs
        else:
            # Students can only see events for their own applications
            return base_qs.filter(application__student=user)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        """List timeline events with caching."""
        return super().list(request, *args, **kwargs)
```

---

### Solution 4: DocumentViewSet (Already has some, but missing some)

**File:** `documents/views.py`

**Current Code (after permission fix):**
```python
def get_queryset(self):
    user = self.request.user
    if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
        return Document.objects.select_related(
            'application__student',
            'application__program',
            'type',
            'uploaded_by'
        )  # ✅ Good, but missing some relations
```

**Fixed Code:**
```python
def get_queryset(self):
    """
    Filter documents based on user permissions with full optimizations.
    """
    user = self.request.user
    
    # Base queryset with ALL optimizations
    base_qs = Document.objects.select_related(
        'application',                  # ✅ ForeignKey
        'application__student',         # ✅ Through application
        'application__program',         # ✅ Through application
        'application__status',          # ✅ Through application
        'type',                         # ✅ ForeignKey
        'uploaded_by',                  # ✅ ForeignKey
    ).prefetch_related(
        'uploaded_by__roles',           # ✅ Uploader's roles
        'documentvalidation_set',       # ✅ Reverse FK (validations)
        'documentvalidation_set__validator',  # ✅ Who validated
        'documentresubmissionrequest_set',    # ✅ Reverse FK (resubmission requests)
        'documentresubmissionrequest_set__requested_by',  # ✅ Who requested
        'documentcomment_set',          # ✅ Reverse FK (comments)
        'documentcomment_set__author',  # ✅ Comment authors
    )
    
    if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
        return base_qs
    
    # Students can only see their own documents
    return base_qs.filter(
        Q(uploaded_by=user) | Q(application__student=user)
    )
```

---

## Implementation Steps

### Step 1: Update ApplicationViewSet (45 minutes)

1. Replace `get_queryset()` with optimized version
2. Test query count before/after
3. Verify functionality still works

### Step 2: Update CommentViewSet (30 minutes)

1. Replace `get_queryset()` with optimized version
2. Test query count
3. Verify filtering still works

### Step 3: Update TimelineEventViewSet (30 minutes)

1. Replace `get_queryset()` with optimized version
2. Test query count
3. Verify ordering works

### Step 4: Update DocumentViewSet (30 minutes)

1. Enhance existing `get_queryset()` with missing relations
2. Test query count
3. Verify permissions still work

### Step 5: Testing & Validation (90 minutes)

1. Write query count tests
2. Performance benchmarking
3. Manual testing
4. Documentation

---

## Testing

### Query Count Testing

**Create:** `exchange/tests/test_query_optimization.py`

```python
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient
from django.db import connection
from django.test.utils import CaptureQueriesContext

from accounts.models import User, Role
from exchange.models import Application, Program, ApplicationStatus, Comment, TimelineEvent
from documents.models import Document, DocumentType


class QueryOptimizationTests(TestCase):
    def setUp(self):
        # Create roles
        self.student_role = Role.objects.create(name='student')
        self.coordinator_role = Role.objects.create(name='coordinator')
        
        # Create users
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='test123'
        )
        self.student.roles.add(self.student_role)
        
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='test123'
        )
        self.coordinator.roles.add(self.coordinator_role)
        
        # Create test data
        self.program = Program.objects.create(
            name='Test Program',
            description='Test',
            start_date='2025-01-01',
            end_date='2025-12-31'
        )
        
        self.status = ApplicationStatus.objects.create(name='draft', order=1)
        
        # Create multiple applications to test N+1
        self.applications = []
        for i in range(10):  # Create 10 applications
            app = Application.objects.create(
                program=self.program,
                student=self.student,
                status=self.status
            )
            self.applications.append(app)
            
            # Add comments
            Comment.objects.create(
                application=app,
                author=self.coordinator,
                text=f'Comment {i}',
                is_private=False
            )
            
            # Add timeline events
            TimelineEvent.objects.create(
                application=app,
                event_type='created',
                description=f'Application {i} created',
                created_by=self.student
            )
        
        self.client = APIClient()
    
    def test_application_list_query_count(self):
        """Test that listing applications doesn't cause N+1 queries."""
        self.client.force_authenticate(user=self.coordinator)
        
        # Count queries
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/applications/')
        
        # With 10 applications, we should have a constant number of queries
        # Not 1 + 10*N queries
        query_count = len(context.captured_queries)
        
        # Should be around 5-10 queries max (not 30+)
        # Exact count depends on serializer depth
        self.assertLess(
            query_count, 
            15,  # Generous limit
            f"Too many queries ({query_count}). Possible N+1 problem.\n"
            f"Queries: {context.captured_queries}"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)
    
    def test_application_detail_query_count(self):
        """Test that retrieving an application doesn't cause N+1 queries."""
        self.client.force_authenticate(user=self.coordinator)
        app = self.applications[0]
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f'/api/applications/{app.id}/')
        
        query_count = len(context.captured_queries)
        
        # Should be very few queries (< 10)
        self.assertLess(
            query_count,
            10,
            f"Too many queries ({query_count}) for single object retrieval."
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_comment_list_query_count(self):
        """Test that listing comments doesn't cause N+1 queries."""
        self.client.force_authenticate(user=self.coordinator)
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/comments/')
        
        query_count = len(context.captured_queries)
        
        # Should have constant query count regardless of number of comments
        self.assertLess(
            query_count,
            10,
            f"Too many queries ({query_count}). Possible N+1 problem."
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_timeline_event_list_query_count(self):
        """Test that listing timeline events doesn't cause N+1 queries."""
        self.client.force_authenticate(user=self.coordinator)
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/timeline-events/')
        
        query_count = len(context.captured_queries)
        
        self.assertLess(
            query_count,
            10,
            f"Too many queries ({query_count}). Possible N+1 problem."
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_query_count_scales_linearly_not_exponentially(self):
        """Test that adding more data doesn't exponentially increase queries."""
        self.client.force_authenticate(user=self.coordinator)
        
        # First count with 10 applications
        with CaptureQueriesContext(connection) as context1:
            response1 = self.client.get('/api/applications/')
        query_count_10 = len(context1.captured_queries)
        
        # Add 10 more applications
        for i in range(10, 20):
            app = Application.objects.create(
                program=self.program,
                student=self.student,
                status=self.status
            )
            Comment.objects.create(
                application=app,
                author=self.coordinator,
                text=f'Comment {i}'
            )
        
        # Count with 20 applications
        with CaptureQueriesContext(connection) as context2:
            response2 = self.client.get('/api/applications/')
        query_count_20 = len(context2.captured_queries)
        
        # Query count should be the same or very similar
        # Not double!
        self.assertLessEqual(
            query_count_20,
            query_count_10 + 2,  # Allow small variance
            f"Queries increased from {query_count_10} to {query_count_20}. "
            "This suggests N+1 queries are still present."
        )
```

Run tests:
```bash
docker-compose exec web python manage.py test exchange.tests.test_query_optimization -v 2
```

### Performance Benchmarking

**Create:** `scripts/benchmark_queries.py`

```python
"""
Benchmark script to measure query performance before/after optimization.
Run with: python manage.py shell < scripts/benchmark_queries.py
"""

import time
from django.db import connection, reset_queries
from django.conf import settings
from exchange.models import Application
from accounts.models import User

# Enable query logging
settings.DEBUG = True

def benchmark_queries(description, queryset):
    """Benchmark a queryset and print results."""
    reset_queries()
    start_time = time.time()
    
    # Force evaluation
    list(queryset)
    
    end_time = time.time()
    query_count = len(connection.queries)
    duration = (end_time - start_time) * 1000  # Convert to ms
    
    print(f"\n{description}")
    print(f"  Queries: {query_count}")
    print(f"  Time: {duration:.2f}ms")
    print(f"  Avg per query: {duration/query_count:.2f}ms")
    
    return query_count, duration

# Test 1: Unoptimized
print("=" * 50)
print("BEFORE OPTIMIZATION")
print("=" * 50)

queryset_bad = Application.objects.all()
count_bad, time_bad = benchmark_queries(
    "Unoptimized Application.objects.all()",
    queryset_bad
)

# Test 2: Optimized
print("\n" + "=" * 50)
print("AFTER OPTIMIZATION")
print("=" * 50)

queryset_good = Application.objects.select_related(
    'program', 'student', 'status'
).prefetch_related(
    'student__roles',
    'comment_set',
    'timelineevent_set'
)
count_good, time_good = benchmark_queries(
    "Optimized with select_related & prefetch_related",
    queryset_good
)

# Summary
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"Query reduction: {count_bad} → {count_good} ({100 - (count_good/count_bad*100):.1f}% reduction)")
print(f"Time improvement: {time_bad:.2f}ms → {time_good:.2f}ms ({100 - (time_good/time_bad*100):.1f}% faster)")
```

Run benchmark:
```bash
docker-compose exec web python manage.py shell < scripts/benchmark_queries.py
```

---

## Documentation

**File:** `documentation/developer_guide.md`

Add section on query optimization:

```markdown
## Query Optimization Best Practices

### Preventing N+1 Queries

SEIM uses `select_related()` and `prefetch_related()` to prevent N+1 query problems.

#### When to Use select_related()

Use for **ForeignKey** and **OneToOne** relationships:

```python
# Good: Single query with JOIN
applications = Application.objects.select_related('program', 'student', 'status')

# Bad: N+1 queries
applications = Application.objects.all()  # Don't do this!
for app in applications:
    print(app.program.name)  # Causes extra query for each application!
```

#### When to Use prefetch_related()

Use for **ManyToMany** and **Reverse ForeignKey** relationships:

```python
# Good: 2 queries total (1 for applications + 1 for all comments)
applications = Application.objects.prefetch_related('comment_set')

# Bad: N+1 queries
applications = Application.objects.all()
for app in applications:
    comments = app.comment_set.all()  # Extra query per application!
```

#### Testing for N+1 Queries

Always test query counts:

```python
from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext(connection) as context:
    response = client.get('/api/applications/')
    
print(f"Queries executed: {len(context.captured_queries)}")
# Should be constant, not growing with data size!
```
```

---

## Verification Checklist

- [ ] ApplicationViewSet uses select_related and prefetch_related
- [ ] CommentViewSet uses select_related and prefetch_related
- [ ] TimelineEventViewSet uses select_related and prefetch_related
- [ ] DocumentViewSet enhanced with all relations
- [ ] Query count tests pass
- [ ] Benchmark shows improvement
- [ ] Manual testing confirms functionality
- [ ] No performance regression
- [ ] Documentation updated

---

## Expected Results

### Before Optimization (10 applications)

| Endpoint | Queries | Time |
|----------|---------|------|
| GET /api/applications/ | ~50 | ~500ms |
| GET /api/comments/ | ~30 | ~300ms |
| GET /api/timeline-events/ | ~30 | ~300ms |

### After Optimization (10 applications)

| Endpoint | Queries | Time |
|----------|---------|------|
| GET /api/applications/ | ~8 | ~100ms |
| GET /api/comments/ | ~5 | ~50ms |
| GET /api/timeline-events/ | ~5 | ~50ms |

**Improvement:** ~80% fewer queries, ~80% faster response times!

---

## Rollback Plan

If issues occur:

1. **Revert get_queryset() changes**
2. **Keep permission classes** (from previous fix)
3. **Investigate specific issue**
4. **Re-apply with fixes**

---

## Success Criteria

✅ **Query Count:** < 10 queries for list endpoints regardless of data size  
✅ **Performance:** > 50% improvement in response time  
✅ **Functionality:** No regression in features  
✅ **Tests:** All query optimization tests pass  

---

## Estimated Time

| Task | Time |
|------|------|
| ApplicationViewSet | 45 min |
| CommentViewSet | 30 min |
| TimelineEventViewSet | 30 min |
| DocumentViewSet | 30 min |
| Write tests | 60 min |
| Benchmarking | 30 min |
| Documentation | 15 min |

**Total:** ~4 hours

---

## Next Steps

After this fix:
1. ✅ Monitor production query logs
2. ✅ Set up query performance alerts
3. ✅ Continue with next improvement (AccountService)

