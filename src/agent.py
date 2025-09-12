# -*- coding: utf-8 -*-
"""
Agente minimalista inspirado en `mini/telegram-assistant/src/agents`.

- Intenta resolver por intents de Lex.
- Si no hay intent o falla, hace fallback a Bedrock (LLM).
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import boto3
from .memory import memory
from .context_loader import load_banesco_context, get_product_recommendations


class Agent:
    """Agente principal del MVP."""

    def __init__(self, bedrock_client=None):
        self.bedrock = bedrock_client or boto3.client('bedrock-runtime', region_name='us-east-1')
        self.context = load_banesco_context()

    def handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje del usuario.

        event debe incluir:
        - `text`: texto del usuario
        - Opcional: `session_id`, `bedrock_model_id`
        """
        text = (event or {}).get("text") or ""
        session_id = (event or {}).get("session_id") or "anon"

        # Detectar intención de apertura de cuenta localmente
        if self._is_account_opening_request(text):
            return {
                "source": "agent", 
                "intent": "OpenAccount",
                "message": "¡Perfecto! Te ayudo a abrir una nueva cuenta. Necesito algunos datos tuyos para crear la solicitud."
            }
        
        # Usar Bedrock si está disponible
        if not os.getenv('MOCK_MODE'):
            try:
                # Usar la nueva API Converse con modelo Jamba
                model_id = event.get("bedrock_model_id") or "ai21.jamba-1-5-large-v1:0"

                print(f"🔧 Usando modelo Bedrock: {model_id}")
                
                # Obtener contexto de conversación
                conversation_context = memory.get_context_summary(session_id)
                
                # Generar recomendaciones de productos
                product_recommendations = get_product_recommendations(text, self.context)
                
                # Construir prompt del sistema con contexto
                system_prompt = f"""Eres un asistente bancario de Banesco Panamá. Eres amigable, profesional y experto en productos bancarios.

{self.context}

{conversation_context}

Instrucciones:
- Responde en español de manera clara y útil
- Usa la información de productos proporcionada para dar respuestas precisas
- Si el usuario pregunta sobre productos específicos, proporciona detalles de requisitos, beneficios y tarifas
- Si no tienes información específica, deriva al usuario a un representante
- Mantén un tono profesional pero amigable
- Si es una consulta sobre apertura de cuenta, indica que necesitas algunos datos del cliente

{product_recommendations}"""
                
                body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": text
                                }
                            ]
                        }
                    ],
                    "system": [
                        {
                            "text": system_prompt
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 512,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                }
                
                resp = self.bedrock.converse(
                    modelId=model_id,
                    messages=body["messages"],
                    system=body["system"],
                    inferenceConfig=body["inferenceConfig"]
                )
                
                message = resp["output"]["message"]["content"][0]["text"]
                
                # Guardar en memoria
                memory.add_message(session_id, text, message, "bedrock")
                
                return {"source": "bedrock", "message": message}
            except Exception as e:
                print(f"[Agent] Error con Bedrock: {e}")
                return self._get_mock_response(text)
        else:
            # Respuesta mock cuando no hay AWS
            return self._get_mock_response(text)

    def _is_account_opening_request(self, text: str) -> bool:
        """Detecta si el usuario quiere abrir una cuenta."""
        text_lower = text.lower()
        account_keywords = [
            'abrir cuenta', 'nueva cuenta', 'crear cuenta', 'cuenta nueva',
            'abrir una cuenta', 'quiero una cuenta', 'necesito cuenta',
            'solicitar cuenta', 'registrar cuenta'
        ]
        return any(keyword in text_lower for keyword in account_keywords)
    
    def _get_mock_response(self, text: str) -> dict:
        """Respuesta mock cuando no hay conexión a AWS."""
        text_lower = text.lower()
        
        if 'saldo' in text_lower or 'balance' in text_lower:
            return {"source": "agent", "message": "Para consultar tu saldo, necesitas acceder a tu banca en línea o contactar a un representante."}
        elif 'transferencia' in text_lower or 'transfer' in text_lower:
            return {"source": "agent", "message": "Para realizar transferencias, puedes usar tu banca en línea o visitar una sucursal."}
        elif 'tarjeta' in text_lower or 'card' in text_lower:
            return {"source": "agent", "message": "Tenemos diferentes tipos de tarjetas disponibles. ¿Te interesa una tarjeta de débito o crédito?"}
        elif 'prestamo' in text_lower or 'loan' in text_lower or 'préstamo' in text_lower:
            return {"source": "agent", "message": "Ofrecemos varios tipos de préstamos. Un representante puede ayudarte a encontrar la mejor opción para ti."}
        else:
            return {"source": "agent", "message": "Hola! Soy tu asistente bancario. Puedo ayudarte con información sobre productos, apertura de cuentas, o conectarte con un representante. ¿En qué puedo ayudarte?"}
