import os, json, zoneinfo, logging, urllib.parse, mimetypes, periodicTriggerService
from pathlib import Path
from v2Apis import router as v2_router
from datetime import datetime
from systemEntities import AnalyticsEventType, Payment, print
from analyticsService import insert_analytic_event, get_group_by_fields,convert_group_data_to_plotly_traces, group_data, ChallengeTrafficAnalyticsEvent, NewUserAnalyticsEvent, UserPaidAnalyticsEvent, UserSubmittedAssignmentAnalyticsEvent, UserPassedAssignmentAnalyticsEvent
from userService import User, submit_user, user_exists, get_user
from paymentService import initiate_user_payement_procedure, get_payment_code_hashes, get_amount_per_payment_code
from assignmentOrchestrator import assignment_description,next_assignment_submission, assignment_task_count, AssignmentSubmission, submit_assignment, user_testing_in_progress, max_submission_for_assignment, last_assignment_submission_result, get_submitted_file
from exportService import fetch_symmetric_key, download_data
from fastapi import FastAPI, BackgroundTasks, Request, Response, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from configurationService import domain_name, protocol, isDevMod
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles

israel_tz = zoneinfo.ZoneInfo("Asia/Jerusalem")
utc_tz = zoneinfo.ZoneInfo("UTC")

class DotTimeFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        return msg.replace(",", ".",1)
for handler in logging.getLogger().handlers:
    handler.setFormatter(DotTimeFormatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    ))    

STATIC_FILES_LIBRARY="./resources/static"
STATIC_SUBMITTED_FILES_LIBRARY = Path("./data/submitted_files")
app = FastAPI()
class StaticFilesWithIndex(StaticFiles):
    async def get_response(self, path: str, scope):
        if path == "":
            index_path = os.path.join(self.directory, "index.html")
            return FileResponse(index_path)
        return await super().get_response(path, scope)

#app.mount("/static", StaticFiles(directory=STATIC_FILES_LIBRARY), name="static")
app.mount("/static", StaticFilesWithIndex(directory=STATIC_FILES_LIBRARY, html=True), name="static") #modified to support /static as well as /static/
app.mount("/terminal", StaticFilesWithIndex(directory=STATIC_FILES_LIBRARY, html=True), name="ternimal")

# Add a route to handle /static
@app.get("/static", include_in_schema=False)
@app.get("/terminal", include_in_schema=False)

async def serve_static_index():
    index_path = os.path.join(STATIC_FILES_LIBRARY, "index.html")
    return FileResponse(index_path)

templates_processors={
    "challenge_page":                               lambda: open(os.path.join("resources","templates","challenge.html"), "r").read().replace("$${{IS_DEV_MODE}}$$",isDevMod),
    "about_page":                                   lambda: open(os.path.join("resources","templates","about.html"), "r").read(),
    "home_page":                                    lambda: open(os.path.join("resources","templates","home.html"), "r").read(),
    "payment_page":                                 lambda: open(os.path.join("resources","templates","payment.html"), "r").read(),
    "enlist_page":                                  lambda: open(os.path.join("resources","templates","enlist.html"), "r").read(),
    "contact_page":                                 lambda: open(os.path.join("resources","templates","contact.html"), "r").read(),
    "assignments_page":                             lambda: open(os.path.join("resources","templates","assignments.html"), "r").read(),
    "assignment_submission_page":                   lambda: open(os.path.join("resources","templates","assignment_submission.html"), "r").read(),
    "assignment_submission_v2test_page":            lambda: open(os.path.join("resources","templates","assignment_submission_v2test.html"), "r").read(),
    "assignment_submission_v2test_with_zip_page":   lambda: open(os.path.join("resources","templates","assignment_submission_v2test_with_zip.html"), "r").read(),
    "last_submission_results_page":                 lambda: open(os.path.join("resources","templates","last_submission_results.html"), "r").read(),
    "submitted_task_file_page":                     lambda: open(os.path.join("resources","templates","submitted_task_file.html"), "r").read(),
    "last_submission_results_no_results_page":      lambda: open(os.path.join("resources","templates","last_submission_results_no_results.html"), "r").read(),
    "analytics_page":                               lambda: open(os.path.join("resources","templates","analytics.html"), "r").read(),
    "payment_redirect_page":                        lambda: f'<html><head><meta http-equiv="refresh" content="5; url={protocol}://{domain_name}/enlist"/></head><body><p>This Page Is Still Under Construction</p><p>User will be redirected back to enlistment page in 5 seconds</p></body></html>',
    "redirect_to_enlistment_page":                  lambda: f'<html><head><meta http-equiv="refresh" content="0; url={protocol}://{domain_name}/enlist"/></head><body></body></html>',
    "redirect_to_last_submission_result_page":      lambda: f'<html><head><meta http-equiv="refresh" content="0; url={protocol}://{domain_name}/last_submission_result"/></head><body></body></html>',
    "redirect_to_shell_frontend":                   lambda: f'<html><head><meta http-equiv="refresh" content="0; url={protocol}://{domain_name}/terminal"/></head><body></body></html>',
}

processed_templates_for_prod_efficiency={}

for key,value in templates_processors.items():
    processed_templates_for_prod_efficiency[key]=value()

def get_template(template_name:str):
    if isDevMod:
        return templates_processors[template_name]()
    else:
        return processed_templates_for_prod_efficiency[template_name]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v2_router)

class SessionAuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        hacker_id=request.query_params.get("hacker_id")
        #print(f"main::SessionAuthenticationMiddleware:: got following value for hacker_id url parameter:'{hacker_id}'")
        if hacker_id:
            user=get_user(hacker_id) 
            if user["status"]=="OK":
                request.state.authenticated_user = user["user"]
            else:
                request.state.authenticated_user = False
        else:
            hacker_id=request.cookies.get('sessionKey')
            print(f"got following cookey value for sessionKey hacker_id:'{hacker_id}'")
            if hacker_id:
                user=get_user(hacker_id) 
                if user["status"]=="OK":
                    request.state.authenticated_user = user["user"]
                else:
                    request.state.authenticated_user = False
            else:
                request.state.authenticated_user = False

        response = await call_next(request)
        if request.state.authenticated_user:
            response.set_cookie(key="sessionKey", value=request.state.authenticated_user["hacker_id"])
        else:
            response.set_cookie(key="sessionKey", value="", max_age=0)

        return response
    
app.add_middleware(SessionAuthenticationMiddleware)    

def escape(s: str) -> str:
    return urllib.parse.quote(s)

@app.get("/submitted_tasks_browser/{path:path}", response_class=HTMLResponse)
@app.get("/submitted_tasks_browser", response_class=HTMLResponse)
async def browse(request: Request, path: str = ""):
    user=request.state.authenticated_user
    if user and user["paid_status"]:
        full_path = STATIC_SUBMITTED_FILES_LIBRARY / user["hacker_id"] / path
        
        path_list=list(path.split('/'))
        print(path_list)
        prefix=""
        if 0 in range(len(path_list)):
            if path_list[0]=='':
                prefix="Assignment_"
            else:
                path_list[0]="assignment_"+path_list[0]
                prefix="Submission_"
        if 1 in range(len(path_list)):
            path_list[1]="submission_"+path_list[1]
            prefix="Task_"
        if 2 in range(len(path_list)):
            path_list[2]="task_"+path_list[2]
        path_str="/".join(path_list)  



        if not full_path.exists():
            return HTMLResponse(content="<h1>ERROR:: file not found</h1>", status_code=404)

        # preview or download of the files user clickcs on
        if full_path.is_file():
            mime, _ = mimetypes.guess_type(str(full_path))
            if mime and mime.startswith("text/"):
                try:
                    content = full_path.read_text(encoding="utf-8")
                except Exception:
                    content = "ERROR:: can't read file, wtf!"
                return HTMLResponse(f"""
                    <h1>📄 {path_str.rsplit('/', 1)[0]}/{full_path.name}</h1>
                    <pre style="background:#f4f4f4; padding:1em; overflow-x:auto;">{content}</pre>
                    <p><a href="/submitted_tasks_browser/{escape('/'.join(path.split('/')[:-1]))}">⬅️ Back</a></p>
                """)
            else:
                return FileResponse(full_path)

        # directory file list
        items = sorted(full_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        list_items = []
        
        if path:
            parent = '/'.join(path.strip('/').split('/')[:-1])
            list_items.append(f'<li><a href="/submitted_tasks_browser/{escape(parent)}">⬅️ .. (up)</a></li>')

        for item in items:
            item_path = f"{path}/{item.name}".strip("/")
            display_name = f"{prefix}{item.name}/" if item.is_dir() else item.name
            list_items.append(f'<li><a href="/submitted_tasks_browser/{escape(item_path)}">{display_name}</a></li>')  

        return HTMLResponse(f"""
            <h1>📁 /{path_str}</h1>
            <ul>
                {''.join(list_items)}
            </ul>
        """)
    
    else:
        assignments_page_html=get_template("redirect_to_enlistment_page")
        return HTMLResponse(content=assignments_page_html, status_code=200)
    
@app.get("/about")
def serve_about(request: Request):
    about_page_html = get_template("about_page") 
    user=request.state.authenticated_user
    print(f"is_session_validated:'{user}'")
    if user:
        if user["paid_status"]:
            about_page_html=about_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Dive In</a>')\
                .replace("$${{ENLISTMENT_PROCESS_SECTION}}$$",'<li>You have successfully passed the challenge and enlisted into our ZeroDayBootcamp program</li><li>You may now engage in our next challenges in the <a href="/assignments" style="color:#778881;">Assignments Page</a></li>')
        else:
            about_page_html=about_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
                .replace("$${{ENLISTMENT_PROCESS_SECTION}}$$",'<li>You have successfully passed the initial screening <a href="/challenge" style="color:#778881;">zeroDayBootCamp</a> challenge</li><li>You can now finish our enlistment process in our <a href="/enlist" style="color:#778881;">Enlistment Page</a></li>')
        html_response=HTMLResponse(content=about_page_html, status_code=200)
    else:
        about_page_html=about_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
            .replace("$${{ENLISTMENT_PROCESS_SECTION}}$$",'<li>One can enlist only after passing the <a href="/challenge" style="color:#778881;">zeroDayBootCamp</a> challenge</li><li>Once passing the challenge, a dedicated link will be sent via mail enabling payment for registration</li>')
        html_response=HTMLResponse(content=about_page_html, status_code=200)
    return html_response

@app.get("/challenge")
def serve_challange(advertise_code:str="unknown",advertise_code_sub_category:str="unknown"):
    insert_analytic_event(ChallengeTrafficAnalyticsEvent(advertise_code=advertise_code, advertise_code_sub_category=advertise_code_sub_category))
    challenge_page_html=get_template("challenge_page")\
        .replace("$${{ADVERTISE_CODE}}$$",advertise_code)\
        .replace("$${{ADVERTISE_CODE_SUB_CATEGORY}}$$",advertise_code_sub_category)
    return HTMLResponse(content=challenge_page_html, status_code=200)

@app.get("/")
def serve_home(request: Request):
    user=request.state.authenticated_user
    print(user)
    home_page_html = get_template("home_page")
    if(user):
        is_paid=user["paid_status"]
        if(is_paid):
            home_page_html=home_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Dive In</a>')\
                .replace("$${{RECRUITE_NAME}}$$",user["name"])\
                .replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">Congratulation for enlisting the ZeroDayBootcamp project!</p><p style="padding-bottom:50px">You may now enter the assignment page to start learning</p><a href="/assignments" class="cta-button" >Enter Assignment Page</a>')
        else:
            home_page_html=home_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
                .replace("$${{RECRUITE_NAME}}$$",user["name"])\
                .replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">Congratulation for completeing the ZeroDayBootCamp challenge successfully!</p><p style="padding-bottom:50px">You may now enlist to the continuation of your journy</p><a href="/enlist" class="cta-button" >Enlist</a>')
    else:
        home_page_html=home_page_html\
            .replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
            .replace("$${{RECRUITE_NAME}}$$",'Dear Recruite')\
            .replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">After completing the challenge bellow you will be invited to join the ZeroDay BootCamp</p><a href="/challenge" class="cta-button" >Take the Challenge</a>')
    return HTMLResponse(content=home_page_html, status_code=200)

@app.get("/payment")
def serve_payment(request: Request):
    user=request.state.authenticated_user
    payment_page_html = get_template("payment_page")
    if(user):
        payment_page_html = payment_page_html\
            .replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])
    else:
        payment_page_html = get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=payment_page_html, status_code=200)

@app.get("/payment_code_hashes")
def serve_payment_codes():
    return get_payment_code_hashes()

@app.get("/amount_per_payment_code")
def serve_amount_per_payment_code(payment_code:str = "regular"):
    return get_amount_per_payment_code(payment_code)
    
@app.get("/paymentRedirect")
def serve_payment_redirect(background_tasks: BackgroundTasks, request: Request, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str, paymentCode:str = "regular"):
    user=request.state.authenticated_user
    if(user):
        payment_page_html = get_template("payment_redirect_page")
        #user=User.model_validate(user)
        now_israel = datetime.now(israel_tz)
        now_utc = datetime.now(utc_tz)
        payment=Payment.model_validate({"user":user,"ClientName":ClientName, "ClientLName":ClientLName, "UserId":UserId, "email":email, "phone":phone, "date":now_israel.strftime("%d/%m/%Y"), "time":now_israel.strftime("%H:%M:%S"),  "utc_date":now_utc.strftime("%d/%m/%Y"), "utc_time":now_utc.strftime("%H:%M:%S"), "paymentCode":paymentCode})
        initiate_user_payement_procedure(payment, background_tasks)
    else:
        payment_page_html = get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=payment_page_html, status_code=200)

@app.get("/enlist")
def serve_enlist(request: Request):
    user=request.state.authenticated_user
    enlist_page_html = get_template("enlist_page")
    if(user):
        if(user["paid_status"]):
            enlist_page_html=enlist_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Dive In</a>')\
                .replace("$${{ENLISTMENT_TITLE}}$$","Enlistment Completed")\
                .replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'href="/assignments"')\
                .replace("$${{BUTTON_CLASS}}$$","cta-button")\
                .replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enter Assignment Page")\
                .replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>User Already Enlisted</p><p>You can now enter assignment page</p><p style="margin:40px;"></p>')
        else:
            enlist_page_html=enlist_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
                .replace("$${{ENLISTMENT_TITLE}}$$","Enlist to Bootcamp")\
                .replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'href="/payment"')\
                .replace("$${{BUTTON_CLASS}}$$","cta-button")\
                .replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist Now")\
                .replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>Challenge Passed Successfully</p><p>Enlistment is Now Opened</p><p class="price">50&#8362;</p>')      
    else:
        enlist_page_html=enlist_page_html\
            .replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
            .replace("$${{ENLISTMENT_TITLE}}$$","Enlist to Bootcamp")\
            .replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'role="link"')\
            .replace("$${{BUTTON_CLASS}}$$","cta-button-inactive")\
            .replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist (deactivated)")\
            .replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>locked until completing <a href="/challenge" style="color:#778881;"><h2>the challenge</h2><p style="padding-bottom:10px"></p></a></p>')
        
    return HTMLResponse(content=enlist_page_html, status_code=200)

@app.get("/contact")
def serve_contact(request: Request):
    user=request.state.authenticated_user
    contact_page_html = get_template("contact_page")
    if user and user["paid_status"]:
        contact_page_html=contact_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Dive In</a>')
    else:
        contact_page_html=contact_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'')
    return HTMLResponse(content=contact_page_html, status_code=200)

@app.get("/assignments")
def serve_assignments(request: Request):
    user=request.state.authenticated_user
    assignments_page_html = get_template("assignments_page")
    if user and user["paid_status"]:
        print("user is paid, redirecting to shell frontend ")
        assignments_page_html=get_template("redirect_to_shell_frontend")
    else:
        print("unpaid/nonExisting user, redirecting to payment page ")
        assignments_page_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=assignments_page_html, status_code=200)

@app.get("/assignments_legacy_static_page")
def serve_assignments(request: Request):
    user=request.state.authenticated_user
    assignments_page_html = get_template("assignments_page")
    if user and user["paid_status"]:
        next_assignment=next_assignment_submission(user["hacker_id"])
        #print(f"next_assignment::{next_assignment}")
        current_assignment_id=next_assignment["assignment_id"]
        current_assignment_description=assignment_description(current_assignment_id)
        #print(current_assignment_description)
        if(current_assignment_description["status"] == "ERROR"):
            assignments_page_html=assignments_page_html\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_DESCRIPTION_CONTENT}}$$","<p>Please check back in a few days</p><p>We will notify you in an email if anything changes</p>")\
            .replace("$${{TITLE}}$$","No Currently Available New Assignments")\
            .replace("$${{BREACH_MAX_ATTEMPT_MESSAGE}}$$","")\
            .replace("$${{SUBMIT_ASSIGNMENT_BUTTON_VISIBILITY}}$$","hidden")
        else:
            submission_result=last_assignment_submission_result(user["hacker_id"])
            submit_assignment_button_visibility=""
            assignment_title="Assignment Description:"
            max_allowed_submissions_breach_message=""
            if submission_result["status"] == "OK": # this branch checks if user breached the max submission results, if so, it blocks him from submitting any more
                submission_result=submission_result["last_assignment_submission_result"]
                last_submitted_assignment_id=submission_result["assignment_id"]
                max_allowed_attempts = max_submission_for_assignment(last_submitted_assignment_id)
                if last_submitted_assignment_id == current_assignment_id and submission_result["submission_id"] == max_allowed_attempts: 
                    submit_assignment_button_visibility="hidden"
                    max_allowed_submissions_breach_message=f'<h4 style="color:red;">(User failed max allowed submission attempts ({max_allowed_attempts}) and can not continue submitting)</h4>'
            current_assignment_description=current_assignment_description["assignment_description"]
            assignments_page_html=assignments_page_html\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_DESCRIPTION_CONTENT}}$$",current_assignment_description)\
            .replace("$${{TITLE}}$$",assignment_title)\
            .replace("$${{CURRENT_ASSIGNMENT_ID}}$$",str(current_assignment_id))\
            .replace("$${{BREACH_MAX_ATTEMPT_MESSAGE}}$$",max_allowed_submissions_breach_message)\
            .replace("$${{SUBMIT_ASSIGNMENT_BUTTON_VISIBILITY}}$$",submit_assignment_button_visibility)
    else:
        assignments_page_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=assignments_page_html, status_code=200)

@app.get("/assignment_submission_old")
def serve_assignment_submission(request: Request):
    user=request.state.authenticated_user 
    assignment_submission_page_html = get_template("assignment_submission_page")
    if user and user["paid_status"]:
        next_assignment_id=next_assignment_submission(user["hacker_id"])["assignment_id"]
        if user_testing_in_progress(user["hacker_id"]):
            print(f'user {user["hacker_id"]} is locked for testing')
            assignment_submission_page_html=get_template("redirect_to_last_submission_result_page")
        else:           
            print(f'user {user["hacker_id"]} is not locked for testing')
            task_count=assignment_task_count(next_assignment_id)["task_count"]
            assignment_submission_page_html=assignment_submission_page_html\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_ID}}$$",str(next_assignment_id))\
            .replace("$${{MUMBER_OF_TASKS_IN_ASSIGNMENT}}$$",str(task_count))
    else:
        assignment_submission_page_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=assignment_submission_page_html, status_code=200)

@app.get("/assignment_submission_v2test")
def serve_assignment_submission_v2test(request: Request):
    user=request.state.authenticated_user 
    assignment_submission_v2test_page_html = get_template("assignment_submission_v2test_page")
    if user and user["paid_status"]:
        next_assignment_id=next_assignment_submission(user["hacker_id"])["assignment_id"]
        if user_testing_in_progress(user["hacker_id"]):
            print(f'user {user["hacker_id"]} is locked for testing')
            assignment_submission_v2test_page_html=get_template("redirect_to_last_submission_result_page")
        else:           
            print(f'user {user["hacker_id"]} is not locked for testing')
            task_count=assignment_task_count(next_assignment_id)["task_count"]
            assignment_submission_v2test_page_html=assignment_submission_v2test_page_html\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_ID}}$$",str(next_assignment_id))\
            .replace("$${{MUMBER_OF_TASKS_IN_ASSIGNMENT}}$$",str(task_count))
    else:
        assignment_submission_v2test_page_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=assignment_submission_v2test_page_html, status_code=200)

@app.get("/assignment_submission")
def serve_assignment_submission_v2test_with_zip(request: Request):
    user=request.state.authenticated_user 
    assignment_submission_v2test_page_with_zip_html = get_template("assignment_submission_v2test_with_zip_page")
    if user and user["paid_status"]:
        next_assignment_id=next_assignment_submission(user["hacker_id"])["assignment_id"]
        if user_testing_in_progress(user["hacker_id"]):
            print(f'user {user["hacker_id"]} is locked for testing')
            assignment_submission_v2test_page_with_zip_html=get_template("redirect_to_last_submission_result_page")
        else:           
            print(f'user {user["hacker_id"]} is not locked for testing')
            task_count=assignment_task_count(next_assignment_id)["task_count"]
            assignment_submission_v2test_page_with_zip_html=assignment_submission_v2test_page_with_zip_html\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_ID}}$$",str(next_assignment_id))\
            .replace("$${{MUMBER_OF_TASKS_IN_ASSIGNMENT}}$$",str(task_count))
    else:
        assignment_submission_v2test_page_with_zip_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=assignment_submission_v2test_page_with_zip_html, status_code=200)

@app.get("/last_submission_result")
def serve_last_submission_result(request: Request):
    user=request.state.authenticated_user 
    last_submission_results_page_html = get_template("last_submission_results_page")
    if user and user["paid_status"]:
        if user_testing_in_progress(user["hacker_id"]):
            assignment_id=next_assignment_submission(user["hacker_id"])["assignment_id"]
            submission_id=next_assignment_submission(user["hacker_id"])["submission_id"]
            last_submission_results_page_html=last_submission_results_page_html\
            .replace("$${{ASSIGNMENT_ID}}$$",str(assignment_id))\
            .replace("$${{SUBMISSION_ID}}$$",str(submission_id))\
            .replace("$${{MAX_ALLOWED_SUBMISSIONS}}$$",str(max_submission_for_assignment(assignment_id)))\
            .replace("$${{REFRESH_META_TAG}}$$",'<meta http-equiv="refresh" content="3">')\
            .replace("$${{WAITING_FOR_RESULT_MESSAGE}}$$","<h3>Testing is still under progress</h3>")\
            .replace("$${{SUBMISSION_RESULT_CONTENT}}$$","")
        else:
            submission_result=last_assignment_submission_result(user["hacker_id"])
            if submission_result["status"] == "OK":
                submission_result=submission_result["last_assignment_submission_result"]
                assignment_id=submission_result["assignment_id"]
                submission_id=submission_result["submission_id"]
                submission_result_for_view=submission_result
                del submission_result_for_view["assignment_file_names"]
                #submission_result_for_view["result"]["collected_results"]=list(map(lambda task_result:{**task_result,"submitted_task_file":f"{protocol}://{domain_name}/submitted_task_file?assignment_id={assignment_id}&submission_id={submission_id}&task_id={task_result['task_idx']}"},submission_result_for_view["result"]["collected_results"]))
                submission_result_for_view["result"]["collected_results"]=list(map(lambda task_result:{**task_result,"submitted_task_files":f"{protocol}://{domain_name}/submitted_tasks_browser/{assignment_id}/{submission_id}/{task_result['task_idx']}"},submission_result_for_view["result"]["collected_results"]))
                submission_result_content=f"data={json.dumps(submission_result_for_view)}"
                assignment_id=submission_result["assignment_id"]
                last_submission_results_page_html=last_submission_results_page_html\
                .replace("$${{ASSIGNMENT_ID}}$$",str(assignment_id))\
                .replace("$${{SUBMISSION_ID}}$$",str(submission_result["submission_id"]))\
                .replace("$${{MAX_ALLOWED_SUBMISSIONS}}$$",str(max_submission_for_assignment(assignment_id)))\
                .replace("$${{REFRESH_META_TAG}}$$",'')\
                .replace("$${{SUBMISSION_RESULT_CONTENT}}$$",submission_result_content)\
                .replace("$${{WAITING_FOR_RESULT_MESSAGE}}$$","")
            else:
                last_submission_results_no_results_page_html = get_template("last_submission_results_no_results_page")
                last_submission_results_page_html=last_submission_results_no_results_page_html
                print(submission_result["ERROR_message"])
    else:
        last_submission_results_page_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=last_submission_results_page_html, status_code=200)

@app.get("/submitted_task_file")
def serve_last_submission_result(request: Request,assignment_id:str, submission_id:str, task_id:str):
    user=request.state.authenticated_user 
    submitted_task_file_page_html = get_template("submitted_task_file_page")
    if user and user["paid_status"]:
        file_content=get_submitted_file(user["hacker_id"], assignment_id, submission_id, task_id)
        submitted_task_file_page_html=submitted_task_file_page_html\
        .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
        .replace("$${{ASSIGNMENT_ID}}$$",assignment_id)\
        .replace("$${{SUBMISSION_ID}}$$",submission_id)\
        .replace("$${{TASK_ID}}$$",task_id)\
        .replace("$${{FILE_CONTENT}}$$",file_content)
    else:
        submitted_task_file_page_html=get_template("redirect_to_enlistment_page")
    return HTMLResponse(content=submitted_task_file_page_html, status_code=200)

@app.get("/user_exists")
def get_user_exists(email:str):
    return user_exists(email)

@app.get("/user")
def get_get_user(hacker_id:str):
    return get_user(hacker_id)

@app.get("/assignment_description")
def get_assignment_description(hacker_id:str):
    next_assignment_id=next_assignment_submission(hacker_id)
    current_assignment_description=assignment_description(next_assignment_id["assignment_id"])
    return PlainTextResponse(current_assignment_description["assignment_description"])

@app.post("/submit_user")
def submit_user_endpoint(user: User):
    submit_user_response=submit_user(user) 
    if submit_user_response["status"]=="SAVED":
        insert_analytic_event(NewUserAnalyticsEvent(advertise_code=user.advertise_code, advertise_code_sub_category=user.advertise_code_sub_category))
    return submit_user_response

@app.get("/fetch_symmetric_key")
def fetch_symmetric_key_endpoint():
    return fetch_symmetric_key()

@app.get("/download/data.tar.gz")
def download_data_endpoint():
    return download_data()


def create_submit_assignment_background_task(tar_bytes: bytes, json_data: dict):
    submit_assignment(tar_bytes, json_data)

@app.post("/submit_assignment")
def post_submit_assignment(background_tasks: BackgroundTasks, tar_file: UploadFile = File(...), json_data: str = Form(...)):
    print("entered submit assignment")
    tar_bytes = tar_file.file.read() 
    json_data = json.loads(json_data)
    background_tasks.add_task(create_submit_assignment_background_task, tar_bytes, json_data)
    print("assignment_submission added as background task")
    return {"status":"SUBMITTED"}

@app.get("/analytics")
def serve_analytics():
    analytics_page_html = get_template("analytics_page")
    html_response=HTMLResponse(content=analytics_page_html, status_code=200)
    return html_response

@app.get("/analytics/data")
def serve_analytics_data(time_bucket:int=3600, group_by_field:str="advertise_code", from_time:int=0, to_time:int=99999999999999, analytics_event_type:str="CHALLENGE_TRAFFIC", filter_field_name:str=None, filter_field_value=None):
    if filter_field_value=="null":
        grouped_data,time_buckets=group_data(from_time, to_time, time_bucket, group_by_field, AnalyticsEventType[analytics_event_type], None, None)   
    else:
        grouped_data,time_buckets=group_data(from_time, to_time, time_bucket, group_by_field, AnalyticsEventType[analytics_event_type], filter_field_name, filter_field_value)
    plotly_traces=convert_group_data_to_plotly_traces(grouped_data, time_buckets)
    return plotly_traces

@app.get("/analytics/eventTypes")
def serve_event_types():
    analytics_event_type=list(AnalyticsEventType.__members__.keys())
    return analytics_event_type 

@app.get("/analytics/groupByFields")
def serve_get_group_by_fields(from_time:int=0, to_time:int=99999999999999, analytics_event_type:str="CHALLENGE_TRAFFIC", filter_field_name:str=None, filter_field_value=None):
    if filter_field_value=="null":
        return get_group_by_fields(from_time, to_time, AnalyticsEventType[analytics_event_type], None, None)
    else:
        return get_group_by_fields(from_time, to_time, AnalyticsEventType[analytics_event_type], filter_field_name, filter_field_value)

