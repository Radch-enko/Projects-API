from fastapi import APIRouter, Depends
from src.crud import *
from src.db.get_db import get_db
from typing import List, Optional
from src.models.schemas import CreateComment, CreateDiscussion, CreateDiscussionComment, DetailDiscussion, DiscussionTopic

router = APIRouter(
    prefix="/discussions",
    tags=["discussions"],
    responses={404: {"description": "Not found"}},
)

# Discussions

@router.get("", tags=["discussions"], response_model=List[Discussion])
async def get_all_discussions(cursor: int = 0, page_size: int = 10, searchQuery: Optional[str] = None, db: Session = Depends(get_db)): 
    return get_db_discussions(cursor, page_size, searchQuery, db)

@router.post("/create", tags=["discussions"], response_model=Discussion)
async def create_discussion(createDiscussion: CreateDiscussion, maker: User = Depends(get_current_user), db: Session = Depends(get_db)): 
    return create_db_discussion(createDiscussion, maker, db)

@router.get("/{discussion_id}", tags=["discussions"], response_model=DetailDiscussion)
async def get_discussion_by_id(discussion_id: str, user: User = Depends(get_current_user_nullable), db: Session = Depends(get_db)): 
    return get_db_discussion_by_id(discussion_id, user, db)

# Post comment
@router.post("/comment", tags=["discussions"], response_model=DetailDiscussion)
async def comment_for__a_post(createComment: CreateDiscussionComment, commenter: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await comment_for_discussion(db, createComment.discussion_id, createComment.text, commenter)
