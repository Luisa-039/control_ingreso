from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging

from app.schemas.access import AccessCreate, AccesUpdate, AccessOut

logger = logging.getLogger(__name__)

#registrar usuario sin equipo por scan
def registro_acceso(db:Session, cod_barras:str, access: AccessCreate, usuario_id: int)->bool:
    
    try:
        persona_query = text("""
                                SELECT p.id_persona, p.documento 
                                FROM personas as p WHERE p.documento = :cod_barras
                                """)
        result_persona = db.execute(persona_query, {"cod_barras": cod_barras}).mappings().first()
        
        if not result_persona:
            logger.warning("Persona no encontrada en el sistema")
            return False

        sede_query = text("""
        SELECT sede_id
        FROM usuarios
        WHERE id_usuario = :id_user
        """)
        sede_result = db.execute(
            sede_query, {"id_user": usuario_id}
        ).mappings().first()
            
        access_query = text("""
                            INSERT INTO registro_accesos(
                                sede_id, persona_id, equipo_id,
                                usuario_registro_id, documento,
                                tipo_movimiento, fecha_entrada
                                ) 
                                VALUES(
                                :sede_id, :persona_id, :equipo_id,
                                :usuario_registro_id, :documento,
                                :tipo_movimiento, :fecha_entrada
                                )
                            """)
        params = {
            **access.model_dump(),
            "sede_id": sede_result["sede_id"],
            "persona_id": result_persona["id_persona"],
            "equipo_id": None,
            "documento": result_persona["documento"],
            "usuario_registro_id": usuario_id
        }

        db.execute(access_query, params)
        db.commit()
        
        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al realizar el registro de acceso: {e}")
        raise Exception("Error de base de datos al realizar el registro de acceso") 

#Asociar el equipo al usuario por scan
def asociar_equipo(db:Session, cod_barras:str):
    try: 
        datos_equip_query = text("""
                                 SELECT id_equipo, persona_id
                                 FROM equipos_externos
                                 WHERE codigo_barras_inv = :cod_barras
                                 """)

        equipo_result = db.execute(
            datos_equip_query, {"cod_barras": cod_barras}
        ).mappings().first()
        
        if not equipo_result:
            return {"Equipo no encontrado en el sistema"}
        
        registro_activo = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE persona_id = :persona_id
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1;
                               """)
        
        result_registro =db.execute(
            registro_activo, {"persona_id": equipo_result["persona_id"]}
        ).mappings().first()
        
        if not result_registro:
            return False        
        
        sentencia = text("""
            UPDATE registro_accesos
            SET equipo_id = :id_equipo
            WHERE id_acceso = :access_id
        """)
        result = db.execute(sentencia, {"id_equipo": equipo_result["id_equipo"], "access_id": result_registro["id_acceso"]})
        db.commit()

        return result.rowcount > 0
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al asociar el equipo: {e}")
        raise Exception("Error de base de datos al asociar el equipo")

#registrar persona por documento si la pistola falla
def registro_acceso_by_doc(db:Session, doc_persona:str, access: AccessCreate, usuario_id: int)->bool:
    
    try:
        persona_query = text("""
                                SELECT p.id_persona, p.documento 
                                FROM personas as p WHERE p.documento = :doc_person
                                """)
        result_persona = db.execute(persona_query, {"doc_person": doc_persona}).mappings().first()
        
        if not result_persona:
            logger.warning("Persona no encontrada en el sistema")
            return False

        sede_query = text("""
        SELECT sede_id
        FROM usuarios
        WHERE id_usuario = :id_user
        """)
        sede_result = db.execute(
            sede_query, {"id_user": usuario_id}
        ).mappings().first()
            
        access_query = text("""
                            INSERT INTO registro_accesos(
                                sede_id, persona_id, equipo_id,
                                usuario_registro_id, documento,
                                tipo_movimiento, fecha_entrada
                                ) 
                                VALUES(
                                :sede_id, :persona_id, :equipo_id,
                                :usuario_registro_id, :documento,
                                :tipo_movimiento, :fecha_entrada
                                )
                            """)
        params = {
            **access.model_dump(),
            "sede_id": sede_result["sede_id"],
            "persona_id": result_persona["id_persona"],
            "equipo_id": None,
            "documento": result_persona["documento"],
            "usuario_registro_id": usuario_id
        }

        db.execute(access_query, params)
        db.commit()
        
        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al realizar el registro de acceso: {e}")
        raise Exception("Error de base de datos al realizar el registro de acceso") 

#registrar por serial si la pistola falla
def asociar_equipo_by_serial(db:Session, serial_equip:str):
    try: 
        datos_equip_query = text("""
                                 SELECT id_equipo, persona_id
                                 FROM equipos_externos
                                 WHERE codigo_barras_inv = :serial_equip
                                 """)

        equipo_result = db.execute(
            datos_equip_query, {"serial_equip": serial_equip}
        ).mappings().first()
        
        if not equipo_result:
            return {"Equipo no encontrado en el sistema"}
        
        registro_activo = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE persona_id = :persona_id
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1;
                               """)
        
        result_registro =db.execute(
            registro_activo, {"persona_id": equipo_result["persona_id"]}
        ).mappings().first()
        
        if not result_registro:
            return False        
        
        sentencia = text("""
            UPDATE registro_accesos
            SET equipo_id = :id_equipo
            WHERE id_acceso = :access_id
        """)
        result = db.execute(sentencia, {"id_equipo": equipo_result["id_equipo"], "access_id": result_registro["id_acceso"]})
        db.commit()

        return result.rowcount > 0
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al asociar el equipo: {e}")
        raise Exception("Error de base de datos al asociar el equipo")

#registrar salida de la persona sin equipo por scan
def check_out_person(db:Session, cod_barras:str):
    try:
        registro_activo = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE documento = :cod_barras
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1;
                               """)
        
        result_registro =db.execute(
            registro_activo, {"cod_barras": cod_barras }
        ).mappings().first()
        
        if not result_registro:
            return False
        
        sentencia = text("""
            UPDATE registro_accesos
            SET fecha_salida = NOW()
            WHERE id_acceso = :access_id
        """)
        
        result = db.execute(sentencia, {"access_id": result_registro["id_acceso"]})
        db.commit()
        
        return result.rowcount > 0
    
    except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al realizar el registro de acceso: {e}")
            raise Exception("Error de base de datos al realizar el registro de acceso") 

#registrar salida de la persona por el código de barras del equipo 
def check_out_equip(db:Session, cod_barras_equip:str):
    try:
        datos_equip_query = text("""
                                 SELECT id_equipo, persona_id
                                 FROM equipos_externos
                                 WHERE codigo_barras_inv = :cod_barras_equip
                                 """)

        equipo_result = db.execute(
            datos_equip_query, {"cod_barras_equip": cod_barras_equip}
        ).mappings().first()
        
        if equipo_result is None:
            raise HTTPException(
                status_code=404,
                detail="El equipo no existe o no está asignado"
            )
            
        validar_eq_person = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE persona_id = :persona_id
                                AND equipo_id = :id_equip
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1
                                """)
        
        result_validacion =db.execute(
            validar_eq_person, {"persona_id": equipo_result["persona_id"], 
                                "id_equip": equipo_result["id_equipo"]}
        ).mappings().first()
        
        if not result_validacion:
            return {"El equipo no está asociado con esta persona"}
        
        
        sentencia = text("""
            UPDATE registro_accesos
            SET fecha_salida = NOW()
            WHERE id_acceso = :access_id
        """)
        
        result = db.execute(sentencia, {"access_id": result_validacion["id_acceso"]})
        db.commit()
        
        return result.rowcount > 0
    
    except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al realizar el registro de salida: {e}")
            raise Exception("Error de base de datos al realizar el registro de salida") 

#registrar salida por documento, si la pistola falla        
def check_out_doc_person(db:Session, documento_person:str):
    try:
        registro_activo = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE documento = :documento_person
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1;
                               """)
        
        result_registro =db.execute(
            registro_activo, {"documento_person": documento_person }
        ).mappings().first()
        
        if not result_registro:
            return False
        
        sentencia = text("""
            UPDATE registro_accesos
            SET fecha_salida = NOW()
            WHERE id_acceso = :access_id
        """)
        
        result = db.execute(sentencia, {"access_id": result_registro["id_acceso"]})
        db.commit()
        
        return result.rowcount > 0
    
    except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al realizar el registro de acceso: {e}")
            raise Exception("Error de base de datos al realizar el registro de acceso") 

#registrar salida por serial, si la pistola falla
def check_out_equip_serial(db:Session, serial_eq:str):
    try:
        datos_equip_query = text("""
                                 SELECT id_equipo, persona_id
                                 FROM equipos_externos
                                 WHERE codigo_barras_inv = :serial_eq
                                 """)

        equipo_result = db.execute(
            datos_equip_query, {"serial_eq": serial_eq}
        ).mappings().first()
        
        if equipo_result is None:
            raise HTTPException(
                status_code=404,
                detail="El equipo no existe o no está asignado"
            )
            
        validar_eq_person = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE persona_id = :persona_id
                                AND equipo_id = :id_equip
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1
                                """)
        
        result_validacion =db.execute(
            validar_eq_person, {"persona_id": equipo_result["persona_id"], 
                                "id_equip": equipo_result["id_equipo"]}
        ).mappings().first()
        
        if not result_validacion:
            return {"El equipo no está asociado con esta persona"}
        
        
        sentencia = text("""
            UPDATE registro_accesos
            SET fecha_salida = NOW()
            WHERE id_acceso = :access_id
        """)
        
        result = db.execute(sentencia, {"access_id": result_validacion["id_acceso"]})
        db.commit()
        
        return result.rowcount > 0
    
    except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al realizar el registro de salida: {e}")
            raise Exception("Error de base de datos al realizar el registro de salida") 
    
 #obtener datos de persona por scan documento
     

def get_access_by_id(db:Session, id_acceso_p:int):
    try:
        access_query = text("""
                            SELECT id_acceso, sede_id, persona_id, 
                            equipo_id, usuario_registro_id,
                            documento, tipo_movimiento,
                            fecha_entrada, fecha_salida
                            FROM registro_accesos
                            WHERE id_acceso = :id_ingreso  
                        """)
        result = db.execute(access_query, {"id_ingreso":id_acceso_p}).mappings().first()
        db.commit
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el registro de acceso por su id: {e}")
        raise Exception("Error de base de datos al obtener el registro de acceso por id")
    
def get_access_by_documento(db:Session, documento_p:str):
    try:
        access_query = text("""
                            SELECT id_acceso, sede_id, persona_id, 
                            equipo_id, usuario_registro_id,
                            documento, tipo_movimiento,
                            fecha_entrada, fecha_salida
                            FROM registro_accesos
                            WHERE documento = :doc_persona
                            ORDER BY fecha_entrada DESC 
                        """)
        result = db.execute(access_query, {"doc_persona":documento_p}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el registro de acceso por documento: {e}")
        raise Exception("Error de base de datos al obtener el registro de acceso por documento")
    
def get_access_by_id_equip(db:Session, id_equipo:int):
    try:
        access_query = text("""
                            SELECT id_acceso, sede_id, persona_id, 
                            equipo_id, usuario_registro_id,
                            documento, tipo_movimiento,
                            fecha_entrada, fecha_salida
                            FROM registro_accesos
                            WHERE equipo_id = :id_equip
                            ORDER BY fecha_entrada DESC 
                        """)
        result = db.execute(access_query, {"id_equip":id_equipo}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el registro de acceso por el id del equipo: {e}")
        raise Exception("Error de base de datos al obtener el registro de acceso por el id del equipo")
    
def get_all_access(db:Session):
    try:
        access_query = text(""" SELECT * FROM registro_accesos """)
        result = db.execute(access_query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener todos los registros: {e}")
        raise Exception("Error de base de datos al obtener todos los registros")
    
        
