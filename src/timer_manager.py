# -*- coding: utf-8 -*-
"""
Timer manager for handling conversation inactivity analysis.
"""
import asyncio
import threading
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from .memory import memory
from .comprehend_analyzer import comprehend_analyzer
from .colors import print_timer, print_success, print_warning, print_error

class ConversationTimerManager:
    """Manages timers for conversation inactivity analysis."""
    
    def __init__(self, inactivity_minutes: int = 1):
        self.inactivity_minutes = inactivity_minutes
        self.active_timers: Dict[str, threading.Timer] = {}
        self.running = False
        self._lock = threading.Lock()
    
    def start_timer(self, session_id: str):
        """Start or restart timer for a session."""
        with self._lock:
            # Cancel existing timer if any
            if session_id in self.active_timers:
                self.active_timers[session_id].cancel()
            
            # Create new timer
            timer = threading.Timer(
                self.inactivity_minutes * 60,  # Convert to seconds
                self._analyze_conversation,
                args=[session_id]
            )
            timer.daemon = True
            timer.start()
            
            self.active_timers[session_id] = timer
            print_timer(f"Timer started for session {session_id} ({self.inactivity_minutes} min)")
    
    def cancel_timer(self, session_id: str):
        """Cancel timer for a session."""
        with self._lock:
            if session_id in self.active_timers:
                self.active_timers[session_id].cancel()
                del self.active_timers[session_id]
                print_timer(f"Timer cancelled for session {session_id}")
    
    def _analyze_conversation(self, session_id: str):
        """Analyze conversation after inactivity period."""
        try:
            print_timer(f"Analyzing conversation {session_id} after {self.inactivity_minutes} min inactivity")
            
            # Get conversation data
            conversation_data = memory.get_conversation_for_analysis(session_id)
            
            if not conversation_data or not conversation_data.get('messages'):
                print_warning(f"No conversation data found for session {session_id}")
                return
            
            # Analyze with Comprehend
            analysis_result = comprehend_analyzer.analyze_conversation_batch(conversation_data)
            
            if 'error' not in analysis_result:
                # Mark as analyzed
                memory.mark_conversation_analyzed(session_id)
                print_success(f"Conversation {session_id} analyzed successfully")
                
                # Log insights
                insights = analysis_result.get('conversation_insights', [])
                if insights:
                    print_success(f"Key insights for {session_id}: {', '.join(insights)}")
            else:
                print_error(f"Error analyzing conversation {session_id}: {analysis_result.get('error')}")
                
        except Exception as e:
            print_error(f"Error in timer analysis for {session_id}: {e}")
        finally:
            # Clean up timer
            with self._lock:
                if session_id in self.active_timers:
                    del self.active_timers[session_id]
    
    def get_active_timers(self) -> Dict[str, float]:
        """Get list of active timers with remaining time."""
        active = {}
        
        with self._lock:
            for session_id, timer in self.active_timers.items():
                if timer.is_alive():
                    # Just return the configured timeout time
                    active[session_id] = self.inactivity_minutes * 60
        
        return active
    
    def cleanup_expired_timers(self):
        """Clean up expired or dead timers."""
        with self._lock:
            expired_sessions = []
            for session_id, timer in self.active_timers.items():
                if not timer.is_alive():
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_timers[session_id]
                print_timer(f"Cleaned up expired timer for {session_id}")

# Global timer manager instance
timer_manager = ConversationTimerManager(inactivity_minutes=1)
