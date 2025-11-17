# Guía de Tests Unitarios

## Estructura de Tests

Los tests están organizados en la carpeta `tests/` con la siguiente estructura:

```
tests/
├── auth/
│   ├── conftest.py              # Fixtures compartidas para tests de auth
│   ├── test_auth_service.py     # Tests de servicios de autenticación
│   ├── test_auth_endpoints.py   # Tests de endpoints de autenticación
│   └── test_auth_utils.py       # Tests de funciones de utilidad
```

## Instalación de Dependencias

Para ejecutar los tests, primero instala las dependencias de testing:

```bash
pip install pytest pytest-asyncio httpx
```

## Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Tests de un módulo específico
```bash
pytest tests/auth/
```

### Tests de un archivo específico
```bash
pytest tests/auth/test_auth_service.py
```

### Ejecutar un test específico
```bash
pytest tests/auth/test_auth_service.py::test_authenticate_user_success
```

### Ver más detalles
```bash
pytest -v
```

### Ejecutar con cobertura
```bash
pip install pytest-cov
pytest --cov=app tests/
```

## Fixtures Disponibles

### `test_db`
Base de datos SQLite en memoria para tests. Se crea limpia para cada test.

```python
def test_something(test_db):
    # test_db es una sesión SQLAlchemy lista para usar
    pass
```

### `test_sucursal`
Crea una sucursal de prueba.

```python
def test_something(test_sucursal):
    assert test_sucursal.id_sucursal is not None
```

### `test_rol`
Crea un rol de prueba.

```python
def test_something(test_rol):
    assert test_rol.id_rol is not None
```

### `test_user`
Crea un usuario de prueba con contraseña "password123".

```python
def test_something(test_user):
    assert test_user.email == "test@example.com"
    # La contraseña es: password123
```

### `client`
Cliente HTTP para probar endpoints. Automáticamente inyecta la DB de test.

```python
def test_endpoint(client):
    response = client.post("/api/auth/login", data={...})
```

## Cobertura de Tests

### tests/auth/test_auth_service.py
- ✅ Autenticación exitosa
- ✅ Autenticación con email inexistente
- ✅ Autenticación con contraseña incorrecta
- ✅ Autenticación de usuario inactivo
- ✅ Creación de sesión
- ✅ Invalidación de sesión anterior
- ✅ Obtención de sesión válida
- ✅ Obtención de sesión inválida
- ✅ Obtención de sesión inactiva
- ✅ Cierre de sesión exitoso
- ✅ Cierre de sesión con token inválido

### tests/auth/test_auth_endpoints.py
- ✅ Login exitoso
- ✅ Login con email inexistente
- ✅ Login con contraseña incorrecta
- ✅ Logout exitoso
- ✅ Logout con token inválido
- ✅ Logout sin token
- ✅ Obtención de información de sesión
- ✅ Obtención de sesión con token inválido
- ✅ Obtención de sesión sin token

### tests/auth/test_auth_utils.py
- ✅ Generación de hash válido
- ✅ Hashes diferentes para la misma contraseña
- ✅ Hash con contraseña vacía genera error
- ✅ Verificación de contraseña válida
- ✅ Verificación de contraseña inválida
- ✅ Verificación con contraseña vacía
- ✅ Verificación con hash vacío
- ✅ Verificación con formato de hash inválido
- ✅ Creación de token válido
- ✅ Token incluye expiración
- ✅ Token con expiración personalizada
- ✅ Error al decodificar con clave incorrecta

## Notas Importantes

1. Los tests usan una base de datos SQLite en memoria para evitar afectar la BD real
2. Cada test recibe una DB limpia, aislando los tests entre sí
3. Las contraseñas se hashean con Scrypt usando los mismos parámetros que producción
4. Los tokens JWT se verifican correctamente
5. Se prueban tanto casos exitosos como casos de error

## Mejoras Futuras

- [ ] Agregar tests para otros controladores (product, user, etc.)
- [ ] Agregar tests de integración
- [ ] Agregar tests de carga
- [ ] Agregar mocking de servicios externos
