from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir estos métodos HTTP
    allow_headers=["*"],  # Permitir cualquier encabezado en las solicitudes
)

app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {
                "message": "ok",
                "autor": "Luisita ok"
            }