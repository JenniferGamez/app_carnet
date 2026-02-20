import random
import secrets
import datetime
from gateway.database import usuarios_col

from gateway.server.qr import qr_render

def new_user(nombre, email, password, base_url):
    anio_actual = str(datetime.datetime.now().year)[-2:]
    # Generar Carnet {Año}-{Aleatorio} único
    while True:
        num = random.randint(10000, 99999) # Posibilida de 90,000 carnets por año
        carnet = f"{anio_actual}-{num}"
        if not usuarios_col.find_one({"carnet": carnet}):
            break
    
    # Generar Token Fijo para el QR
    token_fijo = secrets.token_urlsafe(24)
    url_completa = f"{base_url}scan/{token_fijo}"
    
    # Pasamos la URL completa al renderizador de imagen
    ruta_qr = qr_render(carnet, url_completa)
    
    # Estructura del documento
    nuevo_doc = {
        "nombre": nombre,
        "email": email,
        "password": password, 
        "carnet": carnet,
        "fecha_registro": datetime.datetime.utcnow(),
        "qr_estatico": {
            "token": token_fijo,
            "url_acceso": url_completa,
            "ruta_qr": ruta_qr,
            "activo": True
        }
    }
    
    usuarios_col.insert_one(nuevo_doc)
    return {
        "carnet": carnet, 
        "token_qr": token_fijo, 
        "url_completa": url_completa
    }