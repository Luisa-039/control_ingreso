from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.schemas.users import UserOut
from app.schemas.equipments import EquipoCreate, EquipoUpdate, EquipoOut, TipoEquipo
from app.crud import equipments as crud_equipments
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 7

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_equipo(
    Equipo: EquipoCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_equipments.create_equipment(db, Equipo)
        return {"message": "Equipo registrado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/by-cod_barras",  response_model=EquipoOut)
def scan_equipment(cod_barras: str, 
                   db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments.get_equipment_by_cod_barras(db, cod_barras)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-serial_eq",  response_model=EquipoOut)
def get_by_serial_equip(serial: str, 
                        db: Session = Depends(get_db),
                        user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments.get_equipment_by_serial(db, serial)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-tipo_equip",  response_model=EquipoOut)
def get_by_tipo_equip(tipo_equip: TipoEquipo, 
                        db: Session = Depends(get_db),
                        user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments.get_equipment_by_tipo(db, tipo_equip)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-equips",  response_model=List[EquipoOut])
def scan_equipment(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments.get_all_equipment(db)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipos no encontrados")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/by_id/{id_equip}")
def update_equip_by_id(id_equip: int, 
                 equip: EquipoUpdate, 
                 db: Session = Depends(get_db),
                 user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments.update_equip_by_id(db, id_equip, equip)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el equipo")
        return {"message": "Equipo actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/estado/{id_equip}", status_code=status.HTTP_200_OK)
def estado_equip(
    id_eq: str,
    estado_equip: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments.update_estado_equip(db, id_eq, estado_equip)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado del equipo actualizado a {estado_equip}"}
    except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.put("/by-cod_barras/{codigo_barras_equip}")
def update_equip(codigo_barras_equip: str, 
                 equip: EquipoUpdate, 
                 db: Session = Depends(get_db),
                 user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments.update_equip_by_cod_barras(db, codigo_barras_equip, equip)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el equipo")
        return {"message": "Equipo actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.put("/by_serial/{serial_equip}")
# def update_equip_by_serial(serial_equip: str, 
#                  equip: EquipoUpdate, 
#                  db: Session = Depends(get_db),
#                  user_token: UserOut = Depends(get_current_user)):
#     try:
#         id_rol = user_token.rol_id
#         if not verify_permissions(db, id_rol, modulo, 'actualizar'):
#             raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
#         success = crud_equipments.update_equip_by_id(db, serial_equip, equip)
#         if not success:
#             raise HTTPException(status_code=400, detail="No se pudo actualizar el equipo")
#         return {"message": "Equipo actualizado correctamente"}
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail=str(e))

