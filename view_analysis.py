#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
View Comprehend analysis results.
"""
import json
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.comprehend_analyzer import comprehend_analyzer
from src.memory import memory
from src.colors import print_header, print_success, print_info, print_warning

def view_sentiment_summary():
    """View sentiment analysis summary."""
    print_header("Sentiment Analysis Summary")
    
    try:
        summary = comprehend_analyzer.get_sentiment_summary()
        
        print_info(f"Total sentiment analyses: {summary.get('total_analyses', 0)}")
        print_info(f"Average confidence: {summary.get('average_confidence', 0):.2f}")
        
        distribution = summary.get('sentiment_distribution', {})
        if distribution:
            print_info("Sentiment distribution:")
            for sentiment, count in distribution.items():
                percentage = (count / summary.get('total_analyses', 1)) * 100
                print(f"  {sentiment}: {count} ({percentage:.1f}%)")
        
        recent = summary.get('recent_analyses', [])
        if recent:
            print_info(f"\nRecent analyses (last {len(recent)}):")
            for analysis in recent[-5:]:  # Show last 5
                print(f"  {analysis.get('sentiment', 'UNKNOWN')} (confidence: {analysis.get('confidence', 0):.2f}) - {analysis.get('message', '')[:50]}...")
        
    except Exception as e:
        print_warning(f"Error loading sentiment summary: {e}")

def view_conversation_analyses():
    """View conversation analysis results."""
    print_header("Conversation Analysis Results")
    
    try:
        analysis_data = comprehend_analyzer.analysis_data
        conversations = analysis_data.get('conversations', {})
        
        if not conversations:
            print_info("No conversation analyses found")
            return
        
        print_info(f"Total analyzed conversations: {len(conversations)}")
        
        for session_id, analysis in conversations.items():
            print(f"\n📊 Session: {session_id}")
            print(f"  Analysis time: {analysis.get('analysis_timestamp', 'Unknown')}")
            print(f"  Messages: {analysis.get('message_count', 0)}")
            print(f"  Overall sentiment: {analysis.get('sentiment', {}).get('overall', 'Unknown')}")
            print(f"  Confidence: {analysis.get('sentiment', {}).get('confidence', 0):.2f}")
            
            entities = analysis.get('entities', [])
            if entities:
                print(f"  Entities found: {len(entities)}")
                for entity in entities[:3]:  # Show first 3
                    print(f"    - {entity.get('text', '')} ({entity.get('type', '')})")
            
            insights = analysis.get('conversation_insights', [])
            if insights:
                print(f"  Key insights:")
                for insight in insights:
                    print(f"    - {insight}")
        
    except Exception as e:
        print_warning(f"Error loading conversation analyses: {e}")

def view_memory_status():
    """View memory status and conversation tracking."""
    print_header("Memory Status")
    
    try:
        conversations = memory.conversations
        
        if not conversations:
            print_info("No conversations in memory")
            return
        
        print_info(f"Total conversations in memory: {len(conversations)}")
        
        analyzed_count = 0
        unanalyzed_count = 0
        
        for session_id, conversation in conversations.items():
            metadata = conversation.get('metadata', {})
            analyzed = metadata.get('analyzed_by_comprehend', False)
            
            if analyzed:
                analyzed_count += 1
            else:
                unanalyzed_count += 1
        
        print_info(f"Analyzed by Comprehend: {analyzed_count}")
        print_info(f"Not analyzed: {unanalyzed_count}")
        
        # Show recent conversations
        print_info("\nRecent conversations:")
        for session_id, conversation in list(conversations.items())[-5:]:
            metadata = conversation.get('metadata', {})
            analyzed = metadata.get('analyzed_by_comprehend', False)
            last_activity = metadata.get('last_activity', 'Unknown')
            message_count = metadata.get('message_count', 0)
            
            status = "✅ Analyzed" if analyzed else "⏳ Pending"
            print(f"  {session_id}: {message_count} messages, {status}, last activity: {last_activity}")
        
    except Exception as e:
        print_warning(f"Error loading memory status: {e}")

def view_analysis_files():
    """View analysis files."""
    print_header("Analysis Files")
    
    files_to_check = [
        "conversation_memory.json",
        "comprehend_analysis.json"
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print_success(f"✅ {filename} ({size} bytes)")
        else:
            print_warning(f"❌ {filename} not found")

def main():
    """Main function."""
    print_header("Comprehend Analysis Viewer")
    
    try:
        view_analysis_files()
        print()
        view_memory_status()
        print()
        view_sentiment_summary()
        print()
        view_conversation_analyses()
        
    except Exception as e:
        print_warning(f"Error: {e}")

if __name__ == "__main__":
    main()
