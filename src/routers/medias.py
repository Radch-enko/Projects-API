from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from src.models.schemas import *
from src.crud import *
from src.db.get_db import get_db
from typing import List


router = APIRouter(
    prefix="/projects/medias",
    tags=["medias"],
    responses={404: {"description": "Not found"}},
)

# Get topics
@router.post("/", tags=["medias"], response_model = ProjectSchema)
async def add_medias(project_id: int, files: List[UploadFile], db: Session = Depends(get_db)):
    for file in files:
        addMedia(db, file)

    return get_db_project(db, project_id)
     