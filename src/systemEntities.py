from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, NameEmail, constr
import os
import datetime

_print = print  # preserve original
def print(*args, **kwargs):
    _print(f"{str(datetime.datetime.now())[0:23]}\t", end='')
    _print(*args, **kwargs)


class User(BaseModel):
    email: str
    hacker_id: str
    name: str
    phone: str
    paid_status: bool
    receipt_index: str
    advertise_code: str = "unknown"
    advertise_code_sub_category: str = "unknown"

ANALYTICS_DATA_DIR=os.path.join("./data","analytics_data")
class AnalyticsEventType(StrEnum):
    CHALLENGE_TRAFFIC           = os.path.join(ANALYTICS_DATA_DIR,"CHALLENGE_TRAFFIC")
    NEW_USER                    = os.path.join(ANALYTICS_DATA_DIR,"NEW_USER")
    USER_PAID                   = os.path.join(ANALYTICS_DATA_DIR,"USER_PAID")
    USER_SUBMITTED_ASSIGNMENT   = os.path.join(ANALYTICS_DATA_DIR,"USER_SUBMITTED_ASSIGNMENT")
    USER_PASSED_ASSIGNMENT      = os.path.join(ANALYTICS_DATA_DIR,"USER_PASSED_ASSIGNMENT")

class NotificationType(StrEnum):
    CANDIDATE_KID_INTRO = "CANDIDATE_KID_INTRO"
    ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITH_NEXT_ASSIGNMENT_LINK = "ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITH_NEXT_ASSIGNMENT_LINK"
    ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITHOUT_NEXT_ASSIGNMENT_LINK = "ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITHOUT_NEXT_ASSIGNMENT_LINK"
    ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITH_ANOTHER_ATTEMPT = "ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITH_ANOTHER_ATTEMPT"
    ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITHOUT_ANOTHER_ATTEMPT = "ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITHOUT_ANOTHER_ATTEMPT"
    NEW_ASSIGNMENT_ARRIVED = "NEW_ASSIGNMENT_ARRIVED"
    NEW_USER_FIRST_ASSIGNMENT_AFTER_ENLISTMENT = "NEW_USER_FIRST_ASSIGNMENT_AFTER_ENLISTMENT"
    PAYMENT_ACCEPTED = "PAYMENT_ACCEPTED"

EMAIL_SUBJECT_LENGTH=250
class Email(BaseModel):
    to: NameEmail
    subject: constr(max_length=EMAIL_SUBJECT_LENGTH)
    body_txt: str
    body_html: str

class Payment(BaseModel):
    receipt_index: Optional[str] = None
    user:User
    ClientName:str
    ClientLName:str
    UserId:str
    email:str
    phone:str
    amount: int
    date: str
