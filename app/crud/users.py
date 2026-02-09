from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

from app.schemas.users import UserCreate, UserUpdate

logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO usuarios (
                nombre_usuario, rol_id,
                email, documento, telefono, pass_hash,
                estado
            ) VALUES (
                :nombre_usuario, :rol_id,
                :email, :documento, :telefono, :pass_hash,
                :estado
            )
        """)
        db.execute(query, user.model_dump())
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {e}")
        raise Exception("Error de base de datos al crear el usuario")
        
    
def get_user_by_email_for_login(db: Session, email: str):
    try:
        query = text("""SELECT id_usuario, nombre_usuario, documento, usuarios.rol_id,
                email, telefono, estado, nombre_rol, pass_hash
                     FROM usuarios 
                     INNER JOIN roles ON usuarios.id_rol = roles.id_rol
                     WHERE email = :correo""")
        result = db.execute(query, {"correo": email}).mappings().first()
        return result
    except Exception as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")

def get_user_by_email(db: Session, email: str):
    try:
        query = text("""SELECT *
                     FROM usuarios 
                     WHERE email = :email""")
        result = db.execute(query, {"email": email}).mappings().first()
        return result
    except Exception as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")

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
    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario {user_id}: {e}")
        raise Exception("Error de base de datos al actualizar el usuario")