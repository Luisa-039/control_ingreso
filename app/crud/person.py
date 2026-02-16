from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.person import PersonCreate, PersonUpdate

import logging

logger = logging.getLogger(__name__)

def create_person(db: Session, person: PersonCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO personas (
                tipo_persona, tipo_documento,
                documento, nombre_completo, codigo_barras, fecha_registro,
                estado
            ) VALUES (
                :tipo_persona, :tipo_documento,
                :documento, :nombre_completo, :codigo_barras, :fecha_registro,
                :estado
            )
        """)
        db.execute(query, person.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear la persona: {e}")
        raise Exception("Error de base de datos al crear la persona")
    
def get_person_by_document_number(db: Session, document: str):
    try:
        query = text("""SELECT personas.id_persona, personas.tipo_persona, personas.tipo_documento, 
                     personas.documento, personas.nombre_completo, personas.codigo_barras, 
                     personas.fecha_registro, personas.estado
                     FROM personas
                     WHERE personas.documento = :document
                """)
        
        result = db.execute(query, {"document": document}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por su documento: {e}")
        raise Exception("Error de base de datos al obtener el usuario")

def get_all_person(db: Session):
    try:
        query = text("""
            SELECT id_persona, tipo_persona, tipo_documento, documento,
            nombre_completo, codigo_barras, fecha_registro, estado
            FROM personas
        """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el listado de personas: {e}")
        raise Exception("Error de base de datos al obtener el listado de personas")
    
def update_person_by_document(db: Session, document: str, person: PersonUpdate) -> Optional[bool]:
    try:
        person_data = person.model_dump(exclude_unset=True)
        if not person_data:
            raise Exception("No se enviaron campos para actualizar")

        set_clauses = ", ".join([f"{key} = :{key}" for key in person_data.keys()])
        sentencia = text(f"""
            UPDATE personas 
            SET {set_clauses}
            WHERE documento = :documento
        """)

        person_data["documento"] = document

        result = db.execute(sentencia, person_data)
        db.commit()

        return result.rowcount > 0
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar persona {document}: {e}")
        raise Exception("Error de base de datos al actualizar persona")
    
def change_persona_status(db: Session, id_persona: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE personas
            SET estado = :estado
            WHERE id_persona = :id_persona
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_persona": id_persona})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado de la persona {id_persona}: {e}")
        raise Exception("Error de base de datos al cambiar el estado de la persona")