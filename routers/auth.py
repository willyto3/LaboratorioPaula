from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status

from database.db import db_dependency
from models.user import User
from models.token import Token
from utils.hash import Hash


router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "Prueba"
ALGORITHM = "HS256"


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def authenticate_user(email: str, password: str, db):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False
    if not Hash.verify(password, user.hash_password):
        return False
    return user


def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": email, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso no Autorizado"
            )

        return {"email": email, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso no Autorizado"
        )


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso no Autorizado"
        )

    token = create_access_token(user.email, user.id, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}
