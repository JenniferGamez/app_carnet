from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from gateway.config import get_auth_config

auth_settings = get_auth_config()

SECRET_KEY = auth_settings["SECRET_KEY"]
ALGORITHM = auth_settings["ALGORITHM"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60) # El token dura 1 hora
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        carnet: str = payload.get("sub") # Usamos el carnet como identificador
        if carnet is None:
            raise credentials_exception
        return carnet
    except JWTError:
        raise credentials_exception