from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
import re

from app.schemas.access import AccessCreate, PaginatedAccess

logger = logging.getLogger(__name__)


def _extract_document_number(scanned_value: str) -> str:
    """
    Normaliza la lectura del escáner y extrae el número de documento.
    Si llega un valor simple (solo dígitos), lo usa tal cual.
    Si llega una cadena larga con múltiples datos, intenta detectar el documento.
    """
    if not scanned_value:
        return ""

    clean_value = scanned_value.strip()
    if clean_value.isdigit():
        return clean_value

    # Prioriza números precedidos por etiquetas comunes de documento.
    label_pattern = re.compile(
        r"(?:CC|CEDULA|C[EÉ]DULA|DOCUMENTO|NUMERO|N[UÚ]MERO|NRO|NO)\D{0,12}(\d{5,12})",
        flags=re.IGNORECASE,
    )
    labeled_match = label_pattern.search(clean_value)
    if labeled_match:
        return labeled_match.group(1)

    # Fallback: tomar el bloque numérico más largo para evitar fechas/códigos cortos.
    candidates = re.findall(r"\d{5,12}", clean_value)
    if not candidates:
        return clean_value
    return max(candidates, key=len)

#registrar usuario sin equipo por scan
def registro_acceso(db:Session, cod_barras:str, area_id_s: int, access: AccessCreate, usuario_id: int)->str:
    
    try:
        numero_documento = _extract_document_number(cod_barras)

        if not area_id_s or area_id_s <= 0:
            logger.warning("Ingreso bloqueado. Debe especificar el area de visita")
            return "area_required"

        persona_query = text("""SELECT p.id_persona, p.documento 
                                FROM personas as p WHERE p.documento = :cod_barras
                                """)
        result_persona = db.execute(persona_query, {"cod_barras": numero_documento}).mappings().first()
        
        if not result_persona:
            logger.warning("Persona no encontrada en el sistema")
            return "person_not_found"

        validar_activo_query = text("""
                                SELECT id_acceso
                                FROM registro_accesos
                                WHERE persona_id = :persona_id
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1
                                """)
        
        acceso_activo = db.execute(
            validar_activo_query, {"persona_id": result_persona["id_persona"]}
        ).mappings().first()

        if acceso_activo:
            logger.warning(
                f"Ingreso bloqueado. Persona con documento {numero_documento} ya tiene acceso activo"
            )
            return "active_access_exists"

        area_query = text("""SELECT id_area FROM areas
                        WHERE id_area = :id_area_s
                        """)
        area_result = db.execute( area_query, {"id_area_s": area_id_s}
        ).mappings().first()

        if not area_result:
            logger.warning(f"Area de visita no encontrada: {area_id_s}")
            return "area_not_found"

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
                                usuario_registro_id, area_id,
                                tipo_movimiento, fecha_entrada
                                ) 
                                VALUES(
                                :sede_id, :persona_id, :equipo_id,
                                :usuario_registro_id, :area_id,
                                :tipo_movimiento, :fecha_entrada
                                )
                            """)
        params = {
             **access.model_dump(),
            "sede_id": sede_result["sede_id"],
            "persona_id": result_persona["id_persona"],
            "equipo_id": None,
            "usuario_registro_id": usuario_id,
            "area_id": area_result["id_area"],
            "tipo_movimiento": True,
        }
        
        db.execute(access_query, params)
        db.commit()
        
        return "ok"

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

#registrar por serial si la pistola falla
def asociar_equipo_by_serial(db:Session, serial_equip:str):
    try: 
        datos_equip_query = text("""
                                 SELECT id_equipo, persona_id
                                 FROM equipos_externos
                                 WHERE serial = :serial_equip
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
        numero_documento = _extract_document_number(cod_barras)

        registro_activo = text("""
                                SELECT r_a.id_acceso, p.documento 
                                FROM registro_accesos as r_a
                                INNER JOIN personas as p ON p.id_persona = r_a.persona_id
                                WHERE p.documento = :cod_barras
                                AND fecha_salida IS NULL
                                ORDER BY fecha_entrada DESC
                                LIMIT 1;
                               """)
        
        result_registro =db.execute(
            registro_activo, {"cod_barras": numero_documento }
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

#registrar salida por serial, si la pistola falla
def check_out_equip_serial(db:Session, serial_eq:str):
    try:
        datos_equip_query = text("""
                                 SELECT id_equipo, persona_id
                                 FROM equipos_externos
                                 WHERE serial = :serial_eq
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
                            SELECT ra.id_acceso, ra.sede_id, ra.persona_id, 
                            ra.equipo_id, ra.area_id, ra.usuario_registro_id,
                            ra.tipo_movimiento, ra.fecha_entrada, ra.fecha_salida, 
                            ar.nombre_area, s.nombre AS nombre_sede, p.nombre_completo,
                            e.marca_modelo, e.serial
                            FROM registro_accesos AS ra
                            INNER JOIN personas as p ON p.id_persona = ra.persona_id
                            INNER JOIN equipos_externos as e ON e.id_equipo = ra.equipo_id
                            LEFT JOIN areas as ar ON ar.id_area = ra.area_id
                            LEFT JOIN sedes as s ON s.id_sede = ra.sede_id
                            WHERE id_acceso = :id_ingreso  
                        """)
        result = db.execute(access_query, {"id_ingreso":id_acceso_p}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener el registro de acceso por su id: {e}")
        raise Exception("Error de base de datos al obtener el registro de acceso por id")
        
def get_all_access(db:Session):
    try:
        access_query = text("""SELECT ra.id_acceso, ra.sede_id, ra.persona_id, 
                                ra.equipo_id, ra.area_id, ra.usuario_registro_id,
                                ra.tipo_movimiento, ra.fecha_entrada, ra.fecha_salida, 
                                ar.nombre_area, s.nombre AS nombre_sede, p.nombre_completo,
                                e.marca_modelo, e.serial
                                FROM registro_accesos AS ra
                                INNER JOIN personas as p ON p.id_persona = ra.persona_id
                                INNER JOIN equipos_externos as e ON e.id_equipo = ra.equipo_id
                                LEFT JOIN areas as ar ON ar.id_area = ra.area_id
                                LEFT JOIN sedes as s ON s.id_sede = ra.sede_id
                                ORDER BY fecha_entrada DESC
                                """)
        result = db.execute(access_query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener todos los registros: {e}")
        raise Exception("Error de base de datos al obtener todos los registros")
 
def get_all_access_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los usuarios con paginación.
    También realizar una segunda consulta para contar total de autorizaciones.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_acceso) AS total 
                     FROM registro_accesos
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar usuarios
        data_query = text("""SELECT ra.id_acceso, ra.sede_id, ra.persona_id, 
                            ra.equipo_id, ra.area_id, ra.usuario_registro_id,
                            ra.tipo_movimiento, ra.fecha_entrada, ra.fecha_salida, 
                            ar.nombre_area, s.nombre AS nombre_sede, p.nombre_completo,
                            e.marca_modelo, e.serial
                            FROM registro_accesos AS ra
                            INNER JOIN personas as p ON p.id_persona = ra.persona_id
                            INNER JOIN equipos_externos as e ON e.id_equipo = ra.equipo_id
                            LEFT JOIN areas as ar ON ar.id_area = ra.area_id
                            LEFT JOIN sedes as s ON s.id_sede = ra.sede_id
                            LIMIT :limit OFFSET :skip
                        """)
        access_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "access": access_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener las autorizaciones de salida: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener las autorizaciones de salida")


