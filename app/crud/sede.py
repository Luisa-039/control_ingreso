from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.sede import SedeCreate, SedeUpdate

import logging

logger = logging.getLogger(__name__)

def create_sede(db: Session, sede: SedeCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO sedes (
                nombre, direccion, codigo_sede, centro_id,
                estado
            ) VALUES (
                :nombre, :direccion, :codigo_sede, :centro_id,
                :estado
            )
        """)
        db.execute(query, sede.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear la sede: {e}")
        raise Exception("Error de base de datos al crear la sede")
    
def get_sede_by_code(db: Session, codigo: str):
    try:
        query = text("""SELECT s.id_sede, s.nombre, s.direccion, s.codigo_sede, s.centro_id, 
                     c.codigo_centro AS codigo_centro, c.nombre AS nombre_centro,
                     s.estado
                     FROM sedes s
                     INNER JOIN centros c ON s.centro_id = c.id_centro
                     WHERE s.codigo_sede = :codigo
                """)
        
        result = db.execute(query, {"codigo": codigo}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener sede por su código: {e}")
        raise Exception("Error de base de datos al obtener la sede")
    
def get_all_sedes(db: Session):
    try:
        query = text("""
            SELECT s.id_sede, s.nombre, s.direccion, s.codigo_sede, s.centro_id,
            c.codigo_centro AS codigo_centro, c.nombre AS nombre_centro, 
            s.estado
            FROM sedes s
            INNER JOIN centros c ON s.centro_id = c.id_centro
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el listado de sedes: {e}")
        raise Exception("Error de base de datos al obtener el listado de sedes")
    
def update_sede_by_code(db: Session, code: str, sede: SedeUpdate) -> Optional[bool]:
    try:
        sede_data = sede.model_dump(exclude_unset=True)
        if not sede_data:
            raise Exception("No se enviaron campos para actualizar")

        set_clauses = ", ".join([f"{key} = :{key}" for key in sede_data.keys()])
        sentencia = text(f"""
            UPDATE sedes
            SET {set_clauses}
            WHERE codigo_sede = :codigo_sede
        """)

        sede_data["codigo_sede"] = code

        result = db.execute(sentencia, sede_data)
        db.commit()

        return result.rowcount > 0
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar la sede {code}: {e}")
        raise Exception("Error de base de datos al actualizar la sede")
    
def change_sede_status(db: Session, id_sede: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE sedes
            SET estado = :estado
            WHERE id_sede = :id_sede
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_sede": id_sede})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado de la sede {id_sede}: {e}")
        raise Exception("Error de base de datos al cambiar el estado de la sede")