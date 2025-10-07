#!/bin/bash

# Puertos a liberar
PORTS=(5000 80)

# Función para terminar procesos en un puerto dado
terminate_process_on_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo "Terminando proceso en el puerto $PORT con PID $PID..."
        sudo kill -9 $PID
        echo "Proceso terminado."
    else
        echo "No hay procesos ejecutándose en el puerto $PORT."
    fi
}

# Liberar los puertos
for PORT in "${PORTS[@]}"; do
    terminate_process_on_port $PORT
done

# Iniciar la aplicación Python en el puerto 5000
echo "Iniciando el backend en el puerto 5000..."
cd /home/ubuntu/frescapp/admin/backend || exit
nohup python3 app.py > backend.log 2>&1 &

# Iniciar la aplicación Angular en el puerto 80
echo "Iniciando admin en el puerto 80..."
cd /home/ubuntu/frescapp/admin/app-admin/dist/app-admin || exit
sudo nohup http-server -p 80 --proxy http://localhost:80? > admin.log 2>&1 &

echo "Todas las aplicaciones han sido iniciadas."
