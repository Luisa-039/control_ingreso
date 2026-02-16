from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.center import CenterCreate, CenterUpdate, CenterOut
from app.schemas.users import UserOut
from app.crud import center as crud_center
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 9

@router.post("/crear-centro", status_code=status.HTTP_201_CREATED)
def create_center(  
    centro: CenterCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_center.create_center(db, centro)
        return {"message": "Centro creado correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/centro-by-code", response_model=CenterOut)
def get_center(
    codigo: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        centro = crud_center.get_center_by_code(db, codigo)
        if not centro:
            raise HTTPException(status_code=404, detail="Centro no encontrado")
        return centro
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all/center", response_model=List[CenterOut])
def get_all_center(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        center = crud_center.get_all_center(db)
        return center
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/by-code/{code}")
def update_center_by_code(
    code: str, 
    center: CenterUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_center.update_center_by_code(db, code, center)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el centro")
        return {"message": "Centro actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/cambiar-estado/{id_center}", status_code=status.HTTP_200_OK)
def change_center_status(
    id_center: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_center.change_center_status(db, id_center, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado del centro actualizado a {nuevo_estado}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))