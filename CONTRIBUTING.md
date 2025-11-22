# Contributing to Platanus

¡Gracias por tu interés en contribuir a Platanus! Este documento proporciona directrices para contribuir al proyecto.

## 🚀 Proceso de Desarrollo

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
git clone https://github.com/your-username/platanus.git
cd platanus
```

### 2. Setup del Entorno

```bash
# Instalar dependencias de desarrollo
make dev

# Esto instalará:
# - Todas las dependencias
# - Pre-commit hooks
# - Herramientas de desarrollo
```

### 3. Crear una Branch

```bash
git checkout -b feature/my-new-feature
# o
git checkout -b fix/bug-description
```

### 4. Hacer Cambios

- Escribe código siguiendo las convenciones del proyecto
- Añade tests para nuevas funcionalidades
- Actualiza documentación si es necesario

### 5. Verificar Calidad

```bash
# Formatear código
make format

# Ejecutar linters
make lint

# Ejecutar tests
make test
```

### 6. Commit

```bash
git add .
git commit -m "feat: add new feature"

# Los pre-commit hooks se ejecutarán automáticamente
```

### 7. Push y Pull Request

```bash
git push origin feature/my-new-feature
```

Luego crea un Pull Request en GitHub.

## 📝 Convenciones de Código

### Python Style Guide

- **Formateo**: Black con line length de 100
- **Linting**: Ruff con reglas estrictas
- **Type Hints**: Obligatorios en todas las funciones
- **Docstrings**: Google style para funciones públicas

### Ejemplo de Docstring

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        bool: Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formateo, sin cambios de código
- `refactor:` Refactorización de código
- `test:` Añadir o modificar tests
- `chore:` Mantenimiento, dependencias, etc.

Ejemplos:
```
feat: add user authentication endpoint
fix: resolve database connection leak
docs: update API documentation
test: add tests for user service
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
make test

# Tests específicos
poetry run pytest tests/test_users.py

# Con cobertura
poetry run pytest --cov=app
```

### Escribir Tests

- Tests en directorio `tests/`
- Usar pytest con fixtures en `conftest.py`
- Aim for >80% coverage
- Tests asíncronos con `pytest-asyncio`

Ejemplo:
```python
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    """Test user creation endpoint."""
    response = await client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
    })
    assert response.status_code == 201
```

## 📚 Documentación

### Actualizar Documentación

- Mantener README.md actualizado
- Docstrings en código
- OpenAPI descriptions en endpoints
- Ejemplos en CONTRIBUTING.md

### API Documentation

Cada endpoint debe tener:
- `summary`: Título corto
- `description`: Descripción detallada
- `response_description`: Descripción de respuesta
- `tags`: Categorización

```python
@router.post(
    "/users/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user with the provided information",
    response_description="The created user",
    tags=["Users"],
)
async def create_user(...):
    ...
```

## 🔍 Code Review

### Qué Buscamos

- ✅ Código limpio y legible
- ✅ Tests que pasan
- ✅ Type hints correctos
- ✅ Documentación actualizada
- ✅ Sin linter errors
- ✅ Cobertura de tests adecuada
- ✅ Performance considerations
- ✅ Security best practices

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Linters pass
- [ ] Tests pass
```

## 🐛 Reportar Bugs

### Template de Issue

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- FastAPI version: [e.g., 0.109.0]

**Additional context**
Any other context about the problem.
```

## 💡 Sugerir Features

### Template de Feature Request

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature.
```

## 🎯 Áreas para Contribuir

### Good First Issues

- Mejorar documentación
- Añadir tests
- Corregir typos
- Mejorar ejemplos

### Advanced Issues

- Nuevos endpoints
- Optimizaciones de performance
- Features de seguridad
- Integraciones

## 📞 Obtener Ayuda

- 💬 GitHub Discussions para preguntas
- 🐛 GitHub Issues para bugs
- 📧 Email para temas privados

## 📜 Código de Conducta

### Nuestro Compromiso

Crear un ambiente abierto y acogedor para todos.

### Estándares

✅ Usar lenguaje acogedor e inclusivo
✅ Respetar puntos de vista diferentes
✅ Aceptar críticas constructivas
✅ Enfocarse en lo mejor para la comunidad

❌ No usar lenguaje sexualizado
❌ No trolling o insultos
❌ No acoso público o privado

## 🙏 Agradecimientos

¡Gracias por contribuir a Platanus! Toda contribución, grande o pequeña, es valorada.

---

**Happy Coding! 🚀**
