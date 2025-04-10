from enum import StrEnum
import time, os, json, pathlib, re
from typing import Any, Dict, Tuple
from collections import OrderedDict
from pydantic import BaseModel
from systemEntities import AnalyticsEventType

ANALYTICS_DATA_MEMOIZATION_MAX_ITEMS=10
analytics_data_memoization_state=OrderedDict()


for enum_entry in AnalyticsEventType:
    #print(f"enum_entry.name::'{enum_entry.name}', enum_entry.value::'{enum_entry.value}'")
    os.makedirs(enum_entry.value,exist_ok=True)

class AnalyticsEvent():
    analytic_event_type: AnalyticsEventType
    epoch_time: int
    def __init__(self, analytic_event_type:AnalyticsEventType):
        self.analytic_event_type = analytic_event_type
        self.epoch_time = int(time.time_ns()/1000000)
        #self.persist()
    def __str__(self):
        return f"analytic_event_type::'{self.analytic_event_type}', epoch_time::'{self.epoch_time}'"
    def serialize(self):
        return {k:(v if k!="analytic_event_type" else v.name) for (k,v) in self.__dict__.items()}
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
    return [time_range for time_range in file_times_list if range_query[0]<=time_range[0]<=range_query[1] or range_query[0]<=time_range[1]<=range_query[1]]

def fetch_analytics_data(from_time:int, to_time:int, analytics_event_type: AnalyticsEventType):
    memoization_key=f"from_time_{str(from_time)}_to_time_{str(to_time)}_analytics_event_type_{analytics_event_type.name}"
    if memoization_key in analytics_data_memoization_state:
        print(f"fetch_analytics_data_memoization_state:: {memoization_key} is already in cache, sending memoized data")
        return analytics_data_memoization_state[memoization_key]
    else:
        print(f"fetch_analytics_data_memoization_state:: {memoization_key} not found in cache, reading data from disk")
        file_times_list = [re.findall('from_([0-9]*)_to_([0-9]*).json',str(file_name))[0] for file_name in pathlib.Path(analytics_event_type.value).iterdir() if file_name.is_file()]
        file_times_list = [(int(file_times[0]),int(file_times[1])) for file_times in file_times_list]
        file_data=[]
        for file_times in filter_relevant_time_ranges(file_times_list,(from_time,to_time)):
            with open(os.path.join(analytics_event_type.value,f"from_{file_times[0]}_to_{file_times[1]}.json")) as f:
                single_file_data=json.load(f)
                file_data=file_data+single_file_data
        file_data=[x for x in file_data if from_time <= x["epoch_time"] <=to_time]
        if len(analytics_data_memoization_state.keys())>=ANALYTICS_DATA_MEMOIZATION_MAX_ITEMS:
            analytics_data_memoization_state.popitem(last=False)
        analytics_data_memoization_state[memoization_key]=file_data
        #print(f"fetch_analytics_data_memoization_state:: analytics_data_memoization_state.keys()='{analytics_data_memoization_state.keys()}'")
        return file_data

def create_time_buckets(from_time: int, to_time: int, group_by_time_bucket_sec: int)->list[Tuple[int,int]]:
    time_buckets:list[Tuple[int,int]]=[]
    group_by_time_bucket_sec=group_by_time_bucket_sec*1000
    current_bucket=(from_time, from_time+group_by_time_bucket_sec-1)
    while current_bucket[0]<=to_time:
        time_buckets.append(current_bucket)
        current_bucket=(current_bucket[1]+1, current_bucket[1]+group_by_time_bucket_sec)
    return time_buckets

def split_data_to_buckets(data:list[dict], time_buckets:list[Tuple[int,int]]) -> list[list[dict]]:
    return [[event for event in data if time_bucket[0]<=event["epoch_time"]<=time_bucket[1]] for time_bucket in time_buckets]

def group_data_by_field_per_bucket_using_known_field_values(field_name:str, field_values:list[Any], data:list[list[dict]])->list[dict]:
    grouped_data=[]
    for group in data:
        group_aggragated_data={key:0 for key in field_values}
        for event in group:
            if event[field_name] in group_aggragated_data:
                group_aggragated_data[event[field_name]]=group_aggragated_data[event[field_name]]+1
            else:
                group_aggragated_data[event[field_name]]=1
        grouped_data.append(group_aggragated_data)
    return grouped_data

def filter_data_by_filter_field(data:list[dict], filter_field_name: str, filter_field_value: Any)->list:
    print("filter_data_by_filter_field::data=",data)
    print("filter_data_by_filter_field::filter_field_name=",filter_field_name)
    print("filter_data_by_filter_field::filter_field_value=",filter_field_value)
    return data

def group_data(from_time: int, to_time: int, group_by_time_bucket_sec: int, group_by_field: str, analytics_event_type: AnalyticsEventType)->Tuple[list[dict], list[Tuple[int,int]]]:
    data=fetch_analytics_data(from_time, to_time, analytics_event_type)
    #print("group_data::data=",data)
    #data=filter_data_by_filter_field(data, filter_field_name, filter_field_value)
    if len(data)>0:
        field_values=set()
        for event in data:
            field_values.add(event[group_by_field])
        if to_time >= data[-1]["epoch_time"]:
            to_time=data[-1]["epoch_time"]
        if from_time <= data[0]["epoch_time"]:
            from_time=data[0]["epoch_time"]
        time_buckets:list[Tuple[int,int]]=create_time_buckets(from_time, to_time, group_by_time_bucket_sec)
        data_splitted_to_buckets=split_data_to_buckets(data, time_buckets)
        grouped_data=group_data_by_field_per_bucket_using_known_field_values(group_by_field, field_values, data_splitted_to_buckets)
        return grouped_data,time_buckets
    else:
        return [],[]

def convert_group_data_to_plotly_traces(group_data:list[dict], time_buckets:list[Tuple[int,int]]):
    if len(group_data)>0:
        traces={k:{"x":[], "y":[], "type":'bar', "name":k} for k in [key for key in group_data[0].keys()]}
        idx=0
        for start_time,end_time in time_buckets:
            for traceName in traces.keys():
                #print("group_data[idx]::",group_data[idx])
                traces[traceName]["x"].append(start_time)
                traces[traceName]["y"].append(group_data[idx][traceName])
            idx=idx+1
        traces=[v for k,v in traces.items()]
        return traces
    else:
        return []
    
def group_by_fields(from_time:int, to_time:int, analytics_event_type: AnalyticsEventType)->list[str]:
    data=fetch_analytics_data(from_time, to_time, analytics_event_type)
    unique_field_names=set()
    for entry in data:
        keys=entry.keys()
        for key in keys:
            if not(key=="analytic_event_type") and not(key=="epoch_time"):
                unique_field_names.add(key)
    unique_field_names=list(unique_field_names)
    #print("group_by_fields::unique_field_names=",unique_field_names)
    return list(unique_field_names)

#grouped_data,time_buckets=group_data(from_time=0, to_time=float('inf'), group_by_time_bucket_sec=30, group_by_field="advertise_code", analytics_event_type=AnalyticsEventType.CHALLENGE_TRAFFIC)   
#plotly_traces=convert_group_data_to_plotly_traces(grouped_data, time_buckets)
#print(json.dumps(plotly_traces))