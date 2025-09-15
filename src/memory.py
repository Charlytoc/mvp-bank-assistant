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
            self.conversations[session_id] = {
                "messages": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "analyzed_by_comprehend": False,
                    "analysis_timestamp": None,
                    "message_count": 0
                }
            }
        
        # Add message to conversation
        self.conversations[session_id]["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": message,
            "source": source
        })
        
        self.conversations[session_id]["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant", 
            "content": response,
            "source": source
        })
        
        # Update metadata
        self.conversations[session_id]["metadata"]["last_activity"] = datetime.now().isoformat()
        self.conversations[session_id]["metadata"]["message_count"] = len(self.conversations[session_id]["messages"])
        
        # Limitar el número de mensajes por sesión
        if len(self.conversations[session_id]["messages"]) > self.max_messages_per_session:
            self.conversations[session_id]["messages"] = self.conversations[session_id]["messages"][-self.max_messages_per_session:]
        
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
        if session_id not in self.conversations:
            return ""
        
        messages = self.conversations[session_id].get("messages", [])
        if not messages:
            return ""
        
        context = "Contexto de conversación anterior:\n"
        for msg in messages[-10:]:  # Last 10 messages
            if msg.get('role') == 'user':
                context += f"Usuario: {msg['content']}\n"
            elif msg.get('role') == 'assistant':
                context += f"Asistente: {msg['content']}\n\n"
        
        return context
    
    def get_conversation_for_analysis(self, session_id: str) -> Dict[str, Any]:
        """Gets conversation data ready for Comprehend analysis."""
        if session_id not in self.conversations:
            return {}
        
        conversation = self.conversations[session_id]
        return {
            "session_id": session_id,
            "messages": conversation.get("messages", []),
            "metadata": conversation.get("metadata", {}),
            "created_at": conversation.get("metadata", {}).get("created_at"),
            "last_activity": conversation.get("metadata", {}).get("last_activity"),
            "message_count": conversation.get("metadata", {}).get("message_count", 0)
        }
    
    def mark_conversation_analyzed(self, session_id: str):
        """Mark conversation as analyzed by Comprehend."""
        if session_id in self.conversations:
            self.conversations[session_id]["metadata"]["analyzed_by_comprehend"] = True
            self.conversations[session_id]["metadata"]["analysis_timestamp"] = datetime.now().isoformat()
            self._save_memory()
    
    def get_unanalyzed_conversations(self) -> List[str]:
        """Get list of session IDs that haven't been analyzed yet."""
        unanalyzed = []
        for session_id, conversation in self.conversations.items():
            metadata = conversation.get("metadata", {})
            if not metadata.get("analyzed_by_comprehend", False):
                unanalyzed.append(session_id)
        return unanalyzed
    
    def get_conversations_by_inactivity(self, minutes: int = 1) -> List[str]:
        """Get conversations that have been inactive for specified minutes."""
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        inactive_sessions = []
        
        for session_id, conversation in self.conversations.items():
            metadata = conversation.get("metadata", {})
            last_activity_str = metadata.get("last_activity")
            
            if last_activity_str:
                try:
                    last_activity = datetime.fromisoformat(last_activity_str)
                    if last_activity < cutoff_time and not metadata.get("analyzed_by_comprehend", False):
                        inactive_sessions.append(session_id)
                except ValueError:
                    continue
        
        return inactive_sessions

# Instancia global de memoria
memory = ConversationMemory()
