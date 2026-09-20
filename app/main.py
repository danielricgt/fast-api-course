from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.db import Base, engine
from app.api.v1.post.router import router as post_router

# we need to upload the .env
load_dotenv()

# @app.get("/")
# def home():
#     return {'message': 'welcome to my bloc from daniel galvan '}


def create_app() -> FastAPI:
    app = FastAPI(title='mini Bloc')
    Base.metadata.create_all(bind=engine)  # dev
    # mount the router
    app.include_router(post_router)
    return app
app = create_app()