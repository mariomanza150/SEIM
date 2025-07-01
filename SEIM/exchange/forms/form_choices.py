"""
Form choices and constants for SEIM forms.

This module contains reusable choice constants and lists that can be used
across multiple forms to maintain consistency and avoid duplication.
"""

# Academic level choices for exchange applications
ACADEMIC_LEVEL_CHOICES = [
    ("", "Choose level..."),
    ("UNDERGRADUATE", "Undergraduate"),
    ("GRADUATE", "Graduate"),
    ("DOCTORAL", "Doctoral"),
    ("POSTDOC", "Post-Doctoral"),
]

# Country choices for exchange destinations
COUNTRY_CHOICES = [
    ("", "Choose a country..."),
    ("USA", "United States"),
    ("UK", "United Kingdom"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("JP", "Japan"),
    ("AU", "Australia"),
    ("CA", "Canada"),
    ("IT", "Italy"),
    ("ES", "Spain"),
    ("NL", "Netherlands"),
]

# Academic year choices
CURRENT_YEAR_CHOICES = [("", "Choose year...")] + [(i, f"Year {i}") for i in range(1, 6)]
