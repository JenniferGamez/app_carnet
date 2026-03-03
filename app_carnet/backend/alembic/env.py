import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ---------------------------
# Configurar sys.path
# ---------------------------
# Agrega 'backend' al path para poder importar 'app.models.base'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# ---------------------------
# Cargar el .env externo
# ---------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        f"No se encontró DATABASE_URL en el .env. Revisar que {dotenv_path} exista y tenga la variable."
    )

# ---------------------------
# Configuración Alembic
# ---------------------------
config = context.config
fileConfig(config.config_file_name)

# ---------------------------
# Importar Base de SQLAlchemy
# ---------------------------
from app.models.base import Base
import app.models 
target_metadata = Base.metadata

# ---------------------------
# Funciones para migraciones
# ---------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------
# Ejecutar según el modo
# ---------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()