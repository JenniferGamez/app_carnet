import sys
from pymongo import MongoClient
import os

try:
    from config import config, get_mongo_uri
except ImportError:
    from gateway.config import config, get_mongo_uri

try:
    uri = get_mongo_uri()
    db_name = config['MongoDB']['name']
    client = MongoClient(uri)
    db = client[db_name]
    
    client.admin.command('ping')
    print(f" [Ok] [Server-DB] Conectado exitosamente a MongoDB: {db_name}")
    
except Exception as e:
    print(f" [x] [Server-DB] Error al conectar a MongoDB: {e}")
    sys.exit(1)


# Colecciones
usuarios_col = db['users']