from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.equipments import EquipoCreate, EquipoUpdate

logger = logging.getLogger(__name__)

def create_equipment(db: Session, 
                     user: EquipoCreate,
                     user_token: UserOut = Depends(get_current_user)) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO equipos_externos (
                serial,
                descripcion, tipo_equipo, foto_path, marca_modelo,
                fecha_registro, codigo_barras_inv, estado, persona_id
            ) VALUES (
                :serial, :descripcion, :tipo_equipo, :foto_path,
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
        query = text("""SELECT *
                     FROM equipos_externos 
                     WHERE codigo_barras_inv = :codigo_barras""")
        result = db.execute(query, {"codigo_barras": codigo_barras}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por código de barras: {e}")
        raise Exception("Error de base de datos al obtener el equipo por código de barras")

def get_equipment_by_serial(db: Session, serial_eq: str):
    try:
        query = text("""SELECT *
                     FROM equipos_externos 
                     WHERE serial = :equipo_serial""")
        result = db.execute(query, {"equipo_serial": serial_eq}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener equipo por id: {e}")
        raise Exception("Error de base de datos al obtener el equipo por id")

def get_all_equipment(db: Session):
    try:
        query = text("""SELECT *
                     FROM equipos_externos 
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
    
def update_estado_equip(db:Session, cod_barras_eq: str, estado_equipo: bool):
    try:
        sentencia = text("""
            UPDATE equipos_externos
            SET estado = :estado_eq
            WHERE codigo_barras_inv = :cod_barras
        """)
        result = db.execute(sentencia, {"estado_eq": estado_equipo, "cod_barras": cod_barras_eq})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del equipo {cod_barras_eq}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del equipo")
    
def update_equip_by_serial(db: Session, serial_equip: str, equipment: EquipoUpdate) -> Optional[bool]:
    try:
        equipment_data = equipment.model_dump(exclude_unset=True)
        if not equipment_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in equipment_data.keys()])
        sentencia = text(f"""
            UPDATE equipos 
            SET {set_clauses}
            WHERE serial = :serial_eq
        """)

        equipment_data["serial_eq"] = serial_equip

        result = db.execute(sentencia, equipment_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar el estado del equipo {serial_equip}: {e}")
        raise Exception("Error de base de datos al actualizar el estado del equipo")