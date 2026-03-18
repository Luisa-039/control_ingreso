from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.schemas.users import UserOut
from app.schemas.types import TypeCreate, TypeOut
from app.crud import type as crud_type
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 19

#Endpoint de crear el tipo de movimiento
@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_type(
    Type: TypeCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        #Verficamos que tenga permisos
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_type.create_type(db, Type)
        return {"message": "Tipo de movimiento registrado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Endpoint para obtener tipo de movimiento por id
@router.get("/by-id",  response_model=TypeOut)
def get_type_by_id(id: int, 
              db: Session = Depends(get_db),
              user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        type = crud_type.get_types_by_id(db, id)
        if not type:
            raise HTTPException(status_code=404, detail="Tipo de movimiento no encontrado")
        return type
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Endpoint para obtener todos los tipos de movimientos
@router.get("/all-movements-types",  response_model=List[TypeOut])
def get_all_types(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        #Verificamos permisos
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        type = crud_type.get_all_types(db)
        if not type:
            raise HTTPException(status_code=404, detail="Tipo de movimientos no encontrados")
        return type
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))