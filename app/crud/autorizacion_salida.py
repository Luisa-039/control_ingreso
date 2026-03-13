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


def get_all_autorizaciones(db: Session, skip: int = 0,   limit: int = 100
):
    """Obtener todas las autorizaciones de salida con paginación y filtro opcional"""
    try:
        query = text("""
                     SELECT a_s.id_autorizacion, a_s.equipo_id, a_s.usuario_id_autoriza, a_s.destino,
                     a_s.motivo, a_s.fecha_autorizacion, a_s.estado, u.nombre_usuario, e.serial, e.categoria
                     FROM autorizacion_salida as a_s
                     INNER JOIN usuarios as u ON u.id_usuario = a_s.usuario_id_autoriza
                     INNER JOIN equipos_sede_inv as e ON e.id_equipo_sede = a_s.equipo_id
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


def change_autorizacion_status(db: Session, id_autorizacion: int, estado: bool, fecha_movimiento):

    try:

        update_query = text("""
            UPDATE autorizacion_salida
            SET estado = :estado
            WHERE id_autorizacion = :id_autorizacion
        """)

        db.execute(update_query, {
            "estado": estado,
            "id_autorizacion": id_autorizacion
        })

        # SOLO si se autoriza se crea el movimiento
        if estado:

            insert_mov = text("""
                INSERT INTO movimientos_equipos_sede
                (equipo_id, autorizacion_id, tipo_movimiento, usuario_registra, fecha_movimiento)
                SELECT equipo_id, id_autorizacion, 'Salida', usuario_id_autoriza, :fecha_movimiento
                FROM autorizacion_salida
                WHERE id_autorizacion = :id_autorizacion
            """)

            db.execute(insert_mov, {
                "id_autorizacion": id_autorizacion,
                "fecha_movimiento": fecha_movimiento
            })

        db.commit()

        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar estado: {e}")
        return False

    
    
def get_all_auth_salida_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los usuarios con paginación.
    También realizar una segunda consulta para contar total de autorizaciones.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_autorizacion) AS total 
                     FROM autorizacion_salida
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar usuarios
        data_query = text("""SELECT a_s.id_autorizacion, a_s.equipo_id, a_s.usuario_id_autoriza, a_s.destino,
                          a_s.motivo, a_s.fecha_autorizacion, a_s.estado, u.nombre_usuario, e.serial, e.categoria
                          FROM autorizacion_salida as a_s
                          INNER JOIN usuarios as u ON u.id_usuario = a_s.usuario_id_autoriza
                          INNER JOIN equipos_sede_inv as e ON e.id_equipo_sede = a_s.equipo_id
                          LIMIT :limit OFFSET :skip
        """)
        auth_salida_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "auth_salida": auth_salida_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener las autorizaciones de salida: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener las autorizaciones de salida")


