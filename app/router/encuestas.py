from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.encuestas import EncuestaCreate, EncuestaUpdate, EncuestaOut, PaginatedEncuesta
from app.schemas.users import UserOut
from app.crud import encuesta as crud_encuesta
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 18

@router.post("/crear-encuesta", status_code=status.HTTP_201_CREATED)
def create_encuesta(  
    encuesta: EncuestaCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_encuesta.create_encuesta(db, encuesta)
        return {"message": "Encuesta creada correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/encuesta-by-id", response_model=EncuestaOut)
def get_encuesta(
    id: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        encuesta = crud_encuesta.get_encuesta_by_id(db, id)
        if not encuesta:
            raise HTTPException(status_code=404, detail="Encuesta no encontrada")
        return encuesta
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/encuestas", response_model=List[EncuestaOut])
def get_all_encuestas(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        encuestas = crud_encuesta.get_all_encuestas(db)
        return encuestas
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/by-id/{id}")
def update_encuesta_by_id(
    id: int,
    encuesta: EncuestaUpdate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        # Verificar si la encuesta ya fue enviada
        encuesta_actual = crud_encuesta.get_encuesta_by_id(db, id)
        if not encuesta_actual:
            raise HTTPException(status_code=404, detail="Encuesta no encontrada")
        
        if encuesta_actual.estado_encuesta:
            raise HTTPException(status_code=403, detail="No se puede editar una encuesta que ya fue enviada")
        
        success = crud_encuesta.update_encuesta_by_id(db, id, encuesta)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la encuesta")
        return {"message": "Encuesta actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cambiar-estado/{id_encuesta}", status_code=status.HTTP_200_OK)
def change_encuesta_status(
    id_encuesta: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        # Verificar si la encuesta ya fue enviada
        encuesta_actual = crud_encuesta.get_encuesta_by_id(db, id_encuesta)
        if not encuesta_actual:
            raise HTTPException(status_code=404, detail="Encuesta no encontrada")
        
        # Si ya está enviada, no permitir ningún cambio de estado
        if encuesta_actual.estado_encuesta:
            raise HTTPException(status_code=403, detail="No se puede cambiar el estado de una encuesta que ya fue enviada")

        success = crud_encuesta.change_encuesta_status(db, id_encuesta, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Encuesta no encontrada")

        return {"message": f"Estado de la encuesta actualizado a {nuevo_estado}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e)) 
    
    
@router.get("/all_encuestas-pag", response_model=PaginatedEncuesta)
def get_encuestas_pag(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
): 
    try:        
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        skip = (page - 1) * page_size
        data = crud_encuesta.get_all_encuestas_pag(db, skip=skip, limit=page_size)
        
        total = data["total"]  
        encuestas = data["encuestas"] 
        
        return PaginatedEncuesta(
            page= page,
            page_size= page_size,
            total_encuesta= total,
            total_pages= (total + page_size - 1) // page_size,
            encuestas= encuestas
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

