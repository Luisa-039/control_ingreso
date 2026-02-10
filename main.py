from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import users, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/access", tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {
                "message": "ok",
                "autor": "Luisita ok"
            }