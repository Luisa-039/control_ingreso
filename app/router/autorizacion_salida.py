from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.users import UserOut
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.autorizacion_salida import (
    AutorizacionSalidaCreate,
    AutorizacionSalidaUpdate,
    AutorizacionSalidaOut,
    AutorizacionEstado,
    PaginatedAuth_salida
)
from app.crud import autorizacion_salida as crud_autorizacion

router = APIRouter()
modulo = 12

# Crear autorización
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_autorizacion_salida(
    autorizacion: AutorizacionSalidaCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        crud_autorizacion.create_autorizacion_salida(db, autorizacion)
        return {"message": "Autorización de salida creada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Lista simple
@router.get("/", response_model=list[AutorizacionSalidaOut])
def get_all_autorizaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        return crud_autorizacion.get_all_autorizaciones(db, skip, limit)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Paginación
@router.get("/paginated", response_model=PaginatedAuth_salida)
def get_auth_salida_pag(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "seleccionar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    skip = (page - 1) * page_size

    data = crud_autorizacion.get_all_auth_salida_pag(
        db, skip=skip, limit=page_size
    )

    total = data["total"]
    auth_salida = data["auth_salida"]

    return PaginatedAuth_salida(
        page=page,
        page_size=page_size,
        total_auth_salida=total,
        total_pages=(total + page_size - 1) // page_size,
        auth_salida=auth_salida,
    )


# Autorizaciones por equipo
@router.get("/equipo/{equipo_id}")
def get_autorizaciones_by_equipo(
    equipo_id: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "seleccionar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    return crud_autorizacion.get_autorizaciones_by_equipo(db, equipo_id)


# Autorizaciones por usuario
@router.get("/usuario/{usuario_id}")
def get_autorizaciones_by_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "seleccionar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    return crud_autorizacion.get_autorizaciones_by_usuario(db, usuario_id)


# Obtener por ID
@router.get("/{id_salida}")
def get_autorizacion_by_id(
    id_salida: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "seleccionar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    autorizacion = crud_autorizacion.get_autorizacion_by_id(db, id_salida)

    if not autorizacion:
        raise HTTPException(status_code=404, detail="Autorización no encontrada")

    return autorizacion


# Actualizar autorización
@router.put("/{id_salida}")
def update_autorizacion(
    id_salida: int,
    autorizacion: AutorizacionSalidaUpdate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "actualizar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    success = crud_autorizacion.update_autorizacion_by_id(db, id_salida, autorizacion)

    if not success:
        raise HTTPException(status_code=400, detail="No se pudo actualizar")

    return {"message": "Autorización actualizada correctamente"}


# Cambiar estado
@router.put("/{id_salida}/estado")
def change_autorizacion_status(
    id_salida: int,
    data: AutorizacionEstado,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "actualizar"):
         raise HTTPException(status_code=401, detail="Usuario no autorizado")
    
    success = crud_autorizacion.change_autorizacion_status(db, id_salida, data.estado, data.fecha_movimiento )

    if not success:
        raise HTTPException(status_code=404, detail="Autorización no encontrada")

    return {"message": "Estado actualizado"}


    
