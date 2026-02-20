from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from gateway.database import usuarios_col
from gateway.auth_handler import create_access_token # JWT
from datetime import timedelta

app = FastAPI()

@app.get("/scan/{token_fijo}")
async def procesar_escaneo(token_fijo: str):
    # Buscar al dueño del QR en la BD
    usuario = usuarios_col.find_one({"qr_info.token_estatico": token_fijo})
    
    if not usuario:
        raise HTTPException(status_code=404, detail="QR no válido")

    # Generar un Token de Corta Duración
    # Este token es el que permitirá ver los datos en la web
    token_temporal = create_access_token(
        data={"sub": usuario["carnet"], "tipo": "view_scan"},
        expires_delta=timedelta(minutes=2) 
    )

    # Redirigir al Front-end (Flask) con el token temporal
    # El Front-end recibirá este token y pedirá los datos del usuario
    url_frontal = f"http://tu-app-flask.com/perfil-publico?t={token_temporal}"
    
    return RedirectResponse(url=url_frontal)