import os
from userService import User, submit_user
from mailClient import Email, send_ses_mail
from exportService import fetch_symmetric_key, download_data
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from configurationService import domain_name, protocol, isDevMod
from userService import get_user

app = FastAPI()

challenge_page_html = open(os.path.join("resources","templates","challenge.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{IS_DEV_MODE}}$$",isDevMod)
home_page_html = open(os.path.join("resources","templates","index.html"), "r").read()
enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read()
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

@app.get("/payment")
def serve_home():
    return HTMLResponse(content="<html><body>unimplemented yet</body></html>", status_code=200)

@app.get("/about")
def serve_home(response: Response, hacker_id:str=None):
    about_page_html = open(os.path.join("resources","templates","about.html"), "r").read()
    html_response=HTMLResponse(content=about_page_html, status_code=200)
    if(hacker_id):       
        html_response.set_cookie(key="sessionKey", value="fake-cookie-session-value")
    return html_response

@app.get("/enlist")
def serve_home(request: Request):
    session_key=request.cookies.get('sessionKey')
    if(session_key):
        print(f"found following session key:'{session_key}'")
        enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read().replace("$${{BUTTON_CLASS}}$$","cta-button").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist Now").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>Challenge Passed Successfully</p><p>Enlistment is Now Opened</p><p class="price">50&#8362;</p>')
        return HTMLResponse(content=enlist_page_html, status_code=200)
    else:
        print(f"did not find a session key")
        enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read().replace("$${{BUTTON_CLASS}}$$","cta-button-inactive").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist (deactivated)").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>locked until completing <a href="/challenge" style="color:#778881;"><h2>the challenge</h2><p style="padding-bottom:10px"></p></a></p>')
        return HTMLResponse(content=enlist_page_html, status_code=200)



@app.get("/contact")
def serve_home():
    contact_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()
    return HTMLResponse(content=contact_page_html, status_code=200)

@app.post("/submit")
def submit_user_endpoint(user: User):
    return submit_user(user) 
    

@app.get("/fetch_symmetric_key")
def fetch_symmetric_key_endpoint():
    return fetch_symmetric_key()

@app.get("/download/data.tar.gz")
def download_data_endpoint():
    return download_data()
