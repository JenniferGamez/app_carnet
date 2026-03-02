# Estrategia de Seguridad Integral: Postgres + FastAPI

Este documento define la arquitectura de seguridad dividida en capas independientes: **Infraestructura** (Postgres) y **Lógica de Negocio** (FastAPI).

---

## 1. Capas de Seguridad y Sus Objetivos

| Capa | Responsable | Objetivo Principal |
| --- | --- | --- |
| **Infraestructura** | PostgreSQL | **Integridad Física:** Evitar que el sistema sea destruido (borrado de tablas, bases de datos o esquemas). |
| **Logica de Negocio** | FastAPI | **Autorización:** Controlar qué usuario específico puede ver o editar qué dato (Privacidad). |

---

## 2. Jerarquía de Roles de Infraestructura (Postgres)

La seguridad de infraestructura se basa en el principio de **Mínimo Privilegio**. No se utiliza el usuario Root para el funcionamiento diario.

### A. Usuario Root (`superuser`)

* **Por qué:** Es el dueño de la estructura.
* **Acciones:** Crear/Eliminar tablas, modificar tipos de datos, gestionar extensiones.
* **Uso:** Exclusivo para el Desarrollador en tareas de mantenimiento.

### B. Usuario de Escritura (`app_editor`)

* **Por qué:** Para que la aplicación pueda realizar operaciones de datos sin tener poder sobre la estructura.
* **Acciones:** `SELECT`, `INSERT`, `UPDATE`, `DELETE` sobre las filas de las tablas. No puede hacer `DROP` ni `ALTER`.
* **Uso:** Conexión principal del Backend para usuarios logueados.

### C. Usuario de Lectura (`app_viewer`)

* **Por qué:** Aislar las consultas públicas o de visitantes para que sea imposible alterar los datos por accidente o ataque.
* **Acciones:** Únicamente `SELECT`.
* **Uso:** Consultas de visitantes anónimos o validación de códigos QR.

---

## 3. Seguridad y Lógica de Negocio (FastAPI)

Aquí es donde se gestiona la **Integridad de los Datos** según el perfil del usuario final. No se basa en permisos de Postgres, sino en tablas internas.

### A. Gestión de Identidad (Autenticación)

* **Mecanismo:** Registro de usuarios con contraseñas hasheadas y validación mediante **JWT (JSON Web Tokens)**.

### B. Gestión de Permisos (Autorización RBAC)

Para permitir que los permisos sean compartidos y escalables, se utilizan tres tablas:

1. **Roles:** Grupos de usuarios (Estudiante, Profesor, Admin).
2. **Permisos:** Acciones granulares (ej: `editar_telefono`, `ver_calificaciones`).
3. **Roles_Permisos:** Tabla intermedia que mapea qué acciones puede hacer cada grupo.

---

## 4. Estrategia de Acceso Temporal (Tokens Dinámicos)

Para escenarios de alta sensibilidad (como la consulta de carnets mediante QR), se implementa una sub-capa de seguridad:

* **Tokens de Corta Duración:** Tokens JWT independientes de la sesión principal que expiran en minutos.
* **Propósito:** Garantizar que la información no quede expuesta permanentemente. Si el token expira, el acceso se cierra automáticamente sin intervención manual.

---

## 5. Integridad de los Datos

La integridad se garantiza cruzando ambas capas:

* **Validación de Campos:** El Backend filtra qué columnas puede enviar un usuario (ej: un estudiante no puede enviar el campo "nota" en un JSON de actualización).
* **Filtro de Filas:** El Backend añade siempre la cláusula `WHERE usuario_id = actual` para evitar que un usuario acceda a datos ajenos, aunque Postgres le permita leer la tabla completa.

---

## 6. Resumen de Flujo de Seguridad

1. **El Usuario** solicita una acción.
2. **FastAPI** verifica su identidad (JWT) y sus permisos (Tabla Roles/Permisos).
3. **FastAPI** aplica la lógica de negocio (¿Puede editar este campo específico?).
4. **Postgres** recibe la orden mediante un rol limitado (`app_editor`).
5. **Postgres** ejecuta si la acción no compromete la estructura de la base de datos.

---

## **Diagramas de Entidad-Relación (ERD)**

Aquí tienes el diseño del **Modelo Entidad-Relación (ERD)** que materializa toda la estrategia de roles, permisos y usuarios que hemos discutido. Este diseño permite que los permisos sean compartidos y que la estructura sea escalable.

Este modelo sigue la arquitectura **RBAC (Role-Based Access Control)**.

### 1. Estructura de Tablas

#### A. Entidades Principales

* **`users`**: Almacena la identidad (email, password hash). Tiene una relación **muchos a uno** con `roles`.
* **`roles`**: Define los perfiles (Estudiante, Profesor, Admin).
* **`permissions`**: Define las acciones atómicas (ej: `carnet:read`, `notas:write`, `perfil:edit_phone`).

#### B. Entidad Intermedia (La Llave del Sistema)

* **`role_permissions`**: Tabla de ruptura que permite que un permiso pertenezca a varios roles y un rol tenga muchos permisos. Es la que permite **compartir** funcionalidades.

---

### 2. Diccionario de Datos del ERD

| Tabla | Columna | Tipo | Descripción |
| --- | --- | --- | --- |
| **`users`** | `id` | UUID / INT | Clave primaria. |
|  | `role_id` | FK | Relación con la tabla `roles`. |
|  | `is_active` | BOOLEAN | Control de estado de cuenta. |
| **`roles`** | `id` | INT | Clave primaria. |
|  | `name` | VARCHAR | Nombre único (ej: `admin`). |
| **`permissions`** | `id` | INT | Clave primaria. |
|  | `slug` | VARCHAR | Código único para el backend (ej: `user:edit`). |
| **`role_permissions`** | `role_id` | FK | Referencia al Rol. |
|  | `permission_id` | FK | Referencia al Permiso. |

---

## 🛠️ Cómo este ERD cumple con tus requisitos

1. **Seguridad de Infraestructura:** El usuario `app_editor` de Postgres tiene permiso sobre estas 4 tablas, pero el usuario `app_viewer` solo tiene permiso de `SELECT` sobre `users` y `roles` para validar el QR.
2. **Integridad de Negocio:**
* Si un **Estudiante** quiere editar su nota, FastAPI consulta: `user -> role -> permissions`.
* Al no encontrar el `slug` de `notas:write`, FastAPI detiene la operación antes de que llegue a Postgres.


3. **Flexibilidad:** Si decides que los **Profesores** ahora pueden "Editar Teléfono" (permiso que antes era solo de Estudiantes), simplemente insertas una fila en `role_permissions` vinculando el `role_id` de Profesor con el `permission_id` de `perfil:edit_phone`.

---

## Pasos para la creación en Postgres (como Root)

Para implementar este ERD, el desarrollador (**Root**) debe seguir este orden de creación para respetar las llaves foráneas:

1. **Crear `roles` y `permissions**`: Son las tablas maestras.
2. **Crear `users**`: Requiere que los roles ya existan.
3. **Crear `role_permissions**`: Requiere que tanto roles como permisos existan.
4. **Establecer `ALTER DEFAULT PRIVILEGES**`: Para que el usuario `app_editor` pueda trabajar sobre ellas automáticamente.
