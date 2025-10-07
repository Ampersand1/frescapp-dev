#!/bin/bash

# ==========================================
#  Frescapp - Development Environment Script
#  Inicia backend (Flask) y frontend (Angular Admin)
# ==========================================

# --- Configuración de entorno ---
PROJECT_PATH=$(pwd)
BACKEND_PATH="$PROJECT_PATH/admin/backend"
ADMIN_PATH="$PROJECT_PATH/admin/app-admin"

echo "📦 Iniciando entorno de desarrollo Frescapp..."
echo "Ubicación actual: $PROJECT_PATH"

# --- Liberar puertos usados (opcional) ---
PORTS=(5000 4200)
for PORT in "${PORTS[@]}"; do
  PID=$(lsof -t -i:$PORT)
  if [ -n "$PID" ]; then
    echo "⚠️  Liberando puerto $PORT (PID $PID)..."
    kill -9 $PID
  fi
done

# --- Iniciar Backend (Flask) ---
echo "🚀 Iniciando backend Flask en el puerto 5000..."
cd "$BACKEND_PATH" || exit

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
  source .venv/bin/activate
  echo "🟢 Entorno virtual activado (.venv)"
fi

# Ejecutar backend
nohup flask run --host=0.0.0.0 --port=5000 > backend-dev.log 2>&1 &
BACK_PID=$!
echo "✅ Backend iniciado (PID $BACK_PID)"
cd "$PROJECT_PATH" || exit

# --- Iniciar Admin (Angular) ---
echo "💻 Iniciando Angular Admin en el puerto 4200..."
cd "$ADMIN_PATH" || exit
nohup npm start > admin-dev.log 2>&1 &
ADMIN_PID=$!
echo "✅ Admin iniciado (PID $ADMIN_PID)"
cd "$PROJECT_PATH" || exit

# --- Resumen ---
echo ""
echo "=========================================="
echo "✅ Frescapp entorno de desarrollo iniciado"
echo "Backend Flask: http://localhost:5000"
echo "Admin Angular: http://localhost:4200"
echo "Logs: backend-dev.log / admin-dev.log"
echo "=========================================="
