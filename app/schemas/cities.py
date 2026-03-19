from pydantic import BaseModel, Field
from typing import List, Optional

class CitiesBase(BaseModel): 
    departamento_id: int = Field(gt=0)
    nombre: str = Field(min_length=3, max_length=50)
    codigo: str = Field(min_length=1, max_length=7)

    
class CitiesCreate(CitiesBase):
    pass

class CitiesUpdate(BaseModel):
    departamento_id: Optional[int] = None
    nombre: Optional[str] = Field(None, min_length=3, max_length=50)
    codigo: Optional[str] = Field(None, min_length=1, max_length=7)

class CitiesState(BaseModel):
    estado: bool

class CitiesOut(CitiesBase):
    id_ciudad: int
    estado: bool
    nombre_departamento: str

class PaginatedCities(BaseModel):
    page: int
    page_size: int
    total_cities: int
    total_pages: int
    ciudades: List[CitiesOut]