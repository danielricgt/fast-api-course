import bdb
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.auth import repository
from app.api.v1.auth.repository import UserRepository
from app.api.v1.auth.schemas import UserCreate, UserLogin, UserPublic, TokenResponse
from app.core.db import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import User

# FAKE_USERS = {
#     "ricardo@example.com": {"email": "ricardo@example.com", "username": "ricardo", "password": "secret123"},
#     "alumno@example.com":  {"email": "alumno@example.com",  "username": "alumno",  "password": "123456"},
# }

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends (get_db)):
    repository = UserRepository(   db)
    if repository.get_by_email(payload.email):
        raise HTTPException (status_code=400, detail="email already registered")
    user = repository.create(
        email=payload.email,
        hash_password=hash_password(payload.password),
        full_name=payload.full_name
    )
    # this user comes from orm object with model validate verify its what im 
    # waiting whith my pydantic validacion
    
    return  UserPublic.model_validate(user)
    



@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
     repository = UserRepository(db)
     user = repository.get_by_email(payload.email)
     if not user or not verify_password(payload.password, user.hash_password):
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
     token = create_access_token(sub=str(user.id))
     return TokenResponse(access_token=token, user = UserPublic.model_validate(user))    
     
     
@router.get('/read-me', response_model=UserPublic)
async def get_user(current : User = Depends(get_current_user)):
    return UserPublic.model_validate(current)