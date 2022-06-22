from fastapi import APIRouter, Depends
from src.crud import *
from src.db.get_db import get_db
from typing import List, Optional
from src.models.schemas import CreateComment, ProjectSchema, ProjectUpdate

router = APIRouter(
    prefix="/report",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

@router.get("", tags=["reports"])
async def report_comment(commentId: int, isDiscussionComment: Optional[bool] = False, user:User = Depends(get_current_user), db: Session = Depends(get_db)): 
    return report_db_comment(commentId, isDiscussionComment, user, db)
