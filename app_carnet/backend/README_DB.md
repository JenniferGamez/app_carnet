# Backend - instalacion y base de datos

Guia para instalar, configurar la base de datos y levantar el backend.

## Requisitos

- Python 3.10+
- PostgreSQL 17 (puerto 5432 recomendado)

## Crear entorno e instalar dependencias

Desde la carpeta backend:

```cmd
pip install -r requirements.txt
python -m venv .venv
.\.venv\Scripts\activate
```

## Crear usuario y base de datos

Entrar a psql como postgres (PG17):

```cmd
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5432
```

Crear usuario y DB:

```sql
CREATE USER carnet_user WITH PASSWORD '1234';
CREATE DATABASE carnet_db OWNER carnet_user;
GRANT ALL PRIVILEGES ON DATABASE carnet_db TO carnet_user;
```

Salir:

```sql
\q
```

## Migraciones

Desde la carpeta backend:

```cmd
alembic upgrade head
```

## Bootstrap de SuperAdmin

La migración `c3d4e5f6a7b8_seed_bootstrap_superadmin.py` crea/actualiza un único usuario `SuperAdmin`.

Variables de entorno soportadas:

- `SUPERADMIN_USBID` (default: `1`)
- `SUPERADMIN_PASSWORD_HASH` (recomendado) o `SUPERADMIN_PASSWORD`
- `SUPERADMIN_DEPARTAMENTO_ID` (opcional; si no está, usa el primer departamento)
- `SUPERADMIN_DESCRIPCION` (opcional)

Ejemplo (PowerShell):

```powershell
$env:SUPERADMIN_USBID="1"
$env:SUPERADMIN_PASSWORD="Cambia_Esta_Clave_En_Produccion"
python -m alembic upgrade head
```

## Seguridad y autenticación (ACLARATORIO IMPORTANTE)

El backend maneja dos mecanismos distintos:

1. **Autorización actual por usuario/rol/permiso (RECOMENDADO)**
2. **Token interno legacy entre servicios (OPCIONAL)**

### 1) Mecanismo actual: JWT + RBAC

- **Login**: `POST /auth/login` con `usbid` y `password`.
- **Respuesta**: devuelve `access_token` (JWT tipo Bearer).
- **Uso en endpoints protegidos**:

```http
Authorization: Bearer <token>
```

- El backend valida:
  - usuario activo,
  - rol,
  - permisos requeridos por endpoint.

### 2) Mecanismo legacy: `INTERNAL_API_TOKEN`

- Se activa solo cuando `AUTH_ENABLED=true`.
- Exige header:

```http
X-Internal-Gateway-Token: <INTERNAL_API_TOKEN>
```

- **No identifica usuarios**, solo protege servicio-a-servicio.
- No reemplaza JWT ni control de permisos por rol.

### ¿Qué conviene usar?

- Para frontend/usuarios: **JWT + RBAC** (`AUTHZ_ENABLED=true`).
- Para integración interna (si se necesita): `AUTH_ENABLED=true` + `INTERNAL_API_TOKEN`.

## Variables `.env` (resumen práctico)

- `DATABASE_URL`: conexión PostgreSQL.
- `CORS_ENABLED`: activa middleware CORS.
- `CORS_ORIGINS`: orígenes permitidos (coma separada).
- `AUTHZ_ENABLED`: activa autorización por usuario/rol/permiso.
- `JWT_SECRET_KEY`: clave para firmar JWT.
- `JWT_ALGORITHM`: algoritmo JWT (`HS256`).
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: duración del token (ej. `10080` = 7 días).
- `AUTH_ENABLED`: activa validación de token interno legacy.
- `INTERNAL_API_TOKEN`: token interno legacy (si `AUTH_ENABLED=true`).
- `SUPERADMIN_USBID`: usuario bootstrap superadmin.
- `SUPERADMIN_PASSWORD` / `SUPERADMIN_PASSWORD_HASH`: contraseña inicial/hash para migración bootstrap.
- `SUPERADMIN_DEPARTAMENTO_ID`: departamento de bootstrap (opcional).
- `SUPERADMIN_DESCRIPCION`: descripción de bootstrap.

## Flujo recomendado para desarrollo

1. Ejecutar migraciones:

```cmd
python -m alembic upgrade head
```

2. Levantar API:

```cmd
uvicorn app.main:app --reload
```

3. Hacer login:

```http
POST /auth/login
Content-Type: application/json

{
    "usbid": 1,
    "password": "<tu_clave_superadmin>"
}
```

4. Usar token en requests protegidas:

```http
Authorization: Bearer <access_token>
```

## Recomendaciones de producción

- Cambiar `JWT_SECRET_KEY` por una clave fuerte y privada.
- Usar `SUPERADMIN_PASSWORD_HASH` (evitar contraseña en texto plano).
- Rotar credenciales iniciales después del primer despliegue.
- Mantener `AUTH_ENABLED=false` salvo necesidad real de token interno legacy.

## Levantar el servidor

```cmd
uvicorn app.main:app --reload
```
