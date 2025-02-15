from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class User(BaseModel):
    email: str
    password: str
    name: str

@app.post("/submit")
def submit_user(user: User):
    data = load_data()
    
    # Check if email exists and update
    for entry in data:
        if entry["email"] == user.email:
            entry["name"] = user.name
            save_data(data)
            return {"message": "User updated", "user": entry}
    
    # Add new user
    new_entry = user.dict()
    data.append(new_entry)
    save_data(data)
    return {"message": "User saved", "user": new_entry}
