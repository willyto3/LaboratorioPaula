from typing import Optional
from sqlmodel import Field
from enum import Enum

from models.base import BaseDataModel


class Role(str, Enum):
    ADMIN = "ADMIN"
    CLIENT = "CLIENT"


class EquipmentBase(BaseDataModel):
    model: str
    is_active: bool = Field(default=True)
    serialNumber: str
    manufacturer: str
    role: Role
    document_id: str = Field(unique=True)

    user_id : Optional[int] = Field(default=None, foreign_key="user.id")


class Equipment(EquipmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)


class EquipmentCreate(EquipmentBase):
    pass


class UEquipmentRead(EquipmentBase):
    id: int
