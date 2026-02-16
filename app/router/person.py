from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.person import PersonCreate, PersonUpdate, PersonOut
from app.schemas.users import UserOut
from app.crud import person as crud_person
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 5

@router.post("/crear-persona", status_code=status.HTTP_201_CREATED)
def create_person(  
    person: PersonCreate,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        crud_person.create_person(db, person)
        return {"message": "Persona creada correctamente"}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/person-by-document", response_model=PersonOut)
def get_person(
    document: str,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol=user_token.rol_id

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        person = crud_person.get_person_by_document_number(db, document)
        if not person:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        return person
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all/person", response_model=List[PersonOut])
def get_all_person(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        person = crud_person.get_all_person(db)
        return person
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/by-document/{document}")
def update_person_by_document(
    document: str, 
    person: PersonUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_person.update_person_by_document(db, document, person)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la persona")
        return {"message": "Persona actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/cambiar-estado/{id_persona}", status_code=status.HTTP_200_OK)
def change_person_status(
    id_persona: int,
    nuevo_estado: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        success = crud_person.change_persona_status(db, id_persona, nuevo_estado)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {"message": f"Estado de la persona actualizado a {nuevo_estado}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e)) 