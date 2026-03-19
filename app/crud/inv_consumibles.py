from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.inv_consumibles import Inv_consumibleCreate, Inv_consumibleUpdate, Inv_consumibleEstado

logger = logging.getLogger(__name__)

def create_inv_consumible(db: Session, 
                     inv_consumible: Inv_consumibleCreate,
                     ) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO inv_consumibles (
                sede_id, categoria_id, placa, ubicacion, cantidad, porcentaje_toner,
                marca, modelo,
                fecha_registro, estado
            ) VALUES (
                :sede_id, :categoria_id, :placa, :ubicacion, :cantidad, :porcentaje_toner,
                :marca, :modelo, :fecha_registro, true
            )
        """)
        db.execute(query, inv_consumible.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al registrar el equipo de la sede: {e}")
        raise Exception("Error de base de datos al registrar el equipo de la sede") 

def get_inv_consumible_by_id(db: Session, id_consumible: int):
    try:
        query = text("""SELECT ic.id_consumible, ic.ubicacion, ic.placa, ic.categoria_id, ic.marca, 
                        ic.modelo, ic.sede_id, ic.fecha_registro, ic.cantidad, ic.porcentaje_toner,
                        ic.estado, s.nombre as nombre_sede, c.nombre_categoria
                        FROM inv_consumibles as ic
                        INNER JOIN sedes as s ON ic.sede_id = s.id_sede
                        INNER JOIN categorias as c ON ic.categoria_id = c.id_categoria
                        WHERE ic.id_consumible = :id_consumible""")
        result = db.execute(query, {"id_consumible": id_consumible}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener consumible por ID: {e}")
        raise Exception("Error de base de datos al obtener el consumible por ID")

def get_all_inv_consumibles(db: Session):
    try:
        query = text("""SELECT ic.id_consumible, ic.ubicacion, ic.placa, ic.categoria_id, ic.marca, 
                        ic.modelo, ic.sede_id, ic.fecha_registro, ic.cantidad, ic.porcentaje_toner,
                        ic.estado, s.nombre as nombre_sede, c.nombre_categoria
                        FROM inv_consumibles as ic
                        INNER JOIN sedes as s ON ic.sede_id = s.id_sede
                        INNER JOIN categorias as c ON ic.categoria_id = c.id_categoria
                     """)
        result = db.execute(query).mappings().all()
        print([e.estado for e in result])
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los datos de los consumibles: {e}")
        raise Exception("Error de base de datos al obtener los datos de los consumibles")

def update_inv_consumible_by_id(db: Session, id_consumible: int, consumible: Inv_consumibleUpdate) -> Optional[bool]:
    try:
        consumible_data = consumible.model_dump(exclude_unset=True)
        if not consumible_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in consumible_data.keys()])
        sentencia = text(f"""
            UPDATE inv_consumibles 
            SET {set_clauses}
            WHERE id_consumible = :id_consumible
        """)

        consumible_data["id_consumible"] = id_consumible

        result = db.execute(sentencia, consumible_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el equipo {id_consumible}: {e}")
        raise Exception("Error de base de datos al actualizar el equipo")
    
def update_estado_consumible(db:Session, id_consumible: int, estado_consumible: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE inv_consumibles
            SET estado = :estado_consumible
            WHERE id_consumible = :id_consumible
        """)
        result = db.execute(sentencia, {"estado_consumible": estado_consumible, "id_consumible": id_consumible})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del consumible {id_consumible}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del consumible")
    
def get_all_consumible_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los consumibles con paginación.
    También realizar una segunda consulta para contar total de equipos.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_consumible) AS total 
                     FROM inv_consumibles
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar equipos
        data_query = text("""SELECT ic.id_consumible, ic.ubicacion, ic.placa, ic.categoria_id, ic.marca, 
                             ic.modelo, ic.sede_id, ic.fecha_registro, ic.cantidad, ic.porcentaje_toner,
                             ic.estado, s.nombre as nombre_sede, c.nombre_categoria
                             FROM inv_consumibles as ic
                             INNER JOIN sedes as s ON ic.sede_id = s.id_sede
                             INNER JOIN categorias as c ON ic.categoria_id = c.id_categoria
                             LIMIT :limit OFFSET :skip
                        """)
        equipos_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "consumibles": equipos_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los consumibles: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener los consumibles")

 
