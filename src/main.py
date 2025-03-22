import os
from userService import User, submit_user
from mailClient import Email, send_ses_mail
from exportService import fetch_symmetric_key, download_data
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from configurationService import domain_name, protocol, isDevMod
from userService import get_user

app = FastAPI()

challenge_page_html = open(os.path.join("resources","templates","challenge.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{IS_DEV_MODE}}$$",isDevMod)
registration_page_html = open(os.path.join("resources","templates","registration.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{IS_DEV_MODE}}$$",isDevMod)
home_page_html = open(os.path.join("resources","templates","index.html"), "r").read()
shop_page_html = open(os.path.join("resources","templates","shop.html"), "r").read()
contact_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/challenge")
def serve_challange():
    return HTMLResponse(content=challenge_page_html, status_code=200)

@app.get("/")
def serve_home():
    home_page_html = open(os.path.join("resources","templates","index.html"), "r").read()
    return HTMLResponse(content=home_page_html, status_code=200)

@app.get("/about")
def serve_home():
    about_page_html = open(os.path.join("resources","templates","about.html"), "r").read()
    return HTMLResponse(content=about_page_html, status_code=200)

@app.get("/shop")
def serve_home():
    about_page_html = open(os.path.join("resources","templates","shop.html"), "r").read()
    return HTMLResponse(content=shop_page_html, status_code=200)

@app.get("/contact")
def serve_home():
    about_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()
    return HTMLResponse(content=contact_page_html, status_code=200)

@app.get("/register")
def serve_registration_page(hacker_id:str):
    user=get_user(hacker_id)
    return HTMLResponse(content=registration_page_html.replace("$${{NAME}}$$",user["name"]), status_code=200)

@app.post("/submit")
def submit_user_endpoint(user: User):
    return submit_user(user) 
    

@app.get("/fetch_symmetric_key")
def fetch_symmetric_key_endpoint():
    return fetch_symmetric_key()

@app.get("/download/data.tar.gz")
def download_data_endpoint():
    return download_data()
