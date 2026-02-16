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
    AutorizacionSalidaOut
)
from app.crud import autorizacion_salida as crud_autorizacion

router = APIRouter()
modulo = 12


@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_autorizacion_salida(
    autorizacion: AutorizacionSalidaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva autorización de salida de equipo.
    """
    try:
        crud_autorizacion.create_autorizacion_salida(db, autorizacion)
        return {"message": "Autorización de salida creada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[AutorizacionSalidaOut])
def get_all_autorizaciones(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las autorizaciones de salida con paginación opcional.
    """
    try:
        autorizaciones = crud_autorizacion.get_all_autorizaciones(
            db, skip=skip, limit=limit
        )
        return autorizaciones
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_salida}")
def get_autorizacion_by_id(
    id_salida: int,
    db: Session = Depends(get_db)
):
    """
    Obtener una autorización de salida específica por ID.
    """
    try:
        autorizacion = crud_autorizacion.get_autorizacion_by_id(db, id_salida)
        if not autorizacion:
            raise HTTPException(status_code=404, detail="Autorización no encontrada")
        return autorizacion
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipo/{equipo_id}")
def get_autorizaciones_by_equipo(
    equipo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las autorizaciones de salida de un equipo específico.
    """
    try:
        autorizaciones = crud_autorizacion.get_autorizaciones_by_equipo(db, equipo_id)
        return autorizaciones
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usuario/{usuario_id_autoriza}")
def get_autorizaciones_by_usuario(
    usuario_id_autoriza: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las autorizaciones creadas por un usuario específico.
    """
    try:
        autorizaciones = crud_autorizacion.get_autorizaciones_by_usuario(db, usuario_id_autoriza)
        return autorizaciones
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_salida}")
def update_autorizacion(
    id_salida: int,
    autorizacion: AutorizacionSalidaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una autorización de salida existente.
    """
    try:
        success = crud_autorizacion.update_autorizacion_by_id(db, id_salida, autorizacion)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="No se pudo actualizar la autorización"
            )
        return {"message": "Autorización actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cambiar-estado/{id_autorizacion}", status_code=status.HTTP_200_OK)
def change_person_status(
    id_autorizacion: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_autorizacion.change_autorizacion_status(db, id_autorizacion, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Autorización no encontrado")

        return {"message": f"Estado de la persona actualizado a {nuevo_estado}"}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=str(e)) 