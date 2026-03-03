from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    usbid: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.usbid, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    access_token = create_access_token(usbid=user.usbid)

    role_permissions = sorted({permiso.nombre for permiso in user.rol.permisos}) if user.rol else []

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "usbid": user.usbid,
            "rol": user.rol_nombre,
            "permisos": role_permissions,
        },
    }
