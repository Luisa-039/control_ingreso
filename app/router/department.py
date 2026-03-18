from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.schemas.users import UserOut
from app.schemas.departments import DepartmentCreate, DepartmentOut, PaginatedDeparment
from app.crud import department as crud_department
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 14

#Endpoint de crear departamento
@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_department(
    Department: DepartmentCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        #Verficamos que tenga permisos
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_department.create_department(db, Department)
        return {"message": "Departamento registrado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Endpoint para obtener departamento por código 
@router.get("/by-code",  response_model=DepartmentOut)
def get_department_by_code(codigo: str, 
                   db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        #Verificamos que tenga permisos
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        department = crud_department.get_department_by_code(db, codigo)
        if not department:
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        return department
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Endpoint para obtener todos los departamentos
@router.get("/all-departments",  response_model=List[DepartmentOut])
def get_all_departments(db: Session = Depends(get_db),
                   user_token: UserOut = Depends(get_current_user)):
    try:
        #Verificamos permisos
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        department = crud_department.get_all_departments(db)
        if not department:
            raise HTTPException(status_code=404, detail="Departamentos no encontrados")
        return department
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

#Endpoint para la paginación
@router.get("/all_departments-pag", response_model=PaginatedDeparment)
def get_all_departments_pag(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
): 
    try:
        #Verificamos permisos        
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        skip = (page - 1) * page_size
        data = crud_department.get_all_departments_pag(db, skip=skip, limit=page_size)

        total = data["total"]  
        departamentos = data["departamentos"]

        return PaginatedDeparment(
            page= page,
            page_size= page_size,
            total_departments= total,
            total_pages= (total + page_size - 1) // page_size,
            departamentos= departamentos
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))