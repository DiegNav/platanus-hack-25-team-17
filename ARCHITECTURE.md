# 🏗️ Arquitectura de Platanus

Este documento describe la arquitectura y patrones de diseño utilizados en Platanus.

## 📐 Arquitectura General

Platanus sigue una **arquitectura en capas** (Layered Architecture) con separación de responsabilidades:

```
┌─────────────────────────────────────┐
│     API Layer (FastAPI Routes)     │  ← HTTP Endpoints
├─────────────────────────────────────┤
│       Service Layer (Business)      │  ← Business Logic
├─────────────────────────────────────┤
│      CRUD Layer (Data Access)       │  ← Database Operations
├─────────────────────────────────────┤
│    Models Layer (ORM Entities)      │  ← SQLAlchemy Models
├─────────────────────────────────────┤
│         Database (PostgreSQL)       │  ← Data Storage
└─────────────────────────────────────┘
```

## 🔄 Flujo de una Request

```
1. HTTP Request
   ↓
2. FastAPI Middleware (logging, error handling)
   ↓
3. Router Endpoint (api/v1/endpoints/)
   ↓
4. Dependency Injection (get_db, authentication, etc.)
   ↓
5. Service Layer (business logic, validation)
   ↓
6. CRUD Layer (database operations)
   ↓
7. SQLAlchemy Model (ORM)
   ↓
8. Database (PostgreSQL)
   ↓
9. Response with Pydantic Schema
   ↓
10. HTTP Response
```

## 📂 Estructura de Capas

### 1. API Layer (`app/api/`)

**Responsabilidad**: Manejo de HTTP requests/responses

- Define endpoints y rutas
- Validación de entrada con Pydantic
- Serialización de respuestas
- Dependency Injection
- Documentación OpenAPI

```python
# Ejemplo: app/api/v1/endpoints/users.py
@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.create_user(db, user_in)
```

### 2. Service Layer (`app/services/`)

**Responsabilidad**: Lógica de negocio

- Validaciones de negocio
- Operaciones complejas
- Coordinación entre múltiples CRUDs
- Transacciones
- Casos de uso

```python
# Ejemplo: app/services/user_service.py
class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate):
        # Business logic
        if await user_crud.get_by_email(db, email=user_in.email):
            raise ValueError("Email already exists")

        return await user_crud.create(db, obj_in=user_in)
```

### 3. CRUD Layer (`app/crud/`)

**Responsabilidad**: Operaciones de base de datos

- Create, Read, Update, Delete
- Queries específicas
- Sin lógica de negocio
- Reutilizable

```python
# Ejemplo: app/crud/base.py
class CRUDBase:
    async def get(self, db: AsyncSession, id: int):
        result = await db.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalar_one_or_none()
```

### 4. Models Layer (`app/models/`)

**Responsabilidad**: Definición de entidades de base de datos

- SQLAlchemy ORM models
- Relaciones entre tablas
- Constraints y validaciones de DB

```python
# Ejemplo: app/models/user.py
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

### 5. Schemas Layer (`app/schemas/`)

**Responsabilidad**: Validación y serialización de datos

- Pydantic models
- Request validation
- Response serialization
- Type safety

```python
# Ejemplo: app/schemas/user.py
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
```

## 🎯 Patrones de Diseño

### 1. Repository Pattern (CRUD)

Abstrae el acceso a datos con una interfaz genérica.

**Ventajas:**
- Reutilización de código
- Fácil testing con mocks
- Cambio de base de datos transparente

### 2. Service Layer Pattern

Encapsula lógica de negocio separada de la API.

**Ventajas:**
- Lógica reutilizable
- Testing independiente
- Clara separación de responsabilidades

### 3. Dependency Injection

FastAPI inyecta dependencias automáticamente.

**Ventajas:**
- Código desacoplado
- Testing simplificado
- Gestión automática de recursos

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/users/")
async def list_users(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_multi(db)
```

### 4. Factory Pattern (Database)

Creación centralizada de sesiones de base de datos.

```python
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### 5. Middleware Pattern

Procesamiento de requests/responses de forma transversal.

```python
@app.middleware("http")
async def logging_middleware(request, call_next):
    # Pre-processing
    response = await call_next(request)
    # Post-processing
    return response
```

## 🔐 Seguridad

### Password Hashing

```python
# app/core/security.py
pwd_context = CryptContext(schemes=["bcrypt"])

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### JWT Tokens

```python
def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
```

## 📊 Base de Datos

### Async SQLAlchemy

Toda la interacción con la base de datos es asíncrona:

```python
# Async engine
engine = create_async_engine(DATABASE_URL)

# Async session
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Migraciones con Alembic

```bash
# Crear migración
alembic revision --autogenerate -m "description"

# Aplicar migraciones
alembic upgrade head

# Revertir
alembic downgrade -1
```

## 🧪 Testing

### Test Isolation

Cada test tiene su propia transacción:

```python
@pytest.fixture
async def db_session():
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

### Test Client

Cliente HTTP para tests de integración:

```python
async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
```

## 📝 Logging

Sistema de logging estructurado:

```python
# Console + File logging
setup_logging()

# Usage
logger = get_logger(__name__)
logger.info("User created", extra={"user_id": user.id})
```

## 🔄 Manejo de Errores

### Global Error Handler

```python
@app.middleware("http")
async def error_handler_middleware(request, call_next):
    try:
        return await call_next(request)
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
```

### Custom Exceptions

```python
class UserNotFoundError(Exception):
    pass

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "User not found"}
    )
```

## 🚀 Performance

### Async All The Way

- Async FastAPI
- Async SQLAlchemy
- Async database driver (asyncpg)
- Non-blocking I/O

### Connection Pooling

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # Pool size
    max_overflow=20,     # Max connections
    pool_pre_ping=True,  # Check connections
)
```

### Caching (Ready to implement)

El proyecto está listo para agregar caching:

```python
from functools import lru_cache

@lru_cache()
async def get_user_by_id(user_id: int):
    # Cached function
    pass
```

## 📚 Documentación API

### OpenAPI + Scalar

```python
app = FastAPI(
    title="Platanus API",
    version="0.1.0",
    docs_url=None,  # Disable default
    openapi_url="/openapi.json",
)

# Custom Scalar endpoint
@app.get("/docs")
async def scalar_html():
    return HTMLResponse(scalar_template)
```

### Rich Metadata

```python
@router.post(
    "/users/",
    response_model=User,
    status_code=201,
    summary="Create user",
    description="Detailed description...",
    response_description="Created user",
    tags=["Users"],
)
```

## 🔧 Configuración

### Pydantic Settings

```python
class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

## 🐳 Docker

### Multi-service Setup

```yaml
services:
  db:
    image: postgres:16
  api:
    build: .
    depends_on:
      - db
```

## 📈 Escalabilidad

### Horizontal Scaling

- Stateless API (ready for multiple instances)
- Database connection pooling
- Async I/O para alta concurrencia

### Vertical Scaling

- Uvicorn workers
- Connection pool tuning

```bash
uvicorn app.main:app --workers 4
```

## 🎯 Principios SOLID

### Single Responsibility

Cada clase tiene una única responsabilidad:
- Models: Definición de entidades
- CRUD: Operaciones de DB
- Services: Lógica de negocio
- Routers: HTTP handling

### Open/Closed

Extensible sin modificar código existente:
- CRUD genérico heredable
- Middleware pluggable

### Liskov Substitution

Los tipos derivados son sustituibles:
- CRUDBase puede ser reemplazado por CRUDUser

### Interface Segregation

Interfaces específicas, no genéricas:
- Dependency injection con interfaces claras

### Dependency Inversion

Depender de abstracciones:
- Services usan CRUD interfaces
- API usa Service interfaces

## 🔄 Extensibilidad

### Agregar un Nuevo Recurso

1. Crear model en `app/models/`
2. Crear schemas en `app/schemas/`
3. Crear CRUD en `app/crud/`
4. Crear service en `app/services/`
5. Crear endpoints en `app/api/v1/endpoints/`
6. Registrar router en `app/api/v1/router.py`
7. Crear migración con Alembic

### Agregar Autenticación

1. Implementar endpoint de login
2. Crear dependency `get_current_user`
3. Usar dependency en endpoints protegidos

```python
@router.get("/protected")
async def protected_route(
    user: User = Depends(get_current_user)
):
    return {"user": user}
```

## 📖 Referencias

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

**Este documento es living documentation. Actualízalo cuando cambies la arquitectura.**
