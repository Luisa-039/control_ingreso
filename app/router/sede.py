from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.sede import SedeCreate, SedeUpdate, SedeOut, PaginatedSede
from app.schemas.users import UserOut
from app.crud import sede as crud_sede
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 10

@router.post("/crear-sede", status_code=status.HTTP_201_CREATED)
def create_sede(  
    sede: SedeCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_sede.create_sede(db, sede)
        return {"message": "Sede creada correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/sede-by-code", response_model=SedeOut)
def get_sede(
    codigo_sede: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        sede = crud_sede.get_sede_by_code(db, codigo_sede)
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")
        return sede
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all/sedes", response_model=List[SedeOut])
def get_all_sedes(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        sede = crud_sede.get_all_sedes(db)
        return sede
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/by-code/{code}")
def update_sede_by_code(
    code: str, 
    sede: SedeUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_sede.update_sede_by_code(db, code, sede)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la sede")
        return {"message": "Sede actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/cambiar-estado/{id_sede}", status_code=status.HTTP_200_OK)
def change_sede_status(
    id_sede: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_sede.change_sede_status(db, id_sede, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado de la sede actualizado a {nuevo_estado}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e)) 
    
    
@router.get("/all_sedes-pag", response_model=PaginatedSede)
def get_sedes_pag(
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
        data = crud_sede.get_all_sede_pag(db, skip=skip, limit=page_size)
        
        total = data["total"]  
        sedes = data["sedes"] 
        
        return PaginatedSede(
            page= page,
            page_size= page_size,
            total_sedes= total,
            total_pages= (total + page_size - 1) // page_size,
            sedes= sedes
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

