from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.cities import CitiesCreate, CitiesUpdate, CitiesOut, PaginatedCities
from app.schemas.users import UserOut
from app.crud import cities as crud_cities
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 9

@router.post("/crear-ciudad", status_code=status.HTTP_201_CREATED)
def create_city(  
    ciudad: CitiesCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_cities.create_city(db, ciudad)
        return {"message": "Ciudad creada correctamente"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ciudad-by-code", response_model=CitiesOut)
def get_city(
    codigo: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        ciudad = crud_cities.get_cities_by_code(db, codigo)
        if not ciudad:
            raise HTTPException(status_code=404, detail="Ciudad no encontrada")
        return ciudad
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/cities", response_model=List[CitiesOut])
def get_all_cities(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        cities = crud_cities.get_all_cities(db)
        return cities
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/by-id/{id_ciudad}")
def update_city_by_id(
    id_ciudad: int, 
    ciudad: CitiesUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_cities.update_city_by_id(db, id_ciudad, ciudad)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la ciudad")
        return {"message": "Ciudad actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cambiar-estado/{id_ciudad}", status_code=status.HTTP_200_OK)
def change_city_status(
    id_ciudad: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_cities.change_city_status(db, id_ciudad, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Ciudad no encontrada")

        return {"message": f"Estado de la ciudad actualizado a {nuevo_estado}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get("/all_cities-pag", response_model=PaginatedCities)
def get_cities_pag(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
): 
    try:        
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        skip = (page - 1) * page_size
        data = crud_cities.get_all_cities_pag(db, skip=skip, limit=page_size)

        total = data["total"]  
        ciudades = data["ciudades"]

        return PaginatedCities(
            page= page,
            page_size= page_size,
            total_cities= total,
            total_pages= (total + page_size - 1) // page_size,
            ciudades= ciudades
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
