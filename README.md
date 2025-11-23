# 💰 CoBrot

**Gestión inteligente de gastos grupales mediante WhatsApp**

<img src="./project-logo.png" alt="CoBrot Logo" width="200" />

---

## 📋 Sobre el Proyecto

**CoBrot** es una aplicación fintech que permite a grupos de personas gestionar sus gastos compartidos de manera fácil y segura mediante WhatsApp. Olvídate de las complicadas hojas de cálculo y las discusiones sobre quién debe qué. Con CoBrot, simplemente envía una foto de tu boleta o comando por WhatsApp y el sistema se encarga del resto.

### 🎯 El Problema que Resolvemos

¿Alguna vez has salido con amigos y alguien pagó la cuenta completa? ¿Te ha costado recordar quién pidió qué y cuánto debe cada uno? CoBrot resuelve estos problemas comunes:

- ✅ **División automática de gastos**: Envía una foto de la boleta y el sistema extrae automáticamente todos los items
- ✅ **Asignación inteligente**: Usa comandos en lenguaje natural para asignar items a personas ("Juan paga la cerveza")
- ✅ **Seguimiento de deudas**: Consulta en cualquier momento cuánto debes y a quién
- ✅ **Procesamiento de pagos**: Registra transferencias y el sistema las asocia automáticamente a tus deudas
- ✅ **Todo desde WhatsApp**: Sin necesidad de instalar apps adicionales

---

## ✨ Características Principales

### 🤖 Agente de Inteligencia Artificial
- Procesa comandos en lenguaje natural en español
- Entiende intenciones como "crear sesión", "asignar item", "consultar deudas"
- Extrae información estructurada de mensajes informales

### 📸 Reconocimiento Óptico de Caracteres (OCR)
- Extrae automáticamente items, montos y detalles de boletas
- Clasifica documentos (boletas vs comprobantes de transferencia)
- Procesa imágenes enviadas por WhatsApp

### 💬 Integración con WhatsApp
- Interfaz completamente basada en WhatsApp mediante Kapso API
- Notificaciones automáticas a todos los participantes
- Enlaces a sesiones para unirse fácilmente

### 📊 Gestión de Sesiones
- Crea sesiones para eventos grupales (cena, viaje, salida, etc.)
- Múltiples usuarios pueden unirse a una sesión
- Seguimiento de facturas e items por sesión
- Cierre de sesión con resumen de deudas

### 💳 Sistema de Pagos
- Asignación de items a usuarios específicos
- Cálculo automático de deudas
- Procesamiento de transferencias bancarias
- Matching inteligente de pagos con deudas pendientes

### 🌐 Dashboard Web
- Interfaz web moderna construida con Next.js
- Visualización de sesiones y estados de pago
- Diseño responsive y accesible

---

## 🏗️ Arquitectura Técnica

### Backend
- **FastAPI**: Framework web asíncrono de alto rendimiento
- **SQLAlchemy 2.0**: ORM con soporte async/await
- **PostgreSQL**: Base de datos relacional
- **Alembic**: Migraciones de base de datos
- **LangChain + OpenAI**: Procesamiento de lenguaje natural y OCR
- **Pydantic v2**: Validación de datos y configuración

### Frontend
- **Next.js 16**: Framework React con App Router
- **TypeScript**: Tipado estático
- **Tailwind CSS**: Estilos modernos y responsive
- **Radix UI**: Componentes accesibles

### Integraciones
- **Kapso API**: Integración con WhatsApp
- **OpenAI API**: Procesamiento de imágenes y texto
- **Google Gemini**: Alternativa para procesamiento de IA

### Infraestructura
- **Docker & Docker Compose**: Containerización
- **Alembic**: Versionado de base de datos
- **Logging estructurado**: Sistema de logs completo

---

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.12+
- PostgreSQL 13+
- Node.js 18+ (para frontend)
- Docker y Docker Compose (opcional pero recomendado)

### Opción 1: Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <repo-url>
cd platanus-hack-25-team-17
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales:
# - DATABASE_URL
# - SECRET_KEY
# - KAPSO_API_KEY, KAPSO_URL, KAPSO_PHONE_NUMBER_ID
# - OPENAI_API_KEY o GEMINI_API_KEY
```

3. **Iniciar servicios**
```bash
docker-compose up -d
```

4. **Ejecutar migraciones**
```bash
docker-compose exec api alembic upgrade head
```

5. **Acceder a la aplicación**
- API: http://localhost:8000
- Documentación API: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Opción 2: Instalación Local

#### Backend

1. **Instalar dependencias**
```bash
# Con uv (recomendado)
uv sync

# O con pip
pip install -e .
```

2. **Configurar base de datos**
```bash
# Crear base de datos PostgreSQL
createdb cobrot_db

# Configurar .env
cp .env.example .env
# Editar DATABASE_URL en .env
```

3. **Ejecutar migraciones**
```bash
alembic upgrade head
```

4. **Iniciar servidor**
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. **Instalar dependencias**
```bash
cd frontend
npm install
# o
pnpm install
```

2. **Iniciar servidor de desarrollo**
```bash
npm run dev
```

---

## 📚 Uso de la Aplicación

### Flujo Básico

1. **Crear una sesión**
   - Envía por WhatsApp: "Crear sesión para cena de cumpleaños"
   - El sistema crea una sesión y te envía un enlace para compartir

2. **Unirse a una sesión**
   - Comparte el enlace con tus amigos
   - Ellos envían el UUID de la sesión por WhatsApp

3. **Registrar una boleta**
   - Envía una foto de la boleta por WhatsApp
   - El sistema extrae automáticamente todos los items

4. **Asignar items**
   - Envía: "Juan paga la cerveza"
   - O: "La pizza es de María"
   - El sistema asigna los items automáticamente

5. **Consultar deudas**
   - Envía: "¿Cuánto debo?"
   - El sistema te muestra tus deudas pendientes

6. **Registrar un pago**
   - Envía una foto del comprobante de transferencia
   - El sistema lo procesa y actualiza tus deudas

7. **Cerrar sesión**
   - Envía: "Cerrar sesión"
   - El sistema genera un resumen final

### Comandos Disponibles

| Comando | Ejemplo |
|---------|---------|
| Crear sesión | "Crear sesión para cena" |
| Unirse a sesión | Enviar UUID de la sesión |
| Asignar item | "Juan paga cerveza" |
| Consultar deudas | "¿Cuánto debo?" |
| Registrar pago | Enviar foto de transferencia |
| Cerrar sesión | "Cerrar sesión" |

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_receipt_extraction.py
```

---

## 📖 Documentación de API

Una vez que el servidor esté corriendo, accede a:

- **Scalar UI**: http://localhost:8000/docs (Interfaz moderna e interactiva)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints Principales

- `GET /api/v1/sessions/` - Listar sesiones
- `GET /api/v1/sessions/{session_id}` - Obtener sesión
- `GET /api/v1/invoices/` - Listar facturas
- `GET /api/v1/items/` - Listar items
- `GET /api/v1/payments/` - Listar pagos
- `POST /webhooks/kapso` - Webhook de WhatsApp

Ver `API_ENDPOINTS.md` para documentación completa.

---

## 🛠️ Comandos Útiles

```bash
# Desarrollo
make run          # Iniciar servidor con hot-reload
make test         # Ejecutar tests
make lint         # Verificar código
make format       # Formatear código

# Base de datos
make migrate msg="description"  # Crear migración
make upgrade                     # Aplicar migraciones
make downgrade                   # Revertir migración

# Docker
make docker-up    # Iniciar containers
make docker-down  # Detener containers
make docker-logs  # Ver logs
```

---

## 🏛️ Arquitectura

CoBrot sigue una **arquitectura en capas** con separación clara de responsabilidades:

```
┌─────────────────────────────────────┐
│     API Layer (FastAPI Routes)     │
├─────────────────────────────────────┤
│       Service Layer (Business)      │
│  - Agent Processor                  │
│  - OCR Service                      │
│  - Payment Matcher                  │
├─────────────────────────────────────┤
│      CRUD Layer (Data Access)       │
├─────────────────────────────────────┤
│    Models Layer (ORM Entities)      │
├─────────────────────────────────────┤
│         Database (PostgreSQL)       │
└─────────────────────────────────────┘
```

Ver `ARCHITECTURE.md` para más detalles.

---

## 🔐 Seguridad

- **Password Hashing**: Bcrypt para almacenamiento seguro de contraseñas
- **JWT Tokens**: Autenticación basada en tokens (preparado)
- **Validación de datos**: Pydantic para validación automática
- **SQL Injection Protection**: SQLAlchemy ORM previene inyecciones
- **CORS configurado**: Control de orígenes permitidos

---

## 📊 Estado del Proyecto

### ✅ Completado

- [x] Integración con WhatsApp (Kapso)
- [x] OCR de boletas con IA
- [x] Agente de procesamiento de lenguaje natural
- [x] Sistema de sesiones y facturas
- [x] Asignación de items a usuarios
- [x] Procesamiento de transferencias
- [x] Matching de pagos con deudas
- [x] API REST completa
- [x] Dashboard web básico
- [x] Sistema de notificaciones

### 🚧 En Desarrollo

- [ ] Autenticación completa de usuarios
- [ ] Dashboard web avanzado
- [ ] Reportes y estadísticas
- [ ] Exportación de datos

---

## 👥 Equipo

**Team 17 - Platanus Hack 2025**

- **Joaquin Salas** ([@D3kai](https://github.com/D3kai))
- **Diego Navarrete** ([@DiegNav](https://github.com/DiegNav))
- **Christian Parra** ([@chrismethsillo](https://github.com/chrismethsillo))
- **Félix Melo** ([@Synxian](https://github.com/Synxian))

**Track**: 🛡️ Fintech + Digital Security

---

## 📝 Licencia

Este proyecto fue desarrollado para el Platanus Hack 2025.

---

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [LangChain](https://www.langchain.com/) - Framework para aplicaciones con LLM
- [Next.js](https://nextjs.org/) - Framework React
- [Kapso](https://kapso.cl/) - API de WhatsApp
- [OpenAI](https://openai.com/) - Modelos de IA
- [Platanus](https://platan.us/) - Organizadores del hackathon

---

## 📧 Contacto

Para preguntas o sugerencias sobre CoBrot, abre un issue en GitHub.

---

**¡Gracias por tu interés en CoBrot! 🚀**
