@router.get("/all_users-pag", response_model=PaginatedUsers)
def get_users_pag(
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
        data = crud_users.get_all_users_pag(db, skip=skip, limit=page_size)
        
        total = data["total"] #cambiar a total 
        users = data["users"] #cambiar a users
        
        return PaginatedUsers(
            page= page,
            page_size= page_size,
            total_users= total,
            total_pages= (total + page_size - 1) // page_size,
            users= users
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
