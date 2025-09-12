# -*- coding: utf-8 -*-
"""
Adaptador simple para integración con CRM vía HTTP.

- No incluye autenticación por defecto; agrega headers/tokens si tu CRM lo requiere.
- Usa `CRM_URL` de la configuración como base.
"""
from __future__ import annotations

import json
from typing import Any, Dict

import requests

from .config import CONFIG

BASE_URL = (CONFIG.get("crm_url") or "").rstrip("/")

def create_case(payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
    """Crea un caso en el CRM con POST /cases.

    Agrega autenticación en headers si es necesario.
    """
    if not BASE_URL or BASE_URL == "http://localhost:8000/api":
        return mock_crm_response(payload)
    
    url = f"{BASE_URL}/cases"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BankAssistant/1.0'
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[CRM] Error connecting to CRM: {e}")
        return mock_crm_response(payload)

def update_case(case_id: str, payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
    """Actualiza un caso en el CRM con PUT /cases/{id}."""
    if not BASE_URL or BASE_URL == "http://localhost:8000/api":
        return mock_crm_response(payload, case_id)
    
    url = f"{BASE_URL}/cases/{case_id}"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BankAssistant/1.0'
    }
    
    try:
        resp = requests.put(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[CRM] Error updating case {case_id}: {e}")
        return mock_crm_response(payload, case_id)

def mock_crm_response(payload: Dict[str, Any], case_id: str = None) -> Dict[str, Any]:
    """Simula una respuesta del CRM cuando no hay conexión real."""
    import time
    import random
    
    mock_id = case_id or f"TICKET_{int(time.time())}_{random.randint(1000, 9999)}"
    
    return {
        "id": mock_id,
        "status": "created",
        "message": "Case created successfully (mock response)",
        "data": payload,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "mock_crm"
    }
