from fastapi.security import OAuth2PasswordBearer
# tokens will gut from this endpoint
auth2_scheme = OAuth2PasswordBearer(tokenUrl= "/api/v1/auth/login")