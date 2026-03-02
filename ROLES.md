# Guía de Configuración de Seguridad: PostgreSQL

Este documento detalla la jerarquía de accesos para separar las responsabilidades del Desarrollador (Root) de las de la Aplicación y Visitantes.

## Tipo de operación

- DML (Data Manipulation Language): Es lo que hace tu App. Borrar una fila, cambiar un precio. Es el "trabajo sucio" del día a día. Para esto usamos el mi_app_user.

- DDL (Data Definition Language): Es lo que hace el Root. Borrar una tabla completa, crear un índice, cambiar el tipo de dato de una columna de INT a STRING.

## Jerarquía de Roles

Rol            Usuario      Permisos                                        Uso
Root           postgres     SUPERUSER.                                      Control total de la infraestructura.Solo para el Desarrollador.
Escritura      app_editor   CRUD (Insert, Update, Delete) sobre datos.      Usuarios logueados en la App.
Lectura        app_viewer   Solo SELECT.                                    No puede tocar nada.Visitantes no logueados / Reportes.

## Paso a Paso: Configuración Inicial de Seguridade de Roles a nivel de Infraestructura

Ejecuta estos comandos conectado como usuario Root (postgres).

- 1. Preparar el terreno (Base de Datos y Schemas)
Asegúrate de estar en la base de datos correcta antes de empezar.

```SQL
-- Conectarse a la base de datos del proyecto
\c mi_proyecto_db
```

- 2. Crear los Roles de la Aplicación

```SQL
-- Crear usuario para datos (Escritura)
CREATE ROLE app_editor WITH LOGIN PASSWORD 'pass_seguro_editor';

-- Crear usuario para visitantes (Lectura)
CREATE ROLE app_viewer WITH LOGIN PASSWORD 'pass_seguro_viewer';
```

- 3. Otorgar Permisos de Conexión y Navegación
Antes de tocar tablas, deben poder entrar a la base de datos y al esquema

```SQL
-- Permitir conexión
GRANT CONNECT ON DATABASE mi_proyecto_db TO app_editor, app_viewer;

-- Permitir ver el esquema 'public' (entrar a la habitación)
GRANT USAGE ON SCHEMA public TO app_editor, app_viewer;
```

- 4. Definir qué puede hacer cada uno (DML)
Aquí es donde diferenciamos al que puede modificar del que solo mira.

```SQL
-- Permisos para el EDITOR (Usuarios logueados)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_editor;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_editor; -- Necesario para IDs autoincrementables

-- Permisos para el VIEWER (Visitantes no logueados)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_viewer;
```

- 5. Automatización para el futuro (Crucial)
Como el Root es quien creará las tablas nuevas, debemos decirles a Postgres que las tablas futuras hereden estos permisos automáticamente.

```SQL
-- Para tablas nuevas: el editor podrá escribir y el viewer solo leer
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_editor;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_viewer;
```

