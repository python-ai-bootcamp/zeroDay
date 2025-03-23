import os
from userService import User, submit_user, user_exists, get_user
from mailClient import Email, send_ses_mail
from exportService import fetch_symmetric_key, download_data
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from configurationService import domain_name, protocol, isDevMod


app = FastAPI()

challenge_page_html = open(os.path.join("resources","templates","challenge.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{IS_DEV_MODE}}$$",isDevMod)
home_page_html = open(os.path.join("resources","templates","home.html"), "r").read()
enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read()
contact_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_session(request: Request=None, response: Response=None, hacker_id: str=None):
    if hacker_id:
        user=get_user(hacker_id) 
        if user["status"]=="OK":
            response.set_cookie(key="sessionKey", value=hacker_id)
            return hacker_id
        else:
            response.set_cookie(key="sessionKey", value="")
            return False
    else:
        hacker_id=request.cookies.get('sessionKey')
        if hacker_id:
            user=get_user(hacker_id) 
            if user["status"]=="OK":
                return hacker_id
            else:
                return False
        else:
            return False

@app.get("/challenge")
def serve_challange():
    return HTMLResponse(content=challenge_page_html, status_code=200)

@app.get("/")
def serve_home(request: Request):
    is_session_validated=validate_session(request=request)
    if(is_session_validated):
        user=get_user(hacker_id=is_session_validated)["user"]
        home_page_html = open(os.path.join("resources","templates","home.html"), "r").read().replace("$${{RECRUITE_NAME}}$$",user["name"]).replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">Congratulation for completeing the ZeroDayBootCamp challenge successfully!</p><p style="padding-bottom:50px">You may now enlist to the continuation of your journy</p><a href="/enlist" class="cta-button" >Enlist</a>')
    else:
        home_page_html = open(os.path.join("resources","templates","home.html"), "r").read().replace("$${{RECRUITE_NAME}}$$",'Dear Recruite').replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">After completing the challenge bellow you will be invited to join the ZeroDay BootCamp</p><a href="/challenge" class="cta-button" >Take the Challenge</a>')
    return HTMLResponse(content=home_page_html, status_code=200)

@app.get("/payment")
def serve_home():
    return HTMLResponse(content="<html><body>unimplemented yet</body></html>", status_code=200)

@app.get("/about")
def serve_home(request: Request, hacker_id:str=None):
    about_page_html = open(os.path.join("resources","templates","about.html"), "r").read()
    html_response=HTMLResponse(content=about_page_html, status_code=200)
    is_session_validated=validate_session(request=request, response=html_response, hacker_id=hacker_id)
    print(f"is_session_validated:'{is_session_validated}'")
    return html_response

@app.get("/enlist")
def serve_home(request: Request):
    is_session_validated=validate_session(request=request)
    if(is_session_validated):
        enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read().replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'href="/payment"').replace("$${{BUTTON_CLASS}}$$","cta-button").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist Now").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>Challenge Passed Successfully</p><p>Enlistment is Now Opened</p><p class="price">50&#8362;</p>')
    else:
        enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read().replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'role="link"').replace("$${{BUTTON_CLASS}}$$","cta-button-inactive").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist (deactivated)").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>locked until completing <a href="/challenge" style="color:#778881;"><h2>the challenge</h2><p style="padding-bottom:10px"></p></a></p>')
    return HTMLResponse(content=enlist_page_html, status_code=200)



@app.get("/contact")
def serve_home():
    contact_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()
    return HTMLResponse(content=contact_page_html, status_code=200)

@app.get("/user_exists")
def get_user_exists(email:str):
    return user_exists(email)

@app.get("/user")
def get_get_user(hacker_id:str):
    return get_user(hacker_id)

@app.post("/submit")
def submit_user_endpoint(user: User):
    return submit_user(user) 
    

@app.get("/fetch_symmetric_key")
def fetch_symmetric_key_endpoint():
    return fetch_symmetric_key()

@app.get("/download/data.tar.gz")
def download_data_endpoint():
    return download_data()
