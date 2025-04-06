from enum import StrEnum, Enum
import time,os,json
from pydantic import BaseModel

ANALYTICS_DATA_DIR=os.path.join("./data","analytics_data")

class AnalyticsEventType(StrEnum):
    CHALLENGE_TRAFFIC           = os.path.join(ANALYTICS_DATA_DIR,"CHALLENGE_TRAFFIC")
    NEW_USER                    = os.path.join(ANALYTICS_DATA_DIR,"NEW_USER")
    USER_PAID                   = os.path.join(ANALYTICS_DATA_DIR,"USER_PAID")
    USER_SUBMITTED_ASSIGNMENT   = os.path.join(ANALYTICS_DATA_DIR,"USER_SUBMITTED_ASSIGNMENT")
    USER_PASSED_ASSIGNMENT      = os.path.join(ANALYTICS_DATA_DIR,"USER_PASSED_ASSIGNMENT")


for enum_entry in AnalyticsEventType:
    #print(f"enum_entry.name::'{enum_entry.name}', enum_entry.value::'{enum_entry.value}'")
    os.makedirs(enum_entry.value,exist_ok=True)

class AnalyticsEvent():
    analytic_event_type: AnalyticsEventType
    epoch_time: int
    def __init__(self, analytic_event_type:AnalyticsEventType):
        self.analytic_event_type = analytic_event_type
        self.epoch_time = int(time.time_ns())
    def __str__(self):
        return f"analytic_event_type::'{self.analytic_event_type}', epoch_time::'{self.epoch_time}'"
    def persist_to_disk(self):
        data_to_persist={k:(v if k!="analytic_event_type" else v.name) for (k,v) in self.__dict__.items()}
        data_file=os.path.join(ANALYTICS_DATA_DIR,data_to_persist["analytic_event_type"],str(data_to_persist["epoch_time"]))
        with open(data_file, 'w') as f:
            json.dump(data_to_persist, f)
        

    
class ChallengeTrafficAnalyticsEvent(AnalyticsEvent):
    advertise_code: str
    def __init__(self, advertise_code:str, advertise_code_sub_category:str):
        super().__init__(AnalyticsEventType.CHALLENGE_TRAFFIC)
        self.advertise_code=advertise_code
        self.advertise_code_sub_category=advertise_code_sub_category

    
class NewUserAnalyticsEvent(AnalyticsEvent):
    advertise_code: str
    def __init__(self, analytic_event_type:AnalyticsEventType, advertise_code:str, advertise_code_sub_category:str):
        super().__init__(AnalyticsEventType.NEW_USER)
        self.advertise_code=advertise_code
        self.advertise_code_sub_category=advertise_code_sub_category
    
class UserPaidAnalyticsEvent(AnalyticsEvent):
    advertise_code: str
    def __init__(self, analytic_event_type:AnalyticsEventType, advertise_code:str, advertise_code_sub_category:str):
        super().__init__(AnalyticsEventType.USER_PAID)
        self.advertise_code=advertise_code
        self.advertise_code_sub_category=advertise_code_sub_category

    
class UserSubmittedAssignmentAnalyticsEvent(AnalyticsEvent):
    assignment_id:int
    submisison_id:int
    def __init__(self, analytic_event_type:AnalyticsEventType, assignment_id:str, submisison_id:str):
        super().__init__(AnalyticsEventType.USER_SUBMITTED_ASSIGNMENT)
        self.USER_PASSED_ASSIGNMENT=assignment_id
        self.submisison_id=submisison_id
    
class UserPassedAssignmentAnalyticsEvent(AnalyticsEvent):
    assignment_id:int
    submission_id:int
    def __init__(self, analytic_event_type:AnalyticsEventType, assignment_id:str, submisison_id:str):
        super().__init__(AnalyticsEventType.USER_PASSED_ASSIGNMENT)
        self.USER_PASSED_ASSIGNMENT=assignment_id
        self.submisison_id=submisison_id

