from enum import StrEnum
import time, os, json, pathlib, re
from typing import Dict, Tuple
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
        #self.persist()
    def __str__(self):
        return f"analytic_event_type::'{self.analytic_event_type}', epoch_time::'{self.epoch_time}'"
    def serialize(self):
        return [{k:(v if k!="analytic_event_type" else v.name) for (k,v) in self.__dict__.items()}]
    def persist(self):
        data_file=os.path.join(self.analytic_event_type.value,f"from_{str(self.epoch_time)}_to_{str(self.epoch_time)}.json")
        with open(data_file, 'w') as f:
            json.dump(self.serialize(), f)
     
class ChallengeTrafficAnalyticsEvent(AnalyticsEvent):
    advertise_code: str
    advertise_code_sub_category: str
    def __init__(self, advertise_code:str, advertise_code_sub_category:str):
        self.advertise_code=advertise_code
        self.advertise_code_sub_category=advertise_code_sub_category
        super().__init__(AnalyticsEventType.CHALLENGE_TRAFFIC)
    
class NewUserAnalyticsEvent(AnalyticsEvent):
    advertise_code: str
    advertise_code_sub_category: str
    def __init__(self,advertise_code:str, advertise_code_sub_category:str):
        self.advertise_code=advertise_code
        self.advertise_code_sub_category=advertise_code_sub_category
        super().__init__(AnalyticsEventType.NEW_USER)
    
class UserPaidAnalyticsEvent(AnalyticsEvent):
    advertise_code: str
    advertise_code_sub_category: str
    def __init__(self,advertise_code:str, advertise_code_sub_category:str):
        self.advertise_code=advertise_code
        self.advertise_code_sub_category=advertise_code_sub_category
        super().__init__(AnalyticsEventType.USER_PAID)
    
class UserSubmittedAssignmentAnalyticsEvent(AnalyticsEvent):
    assignment_id:int
    submisison_id:int
    def __init__(self,assignment_id:int, submisison_id:int):
        self.assignment_id=assignment_id
        self.submisison_id=submisison_id
        super().__init__(AnalyticsEventType.USER_SUBMITTED_ASSIGNMENT)
    
class UserPassedAssignmentAnalyticsEvent(AnalyticsEvent):
    assignment_id:int
    submission_id:int
    def __init__(self,assignment_id:int, submisison_id:int):
        self.assignment_id=assignment_id
        self.submisison_id=submisison_id
        super().__init__(AnalyticsEventType.USER_PASSED_ASSIGNMENT)

persistance_queues:Dict[str,list[AnalyticsEvent]] = { k:[] for (k,v) in AnalyticsEventType.__members__.items()}

def insert_analytic_event(event:AnalyticsEvent):
    persistance_queues[event.analytic_event_type.name].append(event)

def persist_analytics_events():
    for (name,value) in AnalyticsEventType.__members__.items():
        persistance_queue:list[AnalyticsEvent]=persistance_queues[name]            
        if len(persistance_queue)>0:
            print(f"analyticsService.persist_analytics_events:: persisting following queue '{name}' with {str(len(persistance_queue))} items")
            from_time=persistance_queue[0].epoch_time
            to_time=persistance_queue[-1].epoch_time
            data_file=os.path.join(value,f"from_{str(from_time)}_to_{str(to_time)}.json")
            with open(data_file, 'w') as f:
                json.dump([x.serialize() for x in persistance_queue],f)
            persistance_queue.clear()

def filter_relevant_time_ranges(file_times_list:list[Tuple[int, int]], range_query:Tuple[int, int])->list[Tuple[int, int]]:        
    return [time_range for time_range in file_times_list if time_range[0]<=range_query[0]<=time_range[1] or time_range[0]<=range_query[1]<=time_range[1]]

def fetch_analytics_data(from_time:int, to_time:int, analytics_event_type: AnalyticsEventType):
    keys=("start","end")
    file_times_list = [re.findall('from_([0-9]*)_to_([0-9]*).json',str(file_name))[0] for file_name in pathlib.Path(analytics_event_type.value).iterdir() if file_name.is_file()]
    file_times_list = [(int(file_times[0]),int(file_times[1])) for file_times in file_times_list]
    filter_relevant_time_ranges(file_times_list,(from_time,to_time))
    return filter_relevant_time_ranges(file_times_list,(from_time,to_time))