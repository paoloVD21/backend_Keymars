from datetime import datetime, timedelta
import jwt
from typing import Optional, Dict, Any
import scrypt
import secrets
import base64
from fastapi import HTTPException, status
from app.config.settings import settings

# Configuración de seguridad desde settings centralizado
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
# Parámetros de Scrypt optimizados para seguridad en 2025

# Parámetros de Scrypt optimizados para seguridad en 2025
SCRYPT_N = 2**16  # CPU/Memory cost factor (debe ser potencia de 2)
SCRYPT_R = 8      # Block size factor
SCRYPT_P = 1      # Parallelization factor
SCRYPT_KEY_LEN = 32  # Longitud de la clave derivada
SALT_LENGTH = 16     # Longitud del salt en bytes

def get_password_hash(password: str) -> str:
    """
    Genera un hash de contraseña usando Scrypt.
    
    Args:
        password (str): La contraseña en texto plano
        
    Returns:
        str: Hash en formato: scrypt$[salt_base64]$[hash_base64]
        
    Raises:
        HTTPException: Si hay un error al generar el hash
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña no puede estar vacía"
        )
        
    try:
        # Genera un salt aleatorio
        salt = secrets.token_bytes(SALT_LENGTH)
        
        # Genera el hash usando scrypt
        hash_bytes = scrypt.hash(
            password.encode('utf-8'),
            salt=salt,
            N=SCRYPT_N,
            r=SCRYPT_R,
            p=SCRYPT_P,
            buflen=SCRYPT_KEY_LEN
        )
        
        # Codifica salt y hash en base64
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        hash_b64 = base64.b64encode(hash_bytes).decode('utf-8')
        
        # Retorna el hash formateado
        return f"scrypt${salt_b64}${hash_b64}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar el hash de la contraseña"
        ) from e

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash usando Scrypt.
    
    Args:
        plain_password (str): La contraseña en texto plano a verificar
        stored_hash (str): El hash almacenado en formato scrypt$[salt]$[hash]
        
    Returns:
        bool: True si la contraseña coincide, False si no
    """
    if not plain_password or not stored_hash:
        return False
        
    try:
        # Separa las partes del hash almacenado
        algorithm, salt_b64, hash_b64 = stored_hash.split('$')
        if algorithm != 'scrypt':
            return False
        
        # Decodifica salt y hash de base64
        salt = base64.b64decode(salt_b64)
        stored_hash_bytes = base64.b64decode(hash_b64)
        
        # Calcula el hash de la contraseña proporcionada
        computed_hash = scrypt.hash(
            plain_password.encode('utf-8'),
            salt=salt,
            N=SCRYPT_N,
            r=SCRYPT_R,
            p=SCRYPT_P,
            buflen=SCRYPT_KEY_LEN
        )
        
        # Compara los hashes usando comparación de tiempo constante
        return secrets.compare_digest(computed_hash, stored_hash_bytes)
    except Exception:
        return False

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT con los datos proporcionados.
    
    Args:
        data (Dict[str, Any]): Datos a incluir en el token
        expires_delta (Optional[timedelta]): Tiempo de expiración del token
        
    Returns:
        str: El token JWT generado
        
    Raises:
        HTTPException: Si hay un error al generar el token
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta if expires_delta 
            else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # PyJWT puede devolver bytes en algunas versiones
        return encoded_jwt if isinstance(encoded_jwt, str) else encoded_jwt.decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar el token de acceso"
        ) from e

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token (str): El token JWT a verificar
        
    Returns:
        Optional[Dict[str, Any]]: Los datos decodificados del token si es válido,
                                 None si no es válido
        
    Raises:
        HTTPException: Si el token ha expirado o es inválido
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de acceso ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )