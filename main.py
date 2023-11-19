from fastapi import Depends, FastAPI
from sqlmodel import SQLModel
import uvicorn


from models.user import User
from models.equipment import Equipment
from routers import auth
from database import db

app = FastAPI(title="Laboratorio Paula")
app.include_router(auth.router)
app.include_router(User.make_router(), dependencies=[Depends(auth.get_current_user)])
app.include_router(
    Equipment.make_router(), dependencies=[Depends(auth.get_current_user)]
)

SQLModel.metadata.create_all(db.engine)


@app.get("/")
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=7000)
