from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.areas import AreaCreate, AreaUpdate, AreaOut, PaginatedAreas
from app.schemas.users import UserOut
from app.crud import area as crud_area
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 17

@router.post("/crear-area", status_code=status.HTTP_201_CREATED)
def create_area(  
    area: AreaCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_area.create_area(db, area)
        return {"message": "Área creada correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-id",  response_model=AreaOut)
def get_area_by_id(id: int, 
              db: Session = Depends(get_db),
              user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        area = crud_area.get_area_by_id(db, id)
        if not area:
            raise HTTPException(status_code=404, detail="Área no encontrado")
        return area
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all/areas", response_model=List[AreaOut])
def get_all_areas(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        area = crud_area.get_all_areas(db)
        return area
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/by-id/{id_area}")
def update_area_by_id(
    id_area: int, 
    area: AreaUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_area.update_area_by_id(db, id_area, area)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el área")
        return {"message": "Área actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/cambiar-estado/{id_area}", status_code=status.HTTP_200_OK)
def change_center_status(
    id_area: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_area.change_area_status(db, id_area, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado del área actualizada a {nuevo_estado}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@router.get("/all_areas-pag", response_model=PaginatedAreas)
def get_areas_pag(
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
        data = crud_area.get_all_areas_pag(db, skip=skip, limit=page_size)

        total = data["total"]
        areas = data["areas"]

        return PaginatedAreas(
            page= page,
            page_size= page_size,
            total_areas= total,
            total_pages= (total + page_size - 1) // page_size,
            areas= areas
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))