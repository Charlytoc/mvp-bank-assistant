# -*- coding: utf-8 -*-
"""
Configuración del MVP de asistente bancario.

- Soporte para .env y variables de entorno
- Región por defecto: us-east-1
"""
import os
from typing import Dict, Optional

# Cargar .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # Forzar sobreescritura de variables existentes
except ImportError:
    pass

def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Obtiene una variable de entorno con valor por defecto opcional."""
    return os.getenv(name, default)

AWS_REGION = _get_env("AWS_REGION", "us-east-1")
AWS_PROFILE = _get_env("AWS_PROFILE")
AWS_ACCESS_KEY_ID = _get_env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = _get_env("AWS_SECRET_ACCESS_KEY")
BEDROCK_ENDPOINT = _get_env("BEDROCK_ENDPOINT")
CRM_URL = _get_env("CRM_URL", "http://localhost:8000/api")
ENVIRONMENT = _get_env("ENVIRONMENT", "dev")

# Exportar configuración como dict simple para fácil importación
CONFIG: Dict[str, Optional[str]] = {
    "aws_region": AWS_REGION,
    "aws_profile": AWS_PROFILE,
    "aws_access_key_id": AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    "bedrock_endpoint": BEDROCK_ENDPOINT,
    "crm_url": CRM_URL,
    "environment": ENVIRONMENT,
}
