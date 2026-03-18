from pydantic import BaseModel, Field
from typing import Optional, List

class DepartmentBase(BaseModel): 
    nombre: str = Field(min_length=3, max_length=50)   
    codigo: str = Field(min_length=1, max_length=7)

class DepartmentCreate(DepartmentBase):
    pass
    
class DepartmentOut(DepartmentBase):
    id_departamento: int

class PaginatedDeparment(BaseModel):
    page: int
    page_size: int
    total_departments: int
    total_pages: int
    departamentos: List[DepartmentOut]