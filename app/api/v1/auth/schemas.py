from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["user", "editor", "admin"]

# responde model and validation 
    
class Userbase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    # to  be compatible with orm
    model_config = ConfigDict(from_attributes=True)
class UserPublic(Userbase):
    id: int
    role: Role
    is_active: bool
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    full_name: str = "DefaultUser"
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class TokenResponse (BaseModel):
    # class attributes
    access_token: str
    token_type: str = "Bearer"
    user: UserPublic
    
class RoleUpdate(BaseModel):
    role: Role
    
class TokenData(BaseModel):
    sub: str 
    username:str
    