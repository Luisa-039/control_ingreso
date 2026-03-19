from pydantic import BaseModel, Field
from typing import List, Optional
    
class AreaBase(BaseModel):
    nombre_area: str = Field(min_length=3, max_length=50)
    sede_id: int
    estado: bool

class AreaCreate(AreaBase):
    pass

class AreaUpdate(BaseModel):
    nombre_area: Optional[str] = Field(default=None,min_length=3, max_length=50)
    
class AreaEstado(BaseModel):
    estado: Optional[bool] = None

class AreaOut(AreaBase):
    id_area: int
    nombre_area: str
    sede_id: int

class PaginatedAreas(BaseModel):
    page: int
    page_size: int
    total_areas: int
    total_pages: int
    areas: List[AreaOut]
    