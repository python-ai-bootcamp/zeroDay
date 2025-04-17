from systemEntities import AnalyticsEventType, print
from assignmentOrchestrator import max_submission_for_assignment, next_assignment_submission
from fastapi import APIRouter, Request

router = APIRouter(prefix="/v2", tags=["v2"])

@router.get("/user")
def serve_get_user(request: Request):
    return request.state.authenticated_user

@router.get("/assignments/current_state")
def serve_assignements_current_state(request: Request):
    user=request.state.authenticated_user
    if(user):
        next_assignment_submission_status=next_assignment_submission(user["hacker_id"])
        next_assignment_submission_status["max_submission_id"]=max_submission_for_assignment(next_assignment_submission_status["assignment_id"])
        return next_assignment_submission_status
    else:
        return {"status":"ERROR", "ERROR_message":"user not found"}