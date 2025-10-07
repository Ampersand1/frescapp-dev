# Frescapp 

Frescapp es una plataforma web orientada a la venta y administración de productos, con soporte para múltiples módulos:
- **Frontend de comprador** (Flutter Web)
- **Panel administrativo** (Angular)
- **Backend API** (Flask + MongoDB)

Actualmente, este repositorio está enfocado en el **desarrollo y despliegue de una nueva funcionalidad de descuentos**, que permite al administrador crear, editar y aplicar descuentos a productos visibles en la app del comprador.

---

## Tecnologías Principales

| Módulo | Framework / Lenguaje | Base de datos |
|---------|----------------------|----------------|
| Backend | Flask (Python) | MongoDB |
| Frontend Admin | Angular (TypeScript) | — |
| Frontend Cliente | Flutter (Dart) | — |

---

## Objetivo Actual (Octubre 2025)

Implementar un **módulo de descuentos** que:
- Permita crear, editar y eliminar descuentos desde el panel admin.
- Aplique descuentos activos al precio de los productos.
- Muestre precios modificados en la aplicación del comprador, en un nuevo apartado llamado Descuentos.
- Sincronice la información con la base de datos MongoDB.

---

## Configuración del Entorno Local

### Requisitos

| Herramienta | Versión mínima | Propósito |
|--------------|----------------|------------|
| **Python** | 3.9+ | Backend Flask |
| **Node.js** | 18+ | Angular admin |
| **Flutter SDK** | 3.0+ | App comprador |
| **MongoDB** | Local o Atlas | Base de datos |
| **Git** | — | Control de versiones |

---
### Para configurar variables de entorno
Pidele el archivo .env al desarrollador principal!

### Para correr el proyecto
#### ! Backend (Flask)
cd admin/backend

python -m venv .venv

source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install flask flask-cors pymongo flask-bcrypt requests reportlab openpyxl python-jose babel pytz

export FLASK_APP=app.py

export FLASK_ENV=development

flask run

#### ! Panel Admin (Angular)
cd admin/app-admin

npm install

ng serve

#### ! Frontend Cliente (Flutter Web)
cd frescapp_web

flutter pub get

flutter run -d chrome


## Licencia
Este proyecto es de uso interno con fines de desarrollo.
