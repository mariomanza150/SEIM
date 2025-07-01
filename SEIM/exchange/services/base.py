"""Base service classes for the exchange application."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import User
from django.db.models import Model, QuerySet


class BaseService(ABC):
    """Abstract base class for all services."""

    def __init__(self, user: Optional[User] = None):
        """Initialize service with optional user context."""
        self.user = user

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data."""
        pass

    def get_queryset(self, model: type[Model]) -> QuerySet:
        """Get base queryset with common filters."""
        return model.objects.all()

    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log service actions for auditing."""
        # TODO: Implement logging mechanism
        pass


class CRUDService(BaseService):
    """Base service for CRUD operations."""

    model: type[Model] = None

    def list(self, filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        """List objects with optional filters."""
        queryset = self.get_queryset(self.model)
        if filters:
            queryset = queryset.filter(**filters)
        return queryset

    def get(self, pk: Any) -> Model:
        """Get single object by primary key."""
        return self.get_queryset(self.model).get(pk=pk)

    def create(self, data: Dict[str, Any]) -> Model:
        """Create new object."""
        validated_data = self.validate(data)
        obj = self.model.objects.create(**validated_data)
        self.log_action("create", {"model": self.model.__name__, "pk": obj.pk})
        return obj

    def update(self, pk: Any, data: Dict[str, Any]) -> Model:
        """Update existing object."""
        obj = self.get(pk)
        validated_data = self.validate(data)
        for key, value in validated_data.items():
            setattr(obj, key, value)
        obj.save()
        self.log_action("update", {"model": self.model.__name__, "pk": obj.pk})
        return obj

    def delete(self, pk: Any) -> None:
        """Delete object."""
        obj = self.get(pk)
        obj.delete()
        self.log_action("delete", {"model": self.model.__name__, "pk": pk})
