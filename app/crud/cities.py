from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.cities import CitiesCreate, CitiesUpdate

import logging

logger = logging.getLogger(__name__)

def create_city(db: Session, ciudad: CitiesCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO ciudades (
                departamento_id, nombre, codigo, estado
            ) VALUES (
                :departamento_id, :nombre, :codigo, true
            )
        """)
        db.execute(query, ciudad.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear la ciudad: {e}")
        raise Exception("Error de base de datos al crear la ciudad")

    
def get_cities_by_code(db: Session, codigo: str):
    try:
        query = text("""SELECT ciu.id_ciudad, ciu.departamento_id, ciu.nombre, ciu.codigo, ciu.estado,
                        dep.nombre AS nombre_departamento
                        FROM ciudades ciu
                        INNER JOIN departamentos dep on ciu.departamento_id = dep.id_departamento
                        WHERE ciu.codigo = :codigo
                    """)
        
        result = db.execute(query, {"codigo": codigo}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener ciudad por su código: {e}")
        raise Exception("Error de base de datos al obtener la ciudad")
    
def get_all_cities(db: Session):
    try:
        query = text("""
            SELECT ciu.id_ciudad, ciu.departamento_id, ciu.nombre, ciu.codigo, ciu.estado,
            dep.nombre AS nombre_departamento
            FROM ciudades ciu
            INNER JOIN departamentos dep on ciu.departamento_id = dep.id_departamento
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el listado de ciudades: {e}")
        raise Exception("Error de base de datos al obtener el listado de ciudades")
    
def update_city_by_id(db: Session, id_ciudad: int, ciudad: CitiesUpdate) -> Optional[bool]:
    try:
        city_data = ciudad.model_dump(exclude_unset=True)
        if not city_data:
            raise Exception("No se enviaron campos para actualizar")

        set_clauses = ", ".join([f"{key} = :{key}" for key in city_data.keys()])
        sentencia = text(f"""
            UPDATE ciudades
            SET {set_clauses}
            WHERE id_ciudad = :id_ciudad
        """)

        city_data["id_ciudad"] = id_ciudad

        result = db.execute(sentencia, city_data)
        db.commit()

        return result.rowcount > 0
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar la ciudad por id: {e}")
        raise Exception("Error de base de datos al actualizar la ciudad")
    
def change_city_status(db: Session, id_ciudad: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE ciudades
            SET estado = :estado
            WHERE id_ciudad = :id_ciudad
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_ciudad": id_ciudad})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado de la ciudad {id_ciudad}: {e}")
        raise Exception("Error de base de datos al cambiar el estado de la ciudad")

