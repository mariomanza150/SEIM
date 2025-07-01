"""
Academic enum serializers.

This package contains serializers for all academic-related enum models.
"""

from .academic_term import *
from .degree import *
from .language import *
from .exchange import *

__all__ = [
    # Academic terms
    "AcademicTermSerializer",
    "AcademicTermListSerializer",
    
    # Degrees
    "DegreeProgramSerializer",
    "DegreeProgramListSerializer",
    
    # Languages
    "LanguageSerializer",
    "LanguageListSerializer",
    "ProficiencyLevelsSerializer",
    "LanguageProficiencyTestSerializer",
    
    # Exchange-related
    "ExchangeProgramSerializer",
    "ExchangeProgramListSerializer",
    "ExchangeProgramDetailSerializer",
    "FundingTypeSerializer",
    "ProgramRequirementsSerializer",
    "ProgramTypeSerializer",
    "PartnerAgreementSerializer",
]
