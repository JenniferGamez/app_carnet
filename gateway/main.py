from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
import os
from gateway.routes import auth, register
from gateway.config import get_internal_token

app = FastAPI(title="Gateway USB")

API_INTERNAL_TOKEN = get_internal_token()



@app.middleware("http")
async def validar_seguridad_global(request: Request, call_next):
    # FORZAR HTTPS (Solo en producción)
    # Si detecta que no es https y no estás en localhost, rechaza.
    if request.url.scheme == "http" and "localhost" not in request.url.hostname:
        raise HTTPException(status_code=400, detail="Solo se permiten conexiones HTTPS")

    token_cliente = request.headers.get("X-Internal-Gateway-Token")
    
    if os.getenv("DEBUG") != "True":
        if token_cliente != API_INTERNAL_TOKEN:
            raise HTTPException(status_code=403, detail="Acceso no autorizado")
    
    response = await call_next(request)
    return response
    
    
# Rutas
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(register.router, prefix="/register", tags=["Registro"])

# Montar archivos estáticos para servir el frontend y ver el QR generado
STATIC_DIR = os.path.join(os.path.dirname(__file__), "server", "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    os.makedirs(os.path.join(STATIC_DIR, "qrcodes"), exist_ok=True)
    
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def check_health():
    return {"status": "Gateway Operativo"}