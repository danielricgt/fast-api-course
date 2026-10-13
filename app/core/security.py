from datetime import timedelta, timezone, datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from typing import Optional
from sqlalchemy.orm import Session
import jwt
import os

from app.core.db import get_db
from app.core.config import settings
from app.models.user import User

auth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

credencials_exception = HTTPException(
        status_code= 
        status.HTTP_401_UNAUTHORIZED,
        detail= "not authenticated",
        headers={"WWW-Authenticate" : "Bearer"}
    )

def token_expired():
    return  HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token expired",
            headers={"WWW-Autheticate" : "Beared"}
        )
    
def decore_token (token:str) -> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    return payload

def raise_forbidden():
    return  HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you have not needed permissions",
        )

# def create_access_token(data:dict, expires_delta : Optional[timedelta]=None):
#     to_encode = data.copy() 
#     expire = datetime.now(tz = timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(payload=to_encode, key=settings, algorithm=settings.ALGORITH)
#     return token

def create_access_token(sub: str, minutes: int | None = None) -> str :
    expire = datetime.now(timezone.utc) + timedelta(minutes= minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "expire": expire}, settings.JWT_SECRET,algorithm=settings.JWT_ALG)
    



def get_current_user(db: Session = Depends(get_db), token: str = Depends(auth2_scheme)) -> User:
    
    try:
        payload = decore_token(token)
        sub : Optional[str] = payload.get("sub")
        username: Optional[str] = payload.get("username")
        if not sub or not username :
            raise credencials_exception
    

        return {"email": sub, "username": username}
    except ExpiredSignatureError:
          raise token_expired( )
    except InvalidTokenError :
        raise credencials_exception