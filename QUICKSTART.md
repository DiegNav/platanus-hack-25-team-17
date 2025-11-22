# 🚀 Guía de Inicio Rápido - Platanus

Esta guía te llevará desde cero a tener tu API funcionando en 5 minutos.

## ⚡ Opción 1: Docker (Recomendado)

### 1. Clonar y configurar

```bash
git clone <your-repo>
cd platanus
cp .env.example .env
```

### 2. Iniciar todo con Docker

```bash
docker-compose up -d
```

### 3. Ejecutar migraciones

```bash
docker-compose exec api alembic upgrade head
```

### 4. (Opcional) Crear datos de ejemplo

```bash
docker-compose exec api python scripts/init_db.py
```

### 5. ¡Listo! Accede a la documentación

Abre tu navegador en: http://localhost:8000/docs

**Credenciales de prueba:**
- Admin: `admin@platanus.com` / `admin123`
- User: `user@platanus.com` / `user123`

---

## 💻 Opción 2: Instalación Local

### Prerequisitos

- Python 3.11+
- PostgreSQL 13+
- Poetry (opcional pero recomendado)

### 1. Instalar PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# O con Docker
docker run -d \
  --name platanus_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=platanus_db \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. Clonar y configurar entorno

```bash
git clone <your-repo>
cd platanus

# Copiar variables de entorno
cp .env.example .env

# Editar .env y configurar DATABASE_URL si es necesario
nano .env
```

### 3. Instalar dependencias

```bash
# Con Poetry (recomendado)
pip install poetry
poetry install

# O con pip
pip install -r requirements.txt  # (debes generar este archivo)
```

### 4. Ejecutar migraciones

```bash
# Con Poetry
poetry run alembic upgrade head

# O activando el virtualenv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
alembic upgrade head
```

### 5. (Opcional) Crear datos de ejemplo

```bash
poetry run python scripts/init_db.py
```

### 6. Iniciar el servidor

```bash
# Con make
make run

# O directamente
poetry run uvicorn app.main:app --reload

# O con uvicorn si activaste el venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. ¡Listo! Accede a la documentación

Abre tu navegador en: http://localhost:8000/docs

---

## 🧪 Verificar que Todo Funciona

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T...",
  "version": "0.1.0",
  "environment": "development",
  "database": "healthy"
}
```

### 2. Crear un Usuario

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 3. Listar Usuarios

```bash
curl http://localhost:8000/api/v1/users/
```

### 4. O usa la UI de Scalar

Ve a http://localhost:8000/docs y prueba los endpoints interactivamente.

---

## 📚 Próximos Pasos

### Explorar la Documentación

- **Scalar UI**: http://localhost:8000/docs (Moderna e interactiva)
- **ReDoc**: http://localhost:8000/redoc (Alternativa)
- **OpenAPI JSON**: http://localhost:8000/openapi.json (Raw schema)

### Entender la Estructura

```
app/
├── main.py           # Punto de entrada
├── config/           # Configuración
├── core/             # Database, security, logging
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── crud/             # Database operations
├── services/         # Business logic
├── api/
│   └── v1/
│       └── endpoints/  # API routes
└── middleware/       # Middlewares
```

### Crear tu Primer Endpoint

1. **Define el modelo** en `app/models/`
2. **Crea el schema** en `app/schemas/`
3. **Implementa CRUD** en `app/crud/`
4. **Añade lógica** en `app/services/`
5. **Crea endpoint** en `app/api/v1/endpoints/`
6. **Registra router** en `app/api/v1/router.py`

### Ejemplo Rápido: Endpoint de "Tasks"

1. **Modelo** (`app/models/task.py`):
```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    completed: Mapped[bool] = mapped_column(default=False)
```

2. **Schema** (`app/schemas/task.py`):
```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str

class Task(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}
```

3. **CRUD** (`app/crud/task.py`):
```python
from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

task = CRUDBase[Task, TaskCreate, TaskUpdate](Task)
```

4. **Endpoint** (`app/api/v1/endpoints/tasks.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.crud.task import task

router = APIRouter()

@router.get("/")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    return await task.get_multi(db)

@router.post("/")
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task.create(db, obj_in=task_in)
```

5. **Registrar** (`app/api/v1/router.py`):
```python
from app.api.v1.endpoints import tasks

api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
```

6. **Crear migración**:
```bash
make migrate msg="add tasks table"
make upgrade
```

---

## 🛠️ Comandos Útiles

```bash
# Desarrollo
make run          # Iniciar servidor con hot-reload
make test         # Ejecutar tests
make lint         # Verificar código
make format       # Formatear código

# Base de datos
make migrate msg="description"  # Nueva migración
make upgrade                     # Aplicar migraciones
make downgrade                   # Revertir última migración

# Docker
make docker-up    # Iniciar containers
make docker-down  # Detener containers
make docker-logs  # Ver logs
```

---

## 🐛 Solución de Problemas

### Error de conexión a base de datos

```bash
# Verificar que PostgreSQL está corriendo
docker ps  # Si usas Docker
# O
sudo systemctl status postgresql  # Linux

# Verificar DATABASE_URL en .env
cat .env | grep DATABASE_URL
```

### Error al instalar dependencias

```bash
# Asegúrate de tener Python 3.11+
python --version

# Actualizar pip y poetry
pip install --upgrade pip poetry

# Reinstalar dependencias
poetry install
```

### Puerto 8000 ya en uso

```bash
# Cambiar puerto en comando
uvicorn app.main:app --reload --port 8001

# O matar el proceso usando el puerto
lsof -ti:8000 | xargs kill -9  # Linux/Mac
```

### Migraciones no se aplican

```bash
# Verificar estado de migraciones
alembic current

# Ver historial
alembic history

# Resetear (CUIDADO: borra datos)
alembic downgrade base
alembic upgrade head
```

---

## 💡 Tips

1. **Usa make**: `make run`, `make test`, etc. para comandos comunes
2. **Hot reload**: El servidor se recarga automáticamente en cambios
3. **Logs**: Revisa `logs/app.log` para debugging
4. **Tests**: Ejecuta tests frecuentemente con `make test`
5. **Documentación**: Explora la UI de Scalar, es muy potente
6. **Pre-commit**: Instala hooks con `make dev` para calidad de código

---

## 📖 Recursos

- **README.md**: Documentación completa
- **CONTRIBUTING.md**: Guía para contribuir
- **Código**: Todo está comentado y con type hints
- **Tests**: En `tests/` como ejemplos

---

## 🎉 ¡Ya Estás Listo!

Ahora tienes una API FastAPI moderna y production-ready.

**Recursos útiles:**
- 📚 [FastAPI Docs](https://fastapi.tiangolo.com/)
- 🗄️ [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- ✅ [Pydantic Docs](https://docs.pydantic.dev/)
- 🔄 [Alembic Docs](https://alembic.sqlalchemy.org/)

**¿Preguntas?** Abre un issue en GitHub.

**¡Happy Coding! 🚀**
