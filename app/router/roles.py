from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.roles import RolesOut
from app.schemas.users import UserOut
from app.crud import roles as crud_roles
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 3
  
@router.get("/all/roles", response_model=List[RolesOut])
def get_all_roles(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        roles = crud_roles.get_all_rol(db)
        return roles
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    