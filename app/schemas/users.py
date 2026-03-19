from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserBase(BaseModel):
    nombre_usuario: str = Field(min_length=3, max_length=50)
    rol_id: int
    email: EmailStr
    telefono: str = Field(min_length=7, max_length=15)
    documento: str = Field(min_length=8, max_length=20)
    sede_id: int
    estado: bool

class UserCreate(UserBase):
    pass_hash: str = Field(min_length=9, max_length=140)

class UserUpdate(BaseModel):
    nombre_usuario: Optional[str] = Field(default=None, min_length=3, max_length=80)
    documento: Optional[str] = Field(default=None, min_length=6, max_length=50)
    email: Optional[str] = Field(default=None, min_length=3, max_length=100)
    sede_id: Optional[int] = None
    telefono: Optional[str] = Field(default=None, min_length=7, max_length=15)

class UserEstado(BaseModel):
    estado: Optional[bool] = None

class UserOut(UserBase):
    id_usuario: int
    nombre: str
    nombre_rol: str

class PaginatedUsers(BaseModel):
    page: int
    page_size: int
    total_users: int
    total_pages: int
    users: List[UserOut]
