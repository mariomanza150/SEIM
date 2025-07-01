"""
Enum models for the exchange application
"""

# Other enums
from .campus import Campus
from .institution import Institution
from .university import University
from .address import Address, City, State, Country

__all__ = [
    # Other
    "Address",
    "City",
    "State",
    "Country",
    "Campus",
    "Institution",
    "University",
]
