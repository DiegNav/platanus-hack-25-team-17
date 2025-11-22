# Configuración de Formateo y Linting

Este documento describe la configuración de herramientas de formateo y linting del proyecto.

## 🛠️ Herramientas Instaladas

### Versiones Actuales (Últimas Disponibles)
- **Ruff**: v0.14.6 - Linter y formatter ultrarrápido
- **Black**: v25.11.0 - Formateador de código
- **Mypy**: v1.18.2 - Type checker estático
- **Pre-commit**: v4.4.0 - Hooks de git automáticos
- **Pytest**: v9.0.1 - Framework de testing
- **Pytest-asyncio**: v1.3.0 - Soporte async para pytest
- **Pytest-cov**: v7.0.0 - Coverage de tests
- **HTTPx**: v0.28.1 - Cliente HTTP para tests

## 📋 Archivos de Configuración

### 1. `ruff.toml`
Archivo dedicado con más de 70 reglas de linting activadas:
- Errores y warnings de pycodestyle (E, W)
- Pyflakes (F)
- Import sorting (I)
- Flake8-bugbear (B)
- Pyupgrade - modernización (UP)
- Seguridad - Bandit (S)
- Pydocstyle - Google convention (D)
- Performance (PERF)
- Y muchas más...

### 2. `pyproject.toml`
Configuraciones de:
- **Black**: Line length 100, Python 3.13
- **Mypy**: Modo strict activado
- **Pytest**: Configuración de async y paths
- **Dependencias dev**: Instaladas con `uv`

### 3. `.pre-commit-config.yaml`
Hooks configurados (versiones actualizadas):
- Pre-commit-hooks: v6.0.0
- Ruff: v0.14.6
- Black: v25.11.0
- Mypy: v1.18.2

### 4. `.editorconfig`
Configuración de editor para consistencia entre IDEs

## 🚀 Comandos Útiles

```bash
# Instalar dependencias de desarrollo
uv sync --extra dev

# Instalar hooks de pre-commit
pre-commit install

# Ejecutar linting manualmente
uv run ruff check .

# Ejecutar linting con corrección automática
uv run ruff check --fix .

# Formatear código con ruff
uv run ruff format .

# Formatear código con black
uv run black .

# Type checking con mypy
uv run mypy .

# Ejecutar todos los checks de pre-commit
pre-commit run --all-files

# Actualizar versiones de hooks
pre-commit autoupdate

# Limpiar cache de pre-commit
pre-commit clean
```

## ⚠️ Errores Pendientes de Corrección Manual

Después de la configuración inicial, quedan 7 errores que requieren atención:

### 1. Exception Chaining (B904) - 3 ocurrencias
**Ubicación**: `app/api/v1/endpoints/users.py`

Usar `raise ... from err` en lugar de solo `raise` dentro de bloques except:

```python
# ❌ Incorrecto
except ValueError as e:
    raise HTTPException(...)

# ✅ Correcto
except ValueError as e:
    raise HTTPException(...) from e
# O si quieres suprimir el contexto:
    raise HTTPException(...) from None
```

### 2. Logging con F-strings (G004) - 4 ocurrencias
**Ubicación**:
- `app/middleware/error_handler.py` (2 ocurrencias)
- `app/middleware/logging_middleware.py` (2 ocurrencias)

Usar lazy formatting (%) en lugar de f-strings:

```python
# ❌ Incorrecto
logger.info(f"Request: {method} {path}")

# ✅ Correcto
logger.info("Request: %s %s", method, path)
```

**Razón**: El lazy formatting es más eficiente porque solo formatea el string si el nivel de log está habilitado.

## 📝 Mejoras Aplicadas Automáticamente

Ruff corrigió automáticamente 8 problemas:
- ✅ Eliminación de asignaciones innecesarias antes de return
- ✅ Simplificación de if-else con operadores ternarios
- ✅ Actualización de sintaxis obsoleta (Generic[T] → [T])
- ✅ Formateo de imports
- ✅ Espacios y líneas en blanco

## 🎯 Reglas Especiales por Archivo

El archivo `ruff.toml` incluye excepciones sensibles:
- **Tests**: Permite asserts, hardcoded passwords, magic values
- **Main files**: Permite print statements para startup/shutdown
- **Config**: Permite binding a 0.0.0.0
- **__init__.py**: Permite unused imports
- **Scripts**: Permite prints y reglas de seguridad más laxas

## 🔄 Workflow Recomendado

1. **Antes de commit**: Pre-commit ejecutará automáticamente todos los checks
2. **Para ver todos los errores**: `pre-commit run --all-files`
3. **Para fixes rápidos**: `uv run ruff check --fix .`
4. **Para type checking**: `uv run mypy .`

## 📚 Recursos

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
