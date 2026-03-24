from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.types import TypeCreate, TypeUpdate

import logging

logger = logging.getLogger(__name__)

#Función para crear tipos de movimientos
def create_type(db: Session, type: TypeCreate) -> Optional[bool]:
    try:
        #Se realiza la consulta
        query = text("""
            INSERT INTO tipo_movimientos (
                nombre_tipo, descripcion
            ) VALUES (
                :nombre_tipo, :descripcion
            )
        """)
        db.execute(query, type.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear el tipo de movimiento: {e}")
        raise Exception("Error de base de datos al crear el tipo de movimiento")

#Función para obtener tipo de movimientos por id  
def get_types_by_id(db: Session, id: int):
    try:
        query = text("""SELECT id_tipo, nombre_tipo, descripcion
                     FROM tipo_movimientos
                     WHERE id_tipo = :id
                """)
        
        result = db.execute(query, {"id": id}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener tipo de movimientos por id: {e}")
        raise Exception("Error de base de datos al obtener el tipo de movimientos")

def update_type_by_id(db: Session, id: int, type: TypeUpdate) -> Optional[bool]:
    try:
        type_data = type.model_dump(exclude_unset=True)
        if not type_data:
            raise Exception("No se enviaron campos para actualizar")

        set_clauses = ", ".join([f"{key} = :{key}" for key in type_data.keys()])
        sentencia = text(f"""
            UPDATE tipo_movimientos
            SET {set_clauses}
            WHERE id_tipo = :id_tipo
        """)

        type_data["id_tipo"] = id

        result = db.execute(sentencia, type_data)
        db.commit()

        return result.rowcount > 0
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el tipo de movimiento: {e}")
        raise Exception("Error de base de datos al actualizar el tipo de movimiento")


#idn para obtener el listado con todos los tipos de movimientos existentes
def get_all_types(db: Session):
    try:
        query = text("""
            SELECT id_tipo, nombre_tipo, descripcion
            FROM tipo_movimientos
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el listado de los tipos de movimientos: {e}")
        raise Exception("Error de base de datos al obtener el listado de los tipos de movimientos")
