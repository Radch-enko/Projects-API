from fastapi import APIRouter, Depends, HTTPException
from src.crud import *
from src.db.database import SessionLocal
from src.db.get_db import get_db
from typing import List, Optional
from src.models.schemas import UserCreate, UserSchema, Token, Login, User, UserUpdate
from src.core.security import create_access_token, verify_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}})

# Users
@router.get("/me", response_model=UserSchema)
async def read_user_me(user: User = Depends(get_current_user)):
    return user

@router.get("", response_model=List[UserSchema])
async def get_all_users(cursor: int = 0, page_size: int = 10, searchQuery: Optional[str] = None, db: Session = Depends(get_db)):
    return get_db_all_users(cursor, page_size, db, searchQuery)

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(user_id: Optional[int], db: Session = Depends(get_db)):
    return get_user_by_id(db, user_id)

@router.post("/create", response_model=UserSchema)
async def create_user(userCreate: UserCreate, db: Session = Depends(get_db)):
    return create_db_user(userCreate, db)

@router.post("/update", response_model=UserSchema)
async def update_user(userCreate: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_db_user(userCreate, user, db)

@router.post("/login", response_model=Token)
async def login(login: Login, db: SessionLocal = Depends(get_db)):
    user = get_user_by_username(login.username, db)
    if user is None or not verify_password(login.password, user.Hashed_password):
        raise HTTPException(status_code=401,
                            detail="Incorrect username or password")

    return Token(
        access_token=create_access_token({"sub": user.username}),
        token_type="Bearer"
    )