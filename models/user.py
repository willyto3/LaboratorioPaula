from typing import Optional
from sqlmodel import Field
from enum import Enum

from models.base import BaseDataModel


class Role(str, Enum):
    ADMIN = "ADMIN"
    CLIENT = "CLIENT"


class UserBase(BaseDataModel):
    first_name: str
    last_name: str
    email: str = Field(unique=True)
    role: Role
    document_id: str = Field(unique=True)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    hash_password: str


class UserCreate(UserBase):
    hash_password: str


class UserRead(UserBase):
    id: int
