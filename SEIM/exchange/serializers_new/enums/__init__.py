"""
Enum serializers for the exchange application.

This package contains serializers for all enum/reference data models including
academic, address, and institutional data.
"""

from .academic import *
from .address import *
from .campus import *
from .institution import *
from .question import *
from .university import *
from .config_model import *

__all__ = [
    # Academic enums
    "AcademicTermSerializer",
    "DegreeSerializer", 
    "LanguageSerializer",
    "ExchangeProgramSerializer",
    "ExchangeProgramListSerializer",
    "ExchangeProgramDetailSerializer",
    "FundingTypeSerializer",
    "PartnerAgreementSerializer",
    "ProgramRequirementsSerializer",
    "ProgramTypeSerializer",
    
    # Address enums
    "CountrySerializer",
    "StateSerializer",
    "CitySerializer",
    
    # Other enums
    "CampusSerializer",
    "InstitutionSerializer",
    "QuestionSerializer",
    "QuestionCategorySerializer",
    "UniversitySerializer",
    "ConfigModelSerializer",
]
