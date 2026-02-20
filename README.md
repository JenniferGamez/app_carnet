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
