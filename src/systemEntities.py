from enum import Enum
from pydantic import BaseModel

class User(BaseModel):
    email: str
    hacker_id: str
    name: str
    phone: str
    paid_status: bool

class NotificationType(Enum):
    CANDIDATE_KID_INTRO = 1
    ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITH_NEXT_ASSIGNMENT_LINK = 2
    ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITH_NO_NEXT_ASSIGNMENT_LINK = 3
    ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITH_VIEW_ASSIGNMENT_RESULT_LINK = 4
    NEW_ASSIGNMENT_ARRIVED = 5