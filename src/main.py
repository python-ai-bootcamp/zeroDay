import os,json, periodicTriggerService
from userService import User, submit_user, user_exists, get_user, initiate_user_payement_procedure
from assignmentOrchestrator import assignment_description,next_assignment_submission, assignment_task_count, AssignmentSubmission, submit_assignment, user_testing_in_progress, max_submission_for_assignment, last_assignment_submission_result, get_submitted_file
from exportService import fetch_symmetric_key, download_data
from fastapi import FastAPI, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from configurationService import domain_name, protocol, isDevMod
from starlette.responses import FileResponse


app = FastAPI()

challenge_page_html = open(os.path.join("resources","templates","challenge.html"), "r").read().replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{IS_DEV_MODE}}$$",isDevMod)
redirect_to_enlistment_page=f'<html><head><meta http-equiv="refresh" content="0; url={protocol}://{domain_name}/enlist"/></head><body></body></html>'
redirect_to_last_submission_result_page=f'<html><head><meta http-equiv="refresh" content="0; url={protocol}://{domain_name}/last_submission_result"/></head><body></body></html>'
home_page_html = open(os.path.join("resources","templates","home.html"), "r").read()
enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read()
contact_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()
payment_page_html = open(os.path.join("resources","templates","payment.html"), "r").read()
assignments_page_html = open(os.path.join("resources","templates","assignments.html"), "r").read()
assignment_submission_page_html = open(os.path.join("resources","templates","assignment_submission.html"), "r").read()
last_submission_results_page_html = open(os.path.join("resources","templates","last_submission_results.html"), "r").read()
last_submission_results_no_results_page_html = open(os.path.join("resources","templates","last_submission_results_no_results.html"), "r").read()
submitted_task_file_page_html = open(os.path.join("resources","templates","submitted_task_file.html"), "r").read()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_session(request: Request=None, hacker_id: str=None):
    if hacker_id:
        user=get_user(hacker_id) 
        if user["status"]=="OK":
            return user["user"]
        else:
            return False
    else:
        hacker_id=request.cookies.get('sessionKey')
        print(f"got following cookey value for sessionKey hacker_id:'{hacker_id}'")
        if hacker_id:
            user=get_user(hacker_id) 
            if user["status"]=="OK":
                return user["user"]
            else:
                return False
        else:
            return False

@app.get("/about")
def serve_about(request: Request, response: Response, hacker_id:str=None):
    about_page_html = open(os.path.join("resources","templates","about.html"), "r").read()
    user=validate_session(request=request, hacker_id=hacker_id)
    print(f"is_session_validated:'{user}'")
    if user:
        if user["paid_status"]:
            about_page_html=about_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>')\
                .replace("$${{ENLISTMENT_PROCESS_SECTION}}$$",'<li>You have successfully passed the challenge and enlisted into our ZeroDayBootcamp program</li><li>You may now engage in our next challenges in the <a href="/assignments" style="color:#778881;">Assignments Page</a></li>')
        else:
            about_page_html=about_page_html\
                .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>')\
                .replace("$${{ENLISTMENT_PROCESS_SECTION}}$$",'<li>You have successfully passed the initial screening <a href="/challenge" style="color:#778881;">zeroDayBootCamp</a> challenge</li><li>You can now finish our enlistment process in our <a href="/enlist" style="color:#778881;">Enlistment Page</a></li>')
        html_response=HTMLResponse(content=about_page_html, status_code=200)
        html_response.set_cookie(key="sessionKey", value=user["hacker_id"])
    else:
        about_page_html=about_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","")\
            .replace("$${{ENLISTMENT_PROCESS_SECTION}}$$",'<li>One can enlist only after passing the <a href="/challenge" style="color:#778881;">zeroDayBootCamp</a> challenge</li><li>Once passing the challenge, a dedicated link will be sent via mail enabling payment for registration</li>')
        html_response=HTMLResponse(content=about_page_html, status_code=200)
        html_response.set_cookie(key="sessionKey", value="", max_age=0)

    return html_response

@app.get("/challenge")
def serve_challange(advertise_code:str="unknown"):
    challenge_page_html=open(os.path.join("resources","templates","challenge.html"), "r").read().\
        replace("$${{DOMAIN_NAME}}$$",domain_name).\
        replace("$${{PROTOCOL}}$$",protocol).\
        replace("$${{IS_DEV_MODE}}$$",isDevMod).\
        replace("$${{ADVERTISE_CODE}}$$",advertise_code)
    return HTMLResponse(content=challenge_page_html, status_code=200)

@app.get("/")
def serve_home(request: Request):
    user=validate_session(request=request)
    print(user)
    home_page_html = open(os.path.join("resources","templates","home.html"), "r").read()
    if(user):
        is_paid=user["paid_status"]
        if(is_paid):
            home_page_html=home_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>').replace("$${{RECRUITE_NAME}}$$",user["name"]).replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">Congratulation for enlisting the ZeroDayBootcamp project!</p><p style="padding-bottom:50px">You may now enter the assignment page to start learning</p><a href="/assignments" class="cta-button" >Enter Assignment Page</a>')
        else:
            home_page_html=home_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","").replace("$${{RECRUITE_NAME}}$$",user["name"]).replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">Congratulation for completeing the ZeroDayBootCamp challenge successfully!</p><p style="padding-bottom:50px">You may now enlist to the continuation of your journy</p><a href="/enlist" class="cta-button" >Enlist</a>')
    else:
        home_page_html=home_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","").replace("$${{RECRUITE_NAME}}$$",'Dear Recruite').replace("$${{HOME_CONTENT}}$$",'<p style="padding-bottom:50px">After completing the challenge bellow you will be invited to join the ZeroDay BootCamp</p><a href="/challenge" class="cta-button" >Take the Challenge</a>')
    return HTMLResponse(content=home_page_html, status_code=200)

@app.get("/payment")
def serve_payment(request: Request):
    user=validate_session(request=request)
    payment_page_html = open(os.path.join("resources","templates","payment.html"), "r").read()
    if(user):
        payment_page_html = payment_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","").replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{HACKER_ID}}$$",user["hacker_id"])
    else:
        #if user has no valid session just redirect him to enlist page so he will see is harsh reality
        payment_page_html = f'<html><head><meta http-equiv="refresh" content="0; url={protocol}://{domain_name}/enlist"/></head><body></body></html>'
    return HTMLResponse(content=payment_page_html, status_code=200)

@app.get("/paymentRedirect")
def serve_payment_redirect(request: Request, hacker_id:str, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str):
    user=validate_session(request=request)
    if(user):
        payment_page_html =  f'<html><head><meta http-equiv="refresh" content="5; url={protocol}://{domain_name}/enlist"/></head><body><p>This Page Is Still Under Construction</p><p>User will be redirected back to enlistment page in 5 seconds</p></body></html>'
        initiate_user_payement_procedure(hacker_id, ClientName, ClientLName, UserId, email, phone)
    else:
        #if user has no valid session just redirect him to enlist page so he will see is harsh reality
        payment_page_html = redirect_to_enlistment_page
    return HTMLResponse(content=payment_page_html, status_code=200)

@app.get("/enlist")
def serve_enlist(request: Request):
    user=validate_session(request=request)
    enlist_page_html = open(os.path.join("resources","templates","enlist.html"), "r").read()
    if(user):
        if(user["paid_status"]):
            enlist_page_html=enlist_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>').replace("$${{ENLISTMENT_TITLE}}$$","Enlistment Completed").replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'href="/assignments"').replace("$${{BUTTON_CLASS}}$$","cta-button").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enter Assignment Page").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>User Already Enlisted</p><p>You can now enter assignment page</p><p style="margin:40px;"></p>')
        else:
            enlist_page_html=enlist_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","").replace("$${{ENLISTMENT_TITLE}}$$","Enlist to Bootcamp").replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'href="/payment"').replace("$${{BUTTON_CLASS}}$$","cta-button").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist Now").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>Challenge Passed Successfully</p><p>Enlistment is Now Opened</p><p class="price">50&#8362;</p>')      
    else:
        enlist_page_html=enlist_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$","").replace("$${{ENLISTMENT_TITLE}}$$","Enlist to Bootcamp").replace("$${{BUTTON_HREF_ATTRIBUTE}}$$",'role="link"').replace("$${{BUTTON_CLASS}}$$","cta-button-inactive").replace("$${{ENLISTMENT_BUTTON_TEXT}}$$","Enlist (deactivated)").replace("$${{ENLISTMENT_MESSAGE}}$$",'<p>locked until completing <a href="/challenge" style="color:#778881;"><h2>the challenge</h2><p style="padding-bottom:10px"></p></a></p>')
    return HTMLResponse(content=enlist_page_html, status_code=200)

@app.get("/contact")
def serve_contact(request: Request):
    user=validate_session(request=request)
    contact_page_html = open(os.path.join("resources","templates","contact.html"), "r").read()
    if user and user["paid_status"]:
        contact_page_html=contact_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>')
    else:
        contact_page_html=contact_page_html.replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'')
    return HTMLResponse(content=contact_page_html, status_code=200)

@app.get("/assignments")
def serve_assignments(request: Request):
    user=validate_session(request=request)
    assignments_page_html = open(os.path.join("resources","templates","assignments.html"), "r").read()
    if user and user["paid_status"]:
        next_assignment=next_assignment_submission(user["hacker_id"])
        print(f"next_assignment::{next_assignment}")
        current_assignment_id=next_assignment["assignment_id"]
        current_assignment_description=assignment_description(current_assignment_id)
        #print(current_assignment_description)
        if(current_assignment_description["status"] == "ERROR"):
            assignments_page_html=assignments_page_html\
            .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>')\
            .replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol)\
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
            .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>')\
            .replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol)\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_DESCRIPTION_CONTENT}}$$",current_assignment_description)\
            .replace("$${{TITLE}}$$",assignment_title)\
            .replace("$${{BREACH_MAX_ATTEMPT_MESSAGE}}$$",max_allowed_submissions_breach_message)\
            .replace("$${{SUBMIT_ASSIGNMENT_BUTTON_VISIBILITY}}$$",submit_assignment_button_visibility)
    else:
        assignments_page_html=redirect_to_enlistment_page
    return HTMLResponse(content=assignments_page_html, status_code=200)

@app.get("/assignment_submission")
def serve_assignment_submission(request: Request):
    user=validate_session(request=request) 
    assignment_submission_page_html = open(os.path.join("resources","templates","assignment_submission.html"), "r").read()
    if user and user["paid_status"]:
        next_assignment_id=next_assignment_submission(user["hacker_id"])["assignment_id"]
        if user_testing_in_progress(user["hacker_id"]):
            print(f'user {user["hacker_id"]} is locked for testing')
            assignment_submission_page_html=redirect_to_last_submission_result_page
        else:           
            print(f'user {user["hacker_id"]} is not locked for testing')
            task_count=assignment_task_count(next_assignment_id)["task_count"]
            print(task_count)
            task_submission_sections=[]
            for task_id in range(1,task_count+1):
                task_submission_sections.append(f'<p><h3>task_{task_id}</h3></p><label for="upload-photo"><input task_id={task_id} type="file" id="upload-photo" class="cta-button"></input></label>')
                print(task_submission_sections)
            task_submission_sections="\n".join(task_submission_sections)
            assignment_submission_page_html=assignment_submission_page_html\
            .replace("$${{ASSIGNMENT_PAGE_LINK}}$$",'<a href="/assignments">Assignments</a>')\
            .replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol)\
            .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
            .replace("$${{ASSIGNMENT_ID}}$$",str(next_assignment_id))\
            .replace("$${{TASK_SUBMITION_SECTIONS}}$$",task_submission_sections)\
            .replace("$${{MUMBER_OF_TASKS_IN_ASSIGNMENT}}$$",str(task_count))
    else:
        assignment_submission_page_html=redirect_to_enlistment_page
    return HTMLResponse(content=assignment_submission_page_html, status_code=200)

@app.get("/last_submission_result")
def serve_last_submission_result(request: Request):
    user=validate_session(request=request) 
    last_submission_results_page_html = open(os.path.join("resources","templates","last_submission_results.html"), "r").read()
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
                assignment_files=submission_result_for_view["assignment_files"]
                del submission_result_for_view["assignment_files"]
                del submission_result_for_view["assignment_file_names"]
                #submission_result_for_view["assignment_files"]=list(map(lambda x: base64.b64decode(x).decode('utf-8') ,submission_result_for_view["assignment_files"]))
                submission_result_for_view["result"]["collected_results"]=list(map(lambda task_result:{**task_result,"submitted_task_file":f"{protocol}://{domain_name}/submitted_task_file?assignment_id={assignment_id}&submission_id={submission_id}&task_id={task_result['task_idx']}"},submission_result_for_view["result"]["collected_results"]))
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
                last_submission_results_no_results_page_html = open(os.path.join("resources","templates","last_submission_results_no_results.html"), "r").read()
                last_submission_results_page_html=last_submission_results_no_results_page_html
                print(submission_result["ERROR_message"])
    else:
        last_submission_results_page_html=redirect_to_enlistment_page
    return HTMLResponse(content=last_submission_results_page_html, status_code=200)

@app.get("/submitted_task_file")
def serve_last_submission_result(request: Request,assignment_id:str, submission_id:str, task_id:str):
    user=validate_session(request=request) 
    submitted_task_file_page_html = open(os.path.join("resources","templates","submitted_task_file.html"), "r").read()
    if user and user["paid_status"]:
        file_content=get_submitted_file(user["hacker_id"], assignment_id, submission_id, task_id)
        submitted_task_file_page_html=submitted_task_file_page_html\
        .replace("$${{HACKER_ID}}$$",user["hacker_id"])\
        .replace("$${{ASSIGNMENT_ID}}$$",assignment_id)\
        .replace("$${{SUBMISSION_ID}}$$",submission_id)\
        .replace("$${{TASK_ID}}$$",task_id)\
        .replace("$${{FILE_CONTENT}}$$",file_content)
    else:
        last_submission_results_page_html=redirect_to_enlistment_page
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
    return submit_user(user) 

@app.get("/fetch_symmetric_key")
def fetch_symmetric_key_endpoint():
    return fetch_symmetric_key()

@app.get("/download/data.tar.gz")
def download_data_endpoint():
    return download_data()

def create_submit_assignment_background_task(assignment_submission):
    submit_assignment(assignment_submission)

@app.post("/submit_assignment")
def post_submit_assignment(assignment_submission: AssignmentSubmission, background_tasks: BackgroundTasks):
    print("entered submit assignment")
    background_tasks.add_task(create_submit_assignment_background_task, assignment_submission)
    print("assignment_submission added as background task")
    return {"status":"SUBMITTED"}
