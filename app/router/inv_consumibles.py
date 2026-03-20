from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.schemas.users import UserOut
from app.schemas.inv_consumibles import Inv_consumibleCreate, Inv_consumibleUpdate, Inv_consumibleEstado, Inv_consumibleOut, PaginatedInv_consumibles
from app.crud import inv_consumibles as crud_inv_consumibles
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 15

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_consumible(
    consumible: Inv_consumibleCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_inv_consumibles.create_inv_consumible(db, consumible)
        return {"message": "Consumible registrado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/by-id",  response_model=Inv_consumibleOut)
def scan_consumible(id_consumible: int, 
                   db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_inv_consumibles.get_inv_consumible_by_id(db, id_consumible)
        if not equipo:
            raise HTTPException(status_code=404, detail="Consumible no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-inv_consumible",  response_model=List[Inv_consumibleOut])
def scan_equipment(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_inv_consumibles.get_all_inv_consumibles(db)
        if not equipo:
            raise HTTPException(status_code=404, detail="Consumibles no encontrados")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/by_id/{id_consumible}")
def update_consumible_by_id(id_consumible: int, 
                 consumible: Inv_consumibleUpdate, 
                 db: Session = Depends(get_db),
                 user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_inv_consumibles.update_inv_consumible_by_id(db, id_consumible, consumible)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el consumible")
        return {"message": "Consumible actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/estado/{id_consumible}", status_code=status.HTTP_200_OK)
def estado_consumible(
    id_consumible: int,
    estado: Inv_consumibleEstado,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_inv_consumibles.update_estado_consumible(db, id_consumible, estado.estado)
        if not success:
            raise HTTPException(status_code=404, detail="Consumible no encontrado")

        return {"message": f"Estado del consumible actualizado a {estado.estado}"}
    except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/all_consumibles-pag", response_model=PaginatedInv_consumibles)
def get_consumibles_pag(
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
        data = crud_inv_consumibles.get_all_consumible_pag(db, skip=skip, limit=page_size)

        total = data["total"]  
        consumibles = data["consumibles"]

        return PaginatedInv_consumibles(
            page= page,
            page_size= page_size,
            total_consumibles= total,
            total_pages= (total + page_size - 1) // page_size,
            consumibles= consumibles
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


