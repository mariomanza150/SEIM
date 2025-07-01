"""
Academic-related enum models
"""

from .academic_term import AcademicTerm
from .degree import Degree
from .language import Language

# Exchange-related models
from .exchange import (
    ExchangeProgram,
    FundingType,
    PartnerAgreement,
    ProgramRequirements,
    ProgramType,
)

__all__ = [
    # Academic
    "AcademicTerm",
    "Degree", 
    "Language",
    # Exchange
    "ExchangeProgram",
    "FundingType",
    "PartnerAgreement",
    "ProgramRequirements",
    "ProgramType",
]
