from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.center import CenterCreate, CenterUpdate

import logging

logger = logging.getLogger(__name__)

def create_center(db: Session, centro: CenterCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO centros (
                codigo_centro, nombre, 
                estado
            ) VALUES (
                :codigo_centro, :nombre,
                :estado
            )
        """)
        db.execute(query, centro.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear el centro: {e}")
        raise Exception("Error de base de datos al crear el centro")
    
def get_center_by_code(db: Session, codigo: str):
    try:
        query = text("""SELECT id_centro, codigo_centro, nombre,
                     estado
                     FROM centros
                     WHERE codigo_centro = :codigo
                """)
        
        result = db.execute(query, {"codigo": codigo}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener centro por su código: {e}")
        raise Exception("Error de base de datos al obtener el centro")
    
def get_all_center(db: Session):
    try:
        query = text("""
            SELECT id_centro, codigo_centro, nombre,
            estado
            FROM centros
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el listado de centros: {e}")
        raise Exception("Error de base de datos al obtener el listado de centros")
    
def update_center_by_code(db: Session, code: str, centro: CenterUpdate) -> Optional[bool]:
    try:
        center_data = centro.model_dump(exclude_unset=True)
        if not center_data:
            raise Exception("No se enviaron campos para actualizar")

        set_clauses = ", ".join([f"{key} = :{key}" for key in center_data.keys()])
        sentencia = text(f"""
            UPDATE centros
            SET {set_clauses}
            WHERE codigo_centro = :codigo_centro
        """)

        center_data["codigo_centro"] = code

        result = db.execute(sentencia, center_data)
        db.commit()

        return result.rowcount > 0
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el centro {code}: {e}")
        raise Exception("Error de base de datos al actualizar el centro")
    
def change_center_status(db: Session, id_centro: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE centros
            SET estado = :estado
            WHERE id_centro = :id_centro
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_centro": id_centro})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del centro {id_centro}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del centro")