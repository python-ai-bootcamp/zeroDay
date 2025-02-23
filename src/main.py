from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr
from mailClient import Email, send_ses_mail

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.serialization import load_ssh_private_key

import json
import os

app = FastAPI()
domain_name = os.environ.get('DOMAIN_NAME', "127.0.0.1:8000")
print(domain_name)
protocol = "https" if os.environ.get('DOMAIN_NAME') else "http"
print(protocol)
index_html = open(os.path.join("resources","templates","index.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol)
public_key = load_ssh_public_key(open(os.path.join("resources","keys","id_rsa.pub"), "r").read().encode("utf-8"))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_DATA_FILE = os.path.join("./data/","user_data.json")
ASSIGNMENT_DATA_FILE = os.path.join("./data/","assignment_data.json")

def load_data(file_type: str = "user"):
    if file_type == "user":
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        return []
    elif file_type == "assignment":
        if os.path.exists(ASSIGNMENT_DATA_FILE):
            with open(ASSIGNMENT_DATA_FILE, "r") as f:
                return json.load(f)
        return {}
    else:
        raise Exception(f"no data file of type '{file_type}'")

def save_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def encrypt_by_public_key(message: str):
    ciphertext = public_key.encrypt(
        message.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(ciphertext)
    return ciphertext

class User(BaseModel):
    email: str
    password: str
    name: str

@app.get("/")
def serve_frontend():
    return HTMLResponse(content=index_html, status_code=200)

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

@app.get("/data")
def fetch_data(file_type: str = "user"):
    current_data = json.dumps(load_data(file_type=file_type))
    return PlainTextResponse(encrypt_by_public_key(current_data))
