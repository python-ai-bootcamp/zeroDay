from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from threading import Lock, Semaphore, Thread
from systemEntities import User,NotificationType
from userService import get_user
import sandboxService, mailService
import json, os, random, sys, subprocess, base64,functools, importlib.util,urllib

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
    assignment_files: List[str]
    submission_id: Optional[int] = None
    result: Optional[dict] = None
    assignment_file_names:  Optional[List[str]] = None

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
    return load_data(AssignmentSubmission(hacker_id=hacker_id,assignment_id=0,assignment_files=[]))

def load_assignment_mapper():
    if os.path.exists(ASSIGNMENT_MAPPER_FILE):
        with open(ASSIGNMENT_MAPPER_FILE, "r") as f:
            return json.load(f)
    return {}

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

def execute_validator_on_task_file(validator_script:str, task_file_name:str, assignment_submission: AssignmentSubmission):
    checked_task_status_validator = import_module_dynamically_from_path(validator_script)
    task_file_name_full_path=os.path.join(SUBMITTED_FILES_DIR,str(assignment_submission.hacker_id),str(assignment_submission.assignment_id),str(assignment_submission.submission_id),task_file_name)
    return checked_task_status_validator.execute_task(task_file_name_full_path,DEFAULT_VALIDATOR_TIMEOUT)
    #https://python.code-maven.com/python-capture-stdout-stderr-exit - this is a nice way to implement a validator with subprocess timeout based killing

def check_assignment_submission(assignment_submission:AssignmentSubmission):  
    assignment_mapper=load_assignment_mapper()
    validator_file_names=list(map(lambda validator_file_name: os.path.join(ASSIGNMENT_VALIDATOR_DIR,validator_file_name),assignment_mapper[str(assignment_submission.assignment_id)]["validators"]))
    validator_idx=0
    collected_results=[]
    for validator_script in validator_file_names:
        task_file_name=f"task_{str(validator_idx+1)}.py"
        task_file_exists=os.path.isfile(os.path.join(SUBMITTED_FILES_DIR,str(assignment_submission.hacker_id),str(assignment_submission.assignment_id),str(assignment_submission.submission_id),task_file_name))
        if task_file_exists:
            print(f"executing validator_script={validator_script},task_file_name={task_file_name}")
            collected_results.append({"task_idx":validator_idx+1,**execute_validator_on_task_file(validator_script=validator_script,task_file_name=task_file_name,assignment_submission=assignment_submission)})
        else:
            collected_results.append({"task_idx":validator_idx+1,"status":"ERROR","ERROR_message":f"missing task ({task_file_name}) in assignment"})
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

def save_assignment_files(assignment_submission: AssignmentSubmission):
    assignment_directory=os.path.join(SUBMITTED_FILES_DIR,assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_directory,exist_ok=True)
    task_id=1
    assignment_file_names=[]
    print("assignment_submission::",assignment_submission)
    for assignment_file in assignment_submission.assignment_files:
        assignment_b64_decoded=base64.b64decode(assignment_file)
        #assignment_simple_str= assignment_b64_decoded.decode("ascii") #fails on hebrew
        print("before printing assignment_b64_decoded undecoded::")
        print(assignment_b64_decoded)
        print("after printing assignment_b64_decoded undecoded::")
        assignment_simple_str= assignment_b64_decoded.decode("utf-8") #works for hebrew but fails on printing result from some strange reason
        #not working from https://stackoverflow.com/questions/64849264/decoding-a-b64-encoded-string-in-python-with-non-english-characters
        #assignment_simple_str= assignment_b64_decoded.decode('latin-1')
        #good link to read on how to properly encode on base64 from utf-8 in javascript
        #https://stackoverflow.com/questions/30106476/using-javascripts-atob-to-decode-base64-doesnt-properly-decode-utf-8-strings
        print("before printing assignment_simple_str decoded::")
        #print(assignment_simple_str)
        print("after printing assignment_simple_str decoded::")
        assignment_file_name=f'task_{task_id}.py'
        assignment_file_name_full_path=os.path.join(assignment_directory,f'task_{task_id}.py')
        assignment_file_names.append(assignment_file_name)
        #with open(assignment_file_name_full_path, "w") as f:
        with open(assignment_file_name_full_path, "w", encoding="utf-8") as f:
            f.write(assignment_simple_str)
        task_id=task_id+1;
    return assignment_file_names

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
def submit_assignment(assignment_submission: AssignmentSubmission):
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
            assignment_submission.assignment_file_names=save_assignment_files(assignment_submission)
            assignment_submission.result = check_assignment_submission(assignment_submission)
            data[assignment_submission.hacker_id]={assignment_submission.assignment_id:[assignment_submission.model_dump()]}      
        else:
            if(str(assignment_submission.assignment_id) in data[assignment_submission.hacker_id]):
                assignment_submission.submission_id = len(data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)])+1                
                if(assignment_submission.submission_id<=max_submissions):
                    assignment_submission.assignment_file_names=save_assignment_files(assignment_submission)
                    assignment_submission.result = check_assignment_submission(assignment_submission)
                    data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)].append(assignment_submission.model_dump())
                else:
                    assignment_submission.result={"status":"ERROR","ERROR_message":f"cannot test assignment (assignment_id={str(assignment_submission.assignment_id)}) because submission attempts ({str(assignment_submission.submission_id)}) passed the allowed max_submissions (max_submissions={max_submissions})"}
                    lockRepository[assignment_submission.hacker_id].release()
                    submision_processing_concurrency_semaphore.release()
                    return assignment_submission.model_dump()
            else:
                assignment_submission.assignment_file_names=save_assignment_files(assignment_submission)
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
    trigger_mail_after_assignment_submission(assignment_submission)
    return assignment_submission.model_dump()

def trigger_mail_after_assignment_submission(assignment_submission:AssignmentSubmission):
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
        return {"assignment_id":1,"submission_id":1} # changed because of ui manual system tests failing, it makes more sense this way since new users still do not actually exist in assignment orchestrator data
        #return {"status": "ERROR", "ERROR_message":f"hacker_id:'{hacker_id}' does not exist"}

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

def last_assignment_submission_result(hacker_id:str):
    data=load_data_by_hacker_id(hacker_id)
    if hacker_id in data:    
        data=data[hacker_id]    
        assignment_keys=list(map(lambda key: int(key), data.keys()))
        assignment_keys.sort()
        last_assignment_keys=str(assignment_keys[-1])
        last_assignment_submissions= data[last_assignment_keys]
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