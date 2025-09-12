# -*- coding: utf-8 -*-
"""
Adaptador para integración con CRM usando CSV local.
"""

import os
import csv
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


def create_case(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un caso en el CRM (CSV local).
    
    Args:
        case_data: Datos del caso incluyendo:
            - customer_name: Nombre del cliente
            - document_id: Documento de identidad
            - birth_date: Fecha de nacimiento
            - address: Dirección
            - income_proof: Comprobante de ingresos
            - business_registry: Registro mercantil
            - phone: Teléfono
            - email: Email
            - session_id: ID de sesión
    
    Returns:
        Dict con resultado de la operación
    """
    try:
        # Generar ID único para el caso
        case_id = str(uuid.uuid4())[:8]
        
        # Preparar datos del caso
        case_record = {
            'id': case_id,
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'estado': 'Nuevo',
            'tipo': 'Apertura de Cuenta',
            'cliente_nombre': case_data.get('customer_name', ''),
            'documento_id': case_data.get('document_id', ''),
            'fecha_nacimiento': case_data.get('birth_date', ''),
            'direccion': case_data.get('address', ''),
            'comprobante_ingresos': case_data.get('income_proof', ''),
            'registro_mercantil': case_data.get('business_registry', ''),
            'telefono': case_data.get('phone', ''),
            'email': case_data.get('email', ''),
            'session_id': case_data.get('session_id', ''),
            'notas': 'Caso creado automáticamente por el bot'
        }
        
        # Escribir al CSV
        csv_file = 'data/crm_cases.csv'
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = case_record.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Escribir header si el archivo es nuevo
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(case_record)
        
        print(f"✅ [CRM] Caso {case_id} creado exitosamente")
        
        return {
            'success': True,
            'id': case_id,
            'message': 'Caso creado exitosamente en CSV local'
        }
        
    except Exception as e:
        print(f"❌ [CRM] Error creando caso: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Error creando el caso en CSV'
        }


def update_case(case_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza un caso existente en el CRM (CSV local).
    
    Args:
        case_id: ID del caso a actualizar
        update_data: Datos a actualizar
    
    Returns:
        Dict con resultado de la operación
    """
    try:
        csv_file = 'data/crm_cases.csv'
        
        if not os.path.exists(csv_file):
            return {
                'success': False,
                'error': 'Archivo CSV no existe',
                'message': 'No se encontró el archivo de casos'
            }
        
        # Leer todos los casos
        cases = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cases = list(reader)
        
        # Buscar el caso a actualizar
        case_found = False
        for i, case in enumerate(cases):
            if case['id'] == case_id:
                # Actualizar campos
                for key, value in update_data.items():
                    if key in case:
                        case[key] = value
                
                # Actualizar fecha de modificación
                case['fecha_modificacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cases[i] = case
                case_found = True
                break
        
        if not case_found:
            return {
                'success': False,
                'error': 'Caso no encontrado',
                'message': f'No se encontró el caso con ID {case_id}'
            }
        
        # Escribir casos actualizados
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if cases:
                fieldnames = cases[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(cases)
        
        print(f"✅ [CRM] Caso {case_id} actualizado exitosamente")
        
        return {
            'success': True,
            'id': case_id,
            'message': 'Caso actualizado exitosamente en CSV local'
        }
        
    except Exception as e:
        print(f"❌ [CRM] Error actualizando caso: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Error actualizando el caso en CSV'
        }


def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un caso específico del CRM (CSV local).
    
    Args:
        case_id: ID del caso a buscar
    
    Returns:
        Dict con datos del caso o None si no se encuentra
    """
    try:
        csv_file = 'data/crm_cases.csv'
        
        if not os.path.exists(csv_file):
            return None
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for case in reader:
                if case['id'] == case_id:
                    return case
        
        return None
        
    except Exception as e:
        print(f"❌ [CRM] Error obteniendo caso: {e}")
        return None


def list_cases(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Lista los casos del CRM (CSV local).
    
    Args:
        limit: Número máximo de casos a retornar
    
    Returns:
        Lista de casos
    """
    try:
        csv_file = 'data/crm_cases.csv'
        
        if not os.path.exists(csv_file):
            return []
        
        cases = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cases = list(reader)
        
        # Ordenar por fecha de creación (más recientes primero)
        cases.sort(key=lambda x: x.get('fecha_creacion', ''), reverse=True)
        
        return cases[:limit]
        
    except Exception as e:
        print(f"❌ [CRM] Error listando casos: {e}")
        return []