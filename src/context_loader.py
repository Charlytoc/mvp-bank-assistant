# -*- coding: utf-8 -*-
"""
Cargador de contexto CSV para el asistente bancario.
"""
import csv
import os
from typing import List, Dict

def load_banesco_context() -> str:
    """Carga el contexto de productos bancarios desde CSV."""
    csv_path = "data/banesco_context.csv"
    
    if not os.path.exists(csv_path):
        return "No se encontró el archivo de contexto de productos."
    
    try:
        context = "Información de productos bancarios de Banesco Panamá:\n\n"
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            current_category = None
            for row in reader:
                categoria = row['categoria']
                producto = row['producto']
                descripcion = row['descripcion']
                requisitos = row['requisitos']
                beneficios = row['beneficios']
                tarifa = row['tarifa']
                
                if categoria != current_category:
                    context += f"\n## {categoria.upper()}\n"
                    current_category = categoria
                
                context += f"**{producto}**\n"
                context += f"- Descripción: {descripcion}\n"
                context += f"- Requisitos: {requisitos}\n"
                context += f"- Beneficios: {beneficios}\n"
                context += f"- Tarifa: {tarifa}\n\n"
        
        return context
        
    except Exception as e:
        return f"Error cargando contexto: {e}"

def get_product_recommendations(user_message: str, context: str) -> str:
    """Genera recomendaciones de productos basadas en el mensaje del usuario."""
    # Palabras clave para detectar necesidades
    keywords = {
        'ahorro': ['ahorro', 'guardar', 'dinero', 'futuro'],
        'transacciones': ['transacciones', 'compras', 'pagos', 'diario'],
        'empresa': ['empresa', 'negocio', 'comercial', 'trabajo'],
        'credito': ['prestamo', 'credito', 'dinero', 'financiamiento'],
        'inversion': ['inversion', 'rendimiento', 'ganar', 'interes'],
        'seguro': ['seguro', 'proteccion', 'vida', 'vehiculo']
    }
    
    user_lower = user_message.lower()
    recommendations = []
    
    for category, words in keywords.items():
        if any(word in user_lower for word in words):
            if category == 'ahorro':
                recommendations.append("Te recomiendo nuestra Cuenta de Ahorros con interés del 2% anual")
            elif category == 'transacciones':
                recommendations.append("Te recomiendo nuestra Cuenta Corriente con chequera gratuita")
            elif category == 'empresa':
                recommendations.append("Te recomiendo nuestra Cuenta Empresarial con asesoría especializada")
            elif category == 'credito':
                recommendations.append("Tenemos Préstamos Personales, Hipotecarios y Vehiculares")
            elif category == 'inversion':
                recommendations.append("Ofrecemos Certificados de Depósito y Fondos de Inversión")
            elif category == 'seguro':
                recommendations.append("Tenemos Seguros de Vida y Vehículo para tu protección")
    
    if recommendations:
        return "Basándome en tu consulta, " + " y ".join(recommendations) + "."
    
    return ""
