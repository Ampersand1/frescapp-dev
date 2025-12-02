import os

# URI local de MongoDB (ajústala según tu entorno)
MONGO_URI = os.getenv("MONGO_URI")

# Clave secreta para JWT, sesiones u otras operaciones seguras
SECRET_KEY = os.getenv("SECRET_KEY")

# Otras configuraciones posibles
DEBUG = True
