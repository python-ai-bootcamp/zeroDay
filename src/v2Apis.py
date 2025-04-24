from systemEntities import AnalyticsEventType, print
from configurationService import domain_name, protocol, isDevMod
from assignmentOrchestrator import AssignmentSubmission, assignment_description, submit_assignment, max_submission_for_assignment, next_assignment_submission, user_testing_in_progress, last_assignment_submission_result
from fastapi import APIRouter, Request, BackgroundTasks, File, Form, UploadFile

router = APIRouter(prefix="/v2", tags=["v2"])

@router.get("/user")
def serve_get_user(request: Request):
    return request.state.authenticated_user

@router.get("/assignments/current_state")
def serve_assignements_current_state(request: Request):
    user=request.state.authenticated_user
    if user:
        next_assignment_submission_status=next_assignment_submission(user["hacker_id"])
        next_assignment_submission_status["max_submission_id"]=max_submission_for_assignment(next_assignment_submission_status["assignment_id"])
        return next_assignment_submission_status
    else:
        return {"status":"ERROR", "ERROR_message":"user not found"}
    
@router.get("assignments/submission/test-status")
def serve_assignements_submissions_test_status(request: Request):
    user=request.state.authenticated_user
    if user_testing_in_progress(user["hacker_id"]):
        return {"status": "IN_PROGRESS"}
    else:
        return {"status": "DONE"}

def create_submit_assignment_background_task(zip_bytes: bytes, json_data: dict):
    submit_assignment(zip_bytes, json_data)

@router.post("/assignments/{assignment_id}/submission")
def post_assignments_submission(assignment_id: int, background_tasks: BackgroundTasks, request: Request, zip_file: UploadFile = File(...)):   
    print("entered v2 submit assignment")
    user=request.state.authenticated_user
    if user:
        hacker_id=user["hacker_id"]
        assignment_submission={"hacker_id":hacker_id, "assignment_id": assignment_id}
        zip_bytes = zip_file.file.read() 
        background_tasks.add_task(create_submit_assignment_background_task, zip_bytes, assignment_submission)
        print(f"assignment_submission ({assignment_submission}) added as background task")
        return {"status":"SUBMITTED"}
    else:
        return {"status":"ERROR", "ERROR_message":"user not found"}

@router.get("/assignments/submission/last_result")
def serve_assignments_submission_last_result(assignment_submission: AssignmentSubmission, background_tasks: BackgroundTasks, request: Request):
    user=request.state.authenticated_user
    submission_result=last_assignment_submission_result(user["hacker_id"])
    if submission_result["status"] == "OK":
        submission_result=submission_result["last_assignment_submission_result"]
        assignment_id=submission_result["assignment_id"]
        submission_id=submission_result["submission_id"]
        submission_result_for_view=submission_result
        del submission_result_for_view["assignment_files"]
        del submission_result_for_view["assignment_file_names"]
        submission_result_for_view["result"]["collected_results"]=list(map(lambda task_result:{**task_result,"submitted_task_file":f"{protocol}://{domain_name}/submitted_task_file?assignment_id={assignment_id}&submission_id={submission_id}&task_id={task_result['task_idx']}"},submission_result_for_view["result"]["collected_results"]))
        return submission_result_for_view
    else:
        return {"status":"ERROR", "ERROR_message":submission_result["ERROR_message"]}
    
@router.get("/assignments/description")
def serve_assignments_description(request: Request):
        user=request.state.authenticated_user
        next_assignment=next_assignment_submission(user["hacker_id"])
        current_assignment_id=next_assignment["assignment_id"]
        current_assignment_description=assignment_description(current_assignment_id)
        return current_assignment_description