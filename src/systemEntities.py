from enum import Enum
from pydantic import BaseModel

class User(BaseModel):
    email: str
    hacker_id: str
    name: str
    phone: str

class NotificationType(Enum):
    CANDIDATE_KID_INTRO = 1
    CANDIDATE_PARENT_INTRO = 2
    NEW_ASSIGNMENT_DESCRIPTION = 3
    ASSIGNMENT_SUBMISSION_RESULT = 4