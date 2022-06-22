from fastapi import APIRouter, Depends
from src.crud import *
from src.db.get_db import get_db
from typing import List, Optional
from src.models.schemas import CreateComment, ProjectSchema, ProjectUpdate
import datetime

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

# Projects

# Get actual projects list with paging
@router.get("", tags=["projects"], response_model=List[Project])
async def get_projects(cursor: int = 0, page_size: int = 10, day: Optional[datetime.date] = None, makerId: Optional[int] = None, voter:User = Depends(get_current_user_nullable), topicId: Optional[int] = None, searchQuery: Optional[str] = None, db: Session = Depends(get_db)): 
    return get_extra_projects(db, voter, cursor, page_size, day, makerId, topicId, searchQuery)

# Get detail info about project
@router.get("/{project_id}", tags=["projects"], response_model=ProjectSchema)
async def get_project(project_id: int, voter: User = Depends(get_current_user_nullable), db: Session = Depends(get_db)):
    return get_extra_project(db, project_id, voter)


# Create new project
@router.post("/create", tags=["projects"], response_model=ProjectSchema)
async def create_project(projectCreate: ProjectCreate, maker: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectSchema:
    project = create_db_project(db, projectCreate, maker)
    return project

@router.post("/{project_id}/update", tags=["projects"], response_model=ProjectSchema)
async def update_project(project_id: int, updateProject: ProjectUpdate, maker: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectSchema:
    return await update_db_project(db, project_id, updateProject, maker)

# Delete project
@router.post("/{project_id}/delete", tags=["projects"])
async def delete_project(project_id: int, deleter: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return delete_db_project(db, project_id, deleter)

# Vote for a post
@router.get("/{project_id}/vote", tags=["projects"])
async def vote_for_a_post(project_id: int, voter: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectSchema:
    return await vote_for_post(db, project_id, voter)

# Post comment
@router.post("/{project_id}/comment", tags=["projects"], response_model=ProjectSchema )
async def comment_for__a_post(createComment: CreateComment, commenter: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectSchema:
    return await comment_for_post(db, createComment.project_id, createComment.text, commenter)