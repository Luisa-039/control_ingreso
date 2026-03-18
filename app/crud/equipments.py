from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.equipments import EquipoCreate, EquipoUpdate

logger = logging.getLogger(__name__)

def create_equipment(db: Session, 
                     user: EquipoCreate,
                     ) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO equipos_externos (
                serial,
                descripcion, categoria_id, foto_path, marca_modelo,
                fecha_registro, codigo_barras_inv, estado, persona_id
            ) VALUES (
                :serial, :descripcion, :categoria_id, :foto_path,
                :marca_modelo, :fecha_registro, :codigo_barras_inv, :estado, :persona_id
            )
        """)
        db.execute(query, user.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al registrar el equipo: {e}")
        raise Exception("Error de base de datos al registrar el equipo") 

def get_equipment_by_cod_barras(db: Session, codigo_barras: str):
    try:
        query = text("""SELECT eq.id_equipo, eq.serial, eq.codigo_barras_inv, eq.descripcion,
                        eq.categoria_id, eq.foto_path, eq.marca_modelo, eq.persona_id, eq.fecha_registro,
                        p.nombre_completo as nombre_completo, eq.estado, c.nombre_categoria
                        FROM equipos_externos as eq
                        INNER JOIN personas as p ON eq.persona_id = p.id_persona
                        INNER JOIN categorias as c ON eq.categoria_id = c.id_categoria
                        WHERE codigo_barras_inv = :codigo_barras
                    """)
        result = db.execute(query, {"codigo_barras": codigo_barras}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por código de barras: {e}")
        raise Exception("Error de base de datos al obtener el equipo por código de barras")

def get_equipment_by_serial(db: Session, serial_eq: str):
    try:
        query = text("""SELECT eq.id_equipo, eq.serial, eq.codigo_barras_inv, eq.descripcion,
                        eq.categoria_id, eq.foto_path, eq.marca_modelo, eq.persona_id, eq.fecha_registro,
                        p.nombre_completo as nombre_completo, eq.estado, c.nombre_categoria
                        FROM equipos_externos as eq
                        INNER JOIN personas as p ON eq.persona_id = p.id_persona
                        INNER JOIN categorias as c ON eq.categoria_id = c.id_categoria
                        WHERE serial = :equipo_serial
                    """)
        result = db.execute(query, {"equipo_serial": serial_eq}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por id: {e}")
        raise Exception("Error de base de datos al obtener el equipo por id")

def get_all_equipment(db: Session):
    try:
        query = text("""SELECT eq.id_equipo, eq.serial, eq.codigo_barras_inv, eq.descripcion,
                        eq.categoria_id, eq.foto_path, eq.marca_modelo, eq.persona_id, eq.fecha_registro,
                        p.nombre_completo as nombre_completo, eq.estado, c.nombre_categoria
                        FROM equipos_externos as eq
                        INNER JOIN personas as p ON eq.persona_id = p.id_persona
                        INNER JOIN categorias as c ON eq.categoria_id = c.id_categoria
                     """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los datos de los equipos: {e}")
        raise Exception("Error de base de datos al obtener los datos de los equipos")

def update_equip_by_cod_barras(db: Session, cod_barras: str, equipment: EquipoUpdate) -> Optional[bool]:
    try:
        equipment_data = equipment.model_dump(exclude_unset=True)
        if not equipment_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in equipment_data.keys()])
        sentencia = text(f"""
            UPDATE equipos_externos 
            SET {set_clauses}
            WHERE codigo_barras_inv = :codigo_barra
        """)

        equipment_data["codigo_barra"] = cod_barras

        result = db.execute(sentencia, equipment_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el equipo {cod_barras}: {e}")
        raise Exception("Error de base de datos al actualizar el equipo")
    
def update_estado_equip(db:Session, id_equip: str, estado_equipo: bool):
    try:
        sentencia = text("""
            UPDATE equipos_externos
            SET estado = :estado_eq
            WHERE id_equipo = :equipo_id
        """)
        result = db.execute(sentencia, {"estado_eq": estado_equipo, "equipo_id": id_equip})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del equipo {id_equip}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del equipo")
    
def update_equip_by_id(db: Session, equipo_id: int, equipment: EquipoUpdate) -> Optional[bool]:
    try:
        equipment_data = equipment.model_dump(exclude_unset=True)
        if not equipment_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in equipment_data.keys()])
        sentencia = text(f"""
            UPDATE equipos_externos 
            SET {set_clauses}
            WHERE id_equipo = :id_equip
        """)
        equipment_data["id_equip"] = equipo_id

        result = db.execute(sentencia, equipment_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el id del equipo {equipo_id}: {e}")
        raise Exception("Error de base de datos al actualizar el id del equipo")
     
def get_equipment_by_tipo(db: Session, tipo_equip: int):
    try:
        query = text("""SELECT eq.id_equipo, eq.serial, eq.codigo_barras_inv, eq.descripcion,
                        eq.categoria_id, eq.foto_path, eq.marca_modelo, eq.persona_id, eq.fecha_registro,
                        p.nombre_completo as nombre_completo, eq.estado, c.nombre_categoria
                        FROM equipos_externos as eq
                        INNER JOIN personas as p ON eq.persona_id = p.id_persona
                        INNER JOIN categorias as c ON eq.categoria_id = c.id_categoria 
                        WHERE categoria_id = :equipo_tipo
                    """)
        result = db.execute(query, {"equipo_tipo": tipo_equip}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por id: {e}")
        raise Exception("Error de base de datos al obtener el equipo por id")

def get_all_equipements_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los equipos con paginación.
    También realizar una segunda consulta para contar total de equipos.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_equipo) AS total 
                     FROM equipos_externos
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar equipos
        data_query = text("""SELECT eq.id_equipo, eq.serial, eq.codigo_barras_inv, eq.descripcion,
                            eq.categoria_id, eq.foto_path, eq.marca_modelo, eq.persona_id, eq.fecha_registro,
                            p.nombre_completo as nombre_completo, eq.estado, c.nombre_categoria
                            FROM equipos_externos as eq
                            INNER JOIN personas as p ON eq.persona_id = p.id_persona
                            INNER JOIN categorias as c ON eq.categoria_id = c.id_categoria
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
