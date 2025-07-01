# Initialize the admin module
from .bulk_action import BulkActionAdmin, BulkActionItemAdmin, BulkActionLogAdmin
from .academic import GradeAdmin, CourseAdmin
from .comment import ReviewAdmin, CommentAdmin
from .document import DocumentAdmin
from .exchange_program import ExchangeProgramAdmin
from .exchange import ExchangeAdmin
from .profiles import StudentProfileAdmin, StaffProfileAdmin, ContactProfileAdmin
from .places import CampusAdmin, CityAdmin, CountryAdmin, StateAdmin, UniversityAdmin, InstitutionAdmin
from .timeline import TimelineAdmin, WorkflowLogAdmin
from .permission import PermissionAdmin

__all__ = [
    'BulkActionAdmin',
    'BulkActionItemAdmin',
    'BulkActionLogAdmin',
    'GradeAdmin',
    'CourseAdmin',
    'ReviewAdmin',
    'CommentAdmin',
    'DocumentAdmin',
    'ExchangeProgramAdmin',
    'ExchangeAdmin',
    'StudentProfileAdmin',
    'StaffProfileAdmin',
    'ContactProfileAdmin',
    'CampusAdmin',
    'CityAdmin',
    'CountryAdmin',
    'StateAdmin',
    'UniversityAdmin',
    'InstitutionAdmin',
    'TimelineAdmin',
    'WorkflowLogAdmin',
    'PermissionAdmin',
]
