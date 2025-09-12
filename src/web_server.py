# -*- coding: utf-8 -*-
"""
Servidor web FastAPI para el Asistente Bancario Banesco Panamá.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .agent import Agent
import json
from .crm_adapter import create_case
from .config import CONFIG
from .colors import *

# Crear instancia de FastAPI
app = FastAPI(title="Banesco Panamá - Asistente Virtual", version="1.0.0")

# Inicializar agente
agent = Agent()

class MessageRequest(BaseModel):
    message: str
    session_id: str
    customer_name: str = None
    customer_email: str = None
    customer_phone: str = None
    account_type: str = None

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Interfaz de chat principal."""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Banesco Panamá - Asistente Virtual</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 25%, #3b82f6 50%, #06b6d4 75%, #10b981 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }
            
            .chat-container {
                width: 95%;
                max-width: 1000px;
                height: 90vh;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                box-shadow: 
                    0 32px 64px rgba(0,0,0,0.25),
                    0 0 0 1px rgba(255,255,255,0.1),
                    inset 0 1px 0 rgba(255,255,255,0.2);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                border: 2px solid rgba(59, 130, 246, 0.3);
                position: relative;
            }
            
            .chat-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
            }
            
            .chat-header {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
                color: white;
                padding: 30px;
                text-align: center;
                position: relative;
                border-radius: 30px 30px 0 0;
                box-shadow: 0 4px 20px rgba(30, 64, 175, 0.3);
            }
            
            .chat-header::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            }
            
            .bank-logo {
                font-size: 32px;
                font-weight: 800;
                margin-bottom: 8px;
                text-shadow: 0 4px 8px rgba(0,0,0,0.3);
                letter-spacing: -0.5px;
                background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .bank-subtitle {
                font-size: 18px;
                opacity: 0.95;
                font-weight: 400;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                letter-spacing: 0.5px;
            }
            
            .chat-messages {
                flex: 1;
                padding: 30px;
                overflow-y: auto;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
                    radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.05) 0%, transparent 70%);
                position: relative;
            }
            
            .chat-messages::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.2), transparent);
            }
            
            .message {
                margin-bottom: 20px;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message.bot {
                justify-content: flex-start;
            }
            
            .message-content {
                max-width: 75%;
                padding: 18px 24px;
                border-radius: 24px;
                word-wrap: break-word;
                box-shadow: 
                    0 4px 12px rgba(0,0,0,0.08),
                    0 2px 4px rgba(0,0,0,0.04);
                backdrop-filter: blur(10px);
                position: relative;
                font-size: 15px;
                line-height: 1.5;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
                color: white;
                border-bottom-right-radius: 8px;
                box-shadow: 
                    0 6px 16px rgba(30, 64, 175, 0.3),
                    0 2px 4px rgba(30, 64, 175, 0.2);
            }
            
            .message.bot .message-content {
                background: rgba(255, 255, 255, 0.9);
                color: #1f2937;
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-bottom-left-radius: 8px;
                position: relative;
                backdrop-filter: blur(10px);
            }
            
            .message.bot .message-content::before {
                content: "🏦";
                position: absolute;
                left: -45px;
                top: 12px;
                font-size: 24px;
                width: 36px;
                height: 36px;
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.9);
            }
            
            .chat-input-container {
                padding: 30px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-top: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 0 0 30px 30px;
                position: relative;
            }
            
            .chat-input-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent);
            }
            
            .chat-input-wrapper {
                display: flex;
                gap: 15px;
                align-items: center;
            }
            
            .chat-input {
                flex: 1;
                padding: 18px 24px;
                border: 2px solid rgba(59, 130, 246, 0.2);
                border-radius: 35px;
                font-size: 16px;
                outline: none;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: rgba(248, 250, 252, 0.8);
                backdrop-filter: blur(10px);
                color: #1f2937;
                font-weight: 400;
            }
            
            .chat-input:focus {
                border-color: #1e40af;
                background: rgba(255, 255, 255, 0.95);
                box-shadow: 
                    0 0 0 4px rgba(30, 64, 175, 0.1),
                    0 4px 12px rgba(30, 64, 175, 0.15);
                transform: translateY(-1px);
            }
            
            .chat-input::placeholder {
                color: #6b7280;
                font-weight: 400;
            }
            
            .send-button {
                padding: 18px 36px;
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
                color: white;
                border: none;
                border-radius: 35px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 
                    0 6px 16px rgba(30, 64, 175, 0.3),
                    0 2px 4px rgba(30, 64, 175, 0.2);
                position: relative;
                overflow: hidden;
            }
            
            .send-button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .send-button:hover {
                transform: translateY(-3px);
                box-shadow: 
                    0 8px 20px rgba(30, 64, 175, 0.4),
                    0 4px 8px rgba(30, 64, 175, 0.3);
            }
            
            .send-button:hover::before {
                left: 100%;
            }
            
            .send-button:disabled {
                background: #9ca3af;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .welcome-message {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
                border-radius: 15px;
                margin-bottom: 20px;
                border: 2px solid #3b82f6;
            }
            
            .welcome-title {
                font-size: 18px;
                font-weight: bold;
                color: #1e40af;
                margin-bottom: 10px;
            }
            
            .welcome-text {
                color: #374151;
                font-size: 14px;
            }
            
            .account-form {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 20px;
                margin: 15px 0;
                border-radius: 15px;
                border: 2px solid #3b82f6;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
            }
            
            .form-group {
                margin: 15px 0;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #1e40af;
            }
            
            .form-group input, .form-group select {
                width: 100%;
                padding: 12px;
                border: 2px solid #d1d5db;
                border-radius: 10px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            
            .form-group input:focus, .form-group select:focus {
                outline: none;
                border-color: #1e40af;
                box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
            }
            
            .submit-account {
                background: linear-gradient(135deg, #059669 0%, #10b981 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }
            
            .submit-account:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
            }
            
            /* Scrollbar personalizado */
            .chat-messages::-webkit-scrollbar {
                width: 8px;
            }
            
            .chat-messages::-webkit-scrollbar-track {
                background: #f1f5f9;
                border-radius: 4px;
            }
            
            .chat-messages::-webkit-scrollbar-thumb {
                background: #3b82f6;
                border-radius: 4px;
            }
            
            .chat-messages::-webkit-scrollbar-thumb:hover {
                background: #1e40af;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <div class="bank-logo">🏦 Banesco Panamá</div>
                <div class="bank-subtitle">Asistente Virtual Bancario</div>
            </div>
            
            <div class="chat-messages" id="chatContainer">
                <div class="welcome-message">
                    <div class="welcome-title">¡Bienvenido a Banesco Panamá!</div>
                    <div class="welcome-text">Soy tu asistente virtual. Puedo ayudarte con información sobre productos bancarios, apertura de cuentas, consultas y mucho más. ¿En qué puedo asistirte hoy?</div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <input type="text" class="chat-input" id="messageInput" placeholder="Escribe tu consulta aquí..." onkeypress="handleKeyPress(event)">
                    <button class="send-button" onclick="sendMessage()">Enviar</button>
                </div>
            </div>
        </div>

        <script>
            let isWaitingForAccount = false;
            let currentSessionId = 'session_' + Date.now();

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;

                addMessage(message, 'user');
                input.value = '';

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            session_id: currentSessionId
                        })
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage(data.response, 'bot');
                        
                        if (data.source === 'crm' || data.source === 'crm_fallback') {
                            addAccountForm();
                        }
                    } else {
                        addMessage('Lo siento, hubo un error procesando tu mensaje.', 'bot');
                    }
                } catch (error) {
                    addMessage('Error de conexión. Por favor, intenta de nuevo.', 'bot');
                }
            }

            function addMessage(text, sender) {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.textContent = text;
                
                messageDiv.appendChild(contentDiv);
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function addAccountForm() {
                if (isWaitingForAccount) return;
                
                isWaitingForAccount = true;
                const chatContainer = document.getElementById('chatContainer');
                
                const formDiv = document.createElement('div');
                formDiv.className = 'account-form';
                formDiv.innerHTML = `
                    <h3 style="color: #1e40af; margin-bottom: 15px;">📝 Información para Apertura de Cuenta</h3>
                    <div class="form-group">
                        <label for="customerName">Nombre Completo:</label>
                        <input type="text" id="customerName" placeholder="Ingresa tu nombre completo">
                    </div>
                    <div class="form-group">
                        <label for="customerEmail">Correo Electrónico:</label>
                        <input type="email" id="customerEmail" placeholder="tu@email.com">
                    </div>
                    <div class="form-group">
                        <label for="customerPhone">Teléfono:</label>
                        <input type="tel" id="customerPhone" placeholder="+507 1234-5678">
                    </div>
                    <div class="form-group">
                        <label for="accountType">Tipo de Cuenta:</label>
                        <select id="accountType">
                            <option value="ahorro">Cuenta de Ahorros</option>
                            <option value="corriente">Cuenta Corriente</option>
                            <option value="empresarial">Cuenta Empresarial</option>
                        </select>
                    </div>
                    <button class="submit-account" onclick="submitAccountRequest()">Solicitar Apertura de Cuenta</button>
                `;
                
                chatContainer.appendChild(formDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function submitAccountRequest() {
                const name = document.getElementById('customerName').value.trim();
                const email = document.getElementById('customerEmail').value.trim();
                const phone = document.getElementById('customerPhone').value.trim();
                const accountType = document.getElementById('accountType').value;

                if (!name || !email || !phone) {
                    addMessage('Por favor, completa todos los campos requeridos.', 'bot');
                    return;
                }

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: `Solicitar apertura de cuenta: ${accountType}`,
                            session_id: currentSessionId,
                            customer_name: name,
                            customer_email: email,
                            customer_phone: phone,
                            account_type: accountType
                        })
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage(data.response, 'bot');
                        if (data.ticket_id) {
                            addMessage(`🎫 Tu solicitud ha sido registrada con el ID: ${data.ticket_id}`, 'bot');
                        }
                    } else {
                        addMessage('Error al procesar la solicitud. Inténtalo de nuevo.', 'bot');
                    }
                } catch (error) {
                    addMessage('Error de conexión. Por favor, intenta de nuevo.', 'bot');
                } finally {
                    isWaitingForAccount = false;
                    // Remover el formulario
                    const form = document.querySelector('.account-form');
                    if (form) {
                        form.remove();
                    }
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat_endpoint(request: MessageRequest):
    """Endpoint para procesar mensajes del chat."""
    try:
        print_user(f"Usuario: {request.message}")
        
        # Preparar evento para el agente
        event = {
            'text': request.message,
            'session_id': request.session_id,
            'bedrock_model_id': 'ai21.jamba-1-5-large-v1:0'
        }
        
        # Procesar mensaje con el agente
        result = agent.handle_message(event)

        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Si es una solicitud de apertura de cuenta, crear caso en CRM
        if (result.get('source') == 'agent' and 
            result.get('intent') == 'OpenAccount' and 
            request.customer_name):
            
            print_crm("Creando caso en CRM...")
            
            crm_data = {
                'customer_name': request.customer_name,
                'customer_email': request.customer_email or '',
                'customer_phone': request.customer_phone or '',
                'account_type': request.account_type or 'ahorro',
                'message': request.message,
                'session_id': request.session_id
            }
            
            crm_result = create_case(crm_data)
            
            if crm_result.get('id'):
                result['message'] = f"¡Perfecto! He registrado tu solicitud de apertura de cuenta {crm_data['account_type']}. Un representante se pondrá en contacto contigo pronto."
                result['ticket_id'] = crm_result.get('id')
                result['source'] = 'crm'
                print_success(f"Caso CRM creado: {crm_result.get('id')}")
            else:
                result['message'] = "He registrado tu solicitud. Aunque hubo un problema técnico con el sistema, un representante se pondrá en contacto contigo pronto."
                result['source'] = 'crm_fallback'
                print_warning("Error en CRM, usando fallback")
        
        return {
            'success': True,
            'response': result.get('message', 'No response generated'),
            'source': result.get('source', 'unknown'),
            'ticket_id': result.get('ticket_id')
        }
        
    except Exception as e:
        print_error(f"Error en chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
