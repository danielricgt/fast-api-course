
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
import os


# we create this callse to represent models un the database

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

print("conected to", DATABASE_URL)
# configure at leat a local database
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
# creating the conection
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)
# creating the session
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session)

# declarative base help us to define orm models as classes

class Base(DeclarativeBase):
    pass

#  a dependence its a functon that can be injectred automatically into the endpoint in fastapi
def get_db():
    db = SessionLocal()
    try:
        # generativde expression
        yield db
    finally:
        # always close database connection
        db.close()