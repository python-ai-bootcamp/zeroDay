from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr

import json
import os
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

relative_data_directory="./data/"
DATA_FILE = os.path.join(relative_data_directory,"assignment_submissions.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


class AssignmentSubmission(BaseModel):
    hacker_id: str
    assignment_id: int
    assignment_file: str
 
def check_assignment_submission(assignment_id:str,assignment_file:str):    
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
def submit_assignment(assignment_submission: AssignmentSubmission):
    data = load_data()
    new_entry = assignment_submission.model_dump()
    new_entry["submission_id"] = 1   
    new_entry["result"] = check_assignment_submission(new_entry["assignment_id"],new_entry["assignment_file"])
    
    if previous_assignment_passed(assignment_submission, data):
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
    