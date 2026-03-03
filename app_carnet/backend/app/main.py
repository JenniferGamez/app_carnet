import os

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.auth import router as auth_router
from app.routes.carnet import router as carnet_router

app = FastAPI()

# static_dir = os.path.join(os.path.dirname(__file__), "static")
# app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.getenv("CORS_ENABLED", "false").lower() == "true":
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    allow_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def enforce_json_only(request: Request, call_next):
    # En produccion, forzar HTTPS fuera de localhost
    hostname = request.url.hostname or ""
    if request.url.scheme == "http" and hostname not in ("localhost", "127.0.0.1"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten conexiones HTTPS",
        )

    if request.query_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten query params",
        )

    if request.method in ("POST", "PUT", "PATCH") and request.url.path != "/carnets/import":
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Solo se permite JSON",
            )

    return await call_next(request)

@app.get("/")
def root():
    return {"message": "Carnet API running"}


app.include_router(carnet_router)
app.include_router(auth_router)