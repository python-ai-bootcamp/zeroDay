from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from threading import Lock, Semaphore, Thread
from systemEntities import User, NotificationType, print
from userService import get_user
import tarfile
import sandboxService, mailService
import json, os, sys, base64,functools, importlib.util, time, datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

relative_data_directory="./data"
relative_assignments_directory="./resources/config/assignments/"
DATA_FILE_DIRECTORY = os.path.join(relative_data_directory,"assignment_data")
ASSIGNMENT_MAPPER_FILE = os.path.join(relative_assignments_directory,"assignment_mapper.json")
NOTIFIED_ASSIGNMENTS_FILE = os.path.join(relative_data_directory,"notification_data","notified_assignments.json")
ASSIGNMENT_VALIDATOR_DIR = os.path.join(relative_assignments_directory,"validators")
ASSIGNMENT_DESCRIPTIONS_DIR = os.path.join(relative_assignments_directory,"assignment_descriptions")
SUBMITTED_FILES_DIR=os.path.join(relative_data_directory,"submitted_files")
DEFAULT_VALIDATOR_TIMEOUT=60
DEFAULT_MAX_SUBMISSIONS=3
MAX_SUBMISION_PROCESSING=2
lockRepository={}
submision_processing_concurrency_semaphore=Semaphore(MAX_SUBMISION_PROCESSING)
print("locking submision_processing_concurrency_semaphore until sandboxService finishes initializing")
for sem_idx in range(MAX_SUBMISION_PROCESSING):
    submision_processing_concurrency_semaphore.acquire()
sandbox_init_thread=Thread(target=sandboxService.startDockerContainer, args=(submision_processing_concurrency_semaphore,MAX_SUBMISION_PROCESSING))
sandbox_init_thread.start()
#sandboxService.startDockerContainer(submision_processing_concurrency_semaphore,MAX_SUBMISION_PROCESSING)

class AssignmentSubmission(BaseModel):
    hacker_id: str
    assignment_id: int
#    assignment_files: List[str]
    submission_id: Optional[int] = None
    result: Optional[dict] = None
    assignment_file_names:  Optional[List[dict]] = None

def load_data(assignment_submission: AssignmentSubmission =None):
    if os.path.exists(DATA_FILE_DIRECTORY):
        if assignment_submission and assignment_submission.hacker_id:
            hacker_id=assignment_submission.hacker_id
            hacker_id_json_filename=os.path.join(DATA_FILE_DIRECTORY,f"{hacker_id}.json")
            if os.path.exists(hacker_id_json_filename):
                with open(hacker_id_json_filename, "r") as f:
                    return json.load(f)
            else:
                return {}
        else:
            filelist=os.listdir(DATA_FILE_DIRECTORY)
            merged_dataset={}
            for filename in filelist:
                with open(os.path.join(DATA_FILE_DIRECTORY,filename), "r") as f:
                    file_data=json.load(f)
                    merged_dataset={**merged_dataset,**file_data}
            return merged_dataset
    else:
        os.makedirs(DATA_FILE_DIRECTORY,exist_ok=True)    
        return {}
def load_data_by_hacker_id(hacker_id:str):
    return load_data(AssignmentSubmission(hacker_id=hacker_id,assignment_id=0))

def load_assignment_mapper():
    if os.path.exists(ASSIGNMENT_MAPPER_FILE):
        with open(ASSIGNMENT_MAPPER_FILE, "r") as f:
            return json.load(f)
    return {}

def load_notified_assignments():
    if os.path.exists(NOTIFIED_ASSIGNMENTS_FILE):
        with open(NOTIFIED_ASSIGNMENTS_FILE, "r") as f:
            return json.load(f)
    ts = time.time()
    return [{"assignment_id":0, "timestamp":datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}]

def save_notified_assignments(assignment_id: int):
    ts = time.time()
    notified_assignments_data=load_notified_assignments()
    notified_assignments_data.append({"assignment_id":assignment_id, "timestamp":datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')})
    with open(NOTIFIED_ASSIGNMENTS_FILE, "w") as f:
        json.dump(notified_assignments_data, f, indent=4)


def save_data(data: dict):
    hacker_id=list(data.keys())[0]
    with open(os.path.join(DATA_FILE_DIRECTORY,f"{hacker_id}.json"), "w") as f:
        json.dump(data, f, indent=4)

dynamically_loaded_modules_repository={}
def import_module_dynamically_from_path(task_file_name):
    # based on following code:: https://www.pythonmorsels.com/dynamically-importing-modules/
    global dynamically_loaded_modules_repository
    if ( task_file_name not in dynamically_loaded_modules_repository):
        spec = importlib.util.spec_from_file_location('loaded_validator_script', task_file_name)
        module = importlib.util.module_from_spec(spec)
        sys.modules['loaded_validator_script'] = module
        spec.loader.exec_module(module)
        dynamically_loaded_modules_repository[task_file_name]=module
        
    return dynamically_loaded_modules_repository[task_file_name]

def execute_validator_on_task_file(validator_script:str, task_file_name:str, task_directory_name: str, assignment_submission: AssignmentSubmission):
    checked_task_status_validator = import_module_dynamically_from_path(validator_script)
    task_file_name_full_path=os.path.join(SUBMITTED_FILES_DIR,str(assignment_submission.hacker_id),str(assignment_submission.assignment_id),str(assignment_submission.submission_id),task_directory_name, task_file_name)
    return checked_task_status_validator.execute_task(task_file_name_full_path, DEFAULT_VALIDATOR_TIMEOUT)
    #https://python.code-maven.com/python-capture-stdout-stderr-exit - this is a nice way to implement a validator with subprocess timeout based killing

def check_assignment_submission(assignment_submission:AssignmentSubmission):  
    assignment_mapper=load_assignment_mapper()
    validator_file_names=list(map(lambda validator_file_name: os.path.join(ASSIGNMENT_VALIDATOR_DIR,validator_file_name),assignment_mapper[str(assignment_submission.assignment_id)]["validators"]))
    validator_idx=0
    collected_results=[]
    for validator_script in validator_file_names:
        task_directory_name=str(validator_idx+1)
        #task_file_name=f"task_{str(validator_idx+1)}.py"
        task_file_name=f"main.py"
        task_file_exists=os.path.isfile(os.path.join(SUBMITTED_FILES_DIR,str(assignment_submission.hacker_id),str(assignment_submission.assignment_id),str(assignment_submission.submission_id),task_directory_name,task_file_name))
        if task_file_exists:
            print(f"executing validator_script={validator_script}, on task_directory_name={task_directory_name} ,task_file_name={task_file_name}")
            collected_results.append({"task_idx":validator_idx+1,**execute_validator_on_task_file(validator_script=validator_script, task_directory_name=task_directory_name, task_file_name=task_file_name, assignment_submission=assignment_submission)})
        else:
            collected_results.append({"task_idx":validator_idx+1,"status":"ERROR","ERROR_message":f"missing task file ({task_file_name}) in assignment directory ({task_directory_name})"})
        validator_idx=validator_idx+1        
    statuses=list(map(lambda result: result["status"],collected_results))
    def calculate_status_based_on_temp_and_new(temp_status,new_status):
        return "ERROR" if (new_status=="ERROR" or temp_status=="ERROR") else "FAIL" if (new_status=="FAIL" and (not temp_status == "ERROR")) else "PASS" if (new_status=="PASS" and temp_status=="PASS") else "FAIL"
    aggragated_status = functools.reduce(lambda temp_status,new_status: calculate_status_based_on_temp_and_new(temp_status,new_status), statuses, 'PASS')
    return {"status":aggragated_status,"collected_results":collected_results}

def assignment_passed(assignment: list[dict]):
    return len(list(filter(lambda submission: submission["result"]["status"]=="PASS",assignment)))>0


def previous_assignment_passed(assignment_submission: AssignmentSubmission, data:dict) :
    if(not assignment_submission.hacker_id in data):
        return (True if str(assignment_submission.assignment_id)=="1" else False)
    else:
        hacker=data[assignment_submission.hacker_id]
        if assignment_submission.assignment_id==1:
            return True
        elif not str(assignment_submission.assignment_id-1) in hacker:
            return False
        else:
            return assignment_passed(hacker[str(assignment_submission.assignment_id-1)])

def save_assignment_files(assignment_submission: AssignmentSubmission, tar_bytes:bytes):
    assignment_submission_directory=os.path.join(SUBMITTED_FILES_DIR,assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    temp_tar_path=os.path.join(assignment_submission_directory,"submitted_tar.tar.gz")
    with open(temp_tar_path, "wb") as out_file: 
        out_file.write(tar_bytes)
    with tarfile.open(temp_tar_path, "r:gz") as tar:
        tar.extractall(path=assignment_submission_directory)
    os.remove(temp_tar_path)
    assignment_submission_task_directories=[p.name for p in Path(assignment_submission_directory).iterdir() if p.is_dir()]
    return [{"task_directory":task_directory, "task_file":"main.py"} for task_directory in assignment_submission_task_directories]

def max_submission_for_assignment(assignment_id:int):
    assignment_mapper=load_assignment_mapper()
    if str(assignment_id) in assignment_mapper:
        assignment_mapper_entry_for_assignment=assignment_mapper[str(assignment_id)]
        if("max_submissions" in assignment_mapper_entry_for_assignment):
            return assignment_mapper_entry_for_assignment["max_submissions"]
        else:
            return DEFAULT_MAX_SUBMISSIONS
    else:
        return DEFAULT_MAX_SUBMISSIONS
@app.post("/submit")
def submit_assignment(tar_bytes: bytes, json_data: dict ):
    assignment_submission=AssignmentSubmission.model_validate(json_data)
    assignment_mapper=load_assignment_mapper()
    if not str(assignment_submission.assignment_id) in assignment_mapper:
        return {"status":"ERROR","ERROR_message":f"missing assignment_id={assignment_submission.assignment_id} in assignment_mapper file"}
    else:
        if not "validators" in assignment_mapper[str(assignment_submission.assignment_id)]:
            return {"status":"ERROR","ERROR_message":f"missing validators entry for assignment_id={assignment_submission.assignment_id} in assignment_mapper file"}
        else:
            number_of_validators=len(assignment_mapper[str(assignment_submission.assignment_id)]["validators"])
            if number_of_validators==0:
                return {"status":"ERROR","ERROR_message":f"no validators mapped for assignment_id={assignment_submission.assignment_id} in assignment_mapper file"}
    max_submissions=max_submission_for_assignment(assignment_submission.assignment_id)
    submision_processing_concurrency_semaphore.acquire()
    if not (assignment_submission.hacker_id in lockRepository):
        lockRepository[assignment_submission.hacker_id]=Lock()
    lockRepository[assignment_submission.hacker_id].acquire()
    data = load_data(assignment_submission)
    if previous_assignment_passed(assignment_submission, data):
        assignment_submission.submission_id = 1 #in case no previous submission, then submission_id=1, will change to calculated value only if exisitng submition_id found
        if(not assignment_submission.hacker_id in data):
            assignment_submission.assignment_file_names=save_assignment_files(assignment_submission, tar_bytes)
            assignment_submission.result = check_assignment_submission(assignment_submission)
            data[assignment_submission.hacker_id]={assignment_submission.assignment_id:[assignment_submission.model_dump()]}      
        else:
            if(str(assignment_submission.assignment_id) in data[assignment_submission.hacker_id]):
                assignment_submission.submission_id = len(data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)])+1                
                if(assignment_submission.submission_id<=max_submissions):
                    assignment_submission.assignment_file_names=save_assignment_files(assignment_submission, tar_bytes)
                    assignment_submission.result = check_assignment_submission(assignment_submission)
                    data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)].append(assignment_submission.model_dump())
                else:
                    assignment_submission.result={"status":"ERROR","ERROR_message":f"cannot test assignment (assignment_id={str(assignment_submission.assignment_id)}) because submission attempts ({str(assignment_submission.submission_id)}) passed the allowed max_submissions (max_submissions={max_submissions})"}
                    print(assignment_submission.result)
                    lockRepository[assignment_submission.hacker_id].release()
                    submision_processing_concurrency_semaphore.release()
                    return assignment_submission.model_dump()
            else:
                assignment_submission.assignment_file_names=save_assignment_files(assignment_submission, tar_bytes)
                assignment_submission.result = check_assignment_submission(assignment_submission)
                data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)]=[assignment_submission.model_dump()]
        save_data(data)
    else:
        assignment_submission.result={"status":"ERROR","ERROR_message":f"cannot test assignment (assignment_id={str(assignment_submission.assignment_id)}) until previous assignment (assignment_id={str(assignment_submission.assignment_id-1)}) passes successfully"}
        lockRepository[assignment_submission.hacker_id].release()
        submision_processing_concurrency_semaphore.release()
        return assignment_submission.model_dump()
    lockRepository[assignment_submission.hacker_id].release()
    submision_processing_concurrency_semaphore.release()
    send_mail_after_assignment_submission(assignment_submission)
    return assignment_submission.model_dump()

def send_mail_after_assignment_submission(assignment_submission:AssignmentSubmission):
    user=User.model_validate(get_user(assignment_submission.hacker_id)["user"])
    if assignment_submission.result["status"] == "PASS":
        if assignment_submission.assignment_id < last_available_assignment_id():
            mailService.notification_producer(user=user,notification_type=NotificationType.ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITH_NEXT_ASSIGNMENT_LINK)
        else:
            mailService.notification_producer(user=user,notification_type=NotificationType.ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITHOUT_NEXT_ASSIGNMENT_LINK)
    else:
        if assignment_submission.submission_id < max_submission_for_assignment(assignment_submission.assignment_id):
            mailService.notification_producer(user=user,notification_type=NotificationType.ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITH_ANOTHER_ATTEMPT)
        else:        
            mailService.notification_producer(user=user,notification_type=NotificationType.ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITHOUT_ANOTHER_ATTEMPT)

def send_new_assignment_mail_for_user(hacker_id):
    #print(f"send_new_assignment_mail_for_user for hacker_id='{hacker_id}'")
    #print(f"loading user with hacker_id='{hacker_id}'")
    fetched_user_result=get_user(hacker_id)
    #print(f"fetched_user_result for hacker_id='{hacker_id} is fetched_user_result='{fetched_user_result}'")
    if fetched_user_result["status"] == "OK":
        user=User.model_validate(fetched_user_result["user"])
        mailService.notification_producer(user=user,notification_type=NotificationType.NEW_ASSIGNMENT_ARRIVED)
    else:
        print(f"user with hacker_id='{hacker_id}' referenced by assignmentOrchestrator module, does not exist in userService data and will not get notified on new assignment")

def new_assignment_added():
    currently_available_last_assignment_id=last_available_assignment_id()
    last_notified_assignment_id=load_notified_assignments()[-1]["assignment_id"]
    if currently_available_last_assignment_id>last_notified_assignment_id:
        save_notified_assignments(currently_available_last_assignment_id)
        return True
    else:
        return False
    

def trigger_new_assignment_mail_if_needed():
    if new_assignment_added():
        latest_assignment_id=last_available_assignment_id()
        all_user_data=load_data()
        #print("all_user_data:: ",all_user_data)
        for hacker_id in all_user_data:
            hacker_data=all_user_data[hacker_id]
            user_last_assignment_key=last_assignment_key(hacker_data)
            if int(user_last_assignment_key)+1 == int(latest_assignment_id):
                send_new_assignment_mail_for_user(hacker_id)

def next_assignment_submission(hacker_id:str):
    data=load_data()
    if hacker_id in data:
        if len(data[hacker_id])>0:
            assignment_id=str(len(data[hacker_id]))
            submission_id=len(data[hacker_id][assignment_id])
            if assignment_passed(data[hacker_id][assignment_id]):
                return {"assignment_id":int(assignment_id)+1,"submission_id": 1}
            else:
                return {"assignment_id":int(assignment_id),"submission_id":submission_id+1 if submission_id>0 else 1}
        else:
            return {"assignment_id":1,"submission_id":1}
    else:
        return {"assignment_id":1,"submission_id":1} 

def assignment_description(assignment_id:int):
    assignment_mapper=load_assignment_mapper()
    if str(assignment_id) in assignment_mapper:
        if "description" in assignment_mapper[str(assignment_id)]:
            assignment_description_file_name=assignment_mapper[str(assignment_id)]['description']
            with open(os.path.join(ASSIGNMENT_DESCRIPTIONS_DIR,assignment_description_file_name), "r") as f:
                assignment_description=f.read()
            return {"status":"OK", "assignment_description":assignment_description}
        else:
            return {"status":"ERROR", "ERROR_message":f"assignment with assignment_id='{str(assignment_id)}' is not mapped to description file"}
    else:
        return {"status":"ERROR", "ERROR_message":f"no entry for assignment with assignment_id='{str(assignment_id)}' inside assignment_mapper file"}

def assignment_task_count(assignment_id:int):
    assignment_mapper=load_assignment_mapper()
    if str(assignment_id) in assignment_mapper:
        if "validators" in assignment_mapper[str(assignment_id)]:
            validators_counter=len(assignment_mapper[str(assignment_id)]["validators"])
            if validators_counter>0:
                return {"status":"OK", "task_count":validators_counter}
            return {"status":"ERROR", "ERROR_message":f"assignment with assignment_id='{str(assignment_id)}' does not contain even a single validator"}
        else:
            return {"status":"ERROR", "ERROR_message":f"assignment with assignment_id='{str(assignment_id)}' is missing validators entry"}
    else:
        return {"status":"ERROR", "ERROR_message":f"no entry for assignment with assignment_id='{str(assignment_id)}' inside assignment_mapper file"}
    
def user_testing_in_progress(hacker_id:str):
    if hacker_id in lockRepository:
        return lockRepository[hacker_id].locked()
    else:
        return False
    
def last_assignment_key(hacker_data):
    assignment_keys=list(map(lambda key: int(key), hacker_data.keys()))
    assignment_keys.sort()
    return str(assignment_keys[-1])

def last_assignment_submission_result(hacker_id:str):
    data=load_data_by_hacker_id(hacker_id)
    if hacker_id in data:    
        hacker_data=data[hacker_id]
        assignment_key=last_assignment_key(hacker_data)
        last_assignment_submissions= hacker_data[assignment_key]
        last_submission=last_assignment_submissions[-1]
        return {"status":"OK", "last_assignment_submission_result":last_submission}
    else:
        return {"status":"ERROR", "ERROR_message":f"user with hacker_id='{hacker_id}' does not have a single assignment submission"}
    
def get_submitted_file(hacker_id:str, assignment_id:str, submission_id:str, task_id:str):
    task_file_name=f"task_{task_id}.py"
    task_file_name_full_path=os.path.join(SUBMITTED_FILES_DIR, hacker_id, assignment_id, submission_id, task_file_name)
    with open(task_file_name_full_path, "r") as f:
            return f.read()

def last_available_assignment_id()->int:
    assignment_mapper=load_assignment_mapper()
    assignment_ids=list(map(lambda key: int(key), assignment_mapper.keys()))
    assignment_ids.sort()
    return assignment_ids[-1]