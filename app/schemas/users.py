from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=50)
    rol_id: int
    email: EmailStr
    telefono: str = Field(min_length=7, max_length=15)
    documento: str = Field(min_length=8, max_length=20)
    estado: bool

class UserCreate(UserBase):
    pass_hash: str = Field(min_length=9, max_length=140)

class UserUpdate(BaseModel):
    nombre_usuario: Optional[str] = Field(default=None, min_length=3, max_length=80)
    documento: Optional[str] = Field(default=None, min_length=6, max_length=50)
    email: Optional[str] = Field(default=None, min_length=3, max_length=100)
    telefono: Optional[str] = Field(default=None, min_length=7, max_length=15)

class UserEstado(BaseModel):
    estado: Optional[bool] = None

class UserOut(UserBase):
    id_usuario: int
