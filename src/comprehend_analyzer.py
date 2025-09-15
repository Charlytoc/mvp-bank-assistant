# -*- coding: utf-8 -*-
"""
Amazon Comprehend integration for conversation analysis.
"""
import json
import os
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from .colors import print_comprehend, print_success, print_error, print_warning


class ComprehendAnalyzer:
    """Handles Amazon Comprehend analysis for conversations."""
    
    def __init__(self):
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')
        self.analysis_file = "comprehend_analysis.json"
        self.analysis_data = self._load_analysis_data()
    
    def _load_analysis_data(self) -> Dict[str, Any]:
        """Load analysis data from file."""
        if os.path.exists(self.analysis_file):
            try:
                with open(self.analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print_error(f"Error loading analysis data: {e}")
                return {"conversations": {}, "sentiment_history": []}
        return {"conversations": {}, "sentiment_history": []}
    
    def _save_analysis_data(self):
        """Save analysis data to file."""
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print_error(f"Error saving analysis data: {e}")
    
    def analyze_user_sentiment(self, user_message: str) -> Dict[str, Any]:
        """Analyze sentiment of a single user message."""
        try:
            print_comprehend(f"Analyzing sentiment for: {user_message[:50]}...")
            
            response = self.comprehend.detect_sentiment(
                Text=user_message,
                LanguageCode='es'
            )
            print(response, "response from comprehend")
            
            sentiment_data = {
                "sentiment": response['Sentiment'],
                "confidence": response['SentimentScore'][response['Sentiment'].capitalize()],
                "scores": response['SentimentScore'],
                "timestamp": datetime.now().isoformat(),
                "message": user_message
            }
            
            # Store in sentiment history
            self.analysis_data["sentiment_history"].append(sentiment_data)
            
            # Keep only last 1000 sentiment analyses
            if len(self.analysis_data["sentiment_history"]) > 1000:
                self.analysis_data["sentiment_history"] = self.analysis_data["sentiment_history"][-1000:]
            
            self._save_analysis_data()
            
            print_success(f"Sentiment: {sentiment_data['sentiment']} (confidence: {sentiment_data['confidence']:.2f})")
            return sentiment_data
            
        except Exception as e:
            print_error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.5,
                "scores": {"POSITIVE": 0.25, "NEGATIVE": 0.25, "NEUTRAL": 0.5, "MIXED": 0.0},
                "timestamp": datetime.now().isoformat(),
                "message": user_message,
                "error": str(e)
            }
    
    def analyze_conversation_batch(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze entire conversation for entities and insights."""
        try:
            session_id = conversation_data.get('session_id', 'unknown')
            messages = conversation_data.get('messages', [])
            
            print_comprehend(f"Analyzing conversation {session_id} with {len(messages)} messages")
            
            # Combine all messages into a single text for analysis
            full_text = ""
            user_messages = []
            
            for msg in messages:
                if msg.get('role') == 'user':
                    user_messages.append(msg.get('content', ''))
                    full_text += msg.get('content', '') + " "
                elif msg.get('role') == 'assistant':
                    full_text += msg.get('content', '') + " "
            
            if not full_text.strip():
                print_warning("No text to analyze in conversation")
                return {"error": "No text to analyze"}
            
            # Analyze entities
            entities_response = self.comprehend.detect_entities(
                Text=full_text,
                LanguageCode='es'
            )
            
            # Analyze sentiment of the entire conversation
            sentiment_response = self.comprehend.detect_sentiment(
                Text=full_text,
                LanguageCode='es'
            )
            
            # Analyze key phrases
            key_phrases_response = self.comprehend.detect_key_phrases(
                Text=full_text,
                LanguageCode='es'
            )
            
            # Create analysis result
            analysis_result = {
                "session_id": session_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "message_count": len(messages),
                "user_message_count": len(user_messages),
                "conversation_length": len(full_text),
                "sentiment": {
                    "overall": sentiment_response['Sentiment'],
                    "confidence": sentiment_response['SentimentScore'][sentiment_response['Sentiment'].capitalize()],
                    "scores": sentiment_response['SentimentScore']
                },
                "entities": [
                    {
                        "text": entity['Text'],
                        "type": entity['Type'],
                        "confidence": entity['Score']
                    }
                    for entity in entities_response['Entities']
                ],
                "key_phrases": [
                    {
                        "text": phrase['Text'],
                        "confidence": phrase['Score']
                    }
                    for phrase in key_phrases_response['KeyPhrases']
                ],
                "user_sentiment_trend": self._analyze_user_sentiment_trend(user_messages),
                "conversation_insights": self._generate_insights(entities_response, key_phrases_response, sentiment_response)
            }
            
            # Store analysis result
            self.analysis_data["conversations"][session_id] = analysis_result
            self._save_analysis_data()
            
            print_success(f"Conversation analysis completed for {session_id}")
            return analysis_result
            
        except Exception as e:
            print_error(f"Error analyzing conversation: {e}")
            return {"error": str(e), "session_id": session_id}
    
    def _analyze_user_sentiment_trend(self, user_messages: List[str]) -> Dict[str, Any]:
        """Analyze sentiment trend across user messages."""
        if not user_messages:
            return {"trend": "stable", "sentiment_changes": 0}
        
        sentiments = []
        for message in user_messages:
            try:
                response = self.comprehend.detect_sentiment(
                    Text=message,
                    LanguageCode='es'
                )
                sentiments.append(response['Sentiment'])
            except:
                sentiments.append('NEUTRAL')
        
        # Count sentiment changes
        changes = 0
        for i in range(1, len(sentiments)):
            if sentiments[i] != sentiments[i-1]:
                changes += 1
        
        # Determine trend
        if changes == 0:
            trend = "stable"
        elif changes <= len(sentiments) * 0.3:
            trend = "slightly_variable"
        else:
            trend = "highly_variable"
        
        return {
            "trend": trend,
            "sentiment_changes": changes,
            "total_messages": len(sentiments),
            "sentiment_sequence": sentiments
        }
    
    def _generate_insights(self, entities_response, key_phrases_response, sentiment_response) -> List[str]:
        """Generate actionable insights from the analysis."""
        insights = []
        
        # Sentiment insights
        sentiment = sentiment_response['Sentiment']
        confidence = sentiment_response['SentimentScore'][sentiment.capitalize()]
        
        if sentiment == 'NEGATIVE' and confidence > 0.8:
            insights.append("High negative sentiment detected - consider immediate follow-up")
        elif sentiment == 'POSITIVE' and confidence > 0.8:
            insights.append("Very positive interaction - good customer experience")
        
        # Entity insights
        entities = entities_response['Entities']
        person_entities = [e for e in entities if e['Type'] == 'PERSON']
        if person_entities:
            insights.append(f"Customer mentioned {len(person_entities)} person(s) - potential family/business context")
        
        # Key phrases insights
        key_phrases = key_phrases_response['KeyPhrases']
        urgent_keywords = ['urgente', 'problema', 'error', 'queja', 'reclamo', 'emergencia']
        urgent_phrases = [kp for kp in key_phrases if any(keyword in kp['Text'].lower() for keyword in urgent_keywords)]
        if urgent_phrases:
            insights.append("Urgent keywords detected - prioritize this conversation")
        
        return insights
    
    def get_conversation_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results for a specific conversation."""
        return self.analysis_data["conversations"].get(session_id)
    
    def get_sentiment_summary(self) -> Dict[str, Any]:
        """Get summary of sentiment analysis across all conversations."""
        sentiment_history = self.analysis_data.get("sentiment_history", [])
        
        if not sentiment_history:
            return {"total_analyses": 0}
        
        # Count sentiment distribution
        sentiment_counts = {}
        total_confidence = 0
        
        for analysis in sentiment_history:
            sentiment = analysis.get('sentiment', 'NEUTRAL')
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            total_confidence += analysis.get('confidence', 0.5)
        
        return {
            "total_analyses": len(sentiment_history),
            "sentiment_distribution": sentiment_counts,
            "average_confidence": total_confidence / len(sentiment_history),
            "recent_analyses": sentiment_history[-10:]  # Last 10 analyses
        }

# Global instance
comprehend_analyzer = ComprehendAnalyzer()
