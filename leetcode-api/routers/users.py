from datetime import date

from fastapi import APIRouter
from models.submissions import (
    SubmissionResponse,
)
from services import user_service

router = APIRouter(prefix="/users")


@router.get("/{username}/submissions/{date}")
def submissions(username: str, date: date) -> list[SubmissionResponse]:
    return user_service.get_recent_submissions(username, date)
