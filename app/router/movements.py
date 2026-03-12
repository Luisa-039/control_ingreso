from typing import List
from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.movements import MovementCreate, MovementUpdate, MovementOut, TipoMovimiento, PaginatedMovements
from app.schemas.users import UserOut
from app.crud import movements as crud_movement
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 11

@router.post("/crear-movimiento", status_code=status.HTTP_201_CREATED)
def create_movement(  
    movement: MovementCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_movement.create_movement(db, movement)
        return {"message": "Movimiento creado correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-id", response_model=MovementOut)
def get_movement_by_id(
    id_movimiento: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="usuario no autorizado")

        movimiento = crud_movement.get_movement_by_id(db, id_movimiento)
        if not movimiento:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return movimiento
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/by-type", response_model=MovementOut)
def get_movement_type(
    tipo_movimiento: TipoMovimiento,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="usuario no autorizado")

        tipo_movimiento = crud_movement.get_movement_type(db, tipo_movimiento)
        if not tipo_movimiento:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return tipo_movimiento
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all-movements",  response_model=List[MovementOut])
def all_movements(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        movimiento = crud_movement.get_all_movements(db)
        if not movimiento:
            raise HTTPException(status_code=404, detail="Movimientos no encontrados")
        return movimiento
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/by-serial",  response_model=List[MovementOut])
def movement_serial(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        movimiento = crud_movement.get_movement_serial(db)
        if not movimiento:
            raise HTTPException(status_code=404, detail="Movimientos no encontrados")
        return movimiento
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/by-id/{movimiento_id}")
def update_movement_by_id(
    movimiento_id: int, 
    movement: MovementUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_movement.update_movement_by_id(db, movimiento_id, movement)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el movimiento")
        return {"message": "Movimiento actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/paginated", response_model=PaginatedMovements)
def get_movements_pag(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "seleccionar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    skip = (page - 1) * page_size

    data = crud_movement.get_all_movements_pag(db, skip=skip, limit=page_size)

    total = data["total"]
    movements = data["movements"]

    return PaginatedMovements(
        page=page,
        page_size=page_size,
        total_movements=total,
        total_pages=(total + page_size - 1) // page_size,
        movements=movements,
    )
