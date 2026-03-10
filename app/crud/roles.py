from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


import logging

logger = logging.getLogger(__name__)

def get_all_rol(db: Session):
    try:
        query = text("""SELECT
                     * FROM roles
                     """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los roles: {e}")
        raise Exception("Error de base de datos al obtener los roles")
