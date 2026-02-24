from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.access import AccessCreate, AccessOut
from app.schemas.users import UserOut
from app.crud import access as crud_access
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 5

#Crear el registro de ingreso de la persona sin equipo
@router.post("/crear-by_document-scan", status_code=status.HTTP_201_CREATED)
def create_center(  
    registro_acc: AccessCreate,
    cod_barras_p: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_access.registro_acceso(db=db,
                                    cod_barras=cod_barras_p,
                                    access=registro_acc,
                                    usuario_id = id_rol
                                    )
        return {"message": "registro creado correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Asociar el equipo que trae la persona al registro creado anteriormente
@router.post("/asociar_equipo_scan", status_code=status.HTTP_201_CREATED)
def asoc_equip(cod_barras_eq: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.asociar_equipo(db=db, cod_barras = cod_barras_eq)
        
        if resultado:
            return {"message": "Equipo asociado al registro correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Equipo no encontrado en el sistema"))    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Actualizar la fecha de salida de la persona por scan carnet o por cod barras equipo. 
@router.put("/salida_person_scan")
def check_out_person(
    cod_barras_person: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.check_out_person(db, cod_barras_person)
        
        if resultado:
            return {"Registro de salida almacenado correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Error al registrar la salida"))
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/salida_equip_scan")
def check_out_equipo(
    cod_barras_equipo: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.check_out_equip(db, cod_barras_equipo)
        
        if resultado:
            return {"Registro de salida almacenado correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Error al registrar la salida"))
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Consultar por id de acceso

@router.get("/registro_by_id", response_model=AccessOut)
def consulta_by_id_access( id_registro: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        registro_ext = crud_access.get_access_by_id(db, id_registro)
        if not registro_ext:
            raise HTTPException(status_code=404, detail="registro no encontrado")
        return registro_ext
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consult_by_doc_person", response_model=list[AccessOut])
def consulta_by_doc_person( documento_p: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        registro_ext = crud_access.get_access_by_documento(db, documento_p)
        if not registro_ext:
            raise HTTPException(status_code=404, detail="registro no encontrado")
        return registro_ext
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.get("/consult_by_id_equipo", response_model=list[AccessOut])
def consulta_by_doc_person( id_equip: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        registro_ext = crud_access.get_access_by_id_equip(db, id_equip)
        if not registro_ext:
            raise HTTPException(status_code=404, detail="registro no encontrado")
        return registro_ext
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@router.get("/consult_all_access", response_model=list[AccessOut])
def consulta_by_doc_person(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        registro_ext = crud_access.get_all_access(db)
        if not registro_ext:
            raise HTTPException(status_code=404, detail="registros no encontrados")
        return registro_ext
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
 
#Modo manual, si la pistola falla
@router.post("/crear-by_document_person", status_code=status.HTTP_201_CREATED)
def create_center(  
    registro_acc: AccessCreate,
    documento_p: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_access.registro_acceso(db,
                                    documento_p,
                                    registro_acc,
                                    id_rol
                                    )
        return {"message": "registro creado correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Actualizar la fecha de salida de la persona a través del scan del equipo
@router.post("/asociar_equipo_serial", status_code=status.HTTP_201_CREATED)
def asoc_equip(serial_eq: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.asociar_equipo_by_serial(db, serial_eq)
        
        if resultado:
            return {"message": "Equipo asociado al registro correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Equipo no encontrado en el sistema"))    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Actualizar fecha de salida por documento
@router.put("/salida_person_by_document")
def check_out_person_document(
    document_person: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.check_out_person(db, document_person)
        
        if resultado:
            return { "Registro de salida almacenado correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Error al registrar la salida"))
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/salida_equip_serial")
def check_out_equipo_serial(
    cod_barras_equipo: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.check_out_equip(db, cod_barras_equipo)
        
        if resultado:
            return {"Registro de salida almacenado correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Error al registrar la salida"))
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
