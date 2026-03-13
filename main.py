from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import users, auth, person, sede, center, equipments, equipments_sede, access, roles, autorizacion_salida, movements
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/access", tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(roles.router, prefix="/rol", tags=["roles"])
app.include_router(person.router, prefix="/person", tags=["person"])
app.include_router(sede.router, prefix="/sede", tags=["sede"])
app.include_router(equipments.router, prefix="/equipments", tags=["equipments"])
app.include_router(center.router, prefix="/center", tags=["center"])
app.include_router(equipments_sede.router, prefix="/equipments_sede", tags=["equipments_sede"])
app.include_router(autorizacion_salida.router, prefix="/autorizacion_salida", tags=["autorizacion_salida"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])
app.include_router(access.router, prefix="/access", tags=["access"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {
                "message": "ok",
                "autor": "Sistema"
            }