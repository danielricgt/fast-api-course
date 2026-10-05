import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.db import Base, engine
from app.api.v1.post.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.uploads.router import router as file_router  
from fastapi.staticfiles import StaticFiles

# we need to upload the .env
load_dotenv()

# @app.get("/")
# def home():
#     return {'message': 'welcome to my bloc from daniel galvan '}
MEDIA_DIR ="app/media"

def create_app() -> FastAPI:
    app = FastAPI(title='devatlles Bloc')
    Base.metadata.create_all(bind=engine)  # dev
    # mount the router
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(file_router)
    # this prevent error
    os.makedirs(MEDIA_DIR, exist_ok=True)
    # app images to disk using and endpointx
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name = "media")
    
    return app
app = create_app()