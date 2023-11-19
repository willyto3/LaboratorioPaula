from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine


sqlite_file_name = "laboratorio.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
