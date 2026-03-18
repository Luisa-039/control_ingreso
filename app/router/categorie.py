from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.categories import CategorieCreate, CategorieUpdate, CategorieOut
from app.schemas.users import UserOut
from app.crud import categorie as crud_categoria
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
modulo = 16

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_categorie(
    Categoria: CategorieCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        #Verficamos que tenga permisos
        id_rol = user_token.rol_id       
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail= 'Usuario no autorizado')
        
        crud_categoria.create_categorie(db, Categoria)
        return {"message": "Categoria creada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/by-id",  response_model=CategorieOut)
def get_categorie_by_id(id: int, 
              db: Session = Depends(get_db),
              user_token: UserOut = Depends(get_current_user)):
    try:
        id_rol=user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        categoria = crud_categoria.get_categoria_by_id(db, id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrado")
        return categoria
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all/categories", response_model=List[CategorieOut])
def get_all_categories(
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, "seleccionar"):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        categoria = crud_categoria.get_all_categories(db)
        return categoria
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/by_id/{id_categoria}")
def update_categorie_by_id(id_categoria: int, 
                 categoria: CategorieUpdate, 
                 db: Session = Depends(get_db),
                 user_token: UserOut = Depends(get_current_user)):
    try:
        id_roles = user_token.rol_id
        if not verify_permissions(db, id_roles, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_categoria.update_categorie_by_id(db, id_categoria, categoria)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la categoria")
        return {"message": "Categoria actualizada correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/estado/{id_categoria}", status_code=status.HTTP_200_OK)
def estado_categoria(
    id_categoria: str,
    estado_categoria: bool,
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        id_rol = user_token.rol_id
        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        
        success = crud_categoria.change_categorie_status(db, id_categoria, estado_categoria)
        if not success:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")

        return {"message": f"Estado de la categoria actualizada a {estado_categoria}"}
    except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))
    