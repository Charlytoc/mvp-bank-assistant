# -*- coding: utf-8 -*-
"""
AWS Lambda handler para el Asistente Bancario.
Optimizado para API Gateway y manejo de CORS.
"""
import json
import os
from typing import Any, Dict

from src.agent import Agent
from src.crm_adapter import create_case
from src.config import CONFIG

# Instanciar el agente una sola vez (reutilizable entre invocaciones)
agent = Agent()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handler de AWS Lambda para API Gateway.

    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda

    Returns:
        Respuesta HTTP para API Gateway
    """
    try:
        # Headers CORS
        cors_headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }

        # Manejar preflight OPTIONS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }

        # Extraer datos del evento
        if event.get('httpMethod') == 'POST':
            body = event.get('body', '{}')
            if isinstance(body, str):
                body = json.loads(body)
            payload = body
        else:
            payload = event or {}

        # Procesar mensaje
        result = agent.handle_message(payload)
        
        # Si es solicitud de apertura de cuenta, crear ticket CRM
        if (result.get('source') == 'lex' and 
            result.get('intent') == 'OpenAccount' and 
            payload.get('customer_name')):
            
            try:
                customer_data = {
                    'type': 'account_opening',
                    'customer_name': payload.get('customer_name', 'Not provided'),
                    'email': payload.get('email', 'Not provided'),
                    'phone': payload.get('phone', 'Not provided'),
                    'message': payload.get('message', ''),
                    'priority': 'medium',
                    'status': 'new',
                    'source': 'chat_bot'
                }
                
                crm_response = create_case(customer_data)
                
                result = {
                    'source': 'crm',
                    'message': f'¡Perfecto! He creado una solicitud para abrir tu cuenta. Un representante se pondrá en contacto contigo pronto. Tu número de ticket es: {crm_response.get("id", "N/A")}',
                    'ticket_id': crm_response.get('id')
                }
            except Exception as e:
                print(f"[Lambda] Error creating CRM ticket: {e}")
                result = {
                    'source': 'crm_fallback',
                    'message': 'He registrado tu solicitud de apertura de cuenta. Un representante se pondrá en contacto contigo pronto.'
                }

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'response': result.get('message', 'No response generated'),
                'source': result.get('source', 'unknown'),
                'ticket_id': result.get('ticket_id')
            }, ensure_ascii=False)
        }

    except Exception as exc:
        print(f"[Lambda] Error: {exc}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'error': str(exc)
            }, ensure_ascii=False)
        }
