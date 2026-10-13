# this class has all the configurations and bring all variables ad atributted to be user
import os

from fastapi.security import OAuth2PasswordBearer


class settings():

    # tokens will gut from this endpoint
    JWT_SECRET: str = os.getenv("SECRET_KEY", "change-me-in-prod")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

