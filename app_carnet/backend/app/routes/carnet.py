import csv
import hashlib
import io
import os
import unicodedata
from datetime import date, datetime
from typing import Dict, List, Tuple

import qrcode
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.afiliacion import (
    Afiliacion,
    Carrera,
    EstudianteInfo,
    PersonaTieneAfiliacion,
    Sede,
    StatusPersonaAfiliacion,
    TrabajadorInfo,
)
from app.models.base import SexoEnum
from app.models.carnet import Carnet, StatusCarnet
from app.models.persona import Persona
from app.security import require_permission

router = APIRouter()

REQUIRED_COLUMNS_STUDENT = {"CARNET", "CEDULA_ESTUDIANTE", "APELLIDOS_ESTUDIANTE", "NOMBRES_ESTUDIANTE", "SEXO", "CARRERA"}
REQUIRED_COLUMNS_OBRERO = {"SEDE", "NO_DE_DOCUMENTO", "PRIMER_APELLIDO", "PRIMER_NOMBRE"}
REQUIRED_COLUMNS_PERSONAL = {"SEDE", "NO_DE_DOCUMENTO", "PRIMER_APELLIDO", "PRIMER_NOMBRE", "FECHA_DE_INGRESO", "TIPO_DE_PERSONAL"}


def _get_active_status_id(db: Session) -> int:
    status = db.query(StatusCarnet).filter(StatusCarnet.nombre == "Activo").first()
    if not status:
        status = db.query(StatusCarnet).first()
    if not status:
        status = StatusCarnet(nombre="Activo")
        db.add(status)
        db.commit()
        db.refresh(status)
    return status.id


def _normalize_sexo(value: str) -> SexoEnum:
    normalized = value.strip().upper()
    if normalized not in ("M", "F"):
        raise ValueError("sexo debe ser 'M' o 'F'")
    return SexoEnum.M if normalized == "M" else SexoEnum.F


def _build_carnet_uuid(usbid: str, cedula: str) -> str:
    seed = f"{cedula}|{usbid}" if cedula and usbid else (cedula or usbid)
    if not seed:
        raise ValueError("No se puede generar uuid sin carnet o cedula")
    return hashlib.md5(seed.encode("utf-8")).hexdigest()


def _get_carrera_codigo(db: Session, raw_value: str) -> int:
    value = (raw_value or "").strip()
    if not value:
        raise ValueError("CARRERA vacia")

    carrera = None
    if value.isdigit():
        carrera = db.query(Carrera).filter(Carrera.codigo == int(value)).first()
    if not carrera:
        carrera = db.query(Carrera).filter(func.lower(Carrera.nombre) == value.lower()).first()

    if not carrera:
        raise ValueError(f"La carrera '{value}' no existe en BD")

    return carrera.codigo


def _get_sede_id(db: Session, raw_value: str) -> int:
    value = (raw_value or "").strip()
    if not value:
        raise ValueError("SEDE vacia")

    sede = db.query(Sede).filter(func.lower(Sede.nombre) == value.lower()).first()
    if not sede:
        raise ValueError(f"La sede '{value}' no existe en BD")
    return sede.id


def _get_status_persona_activo_id(db: Session) -> int:
    status_persona = db.query(StatusPersonaAfiliacion).filter(func.lower(StatusPersonaAfiliacion.nombre) == "activo").first()
    if not status_persona:
        status_persona = db.query(StatusPersonaAfiliacion).first()
    if not status_persona:
        status_persona = StatusPersonaAfiliacion(nombre="Activo")
        db.add(status_persona)
        db.flush()
    return status_persona.id


def _get_or_create_afiliacion(db: Session, nombre: str, default_vigencia: int | None = None) -> Afiliacion:
    value = (nombre or "").strip()
    if not value:
        raise ValueError("Afiliacion vacia")

    afiliacion = db.query(Afiliacion).filter(func.lower(Afiliacion.nombre) == value.lower()).first()
    if not afiliacion:
        afiliacion = Afiliacion(nombre=value)
        if default_vigencia is not None:
            afiliacion.duracion_vigencia_anos = default_vigencia
        db.add(afiliacion)
        db.flush()
    return afiliacion


def _parse_date(value: str) -> date:
    raw = (value or "").strip()
    if not raw:
        raise ValueError("Fecha vacia")

    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Fecha invalida: '{raw}'")


def _add_years(base_date: date, years: int) -> date:
    try:
        return base_date.replace(year=base_date.year + years)
    except ValueError:
        return base_date.replace(month=2, day=28, year=base_date.year + years)


def _upsert_persona(
    db: Session,
    cedula: str,
    usbid: str,
    nombres: str,
    apellidos: str,
    sexo: SexoEnum | None,
):
    persona = db.query(Persona).filter(Persona.cedula == cedula).first()
    if not persona:
        if not sexo:
            raise ValueError("SEXO es requerido para crear persona nueva")
        persona = Persona(
            cedula=cedula,
            carnet_usbid=usbid,
            nombres=nombres,
            apellidos=apellidos,
            sexo=sexo,
            discapacidad=False,
        )
        db.add(persona)
    else:
        persona.carnet_usbid = usbid
        persona.nombres = nombres
        persona.apellidos = apellidos
        if sexo:
            persona.sexo = sexo


def _upsert_persona_afiliacion(
    db: Session,
    cedula: str,
    afiliacion_id: int,
    status_persona_id: int,
    sede_id: int,
    fecha_incorporacion: date | None,
):
    persona_afiliacion = db.query(PersonaTieneAfiliacion).filter(
        PersonaTieneAfiliacion.persona_cedula == cedula,
        PersonaTieneAfiliacion.afiliacion_id == afiliacion_id,
    ).first()

    if not persona_afiliacion:
        persona_afiliacion = PersonaTieneAfiliacion(
            persona_cedula=cedula,
            afiliacion_id=afiliacion_id,
            status_persona_id=status_persona_id,
            sede_id=sede_id,
            fecha_incorporacion=fecha_incorporacion,
        )
        db.add(persona_afiliacion)
    else:
        persona_afiliacion.status_persona_id = status_persona_id
        persona_afiliacion.sede_id = sede_id
        if fecha_incorporacion:
            persona_afiliacion.fecha_incorporacion = fecha_incorporacion


def _upsert_estudiante_info(db: Session, cedula: str, afiliacion_id: int, carrera_codigo: int):
    estudiante_info = db.query(EstudianteInfo).filter(
        EstudianteInfo.persona_tiene_afiliacion_persona_cedula == cedula,
        EstudianteInfo.persona_tiene_afiliacion_afiliacion_id == afiliacion_id,
    ).first()
    if not estudiante_info:
        estudiante_info = EstudianteInfo(
            persona_tiene_afiliacion_persona_cedula=cedula,
            persona_tiene_afiliacion_afiliacion_id=afiliacion_id,
            carrera_codigo=carrera_codigo,
        )
        db.add(estudiante_info)
    else:
        estudiante_info.carrera_codigo = carrera_codigo


def _upsert_trabajador_info(db: Session, cedula: str, afiliacion_id: int, row: Dict[str, str]):
    trabajador_info = db.query(TrabajadorInfo).filter(
        TrabajadorInfo.persona_tiene_afiliacion_persona_cedula == cedula,
        TrabajadorInfo.persona_tiene_afiliacion_afiliacion_id == afiliacion_id,
    ).first()

    codtpe_raw = (row.get("CODTPE", "") or "").strip()
    codtpe = int(codtpe_raw) if codtpe_raw.isdigit() else 0

    if not trabajador_info:
        trabajador_info = TrabajadorInfo(
            persona_tiene_afiliacion_persona_cedula=cedula,
            persona_tiene_afiliacion_afiliacion_id=afiliacion_id,
            codtpe=codtpe,
        )
        db.add(trabajador_info)
    else:
        trabajador_info.codtpe = codtpe


def _normalize_header(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").strip())
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    upper = without_accents.upper()
    chars = [ch if ch.isalnum() else "_" for ch in upper]
    compact = "".join(chars)
    while "__" in compact:
        compact = compact.replace("__", "_")
    return compact.strip("_")


def _qr_url_for(carnet_uuid: str, request: Request | None = None) -> str:
    configured_base_url = os.getenv("QR_BASE_URL", "").strip()

    if configured_base_url:
        if configured_base_url.startswith("http://") or configured_base_url.startswith("https://"):
            base_url = configured_base_url
        elif request:
            base_url = f"{str(request.base_url).rstrip('/')}{configured_base_url if configured_base_url.startswith('/') else f'/{configured_base_url}'}"
        else:
            base_url = f"http://localhost:8000/{configured_base_url.lstrip('/')}"
    elif request:
        base_url = f"{str(request.base_url).rstrip('/')}/carnets/qr"
    else:
        base_url = "http://localhost:8000/carnets/qr"

    return f"{base_url.rstrip('/')}/{carnet_uuid}"


def _generate_qr_png_bytes(carnet_uuid: str, request: Request | None = None) -> bytes:
    qr = qrcode.make(_qr_url_for(carnet_uuid, request))
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()


def _parse_csv(contents: bytes) -> Tuple[List[Dict[str, str]], List[str]]:
    text = contents.decode("utf-8-sig")
    if not text.strip():
        return [], []

    delimiter = "," if text.count(",") >= text.count(";") else ";"
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        return [], []

    columns = [_normalize_header(col) for col in reader.fieldnames]
    rows = []
    for raw_row in reader:
        row = {_normalize_header(key): (value or "").strip() for key, value in raw_row.items()}
        rows.append(row)

    return rows, columns


@router.post(
    "/carnets/import/estudiantes",
    dependencies=[
        Depends(require_permission("carnet.crear")),
        Depends(require_permission("afiliacion.gestionar")),
        Depends(require_permission("carrera.asignar")),
    ],
)
async def import_carnets_estudiantes(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    rows, columns = _parse_csv(contents)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo esta vacio o no tiene encabezados",
        )

    columns_set = set(columns)
    missing_student = REQUIRED_COLUMNS_STUDENT - columns_set
    if missing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faltan columnas para estudiantes: {', '.join(sorted(missing_student))}",
        )

    status_id = _get_active_status_id(db)
    status_persona_id = _get_status_persona_activo_id(db)
    afiliacion_estudiante = _get_or_create_afiliacion(db, "Estudiante", default_vigencia=6)
    sede_default = db.query(Sede).first()
    if not sede_default:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe ninguna sede en BD")

    errors = []
    created = 0
    updated = 0

    for index, row in enumerate(rows, start=2):
        try:
            usbid = row.get("CARNET", "")
            cedula = row.get("CEDULA_ESTUDIANTE", "")
            nombres = row.get("NOMBRES_ESTUDIANTE", "")
            apellidos = row.get("APELLIDOS_ESTUDIANTE", "")
            sexo = _normalize_sexo(row.get("SEXO", ""))
            carrera_codigo = _get_carrera_codigo(db, row.get("CARRERA", ""))

            if not all([usbid, cedula, nombres, apellidos]):
                raise ValueError("Campos requeridos vacios")
            if len(usbid) > 10:
                raise ValueError("CARNET excede longitud maxima de 10")

            carnet_uuid = _build_carnet_uuid(usbid, cedula)
            fecha_emision = date.today()
            fecha_vencimiento = _add_years(fecha_emision, 6)

            carnet = db.query(Carnet).filter(Carnet.usbid == usbid).first()
            if not carnet:
                carnet = Carnet(
                    usbid=usbid,
                    uuid=carnet_uuid,
                    status_carnet_id=status_id,
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_vencimiento,
                )
                db.add(carnet)
                created += 1
            else:
                carnet.uuid = carnet_uuid
                carnet.status_carnet_id = status_id
                carnet.fecha_emision = fecha_emision
                carnet.fecha_vencimiento = fecha_vencimiento
                updated += 1

            _upsert_persona(db, cedula, usbid, nombres, apellidos, sexo)
            _upsert_persona_afiliacion(
                db=db,
                cedula=cedula,
                afiliacion_id=afiliacion_estudiante.id,
                status_persona_id=status_persona_id,
                sede_id=sede_default.id,
                fecha_incorporacion=fecha_emision,
            )
            _upsert_estudiante_info(db, cedula, afiliacion_estudiante.id, carrera_codigo)

        except Exception as exc:
            errors.append({"line": index, "error": str(exc)})

    db.commit()

    return {
        "status": "success",
        "tipo_importacion": "estudiantes",
        "created": created,
        "updated": updated,
        "errors": errors,
    }


@router.post(
    "/carnets/import/personal",
    dependencies=[
        Depends(require_permission("carnet.crear")),
        Depends(require_permission("afiliacion.gestionar")),
        Depends(require_permission("departamento.asignar")),
    ],
)
async def import_carnets_personal(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    rows, columns = _parse_csv(contents)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo esta vacio o no tiene encabezados",
        )

    columns_set = set(columns)
    missing_personal = REQUIRED_COLUMNS_PERSONAL - columns_set
    if missing_personal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faltan columnas para personal: {', '.join(sorted(missing_personal))}",
        )

    status_id = _get_active_status_id(db)
    status_persona_id = _get_status_persona_activo_id(db)

    errors = []
    created = 0
    updated = 0

    for index, row in enumerate(rows, start=2):
        try:
            cedula = row.get("NO_DE_DOCUMENTO", "")
            primer_nombre = row.get("PRIMER_NOMBRE", "")
            segundo_nombre = row.get("SEGUNDO_NOMBRE", "")
            primer_apellido = row.get("PRIMER_APELLIDO", "")
            segundo_apellido = row.get("SEGUNDO_APELLIDO", "")
            sede_id = _get_sede_id(db, row.get("SEDE", ""))
            fecha_ingreso = _parse_date(row.get("FECHA_DE_INGRESO", ""))

            nombres = " ".join(part for part in [primer_nombre, segundo_nombre] if part).strip()
            apellidos = " ".join(part for part in [primer_apellido, segundo_apellido] if part).strip()
            if not all([cedula, nombres, apellidos]):
                raise ValueError("Campos requeridos vacios")

            usbid = row.get("CARNET", "") or cedula
            if len(usbid) > 10:
                raise ValueError("CARNET/identificador excede longitud maxima de 10")

            tipo_personal = row.get("TIPO_DE_PERSONAL", "")
            afiliacion = _get_or_create_afiliacion(db, tipo_personal)
            if not afiliacion.duracion_vigencia_anos:
                raise ValueError(f"La afiliacion '{afiliacion.nombre}' no tiene duracion_vigencia_anos")

            fecha_emision = fecha_ingreso
            fecha_vencimiento = _add_years(fecha_ingreso, int(afiliacion.duracion_vigencia_anos))

            sexo_raw = row.get("SEXO", "")
            sexo = _normalize_sexo(sexo_raw) if sexo_raw else None

            carnet_uuid = _build_carnet_uuid(usbid, cedula)
            carnet = db.query(Carnet).filter(Carnet.usbid == usbid).first()
            if not carnet:
                carnet = Carnet(
                    usbid=usbid,
                    uuid=carnet_uuid,
                    status_carnet_id=status_id,
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_vencimiento,
                )
                db.add(carnet)
                created += 1
            else:
                carnet.uuid = carnet_uuid
                carnet.status_carnet_id = status_id
                carnet.fecha_emision = fecha_emision
                carnet.fecha_vencimiento = fecha_vencimiento
                updated += 1

            _upsert_persona(db, cedula, usbid, nombres, apellidos, sexo)
            _upsert_persona_afiliacion(
                db=db,
                cedula=cedula,
                afiliacion_id=afiliacion.id,
                status_persona_id=status_persona_id,
                sede_id=sede_id,
                fecha_incorporacion=fecha_ingreso,
            )
            _upsert_trabajador_info(db, cedula, afiliacion.id, row)

        except Exception as exc:
            errors.append({"line": index, "error": str(exc)})

    db.commit()

    return {
        "status": "success",
        "tipo_importacion": "personal",
        "created": created,
        "updated": updated,
        "errors": errors,
    }


@router.post(
    "/carnets/import",
    dependencies=[
        Depends(require_permission("carnet.crear")),
        Depends(require_permission("afiliacion.gestionar")),
        Depends(require_permission("carrera.asignar")),
    ],
)
async def import_carnets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await import_carnets_estudiantes(file=file, db=db)


@router.get(
    "/carnets/{usbid}/qr",
    dependencies=[Depends(require_permission("qr.generar"))],
)
def get_qr(usbid: str, request: Request, db: Session = Depends(get_db)):
    carnet = db.query(Carnet).filter(Carnet.usbid == usbid).first()
    if not carnet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carnet no encontrado")

    qr_bytes = _generate_qr_png_bytes(carnet.uuid, request)
    return StreamingResponse(io.BytesIO(qr_bytes), media_type="image/png")


@router.get(
    "/carnets/qr/{uuid}",
    dependencies=[Depends(require_permission("qr.leer"))],
)
def scan_qr(uuid: str, db: Session = Depends(get_db)):
    carnet = db.query(Carnet).filter(Carnet.uuid == uuid).first()
    if not carnet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UUID invalido")

    persona = db.query(Persona).filter(Persona.carnet_usbid == carnet.usbid).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UUID no valido: no se encontro persona asociada al carnet.",
        )

    return {
        "status": "success",
        "data": {
            "carnet": {
                "usbid": carnet.usbid,
                "uuid": carnet.uuid,
                "status_carnet_id": carnet.status_carnet_id,
            },
            "persona": {
                "cedula": persona.cedula,
                "nombres": persona.nombres,
                "apellidos": persona.apellidos,
                "sexo": persona.sexo.value,
            },
        },
    }
