"""
Tests for SavedSearch model and API.
"""

import pytest
from rest_framework.test import APIClient

from exchange.models import SavedSearch


@pytest.mark.django_db
class TestSavedSearchModel:
    """Test SavedSearch model."""
    
    def test_create_saved_search(self, user_coordinator):
        """Test creating a saved search."""
        search = SavedSearch.objects.create(
            user=user_coordinator,
            name="Active Programs",
            search_type="program",
            filters={'is_active': True, 'min_gpa_max': 3.5}
        )
        
        assert search.id is not None
        assert search.name == "Active Programs"
        assert search.search_type == "program"
        assert search.filters['is_active'] is True
        assert not search.is_default
    
    def test_set_default_search(self, user_coordinator):
        """Test setting a search as default."""
        search1 = SavedSearch.objects.create(
            user=user_coordinator,
            name="Search 1",
            search_type="program",
            filters={'is_active': True},
            is_default=True
        )
        
        # Create second search and set as default
        search2 = SavedSearch.objects.create(
            user=user_coordinator,
            name="Search 2",
            search_type="program",
            filters={'recurring': True},
            is_default=True
        )
        
        # First search should no longer be default
        search1.refresh_from_db()
        assert not search1.is_default
        assert search2.is_default
    
    def test_multiple_defaults_per_type(self, user_coordinator):
        """Test that default is per search type."""
        program_search = SavedSearch.objects.create(
            user=user_coordinator,
            name="Default Program Search",
            search_type="program",
            filters={'is_active': True},
            is_default=True
        )
        
        app_search = SavedSearch.objects.create(
            user=user_coordinator,
            name="Default Application Search",
            search_type="application",
            filters={'withdrawn': False},
            is_default=True
        )
        
        # Both should be default (different types)
        assert program_search.is_default
        assert app_search.is_default
    
    def test_user_can_have_multiple_searches(self, user_coordinator):
        """Test user can have multiple saved searches."""
        search1 = SavedSearch.objects.create(
            user=user_coordinator,
            name="Active Programs",
            search_type="program",
            filters={'is_active': True}
        )
        
        search2 = SavedSearch.objects.create(
            user=user_coordinator,
            name="High GPA Programs",
            search_type="program",
            filters={'min_gpa_min': 3.5}
        )
        
        searches = SavedSearch.objects.filter(user=user_coordinator)
        assert searches.count() == 2


@pytest.mark.django_db
class TestSavedSearchAPI:
    """Test SavedSearch API endpoints."""
    
    def test_list_saved_searches(self, api_client_authenticated_coordinator, saved_searches):
        """Test listing saved searches."""
        response = api_client_authenticated_coordinator.get('/api/saved-searches/')
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert len(data['results']) == len(saved_searches)
    
    def test_create_saved_search(self, api_client_authenticated_coordinator):
        """Test creating a saved search via API."""
        response = api_client_authenticated_coordinator.post('/api/saved-searches/', {
            'name': 'New Search',
            'search_type': 'program',
            'filters': {'is_active': True},
            'is_default': False
        }, format='json')
        
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'New Search'
        assert data['search_type'] == 'program'
    
    def test_apply_saved_search(self, api_client_authenticated_coordinator, saved_searches):
        """Test applying a saved search."""
        search = saved_searches[0]
        
        response = api_client_authenticated_coordinator.post(
            f'/api/saved-searches/{search.id}/apply/'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['search_type'] == search.search_type
        assert data['filters'] == search.filters
        assert data['name'] == search.name
    
    def test_set_default_search(self, api_client_authenticated_coordinator, saved_searches):
        """Test setting search as default."""
        search = saved_searches[0]
        
        response = api_client_authenticated_coordinator.post(
            f'/api/saved-searches/{search.id}/set_default/'
        )
        
        assert response.status_code == 200
        
        # Verify in database
        search.refresh_from_db()
        assert search.is_default
    
    def test_delete_saved_search(self, api_client_authenticated_coordinator, saved_searches):
        """Test deleting a saved search."""
        search = saved_searches[0]
        search_id = search.id
        
        response = api_client_authenticated_coordinator.delete(
            f'/api/saved-searches/{search_id}/'
        )
        
        assert response.status_code == 204
        assert not SavedSearch.objects.filter(id=search_id).exists()
    
    def test_user_can_only_see_own_searches(self, api_client_authenticated_student, saved_searches):
        """Test users can only see their own saved searches."""
        response = api_client_authenticated_student.get('/api/saved-searches/')
        
        assert response.status_code == 200
        data = response.json()
        # Student shouldn't see coordinator's searches
        assert len(data['results']) == 0
    
    def test_filter_by_search_type(self, api_client_authenticated_coordinator, saved_searches):
        """Test filtering saved searches by type."""
        response = api_client_authenticated_coordinator.get(
            '/api/saved-searches/?search_type=program'
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data['results']
        assert all(s['search_type'] == 'program' for s in results)


@pytest.fixture
def saved_searches(user_coordinator):
    """Create test saved searches."""
    searches = []
    
    searches.append(SavedSearch.objects.create(
        user=user_coordinator,
        name="Active Programs",
        search_type="program",
        filters={'is_active': True},
        is_default=True
    ))
    
    searches.append(SavedSearch.objects.create(
        user=user_coordinator,
        name="High GPA Programs",
        search_type="program",
        filters={'min_gpa_min': 3.5}
    ))
    
    searches.append(SavedSearch.objects.create(
        user=user_coordinator,
        name="Pending Applications",
        search_type="application",
        filters={'status_name': 'submitted', 'withdrawn': False}
    ))
    
    return searches


@pytest.fixture
def api_client_authenticated_coordinator(user_coordinator):
    """Create authenticated API client for coordinator."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(user_coordinator)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client


@pytest.fixture
def api_client_authenticated_student(user_student):
    """Create authenticated API client for student."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(user_student)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client

