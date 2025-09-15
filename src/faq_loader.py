# -*- coding: utf-8 -*-
"""
Cargador de FAQ (Preguntas Frecuentes) para el asistente bancario.
"""
import csv

def get_faq_text() -> str:
    """Lee el CSV de FAQ y devuelve el texto formateado."""
    try:
        faq_text = "\n\nPREGUNTAS FRECUENTES (FAQ):\n"
        
        with open('data/faq.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, 1):
                pregunta = row.get('pregunta', '').strip()
                respuesta = row.get('respuesta', '').strip()
                categoria = row.get('categoria', '').strip()
                
                if pregunta and respuesta:
                    faq_text += f"{i}. P: {pregunta}\n"
                    faq_text += f"   R: {respuesta}\n"
                    faq_text += f"   Categoría: {categoria}\n\n"
        
        return faq_text
        
    except Exception as e:
        print(f"❌ Error cargando FAQ: {e}")
        return ""