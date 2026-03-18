import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.schemas.users import UserOut
from app.schemas.equipments import EquipoCreate, EquipoUpdate, EquipoOut, PaginatedEquipos
from app.crud import equipments as crud_equipments
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 7

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_equipo(
    persona_id: int = Form(...),
    categoria_id: int = Form(...),
    serial: str = Form(...),
    marca_modelo: str = Form(...),
    descripcion: str = Form(...),
    codigo_barras_inv: str = Form(...),
    fecha_registro: str = Form(...),
    estado: bool = Form(...),
    foto_path: UploadFile = File(None),
     
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        file_path = None

        if foto_path:
            os.makedirs("uploads", exist_ok=True)
            file_path = f"uploads/{codigo_barras_inv}.jpg"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(foto_path.file, buffer)

        equipo_data = EquipoCreate(
            persona_id=persona_id,
            categoria_id=categoria_id,
            serial=serial,
            marca_modelo=marca_modelo,
            descripcion=descripcion,
            codigo_barras_inv=codigo_barras_inv,
            fecha_registro=fecha_registro,
            estado=estado,
            foto_path=file_path
        )
        crud_equipments.create_equipment(db, equipo_data)
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
def get_by_tipo_equip(tipo_equip: int, 
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
    id_equip: str,
    estado_equip: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_equipments.update_estado_equip(db, id_equip, estado_equip)
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

@router.get("/all_equips-pag", response_model=PaginatedEquipos)
def get_equipements_pag(
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
        data = crud_equipments.get_all_equipements_pag(db, skip=skip, limit=page_size)

        total = data["total"] #cambiar a total 
        equipos = data["equipos"] #cambiar a equipements

        return PaginatedEquipos(
            page= page,
            page_size= page_size,
            total_equipements= total,
            total_pages= (total + page_size - 1) // page_size,
            equipos= equipos
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

