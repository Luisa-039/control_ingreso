from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import get_hashed_password
from app.schemas.users import UserCreate, UserUpdate

import logging

logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate) -> Optional[bool]:
    try:
        pass_encript = get_hashed_password(user.pass_hash)
        user.pass_hash = pass_encript
        query = text("""
            INSERT INTO usuarios (
                nombre_usuario, rol_id,
                email, documento, telefono, pass_hash,sede_id,
                estado
            ) VALUES (
                :nombre_usuario, :rol_id,
                :email, :documento, :telefono, :pass_hash, :sede_id,
                :estado
            )
        """)
        db.execute(query, user.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {e}")
        raise Exception("Error de base de datos al crear el usuario")
    
def get_user_by_email_for_login(db: Session, email: str):
    try:
        query = text("""SELECT id_usuario, nombre_usuario, documento, usuarios.rol_id, sede_id,
                email, telefono, estado, roles.nombre, pass_hash
                     FROM usuarios 
                     INNER JOIN roles ON usuarios.rol_id = roles.id_rol
                     WHERE email = :correo""")
        result = db.execute(query, {"correo": email}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")

def get_user_by_email(db: Session, email: str):
    try:
        query = text("""SELECT *
                     FROM usuarios 
                     WHERE email = :email""")
        result = db.execute(query, {"email": email}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")
    
def get_all_user_except_admins(db: Session):
    try:
        query = text("""SELECT u.id_usuario, u.nombre_usuario, u.documento, u.rol_id, 
                     u.email, u.telefono, u.sede_id, u.estado, u.pass_hash, r.nombre
                     FROM usuarios as u
                     INNER JOIN roles as r ON u.rol_id = r.id_rol
                     WHERE u.rol_id NOT IN (1)""")
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los usuarios: {e}")
        raise Exception("Error de base de datos al obtener los usuarios")

def update_user_by_id(db: Session, user_id: int, user: UserUpdate) -> Optional[bool]:
    try:
        user_data = user.model_dump(exclude_unset=True)
        if not user_data:
            return False 

        set_clauses = ", ".join([f"{key} = :{key}" for key in user_data.keys()])
        sentencia = text(f"""
            UPDATE usuarios 
            SET {set_clauses}
            WHERE id_usuario = :id_usuario
        """)

        user_data["id_usuario"] = user_id

        result = db.execute(sentencia, user_data)
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario {user_id}: {e}")
        raise Exception("Error de base de datos al actualizar el usuario")
    
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> bool:
    try:
        fields = user_update.model_dump(exclude_unset=True)
        if not fields:
            return False
        set_clause = ", ".join([f"{key} = :{key}" for key in fields])
        fields["user_id"] = user_id

        query = text(f"UPDATE usuarios SET {set_clause} WHERE id_usuario = :user_id")
        db.execute(query, fields)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario: {e}")
        raise Exception("Error de base de datos al actualizar usuario")
    
def get_user_by_id(db: Session, id: int):
    try:
        query = text("""SELECT id_usuario, nombre_usuario, documento, usuarios.rol_id, email, telefono, usuarios.estado
                     FROM usuarios
                     JOIN roles ON usuarios.rol_id = roles.id_rol
                     WHERE id_usuario = :id_user
                     """)
        result = db.execute(query, {"id_user": id}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por id: {e}")
        raise Exception("Error de base de datos al obtener el usuario")
    
def get_user_by_document_number(db: Session, document: str):
    try:
        query = text("""SELECT id_usuario, nombre_usuario, documento, usuarios.rol_id, email, telefono, usuarios.estado, roles.descripcion as descripcion_rol 
                     FROM usuarios INNER JOIN roles ON usuarios.rol_id = roles.id_rol
                     WHERE usuarios.documento = :document
                """)
        result = db.execute(query, {"document": document}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por su documento: {e}")
        raise Exception("Error de base de datos al obtener el usuario")
    
def get_user_by_rol(db: Session, rol: str):
    try:
        query = text("""SELECT id_usuario, nombre_usuario, documento, usuarios.rol_id, email, telefono, usuarios.estado, 
                     roles.nombre AS nombre_rol, roles.descripcion as descripcion_rol
                     FROM usuarios INNER JOIN roles ON usuarios.rol_id = roles.id_rol
                     WHERE LOWER(roles.nombre) = LOWER(:rol)
                """)
        result = db.execute(query, {"rol": rol}).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por rol: {e}")
        raise Exception("Error de base de datos al obtener los usuarios")
    
def change_user_status(db: Session, id_usuario: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE usuarios
            SET estado = :estado
            WHERE id_usuario = :id_usuario
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_usuario": id_usuario})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del usuario {id_usuario}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del usuario")
    
def get_all_users_pag(db: Session, skip:int = 0, limit = 10):
    """
    Obtiene los usuarios con paginación.
    También realizar una segunda consulta para contar total de usuarios.
    compatible con PostgreSQL, MySQL y SQLite 
    """
    try: 
        
        count_query = text("""SELECT COUNT(id_usuario) AS total 
                     FROM usuarios
                     """)
        total_result = db.execute(count_query).scalar()

        #2 Consultar usuarios
        data_query = text("""SELECT u.id_usuario, u.rol_id, u.nombre_usuario, u.documento, u.email, u.telefono, u.estado, u.sede_id, s.nombre
                    FROM usuarios as u
                    INNER JOIN sedes as s ON u.sede_id = s.id_sede
                    WHERE rol_id != 1
                     LIMIT :limit OFFSET :skip
        """)
        users_list = db.execute(data_query,{"skip": skip, "limit": limit}).mappings().all()
        
        return {
                "total": total_result or 0,
                "users": users_list
            }
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los usuarios: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener los usuarios")
