# Sistema de Carnetización Inteligente USB

Este proyecto es un sistema de gestión de carnets universitarios que utiliza una arquitectura de **API Gateway** para separar la seguridad de la lógica de negocio, generando códigos QR dinámicos para el acceso.

## Arquitectura
- **Gateway (FastAPI):** Punto de entrada único. Gestiona seguridad (HTTPS, Tokens internos) y sirve archivos estáticos.
- **Logic Server (Python):** Genera números de carnet únicos basados en el año actual y renderiza imágenes QR.
- **Frontend (Flask):** Interfaz de usuario para registro, login y visualización del carnet.
- **Base de Datos:** MongoDB para almacenamiento de perfiles y rutas de archivos.

## Instalación y Configuración

### Requisitos previos
- Python 3.10+
- MongoDB corriendo localmente o en la nube.

### Configuración del Entorno
1. Instala las dependencias necesarias:
   ```bash
   pip install fastapi uvicorn qrcode[pil] pymongo requests flask pydantic[email] qrcode[pil] python-jose[cryptography] python-multipart

PROYECTO_CARNET/
├── gateway_api/              # EL BACKEND (FastAPI)
│   ├── .venv/                # Entorno virtual del Backend
│   ├── gateway/              # Rutas, Middleware y Configuración
│   ├── server/               # Lógica de negocio (Generación de QR y Carnet)
│   │   └── static/qrcodes/   # Carpeta donde se guardan los archivos .png
│   └── main.py               # Punto de arranque del Gateway
└── frontend_flask/           # EL FRONTEND (Flask)
    ├── .venv/                # Entorno virtual del Frontend
    ├── templates/            # Archivos HTML (index, registro, perfil)
    └── app.py                # Lógica de la aplicación web


🛠️ Requisitos e Instalación
1. Preparar el Backend (Gateway)
Entra en la carpeta gateway_api, crea el entorno e instala las librerías de procesamiento:

Bash
cd gateway_api
python -m venv .venv
# Activar (Windows: .venv\Scripts\activate | Mac/Linux: source .venv/bin/activate)
pip install fastapi uvicorn pymongo pydantic[email] qrcode[pil]
2. Preparar el Frontend (Flask)
Entra en la carpeta frontend_flask, crea su propio entorno e instala las librerías de cliente:

Bash
cd frontend_flask
python -m venv .venv
# Activar (Windows: .venv\Scripts\activate | Mac/Linux: source .venv/bin/activate)
pip install flask requests


usb_carnet/
├── gateway/
│   ├── main.py                # Punto de entrada y seguridad (CORS/Sanitización)
│   ├── config.py              # Lectura de .ini
│   ├── database.py            # Conexión a Mongo
│   ├── auth_handler.py        # Lógica de JWT
│   └── routes/
│       ├── __init__.py
│       ├── auth.py            # Login y verificación de existencia
│       └── register.py        # Proceso de registro (llama al Server)
└── server/
    ├── logic.py               # Generación de Carnet y Token HMAC
    └── qr_generator.py        # Generación de la imagen PNG
└── frontend_web/       # Interfaz de usuario (Streamlit o Flask)
    └── app.py

## ROLES DE LAS CARPETAS

- Gateway (La Puerta): Su único trabajo es recibir peticiones, validar que no sean ataques (limpieza de caracteres, seguridad), verificar si el usuario existe (Auth) y redirigir la orden al servidor de lógica. Es un "tráfico" inteligente.

- Server (El Cerebro): Aquí reside la lógica pesada. Generar el ID del carnet (26-XXXXX), crear el token HMAC de seguridad y generar la imagen física del QR. El Gateway le pregunta al Server: "Oye, regístrame a este usuario", y el Server hace el trabajo sucio.
