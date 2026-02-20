from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from gateway.database import usuarios_col
from gateway.auth_handler import create_access_token
from pydantic import BaseModel

router = APIRouter()

class LoginSchema(BaseModel):
    carnet: str
    password: str

@router.post("/login")
async def login(datos: LoginSchema):
    # Buscar usuario por carnet y password
    user = usuarios_col.find_one({"carnet": datos.carnet, "password": datos.password})
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status": "fail",
                "message": "Carnet o contraseña incorrectos",
                "data": None
            }
        )
    
    # Generar Token JWT de acceso (para su sesión)
    token = create_access_token(data={"sub": user["carnet"]})
    
    return {
        "status": "success",
        "message": "Inicio de sesión exitoso",
        "data": {
            "token": {
                "access_token": token,
                "token_type": "bearer"
            },
            "user": {
                "nombre": user["nombre"],
                "carnet": user["carnet"],
                "qr_image_url": f"/static/qrcodes/qr_{user['carnet']}.png"
            }
        }
    }