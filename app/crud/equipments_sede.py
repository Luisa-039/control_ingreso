from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.equipments_sede import Equipo_sedeCreate, Equipo_sedeUpdate, TipoEquipo_sede, Estado_equip_sede

logger = logging.getLogger(__name__)

#Función para crear los equipos de la sede
def create_equipment_sede(db: Session, 
                     equipo_sede: Equipo_sedeCreate,
                     ) -> Optional[bool]:
    try:
        #Realizamos la consulta en la base de datos
        query = text("""
            INSERT INTO equipos_sede_inv (
                sede_id, categoria, serial, codigo_barras_equipo,
                descripcion, marca, modelo,
                fecha_registro, estado
            ) VALUES (
                :sede_id, :categoria, :serial, :codigo_barras_equipo,
                :descripcion, :marca, :modelo, :fecha_registro, :estado
            )
        """)
        db.execute(query, equipo_sede.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al registrar el equipo de la sede: {e}")
        raise Exception("Error de base de datos al registrar el equipo de la sede") 

#Función para obtener los equipos por codigo de barras
def get_equipment_sede_by_cod_barras(db: Session, codigo_barras: str):
    try:
        query = text("""SELECT *
                     FROM equipos_sede_inv 
                     WHERE codigo_barras_equipo = :codigo_barras""")
        result = db.execute(query, {"codigo_barras": codigo_barras}).mappings().first()
        print([e.estado for e in result])
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por código de barras: {e}")
        raise Exception("Error de base de datos al obtener el equipo por código de barras")

#Función para obtener los equipos por serial
def get_equipment_sede_by_serial(db: Session, serial_eq: str):
    try:
        query = text("""SELECT *, s.nombre
                    FROM equipos_sede_inv as eq
                    INNER JOIN sedes as s ON eq.sede_id = s.id_sede
                     WHERE serial = :equipo_serial""")
        result = db.execute(query, {"equipo_serial": serial_eq}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por id: {e}")
        raise Exception("Error de base de datos al obtener el equipo por id")

#Función para obtener el listado de los los equipos
def get_all_equipments_sede(db: Session):
    try:
        query = text("""SELECT eq.*, s.nombre
                    FROM equipos_sede_inv as eq
                    INNER JOIN sedes as s ON eq.sede_id = s.id_sede 
                     """)
        result = db.execute(query).mappings().all()
        print([e.estado for e in result])
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los datos de los equipos: {e}")
        raise Exception("Error de base de datos al obtener los datos de los equipos")

#Función para actualizar los equipos por código de barras
def update_equip_sede_by_cod_barras(db: Session, cod_barras: str, equipment: Equipo_sedeUpdate) -> Optional[bool]:
    try:
        equipment_data = equipment.model_dump(exclude_unset=True)
        if not equipment_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in equipment_data.keys()])
        sentencia = text(f"""
            UPDATE equipos_sede_inv 
            SET {set_clauses}
            WHERE codigo_barras_equipo = :codigo_barra
        """)

        equipment_data["codigo_barra"] = cod_barras

        result = db.execute(sentencia, equipment_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el equipo {cod_barras}: {e}")
        raise Exception("Error de base de datos al actualizar el equipo")

#Función para cambiar el estado del equipo
def update_estado_equip_sede(db:Session, id_equip: int, estado_equipo: Estado_equip_sede):
    try:
        sentencia = text("""
            UPDATE equipos_sede_inv
            SET estado = :estado_eq
            WHERE id_equipo_sede = :equipo_id
        """)
        result = db.execute(sentencia, {"estado_eq": estado_equipo.value, "equipo_id": id_equip})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del equipo {id_equip}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del equipo")

#Función para actualizar el equipo por ID
def update_equip_sede_by_id(db: Session, equipo_id: int, equipment: Equipo_sedeUpdate) -> Optional[bool]:
    try:
        equipment_data = equipment.model_dump(exclude_unset=True)
        if not equipment_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in equipment_data.keys()])
        sentencia = text(f"""
            UPDATE equipos_sede_inv 
            SET {set_clauses}
            WHERE id_equipo_sede = :id_equip
        """)
        equipment_data["id_equip"] = equipo_id

        result = db.execute(sentencia, equipment_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el id del equipo {equipo_id}: {e}")
        raise Exception("Error de base de datos al actualizar el id del equipo")

#Función para obtener equipos dependiendo del tipo de equipo     
def get_equipment_sede_by_tipo(db: Session, tipo_equip: TipoEquipo_sede):
    try:
        query = text("""SELECT *s.nombre
                     FROM equipos_sede_inv as eq 
                     INNER JOIN sedes as s ON eq.sede_id = s.id_sede
                     WHERE categoria = :equipo_tipo""")
        result = db.execute(query, {"equipo_tipo": tipo_equip}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por id: {e}")
        raise Exception("Error de base de datos al obtener el equipo por id")

#Función para obtener todos los equipos haciendo uso de la paginación
def get_all_equipements_sede_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los equipos con paginación.
    También realizar una segunda consulta para contar total de equipos.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_equipo_sede) AS total 
                     FROM equipos_sede_inv
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar equipos
        data_query = text("""SELECT eq.id_equipo_sede, eq.serial, eq.codigo_barras_equipo, eq.descripcion,
                          eq.categoria, eq.marca, eq.modelo, eq.sede_id, eq.fecha_registro,
                          eq.estado, s.nombre
                          FROM equipos_sede_inv as eq
                          INNER JOIN sedes as s ON eq.sede_id = s.id_sede
                          LIMIT :limit OFFSET :skip
                        """)
        equipos_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "equipos": equipos_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los equipos: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener los equipos")
