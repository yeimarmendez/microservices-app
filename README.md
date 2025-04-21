Descripción del Proyecto
Este proyecto implementa un sistema de microservicios con:

User Service: Gestión completa de usuarios (CRUD) con autenticación JWT

Order Service: Administración de pedidos relacionados con usuarios

Interfaces Web: Interfaces intuitivas para ambos servicios

PostgreSQL: Base de datos relacional para persistencia de datos

Docker: Containerización para fácil despliegue

Tecnologías Utilizadas
Backend: Python + Flask

Frontend: HTML + Jinja2

Base de datos: PostgreSQL

Containerización: Docker + Docker Compose

Orquestación: Kubernetes (opcional)

Requisitos Previos
Para ejecutar este proyecto necesitas:

Docker versión 20.10 o superior

Docker Compose versión 2.0 o superior

Git para clonar el repositorio

Instalación y Configuración
Clonar el repositorio:
git clone https://github.com/SantiagoLozanoGi/microservices-app.git
cd microservices-app
Construir e iniciar los contenedores:
docker compose up -d --build
Uso del Sistema
Acceso a las Interfaces Web
User Service: Disponible en http://localhost:5000

Usuario predeterminado: admin

Contraseña predeterminada: 12345

Order Service: Disponible en http://localhost:5001

API Endpoints
User Service (5000)
POST /api/v1/login - Autenticación

GET /api/v1/users - Listar usuarios

POST /api/v1/users - Crear usuario

PUT /api/v1/users/<id> - Actualizar usuario

DELETE /api/v1/users/<id> - Eliminar usuario

Order Service (5001)
GET /api/v1/orders - Listar órdenes

POST /api/v1/orders - Crear orden

PUT /api/v1/orders/<id> - Actualizar orden

DELETE /api/v1/orders/<id> - Eliminar orden

Estructura del Proyecto

microservices-app/
├── docker-compose.yml
├── kubernetes/
│   ├── order-deployment.yml
│   ├── order-service.yml
│   ├── user-deployment.yml
│   └── user-service.yml
├── order-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── templates/
│       └── orders/
│           ├── edit.html
│           ├── index.html
│           └── new.html
└── user-service/
    ├── app.py
    ├── Dockerfile
    ├── requirements.txt
    └── templates/
        ├── edit_user.html
        ├── index.html
        └── new_user.html
