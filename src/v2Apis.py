from systemEntities import AnalyticsEventType, print
from userService import get_user
from fastapi import APIRouter, Request

router = APIRouter(prefix="/v2", tags=["v2"])

@router.get("/user")
def serve_get_user(request: Request):
    return request.state.authenticated_user
