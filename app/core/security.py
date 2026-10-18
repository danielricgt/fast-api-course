from datetime import timedelta, timezone, datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWKError
from pwdlib import PasswordHash
from typing import Literal, Optional
from sqlalchemy.orm import Session
import jwt
import os

from app.api.v1.auth.repository import UserRepository
from app.core.db import get_db
from app.core.config import settings
from app.models.user import User

auth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
password_hash = PasswordHash.recommended()

credencials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="not authenticated",
    headers={"WWW-Authenticate": "Bearer"}
)


def token_expired():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token expired",
        headers={"WWW-Autheticate": "Beared"}
    )


def decore_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET,
                         algorithms=[settings.JWT_ALG])
    return payload


def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="you have not needed permissions",
    )
    
def invalid_credentials():
    return HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED ,
        detail= "invalid credentials"
    )

# def create_access_token(data:dict, expires_delta : Optional[timedelta]=None):
#     to_encode = data.copy()
#     expire = datetime.now(tz = timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(payload=to_encode, key=settings, algorithm=settings.ALGORITH)
#     return token


def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(
        timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(auth2_scheme)) -> User:

    try:
        payload = decore_token(token)
        sub: Optional[str] = payload.get("sub")
        if not sub :
            raise credencials_exception
        user_id = int(sub)
        
    except ExpiredSignatureError:
        raise token_expired()
    except InvalidTokenError:
        raise credencials_exception
    except PyJWKError:
        raise invalid_credentials()
    
    user = db.get(User, user_id)
    if not user or not user.is_active:
        
        raise credencials_exception
        
    return user   

def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor" : 1, "admin" : 2}    
    
    def evaluation(user: User = Depends(get_current_user)) -> User: 
        if order[user.role] < order[min_role]:
            raise invalid_credentials()
        return user
    return evaluation

require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


async def   oauth2_ptoken(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(form.username) 
    if not user or not verify_password(form.password, user.hash_password):
        raise invalid_credentials()
    token  = create_access_token(sub = str(user.id ))
    return {"access_token": token,
            "token_type": "bearer  "}