from pydantic import BaseModel, EmailStr, Field, field_validator, field_validator
import re
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from gateway.database import usuarios_col

# SERVER
from gateway.server.register import new_user 

router = APIRouter()

class RegistroSchema(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator('nombre')
    def nombre_limpio(cls, v):
        if re.search(r'[<>{}\[\]\\$|&;]', v):
            raise ValueError('El nombre contiene caracteres no permitidos')
        return v.strip()
    
@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(datos: RegistroSchema, request: Request):

    if usuarios_col.find_one({"email": datos.email}):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "El correo electrónico ya se encuentra registrado",
                "data": None
            }
        )
    try:
        base_url = str(request.base_url)
        
        # SERVIDOR (donde se crea el carnet y el token fijo)
        resultado = new_user(datos.nombre, datos.email, datos.password, base_url)
    
        return {
            "status": "success",
            "message": "Usuario creado exitosamente",
            "data": {
                "carnet": resultado["carnet"],
                "token_qr": resultado["token_qr"],
                "url_qr": resultado["url_completa"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": str(e), "data": None}
        )