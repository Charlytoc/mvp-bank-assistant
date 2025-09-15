# -*- coding: utf-8 -*-
"""
Agente minimalista inspirado en `mini/telegram-assistant/src/agents`.

- Intenta resolver por intents de Lex.
- Si no hay intent o falla, hace fallback a Bedrock (LLM).
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import boto3
from .memory import memory
from .context_loader import load_banesco_context, get_product_recommendations
from .faq_loader import get_faq_text
from .comprehend_analyzer import comprehend_analyzer
from .timer_manager import timer_manager


class Agent:
    """Agente principal del MVP."""

    def __init__(self, bedrock_client=None):
        self.bedrock = bedrock_client or boto3.client('bedrock-runtime', region_name='us-east-1')
        self.context = load_banesco_context()

    def _extract_tool_calls(self, message: str) -> List[Dict[str, Any]]:
        """Extrae tool calls del mensaje usando regex."""
        tool_calls = []
        
        # Patrón para encontrar <tool_calls>[...]</tool_calls>
        pattern = r'<tool_calls>\[(.*?)\]</tool_calls>'
        match = re.search(pattern, message, re.DOTALL)
        
        if match:
            try:
                # Extraer el JSON dentro de los corchetes
                json_str = '[' + match.group(1) + ']'
                print(f"[Agent] JSON extraído: {json_str}")
                tool_calls = json.loads(json_str)
                print(f"[Agent] Tool calls parseadas: {tool_calls}")
            except json.JSONDecodeError as e:
                print(f"[Agent] Error parsing tool calls JSON: {e}")
                print(f"[Agent] JSON problemático: {json_str}")
                
                # Intentar arreglar el JSON común
                try:
                    # Reemplazar None por null
                    json_str_fixed = json_str.replace('None', 'null')
                    tool_calls = json.loads(json_str_fixed)
                    print(f"[Agent] JSON arreglado exitosamente: {tool_calls}")
                except json.JSONDecodeError as e2:
                    print(f"[Agent] Error arreglando JSON: {e2}")
        
        return tool_calls

    def _process_tool_calls(self, tool_calls: List[Dict[str, Any]], session_id: str) -> str:
        """Procesa las tool calls extraídas."""
        if not tool_calls:
            return ""
        
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get('name', '')
            arguments = tool_call.get('arguments', {})
            
            if tool_name == 'abrir_cuenta':
                # Procesar apertura de cuenta
                result = self._handle_account_opening(arguments, session_id)
                results.append(result)
            else:
                results.append(f"Tool call '{tool_name}' no reconocida")
        
        return "\n".join(results)

    def _handle_account_opening(self, arguments: Dict[str, Any], session_id: str) -> str:
        """Maneja la apertura de cuenta con los datos proporcionados."""
        try:
            # Importar aquí para evitar dependencias circulares
            from .crm_adapter import create_case
            
            crm_data = {
                'customer_name': arguments.get('nombre', '') or '',
                'document_id': arguments.get('documento_identidad', '') or '',
                'birth_date': arguments.get('fecha_nacimiento', '') or '',
                'address': arguments.get('direccion_residencia', '') or '',
                'income_proof': arguments.get('comprobante_ingresos', '') or '',
                'business_registry': arguments.get('registro_mercantil', '') or '',
                'phone': arguments.get('telefono', '') or '',
                'email': arguments.get('correo_electronico', '') or '',
                'session_id': session_id
            }
            
            print(f"[Agent] Creando caso CRM con datos: {crm_data}")
            
            # Crear caso en CRM
            crm_result = create_case(crm_data)
            
            if crm_result.get('id'):
                return f"✅ ¡Perfecto! He creado tu solicitud de apertura de cuenta. Número de caso: {crm_result['id']}. Un representante se pondrá en contacto contigo pronto."
            else:
                return "⚠️ He registrado tu solicitud, pero hubo un problema al crear el caso en el sistema. Un representante se pondrá en contacto contigo."
                
        except Exception as e:
            print(f"[Agent] Error procesando apertura de cuenta: {e}")
            return "⚠️ He registrado tu solicitud, pero hubo un problema técnico. Un representante se pondrá en contacto contigo."

    def handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje del usuario con agent loop.

        event debe incluir:
        - `text`: texto del usuario
        - Opcional: `session_id`, `bedrock_model_id`
        """
        text = (event or {}).get("text") or ""
        session_id = (event or {}).get("session_id") or "banon"

        # Real-time sentiment analysis for user message
        sentiment_data = None
        if not os.getenv('MOCK_MODE') and text.strip():
            try:
                sentiment_data = comprehend_analyzer.analyze_user_sentiment(text)
                # Imprimir análisis en amarillo
                from .colors import print_warning
                print_warning(f"🧠 Sentiment Analysis: {sentiment_data['sentiment']} (confidence: {sentiment_data['confidence']:.2f})")
            except Exception as e:
                print(f"[Agent] Error analyzing sentiment: {e}")
                sentiment_data = {
                    "sentiment": "NEUTRAL",
                    "confidence": 0.5,
                    "scores": {"POSITIVE": 0.25, "NEGATIVE": 0.25, "NEUTRAL": 0.5, "MIXED": 0.0}
                }

        # Start/restart timer for inactivity analysis
        timer_manager.start_timer(session_id)

        # Usar Bedrock si está disponible
        if not os.getenv('MOCK_MODE'):
            return self._agent_loop(text, session_id, event, sentiment_data=sentiment_data)
        else:
            # Respuesta mock cuando no hay AWS
            mock_response = self._get_mock_response(text)
            
            # Incluir análisis de sentimientos en modo mock también
            if sentiment_data:
                mock_response["sentiment_analysis"] = {
                    "sentiment": sentiment_data['sentiment'],
                    "confidence": sentiment_data['confidence'],
                    "scores": sentiment_data['scores']
                }
            
            return mock_response

    def _agent_loop(self, initial_text: str, session_id: str, event: Dict[str, Any], max_iterations: int = 5, sentiment_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Loop principal del agente que procesa tool calls iterativamente."""
        model_id = event.get("bedrock_model_id") or "ai21.jamba-1-5-large-v1:0"
        
        # Obtener contexto de conversación
        conversation_context = memory.get_context_summary(session_id)
        
        # Generar recomendaciones de productos
        product_recommendations = get_product_recommendations(initial_text, self.context)
        
        # Generar texto de FAQ
        faq_text = get_faq_text()
        print(f"[Agent] FAQ text: {faq_text}")
        
        # Construir prompt del sistema con contexto
        system_prompt = f"""Eres un asistente bancario de Banesco Panamá. Eres amigable, profesional y experto en productos bancarios.

{self.context}

{conversation_context}

Esta es una lista de preguntas frecuentes que puedes usar para responder las consultas del usuario, las preguntas no tienen que ser necesariamente las mismas que las preguntas frecuentes, puedes usar las preguntas frecuentes como base para tu respuesta.


{faq_text}

Instrucciones:
- Responde en español de manera clara y útil
- Usa la información de productos proporcionada para dar respuestas precisas
- Si el usuario pregunta sobre productos específicos, proporciona detalles de requisitos, beneficios y tarifas
- Usa las preguntas frecuentes (FAQ) proporcionadas para responder consultas comunes
- Si encuentras una FAQ relevante, úsala como base para tu respuesta
- Si no tienes información específica, deriva al usuario a un representante
- Mantén un tono profesional pero amigable

HERRAMIENTAS DISPONIBLES:
- abrir_cuenta: Para procesar solicitudes de apertura de cuenta
  Argumentos: nombre, documento_identidad, fecha_nacimiento, direccion_residencia, comprobante_ingresos, registro_mercantil, telefono, correo_electronico

CUANDO USAR HERRAMIENTAS:
- Si el usuario proporciona TODOS los datos necesarios para abrir una cuenta, usa la herramienta abrir_cuenta
- Si solo faltan algunos datos, pide los datos faltantes
- Para otras consultas, responde normalmente sin usar herramientas

FORMATO DE HERRAMIENTAS:
<tool_calls>
[{{"name": "abrir_cuenta", "arguments": {{"nombre": "Juan Pérez", "documento_identidad": "123456789", ...}}}}
]
</tool_calls>

{product_recommendations}"""

        # Inicializar mensajes de conversación
        messages = [
            {
                "role": "user",
                "content": [{"text": initial_text}]
            }
        ]
        
        iteration = 0
        final_response = ""
        
        while iteration < max_iterations:
            iteration += 1
            print(f"🔄 [Agent] Iteración {iteration}")
            
            try:
                # Llamar a Bedrock
                resp = self.bedrock.converse(
                    modelId=model_id,
                    messages=messages,
                    system=[{"text": system_prompt}],
                    inferenceConfig={
                        "maxTokens": 512,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                )
                
                message = resp["output"]["message"]["content"][0]["text"]
                print(f"🤖 [Agent] Respuesta: {message[:100]}...")
                
                # Extraer tool calls
                tool_calls = self._extract_tool_calls(message)
                
                if tool_calls:
                    print(f"🔧 [Agent] Tool calls encontradas: {len(tool_calls)}")
                    
                    # Procesar tool calls
                    tool_results = []
                    for tool_call in tool_calls:
                        tool_result = self._process_tool_calls([tool_call], session_id)
                        tool_results.append(tool_result)
                    
                    # Limpiar tool calls del mensaje para mostrar solo el texto
                    clean_message = re.sub(r'<tool_calls>.*?</tool_calls>', '', message, flags=re.DOTALL).strip()
                    
                    # Agregar respuesta del asistente a los mensajes
                    messages.append({
                        "role": "assistant",
                        "content": [{"text": message}]
                    })
                    
                    # Agregar resultados de herramientas a los mensajes
                    for i, tool_result in enumerate(tool_results):
                        messages.append({
                            "role": "user",
                            "content": [{"text": f"Resultado de herramienta {i+1}: {tool_result}"}]
                        })
                    
                    print(f"✅ [Agent] Tool calls procesadas, continuando loop...")
                    
                else:
                    # No hay tool calls, esta es la respuesta final
                    final_response = message
                    print(f"✅ [Agent] Respuesta final obtenida")
                    break
                    
            except Exception as e:
                print(f"❌ [Agent] Error en iteración {iteration}: {e}")
                final_response = f"Error procesando tu solicitud: {str(e)}"
                break
        
        if iteration >= max_iterations:
            print(f"⚠️ [Agent] Máximo de iteraciones alcanzado ({max_iterations})")
            final_response = "He procesado tu solicitud pero alcanzé el límite de iteraciones. ¿Hay algo más en lo que pueda ayudarte?"
        
        # Guardar en memoria
        memory.add_message(session_id, initial_text, final_response, "bedrock")
        
        # Preparar respuesta con análisis de sentimientos
        response_data = {
            "source": "bedrock", 
            "message": final_response
        }
        
        # Incluir análisis de sentimientos si está disponible
        if sentiment_data:
            response_data["sentiment_analysis"] = {
                "sentiment": sentiment_data['sentiment'],
                "confidence": sentiment_data['confidence'],
                "scores": sentiment_data['scores']
            }
        
        return response_data

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
