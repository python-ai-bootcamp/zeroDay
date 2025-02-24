from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr
from typing import List


import json, os, random, sys, subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

relative_data_directory="./data/"
relative_assignments_directory="./resources/config/assignments/"
DATA_FILE = os.path.join(relative_data_directory,"assignment_data.json")
ASSIGNMENT_MAPPER_FILE = os.path.join(relative_assignments_directory,"assignment_mapper.json")
ASSIGNMENT_VALIDATOR_DIR = os.path.join(relative_assignments_directory,"validators")

def load_data():
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

def execute_validator_on_task_file(validator_script:str, assignment_file:str):
    #cmd="ll -tr" #temporary command until the assignment_file saves a proper file to run tests on and a proper validator is set up
    #proc = subprocess.Popen(cmd,
    #    stdout = subprocess.PIPE,
    #    stderr = subprocess.PIPE,
    #)
    return {result:"PASS"} if random.random()>0.5 else {result:"FAIL", "FAIL_message":"you SUCK!"}

def check_assignment_submission(assignment_id:str,assignment_files:str):  
    assignment_mapper=load_assignment_mapper()
    print(assignment_mapper)
    validator_file_names=list(map(lambda validator_file_name: os.path.join(ASSIGNMENT_VALIDATOR_DIR,validator_file_name),assignment_mapper[assignment_id]["validators"]))
    task_idx=1
    for validator_script in validator_file_names:
        if assignment_files[task_idx] == f"task_{str(task_idx)}.py":
            execute_validator_on_task_file()
            #need to execute each validator script with assignment file name for task as its input
            #https://python.code-maven.com/python-capture-stdout-stderr-exit - this is a nice way to do it with subprocess
            #capture the STDOUT and STDERR of validator script
            #split first line as status
            #split rest of lines as message (if exists)
            #create a result and result message object and return it
            print(validator_script)
        else:
            return ERROR
    #return PASS if and only if all tasks returned result=True
    #if some task failed return FAIL and add its failure reason for the FAIL_message with a title of the task name
    return "PASS" if random.random()>0.5 else "FAIL"

def assignment_passed(assignment: list[dict]):
    return len(list(filter(lambda submission: submission["result"]=="PASS",assignment)))>0


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

@app.post("/submit")
def submit_assignment(assignment_submission: AssignmentSubmission): #NEED TO ADD FILE SAVE AT THIS POINT (under parallel structure like the data json under the data library) AND THEN ONLY PASS THE FILE NAME
    data = load_data()
    new_entry = assignment_submission.model_dump()
    if previous_assignment_passed(assignment_submission, data):
        new_entry["submission_id"] = 1   
        new_entry["result"] = check_assignment_submission(new_entry["assignment_id"], new_entry["assignment_files"])
        if(not assignment_submission.hacker_id in data):
            data[assignment_submission.hacker_id]={new_entry["assignment_id"]:[new_entry]}      
        else:
            if(str(new_entry["assignment_id"]) in data[assignment_submission.hacker_id]):
                new_entry["submission_id"]=len(data[assignment_submission.hacker_id][str(new_entry["assignment_id"])])+1
                data[assignment_submission.hacker_id][str(new_entry["assignment_id"])].append(new_entry)
            else:
                data[assignment_submission.hacker_id][str(new_entry["assignment_id"])]=[new_entry]
        save_data(data)
    else:
        new_entry["result"]="ERROR"
        new_entry["ERROR_message"]=f"cannot test assignment (assignment_id={str(new_entry['assignment_id'])}) until previous assignment (assignment_id={str(new_entry['assignment_id']-1)}) passes successfully"
        return new_entry
    return new_entry
