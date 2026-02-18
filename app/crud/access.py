from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.access import AccessCreate, AccesUpdate, AccessOut

logger = logging.getLogger(__name__)

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
        
        print(access_query)
        return True

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al realizar el registro de acceso: {e}")
        raise Exception("Error de base de datos al realizar el registro de acceso") 


def asociar_equipo(db:Session, cod_barras:str)->bool:
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
            return False
        
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
    