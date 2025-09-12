#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio para el Asistente Bancario con colores.

Uso:
    python start_bot.py

Opciones:
    --port: Puerto para el servidor (default: 5000)
    --host: Host para el servidor (default: 0.0.0.0)
    --mock: Usar modo mock sin AWS (para desarrollo)
"""
import argparse
import sys
import os
from src.colors import *
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)


def main():
    parser = argparse.ArgumentParser(description='Iniciar el Asistente Bancario')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor')
    parser.add_argument('--host', default='0.0.0.0', help='Host del servidor')
    parser.add_argument('--mock', action='store_true', help='Usar modo mock (sin AWS)')
    
    args = parser.parse_args()
    
    print_header("Asistente Bancario")
    
    if args.mock:
        os.environ['MOCK_MODE'] = 'true'
        print_warning("Modo mock activado - Sin conexión a AWS")
    else:
        # Verificar credenciales AWS
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            print_success("Credenciales AWS configuradas - Usando Bedrock real")
        else:
            print_warning("Credenciales AWS no configuradas - Usando modo mock")
            os.environ['MOCK_MODE'] = 'true'
    
    print_system(f"Servidor: http://{args.host}:{args.port}")
    print_info("Para detener el servidor: Ctrl+C")
    
    try:
        from src.web_server import app
        import uvicorn
        
        print_loading("Iniciando servidor")
        
        uvicorn.run(
            app, 
            host=args.host, 
            port=args.port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print_success("Servidor detenido")
    except Exception as e:
        print_error(f"Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
