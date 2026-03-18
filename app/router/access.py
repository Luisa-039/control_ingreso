from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.access import AccessCreate, AccessOut, PaginatedAccess
from app.schemas.users import UserOut
from app.crud import access as crud_access
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 5

#Crear el registro de ingreso de la persona sin equipo
@router.post("/crear-by_document-scan", status_code=status.HTTP_201_CREATED)
def create_center(  
    cod_barras_p: str,
    registro_acc: AccessCreate,
    area_id: int,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        resultado = crud_access.registro_acceso(db=db,
                                                cod_barras=cod_barras_p,
                                                access=registro_acc,
                                                area_id_s=area_id,
                                                usuario_id = id_rol
                                                )

        if resultado == "person_not_found":
            raise HTTPException(status_code=404, detail="Persona no encontrada en el sistema")

        if resultado == "active_access_exists":
            raise HTTPException(
                status_code=409,
                detail="La persona ya tiene un ingreso activo. Debe registrar salida antes de un nuevo ingreso.",
            )

        if resultado == "area_required":
            raise HTTPException(
                status_code=422,
                detail="Debe enviar el area de visita para registrar el ingreso.",
            )

        if resultado == "area_not_found":
            raise HTTPException(
                status_code=404,
                detail="El area de visita no existe en el sistema.",
            )

        if resultado != "ok":
            raise HTTPException(status_code=400, detail="No fue posible registrar el ingreso")

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

#Actualizar fecha de salida por cod barras equipo
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

#Consulta de un registro de acceso por id del registro
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

#Consulta de todos los registros de acceso sin paginación
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

#Asociar al usuario por serial del equipo
@router.post("/asociar_equipo_serial", status_code=status.HTTP_201_CREATED)
def asoc_equip(serial: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.asociar_equipo_by_serial(db, serial)
        
        if resultado:
            return {"message": "Equipo asociado al registro correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Equipo no encontrado en el sistema"))    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Actualizar fecha de salida por serial equipo
@router.put("/salida_equip_serial")
def check_out_equipo_serial(
    serial_equipo: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id             
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        resultado = crud_access.check_out_equip(db, serial_equipo)
        
        if resultado:
            return {"Registro de salida almacenado correctamente"}
        else:
            raise HTTPException(status_code=404, detail=("Error al registrar la salida"))
        
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Consulta paginada de registros de acceso
@router.get("/paginated", response_model=PaginatedAccess)
def get_access_pag(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):

    id_rol = user_token.rol_id
    if not verify_permissions(db, id_rol, modulo, "seleccionar"):
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    skip = (page - 1) * page_size

    data = crud_access.get_all_access_pag(
        db, skip=skip, limit=page_size
    )

    total = data["total"]
    access = data["access"]

    return PaginatedAccess(
        page=page,
        page_size=page_size,
        total_access=total,
        total_pages=(total + page_size - 1) // page_size,
        access=access,
    )


