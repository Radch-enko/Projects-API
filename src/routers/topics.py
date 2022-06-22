from fastapi import APIRouter, Depends
from src.models.schemas import *
from src.crud import *
from src.db.get_db import get_db
from typing import List

router = APIRouter(
    prefix="/topics",
    tags=["topics"],
    responses={404: {"description": "Not found"}},
)

# Get topics
@router.get("", tags=["topics"], response_model=List[Topic])
async def get_all_topics(db: Session = Depends(get_db)):
    return get_db_topics(db)