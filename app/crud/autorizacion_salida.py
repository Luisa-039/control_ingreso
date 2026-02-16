from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.autorizacion_salida import (
    AutorizacionSalidaCreate,
    AutorizacionSalidaUpdate
)

logger = logging.getLogger(__name__)


def create_autorizacion_salida(db: Session, autorizacion: AutorizacionSalidaCreate) -> Optional[bool]:
    """Crear una nueva autorización de salida"""
    try:
        query = text("""
            INSERT INTO autorizacion_salida (
                equipo_id, usuario_id_autoriza, fecha_autorizacion,
                destino, motivo, estado
            ) VALUES (
                :equipo_id, :usuario_id_autoriza, :fecha_autorizacion,
                :destino, :motivo, :estado
            )
        """)
        db.execute(query, autorizacion.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear autorización de salida: {e}")
        raise Exception("Error de base de datos al crear la autorización de salida")

def get_autorizacion_by_id(db: Session, id_autorizacion: int):
    """Obtener una autorización de salida por ID"""
    try:
        query = text("""
            SELECT * FROM autorizacion_salida
            WHERE id_autorizacion = :id_autorizacion
        """)
        result = db.execute(query, {"id_autorizacion": id_autorizacion}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener autorización por ID: {e}")
        raise Exception("Error de base de datos al obtener la autorización")


def get_all_autorizaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    """Obtener todas las autorizaciones de salida con paginación y filtro opcional"""
    try:
        query = text("""
            SELECT * FROM autorizacion_salida
            ORDER BY fecha_autorizacion DESC
            LIMIT :limit OFFSET :skip
            """)
        result = db.execute(query, {
            "limit": limit,
            "skip": skip
        }).mappings().all()
            
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener autorizaciones: {e}")
        raise Exception("Error de base de datos al obtener las autorizaciones")


def get_autorizaciones_by_equipo(db: Session, equipo_id: int):
    """Obtener todas las autorizaciones de un equipo específico"""
    try:
        query = text("""
            SELECT * FROM autorizacion_salida
            WHERE equipo_id = :equipo_id
            ORDER BY fecha_autorizacion DESC
        """)
        result = db.execute(query, {"equipo_id": equipo_id}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener autorizaciones por equipo: {e}")
        raise Exception("Error de base de datos al obtener las autorizaciones")


def get_autorizaciones_by_usuario(db: Session, usuario_id_autoriza: int):
    """Obtener todas las autorizaciones creadas por un usuario específico"""
    try:
        query = text("""
            SELECT * FROM autorizacion_salida
            WHERE usuario_id_autoriza = :usuario_id_autoriza
            ORDER BY fecha_autorizacion DESC
        """)
        result = db.execute(query, {"usuario_id_autoriza": usuario_id_autoriza}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener autorizaciones por usuario: {e}")
        raise Exception("Error de base de datos al obtener las autorizaciones")


def update_autorizacion_by_id(
    db: Session,
    id_autorizacion: int,
    autorizacion: AutorizacionSalidaUpdate
) -> Optional[bool]:
    """Actualizar una autorización de salida existente"""
    try:
        autorizacion_data = autorizacion.model_dump(exclude_unset=True)
        if not autorizacion_data:
            return False

        set_clauses = ", ".join([f"{key} = :{key}" for key in autorizacion_data.keys()])
        sentencia = text(f"""
            UPDATE autorizacion_salida
            SET {set_clauses}
            WHERE id_autorizacion = :id_autorizacion
        """)

        autorizacion_data["id_autorizacion"] = id_autorizacion

        result = db.execute(sentencia, autorizacion_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar autorización {id_autorizacion}: {e}")
        raise Exception("Error de base de datos al actualizar la autorización")


def change_autorizacion_status(db: Session, id_autorizacion: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE autorizacion_salida
            SET estado = :estado
            WHERE id_autorizacion = :id_autorizacion
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_autorizacion": id_autorizacion})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado de la persona {id_autorizacion}: {e}")
        raise Exception("Error de base de datos al cambiar el estado de la persona")