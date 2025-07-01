"""
Exchange-specific academic serializers.

This package contains serializers for exchange program related models.
"""

from .funding import *
from .program_requirements import *
from .program_type import *
from .academic_program import *
from .partner_agreement import *

__all__ = [
    # Exchange program
    "ExchangeProgramSerializer",
    "ExchangeProgramListSerializer",
    "ExchangeProgramDetailSerializer",
    "ExchangeProgramCreateSerializer",
    "ExchangeProgramEligibilitySerializer",
    
    # Funding
    "FundingTypeSerializer",
    "FundingTypeListSerializer",
    
    # Program requirements
    "ProgramRequirementsSerializer",
    "ProgramRequirementsCreateSerializer",
    
    # Program type
    "ProgramTypeSerializer",
    
    # Partner agreement
    "PartnerAgreementSerializer",
]
