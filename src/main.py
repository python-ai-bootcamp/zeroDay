import os
from userService import User, submit_user
from mailClient import Email, send_ses_mail
from exportService import fetch_symmetric_key, download_data
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()
domain_name = os.environ.get('DOMAIN_NAME', "127.0.0.1:8000")
print(domain_name)
protocol = "https" if os.environ.get('DOMAIN_NAME') else "http"
print(protocol)
isDevMod = "false" if os.environ.get('DOMAIN_NAME') else "true"
index_html = open(os.path.join("resources","templates","index.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{IS_DEV_MODE}}$$",isDevMod)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_frontend():
    return HTMLResponse(content=index_html, status_code=200)

@app.post("/submit")
def submit_user_endpoint(user: User):
    return submit_user(user) 

@app.get("/fetch_symmetric_key")
def fetch_symmetric_key_endpoint():
    return fetch_symmetric_key()

@app.get("/download/data.tar.gz")
def download_data_endpoint():
    return download_data()
