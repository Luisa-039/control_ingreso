from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.movements import MovementCreate, MovementUpdate, TipoMovimiento

import logging

logger = logging.getLogger(__name__)

def create_movement(db: Session, movement: MovementCreate) -> Optional[bool]:
    try:
        estado_query = text("""SELECT a.estado
                            FROM autorizacion_salida a
                            WHERE a.id_autorizacion = :id_autorizacion
                            """)
        result = db.execute(estado_query, {"id_autorizacion": movement.autorizacion_id}).fetchone()

        if not result:
            return False
        
        estado_autorizacion = result[0]
        
        if estado_autorizacion == True :
            insert_query = text("""
            INSERT INTO movimientos_equipos_sede (
                equipo_id, autorizacion_id,
                usuario_registra, tipo_movimiento, fecha_movimiento
            ) VALUES (
                :equipo_id, :autorizacion_id,
                :usuario_registra, :tipo_movimiento, :fecha_movimiento
            )
            """)
            db.execute(insert_query, movement.model_dump())
            db.commit()
            return True
        
        return False
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear el movimiento: {e}")
        raise Exception("Error de base de datos al crear el movimiento")
    
def update_movement_by_id(db: Session, id_movimiento: int, movement_update: TipoMovimiento) -> bool:
    try:
        query = text("""
            UPDATE movimientos_equipos_sede
            SET tipo_movimiento = :movimiento_eq
            WHERE id_movimiento_sede = :id_movimiento_sede
        """)
        result = db.execute(query, {"movimiento_eq": movement_update.value, "id_movimiento_sede": id_movimiento})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el movimiento del equipo {id_movimiento}: {e}")
        raise Exception("Error de base de datos al cambiar el movimiento del equipo")

    
def get_movement_type(db:Session, tipo_movimiento: List[TipoMovimiento]):
    try:
        query = text("""SELECT m.id_movimiento_sede, m.equipo_id, m.autorizacion_id,
                        m.usuario_registra, m.tipo_movimiento, m.fecha_movimiento, e.serial AS serial_equipo, e.categoria, u.nombre_usuario
                        FROM movimientos_equipos_sede m
                        INNER JOIN equipos_sede_inv e ON m.equipo_id = e.id_equipo_sede
                        INNER JOIN usuarios as u ON u.id_usuario = m.usuario_registra
                     WHERE tipo_movimiento = :tipo_movimiento
                     """)
        result = db.execute(query, {"tipo_movimiento": tipo_movimiento}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener movimiento por tipo: {e}")
        raise Exception("Error de base de datos al obtener movimiento")
    
def get_movement_serial(db:Session, serial: str):
    try:
        query = text("""SELECT m.id_movimiento_sede, m.equipo_id, m.autorizacion_id,
                        m.usuario_registra, m.tipo_movimiento, m.fecha_movimiento, e.serial AS serial_equipo, e.categoria, u.nombre_usuario
                        FROM movimientos_equipos_sede m
                        INNER JOIN equipos_sede_inv e ON m.equipo_id = e.id_equipo_sede
                        INNER JOIN usuarios as u ON u.id_usuario = m.usuario_registra
                        WHERE e.serial = :serial
                    """)
        result = db.execute(query, {"serial": serial}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener movimiento por serial")
        raise Exception("Error de base de datos al obtener movimiento")
    
def get_all_movements(db: Session):
    try:
        query = text("""SELECT m.id_movimiento_sede, m.equipo_id, m.autorizacion_id,
                        m.usuario_registra, m.tipo_movimiento, m.fecha_movimiento, e.serial AS serial_equipo, e.categoria, u.nombre_usuario
                        FROM movimientos_equipos_sede m
                        INNER JOIN equipos_sede_inv e ON m.equipo_id = e.id_equipo_sede
                        INNER JOIN usuarios as u ON u.id_usuario = m.usuario_registra
                    """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el listado de movimientos: {e}")
        raise Exception("Error de base de datos al obtener el listado de movimientos")
    
def update_movement_by_id(db: Session, movimiento_id: int, movement_update: MovementUpdate) -> bool:
    try:
        fields = movement_update.model_dump(exclude_unset=True)
        if not fields:
            return False
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        fields["movimiento_id"] = movimiento_id

        query = text(f"UPDATE movimientos_equipos_sede SET {set_clause} WHERE id_movimiento_sede = :movimiento_id")
        db.execute(query, fields)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar los movimientos: {e}")
        raise Exception("Error de base de datos al actualizar los movimientos")

def get_all_movements_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los usuarios con paginación.
    También realizar una segunda consulta para contar total de autorizaciones.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_movimiento_sede) AS total 
                     FROM movimientos_equipos_sede
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar movimientos
        data_query = text("""SELECT m.id_movimiento_sede, m.equipo_id, m.autorizacion_id,
                            m.usuario_registra, m.tipo_movimiento, m.fecha_movimiento, e.serial AS serial_equipo, e.categoria, u.nombre_usuario
                            FROM movimientos_equipos_sede m
                            INNER JOIN equipos_sede_inv e ON m.equipo_id = e.id_equipo_sede
                            INNER JOIN usuarios as u ON u.id_usuario = m.usuario_registra
                            LIMIT :limit OFFSET :skip
                        """)
        movements_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "movements": movements_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener las autorizaciones de salida: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener las autorizaciones de salida")
