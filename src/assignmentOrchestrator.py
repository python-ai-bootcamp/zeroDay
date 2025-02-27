from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional


import json, os, random, sys, subprocess, base64,functools

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
DATA_FILE = os.path.join(relative_data_directory,"assignment_data.json")
ASSIGNMENT_MAPPER_FILE = os.path.join(relative_assignments_directory,"assignment_mapper.json")
ASSIGNMENT_VALIDATOR_DIR = os.path.join(relative_assignments_directory,"validators")
SUBMITTED_FILES_DIR=os.path.join(relative_data_directory,"submitted_files")

def load_data():
    #need to create some fancy locking mechanism to avoid race conditions https://theorangeduck.com/page/synchronized-python
    #not sure if should be done here, maybe should be in submit because its the only one that access load_data() and save_data() in a problematic way
    #def synchronized(func):
	#
    #func.__lock__ = threading.Lock()
	#	
    #def synced_func(*args, **kws):
    #    with func.__lock__:
    #        return func(*args, **kws)
    #
    #return synced_func

    #better explenation
    #https://www.geeksforgeeks.org/file-locking-in-python/

    #still not sure about weather to use multiprocessing.lock or theading.lock

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def load_assignment_mapper():
    if os.path.exists(ASSIGNMENT_MAPPER_FILE):
        with open(ASSIGNMENT_MAPPER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


class AssignmentSubmission(BaseModel):
    hacker_id: str
    assignment_id: int
    assignment_files: List[str]
    submission_id: Optional[int] = None
    result: Optional[dict] = None
    assignment_file_names:  Optional[List[str]] = None

def execute_validator_on_task_file(validator_script:str, assignment_file:str):
    #need to execute validator script with assignment file name for task as its input
    #https://python.code-maven.com/python-capture-stdout-stderr-exit - this is a nice way to do it with subprocess
    #capture the STDOUT and STDERR of validator script
    #split first line as status
    #split rest of lines as message (if exists)
    #create a result and result message object and return it
    #cmd="ll -tr" #temporary command until the assignment_file saves a proper file to run tests on and a proper validator is set up
    #proc = subprocess.Popen(cmd,
    #    stdout = subprocess.PIPE,
    #    stderr = subprocess.PIPE,
    #)
    return {"status":"PASS"} if random.random()>0.5 else {"status":"FAIL","FAIL_message":"face it, your code is shit!"}

def check_assignment_submission(assignment_submission:AssignmentSubmission):  
    assignment_mapper=load_assignment_mapper()
    print(assignment_mapper)
    validator_file_names=list(map(lambda validator_file_name: os.path.join(ASSIGNMENT_VALIDATOR_DIR,validator_file_name),assignment_mapper[assignment_submission.assignment_id]["validators"]))
    task_idx=1
    collected_results=[]
    for validator_script in validator_file_names:
        assignment_file=f"task_{str(task_idx)}.py"
        if assignment_submission.assignment_file_names[task_idx] == assignment_file:
            collected_results.append({"task_idx":task_idx,**execute_validator_on_task_file(validator_script=validator_script,assignment_file=assignment_file)})
        else:
            collected_results.append({"task_idx":task_idx,"status":"ERROR","ERROR_message":f"missing task ({assignment_file}) in assignment"})
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
    for assignment_file in assignment_submission.assignment_files:
        assignment_b64_decoded=base64.b64decode(assignment_file)
        assignment_simple_str= assignment_b64_decoded.decode("ascii")
        assignment_file_name=f'task_{task_id}.py'
        assignment_file_name_full_path=os.path.join(assignment_directory,f'task_{task_id}.py')
        assignment_file_names.append(assignment_file_name)
        with open(assignment_file_name_full_path, "w") as f:
            f.write(assignment_simple_str)
        task_id=task_id+1;
    return assignment_file_names

@app.post("/submit")
def submit_assignment(assignment_submission: AssignmentSubmission):
    data = load_data()
    if previous_assignment_passed(assignment_submission, data):
        assignment_submission.submission_id = 1 #in case no previous submission, then submission_id=1, will change to calculated value only if exisitng submition_id found
        if(not assignment_submission.hacker_id in data):
            assignment_submission.assignment_file_names=save_assignment_files(assignment_submission)
            assignment_submission.result = check_assignment_submission(assignment_submission)
            data[assignment_submission.hacker_id]={assignment_submission.assignment_id:[assignment_submission.model_dump()]}      
        else:
            if(str(assignment_submission.assignment_id) in data[assignment_submission.hacker_id]):
                assignment_submission.submission_id = len(data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)])+1
                assignment_submission.assignment_file_names=save_assignment_files(assignment_submission)
                assignment_submission.result = check_assignment_submission(assignment_submission)
                data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)].append(assignment_submission.model_dump())
            else:
                assignment_submission.assignment_file_names=save_assignment_files(assignment_submission)
                assignment_submission.result = check_assignment_submission(assignment_submission)
                data[assignment_submission.hacker_id][str(assignment_submission.assignment_id)]=[assignment_submission.model_dump()]
        save_data(data)
    else:
        assignment_submission.result={"status":"ERROR","ERROR_message":f"cannot test assignment (assignment_id={str(assignment_submission.assignment_id)}) until previous assignment (assignment_id={str(assignment_submission.assignment_id-1)}) passes successfully"}
        return assignment_submission.model_dump()
    return assignment_submission.model_dump()