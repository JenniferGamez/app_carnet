import configparser
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
ruta_ini = os.path.join(base_dir, 'config.ini')

# Inicializar el lector de configuración
config = configparser.ConfigParser()

if not os.path.exists(ruta_ini):
    print(f" [x] Error: No se encontró el archivo {ruta_ini}")
    sys.exit(1)
    
config.read(ruta_ini)

def get_mongo_uri():
    try:
        host = config['MongoDB']['host']
        port = config['MongoDB']['port']
        db_name = config['MongoDB']['name']
        user = config['MongoDB'].get('username')
        password = config['MongoDB'].get('password')

        auth_db = config['MongoDB'].get('auth_db', 'admin')

        if user and password:
            return f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource={auth_db}"
        
        return f"mongodb://{host}:{port}/{db_name}"
        
    except Exception as e:
        print(f" [x] Error al conectar a MongoDB: {e}")
        sys.exit(1)

def get_auth_config():
    return {
        "SECRET_KEY": config['Auth']['SECRET_KEY'].replace('"', ''),
        "ALGORITHM": config['Auth']['ALGORITHM'].replace('"', '')
    }
    
def get_internal_token():
    return config['Auth']['API_INTERNAL_TOKEN'].replace('"', '')