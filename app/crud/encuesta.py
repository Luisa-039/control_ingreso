from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.encuestas import EncuestaCreate, EncuestaUpdate

import logging

logger = logging.getLogger(__name__)

def create_encuesta(db: Session, encuesta: EncuestaCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO encuestas (
                acceso_id, calificacion, observacion, estado_encuesta
            ) VALUES (
                :acceso_id, :calificacion, :observacion, false
            )
        """)
        db.execute(query, encuesta.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear la encuesta: {e}")
        raise Exception("Error de base de datos al crear la encuesta")

def get_all_encuestas(db: Session):
    try:
        query = text("""SELECT e.id_encuesta, e.acceso_id, e.calificacion, e.observacion, e.estado_encuesta,
                     p.nombre_completo, ar.nombre_area, se.nombre AS nombre_sede
                     FROM encuestas e
                     INNER JOIN registro_accesos ra ON e.acceso_id = ra.id_acceso
                     INNER JOIN personas p ON ra.persona_id = p.id_persona
                     LEFT JOIN areas ar ON ra.area_id = ar.id_area
                     LEFT JOIN sedes se ON ra.sede_id = se.id_sede""")
        
        result = db.execute(query).mappings().all()
        
        return result
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al registrar la encuesta: {e}")
        raise Exception("Error de base de datos al registrar la encuesta")

def get_encuesta_by_id(db: Session, id: int):
    try:
        query = text("""SELECT e.id_encuesta, e.acceso_id, e.calificacion, e.observacion, e.estado_encuesta,
                     p.nombre_completo, ar.nombre_area, se.nombre AS nombre_sede
                     FROM encuestas e
                     INNER JOIN registro_accesos ra ON e.acceso_id = ra.id_acceso
                     INNER JOIN personas p ON ra.persona_id = p.id_persona
                     LEFT JOIN areas ar ON ra.area_id = ar.id_area
                     LEFT JOIN sedes se ON ra.sede_id = se.id_sede
                     WHERE e.id_encuesta = :id
                """)
        
        result = db.execute(query, {"id": id}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener encuesta por su ID: {e}")
        raise Exception("Error de base de datos al obtener la encuesta")

def update_encuesta_by_id(db: Session, id: int, encuesta: EncuestaUpdate) -> Optional[bool]:
    try:
        encuesta_data = encuesta.model_dump(exclude_unset=True)
        if not encuesta_data:
            raise Exception("No se enviaron campos para actualizar")

        set_clauses = ", ".join([f"{key} = :{key}" for key in encuesta_data.keys()])
        sentencia = text(f"""
            UPDATE encuestas
            SET {set_clauses}
            WHERE id_encuesta = :id_encuesta
        """)

        encuesta_data["id_encuesta"] = id

        result = db.execute(sentencia, encuesta_data)
        db.commit()

        return result.rowcount > 0
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar la encuesta {id}: {e}")
        raise Exception("Error de base de datos al actualizar la encuesta")

def change_encuesta_status(db: Session, id_encuesta: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE encuestas
            SET estado_encuesta = :estado_encuesta
            WHERE id_encuesta = :id_encuesta
        """)
        result = db.execute(sentencia, {"estado_encuesta": nuevo_estado, "id_encuesta": id_encuesta})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado de la encuesta {id_encuesta}: {e}")
        raise Exception("Error de base de datos al cambiar el estado de la encuesta")

def get_all_encuestas_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene las encuestas con paginación.
    También realizar una segunda consulta para contar total de encuestas.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_encuesta) AS total 
                     FROM encuestas""")
        
        total_result = db.execute(count_query).scalar()

        #2 Consultar encuestas
        data_query = text("""SELECT e.id_encuesta, e.acceso_id, e.calificacion, e.observacion, e.estado_encuesta,
                            p.nombre_completo, ar.nombre_area, se.nombre AS nombre_sede
                            FROM encuestas e
                            INNER JOIN registro_accesos ra ON e.acceso_id = ra.id_acceso
                            INNER JOIN personas p ON ra.persona_id = p.id_persona
                            LEFT JOIN areas ar ON ra.area_id = ar.id_area
                            LEFT JOIN sedes se ON ra.sede_id = se.id_sede
                            LIMIT :limit OFFSET :skip
                        """)
        
        encuestas_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "encuestas": encuestas_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener las encuestas: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener las encuestas")
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener las encuestas: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener las encuestas")
