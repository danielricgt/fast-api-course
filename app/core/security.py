from datetime import timedelta, timezone, datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

import os

import jwt

# tokens will gut from this endpoint
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod") 
ALGORITH = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES  = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
auth2_scheme = OAuth2PasswordBearer(tokenUrl= "/api/v1/auth/login")

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
    
def raise_forbidden():
    return  HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you have not needed permissions",
        )

def create_access_token(data:dict, expires_delta : Optional[timedelta]=None):
    to_encode = data.copy() 
    expire = datetime.now(tz = timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITH)
    return token


def decore_token (token:str) -> dict:
    payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITH])
    return payload


def get_current_user(token: str = Depends(auth2_scheme)):

    
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