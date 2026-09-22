from pydantic import BaseModel, ConfigDict


# responde model and validation 
class Token (BaseModel):
    # class attributes
    access_token: str
    token_type: str = "Bearer"
    
class TokenData(BaseModel):
    sub: str
    username:str
    
class UserPublic(BaseModel):
    email: str
    username: str
    # to  be compatible with orm
    model_config = ConfigDict(from_attributes=True)