from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.schemas.users import UserOut
from app.schemas.equipments_sede import Equipo_sedeCreate, Equipo_sedeUpdate, Equipo_sedeOut, TipoEquipo_sede, Estado_equip_sede
from app.crud import equipments_sede as crud_equipments_sede
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 10

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_equipo(
    Equipo: Equipo_sedeCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_equipments_sede.create_equipment_sede(db, Equipo)
        return {"message": "Equipo registrado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/by-cod_barras",  response_model=Equipo_sedeOut)
def scan_equipment(cod_barras: str, 
                   db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments_sede.get_equipment_sede_by_cod_barras(db, cod_barras)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-serial_eq",  response_model=Equipo_sedeOut)
def get_by_serial_equip(serial: str, 
                        db: Session = Depends(get_db),
                        user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments_sede.get_equipment_sede_by_serial(db, serial)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-tipo_equip",  response_model=Equipo_sedeOut)
def get_by_tipo_equip(tipo_equip: TipoEquipo_sede, 
                        db: Session = Depends(get_db),
                        user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments_sede.get_equipment_sede_by_tipo(db, tipo_equip)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-equips_sede",  response_model=List[Equipo_sedeOut])
def scan_equipment(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        equipo = crud_equipments_sede.get_all_equipments_sede(db)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipos no encontrados")
        return equipo
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/by_id/{id_equip}")
def update_equip_by_id(id_equip: int, 
                 equip: Equipo_sedeUpdate, 
                 db: Session = Depends(get_db),
                 user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments_sede.update_equip_sede_by_id(db, id_equip, equip)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el equipo")
        return {"message": "Equipo actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/estado/{id_equip}", status_code=status.HTTP_200_OK)
def estado_equip(
    id_eq: str,
    estado_equip: Estado_equip_sede,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments_sede.update_estado_equip_sede(db, id_eq, estado_equip)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado del equipo actualizado a {estado_equip.value}"}
    except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.put("/by-cod_barras/{codigo_barras_equip}")

def update_equip(codigo_barras_equip: str, 
                 equip: Equipo_sedeUpdate, 
                 db: Session = Depends(get_db),
                 user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments_sede.update_equip_sede_by_cod_barras(db, codigo_barras_equip, equip)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el equipo")
        return {"message": "Equipo actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
