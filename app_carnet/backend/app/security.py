import os
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import Usuario


pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def _auth_enabled() -> bool:
    return os.getenv("AUTH_ENABLED", "false").lower() == "true"


def _authz_enabled() -> bool:
    return os.getenv("AUTHZ_ENABLED", "false").lower() == "true"


def _jwt_secret_key() -> str:
    key = os.getenv("JWT_SECRET_KEY", "").strip()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY no configurado",
        )
    return key


def _jwt_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256").strip() or "HS256"


def _jwt_expire_minutes() -> int:
    raw = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 60



def require_internal_token(
    x_internal_gateway_token: Optional[str] = Header(default=None),
) -> None:
    if not _auth_enabled():
        return

    expected = os.getenv("INTERNAL_API_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_API_TOKEN no configurado",
        )

    if x_internal_gateway_token != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso no autorizado",
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def authenticate_user(db: Session, usbid: str, password: str) -> Optional[Usuario]:
    user = db.query(Usuario).filter(Usuario.usbid == usbid, Usuario.activo.is_(True)).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(*, usbid: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=_jwt_expire_minutes()))
    to_encode = {"sub": str(usbid), "exp": expire}
    return jwt.encode(to_encode, _jwt_secret_key(), algorithm=_jwt_algorithm())


def _decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _jwt_secret_key(), algorithms=[_jwt_algorithm()])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    return str(subject)


def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_user_usbid: Optional[str] = Header(default=None, alias="X-User-USBID"),
    db: Session = Depends(get_db),
) -> Optional[Usuario]:
    if not _authz_enabled():
        return None

    usbid: Optional[str] = None

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        usbid = _decode_access_token(token)
    elif x_user_usbid:
        usbid = x_user_usbid
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta Authorization Bearer",
        )

    user = db.query(Usuario).filter(Usuario.usbid == usbid, Usuario.activo.is_(True)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    return user


def require_permission(permission_name: str) -> Callable:
    def _dependency(current_user: Optional[Usuario] = Depends(get_current_user)) -> None:
        if not _authz_enabled():
            return

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado",
            )

        if current_user.rol_nombre == "SuperAdmin":
            return

        role = current_user.rol
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin rol asignado",
            )

        role_permissions = {permiso.nombre for permiso in role.permisos}
        if permission_name not in role_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permission_name}",
            )

    return _dependency
