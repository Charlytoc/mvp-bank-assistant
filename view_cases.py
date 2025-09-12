#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ver los casos del CRM (CSV local).
"""

import sys
import os
sys.path.append('src')

from crm_adapter import list_cases, get_case

def main():
    """Función principal para mostrar casos."""
    print("🏦 Casos del CRM - Banesco Panamá")
    print("=" * 50)
    
    # Listar todos los casos
    cases = list_cases(limit=100)
    
    if not cases:
        print("📭 No hay casos registrados")
        return
    
    print(f"📊 Total de casos: {len(cases)}")
    print()
    
    # Mostrar cada caso
    for i, case in enumerate(cases, 1):
        print(f"🔹 Caso #{i}")
        print(f"   ID: {case.get('id', 'N/A')}")
        print(f"   Cliente: {case.get('cliente_nombre', 'N/A')}")
        print(f"   Estado: {case.get('estado', 'N/A')}")
        print(f"   Tipo: {case.get('tipo', 'N/A')}")
        print(f"   Fecha: {case.get('fecha_creacion', 'N/A')}")
        print(f"   Email: {case.get('email', 'N/A')}")
        print(f"   Teléfono: {case.get('telefono', 'N/A')}")
        print(f"   Documento: {case.get('documento_id', 'N/A')}")
        print()

if __name__ == "__main__":
    main()
