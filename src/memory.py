# -*- coding: utf-8 -*-
"""
Sistema de memoria para conversaciones del asistente bancario.
"""
import json
import os
from typing import Dict, List, Any
from datetime import datetime

class ConversationMemory:
    """Maneja la memoria de conversaciones."""
    
    def __init__(self, max_conversations: int = 100, max_messages_per_session: int = 20):
        self.max_conversations = max_conversations
        self.max_messages_per_session = max_messages_per_session
        self.memory_file = "conversation_memory.json"
        self.conversations = self._load_memory()
    
    def _load_memory(self) -> Dict[str, List[Dict]]:
        """Carga la memoria desde archivo."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_memory(self):
        """Guarda la memoria en archivo."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando memoria: {e}")
    
    def add_message(self, session_id: str, message: str, response: str, source: str = "unknown"):
        """Agrega un mensaje a la conversación."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": response,
            "source": source
        })
        
        # Limitar el número de mensajes por sesión
        if len(self.conversations[session_id]) > self.max_messages_per_session:
            self.conversations[session_id] = self.conversations[session_id][-self.max_messages_per_session:]
        
        # Limitar el número de conversaciones
        if len(self.conversations) > self.max_conversations:
            oldest_session = min(self.conversations.keys())
            del self.conversations[oldest_session]
        
        self._save_memory()
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Obtiene el historial de conversación."""
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id][-limit:]
    
    def get_context_summary(self, session_id: str) -> str:
        """Obtiene un resumen del contexto de la conversación."""
        history = self.get_conversation_history(session_id, 10)
        
        if not history:
            return ""
        
        context = "Contexto de conversación anterior:\n"
        for msg in history:
            context += f"Usuario: {msg['user_message']}\n"
            context += f"Asistente: {msg['bot_response']}\n\n"
        
        return context

# Instancia global de memoria
memory = ConversationMemory()
