from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.access import AccessCreate, AccesUpdate, AccessOut
from app.schemas.users import UserOut
from app.crud import access as crud_access
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 5

@router.post("/crear-registro", status_code=status.HTTP_201_CREATED)
def create_center(  
    registro_acc: AccessCreate,
    cod_barras_p: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_access.registro_acceso(db=db,
                                    cod_barras=cod_barras_p,
                                    access=registro_acc,
                                    usuario_id = id_rol
                                    )
        return {"message": "registro creado correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/registrar_equipo", status_code=status.HTTP_201_CREATED)
def asoc_equip(cod_barras_eq: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_access.asociar_equipo(db=db, cod_barras = cod_barras_eq)
        return {"message": "equipo asociado al registro correctamente"}
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
      