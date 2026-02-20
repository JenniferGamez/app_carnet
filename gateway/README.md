Gateway (La Puerta): Su único trabajo es recibir peticiones, validar que no sean ataques (limpieza de caracteres, seguridad), verificar si el usuario existe (Auth) y redirigir la orden al servidor de lógica. Es un "tráfico" inteligente.

run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

## FAST API

pip install fastapi uvicorn pydantic[email]

Tokens JWT:

pip install python-jose[cryptography] passlib[bcrypt]


qr

pip install qrcode[pil]

pip install Flask requests

pip install fastapi uvicorn pymongo pydantic[email] qrcode[pil]

pip install python-jose[cryptography]


## SOLO ESTO
pip install fastapi uvicorn pymongo pydantic[email] qrcode[pil] python-jose[cryptography] python-multipart



# En Windows (PowerShell)
$env:DEBUG="True"
uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload


## Flujo de QR escaneo y token

Para que esto funcione, el flujo debe ser el siguiente:

El QR estático: Contiene una URL que apunta a tu Gateway, por ejemplo: https://api.usb.ve/scan/{id_seguro}.

El Escaneo (Gateway): Cuando alguien escanea el código, el Gateway recibe ese id_seguro, verifica que el carnet esté activo y genera un Token de Sesión Temporal (que dura, por ejemplo, 1 o 2 minutos).

Redirección: El Gateway redirige al navegador del que escaneó a una página del Front-end (Flask) pasando ese token corto.

Visualización: La página muestra los datos. Si alguien intenta usar ese mismo enlace 5 minutos después, el token habrá expirado y los datos no se verán.

Vamos a implementar esto en el Gateway usando FastAPI:




### LEER

Entiendo perfectamente la confusión. Vamos a aclarar por qué necesitamos ese **token estático** y por qué se genera en el servidor.

Imagina que el carnet físico es como una llave. Si esa llave cambiara cada 5 minutos, tendrías que imprimir un carnet nuevo a cada momento. Por eso necesitamos algo que **no cambie** en el papel, pero que nos lleve a algo que **sí venza** en el mundo digital.

### ¿Qué hace exactamente esa función?

1. **El `token_fijo` (La Identidad de la Llave):**
Es un código único (ejemplo: `xK3_92Lp`) que se genera **una sola vez** cuando el usuario se registra. Este código se guarda en la base de datos asociado a ese usuario. Su función es ser el identificador "secreto" que está impreso en el QR.
2. **La `url_qr` (Lo que lee el celular):**
Es la dirección que el servidor va a convertir en cuadritos negros y blancos (la imagen del QR).
* **No lleva datos personales.**
* **No lleva el nombre del usuario.**
* Solo lleva una ruta que apunta a tu **Gateway**.



### ¿Cómo funciona el proceso completo?

Aquí está la clave de tu arquitectura:

1. **REGISTRO (En el Servidor):**
* El servidor genera el carnet `26-10001`.
* El servidor genera el `token_fijo` (ejemplo: `ABC123`).
* El servidor crea la imagen del QR que apunta a `http://gateway.com/scan/ABC123`.
* **Esto no cambia nunca.** El usuario imprime su carnet y lo guarda en su billetera.


2. **ESCANEADO (En el Gateway):**
* Alguien escanea el carnet. El teléfono abre: `http://gateway.com/scan/ABC123`.
* El **Gateway** recibe el código `ABC123`.
* El Gateway busca en la base de datos: *¿Quién es el dueño del token ABC123?*
* La base de datos responde: *Es el carnet 26-10001*.


3. **EL TRUCO DE SEGURIDAD (El Token Temporal):**
* Aquí es donde entra lo que me pediste antes: el Gateway, **en ese mismo instante**, genera un "pase temporal" (JWT) que dura 2 minutos.
* El Gateway redirige al navegador a: `http://frontend.com/ver-perfil?token=JWT_TEMPORAL`.



### ¿Por qué lo hacemos así?

* **Si el carnet se pierde:** Puedes entrar al sistema y cambiar el `token_fijo` en la base de datos. Automáticamente, el código QR impreso en el carnet viejo dejará de funcionar porque el Gateway ya no lo reconocerá cuando alguien lo escanee.
* **Privacidad:** Si alguien intercepta la URL del QR, no puede saber quién es el usuario a menos que el Gateway le dé permiso (validando el escaneo).
* **Eficiencia:** El servidor de lógica solo trabaja una vez (al crear el carnet). El Gateway se encarga de todo el "tráfico" de validaciones rápidas después.

**¿Ahora queda más claro por qué el servidor debe guardar ese código fijo al principio?** Es el vínculo permanente entre el papel físico y tu base de datos.