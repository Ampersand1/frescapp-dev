import os

class Config:
    # Clave secreta para proteger las sesiones de usuario
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_predeterminada'

    # Configuración de la base de datos MongoDB
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGODB_URI') or 'mongodb://localhost/frescapp'
    }

    # Otras configuraciones opcionales pueden agregarse aquí
