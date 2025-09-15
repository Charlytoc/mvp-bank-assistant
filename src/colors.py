# -*- coding: utf-8 -*-
"""
Sistema de colores para la consola del asistente bancario.
"""
import os
import sys

# Códigos de color ANSI
class Colors:
    # Colores básicos
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Colores brillantes
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_YELLOW = '\033[93;1m'
    BRIGHT_BLUE = '\033[94;1m'
    BRIGHT_MAGENTA = '\033[95;1m'
    BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_WHITE = '\033[97;1m'
    
    # Fondos
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_MAGENTA = '\033[105m'
    BG_CYAN = '\033[106m'
    BG_WHITE = '\033[107m'
    
    # Estilos
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'

def colored_print(text, color=Colors.WHITE, style=Colors.RESET, end='\n'):
    """Imprime texto con color y estilo."""
    if os.name == 'nt':  # Windows
        # En Windows, solo usar colores si se soporta
        try:
            import colorama
            colorama.init()
            print(f"{color}{style}{text}{Colors.RESET}", end=end)
        except ImportError:
            print(text, end=end)
    else:  # Unix/Linux/macOS
        print(f"{color}{style}{text}{Colors.RESET}", end=end)

def print_success(text):
    """Imprime texto de éxito en verde."""
    colored_print(f"✅ {text}", Colors.GREEN, Colors.BOLD)

def print_error(text):
    """Imprime texto de error en rojo."""
    colored_print(f"❌ {text}", Colors.RED, Colors.BOLD)

def print_warning(text):
    """Imprime texto de advertencia en amarillo."""
    colored_print(f"⚠️ {text}", Colors.YELLOW, Colors.BOLD)

def print_info(text):
    """Imprime texto informativo en azul."""
    colored_print(f"ℹ️ {text}", Colors.BLUE, Colors.BOLD)

def print_bot(text):
    """Imprime mensaje del bot en cyan."""
    colored_print(f"🤖 Bot: {text}", Colors.CYAN, Colors.BOLD)

def print_user(text):
    """Imprime mensaje del usuario en magenta."""
    colored_print(f"👤 Usuario: {text}", Colors.MAGENTA, Colors.BOLD)

def print_system(text):
    """Imprime mensaje del sistema en blanco brillante."""
    colored_print(f"🔧 {text}", Colors.BRIGHT_WHITE, Colors.BOLD)

def print_aws(text):
    """Imprime mensaje de AWS en naranja."""
    colored_print(f"☁️ AWS: {text}", Colors.YELLOW, Colors.BOLD)

def print_crm(text):
    """Imprime mensaje de CRM en verde brillante."""
    colored_print(f"📋 CRM: {text}", Colors.BRIGHT_GREEN, Colors.BOLD)

def print_header(text):
    """Imprime encabezado con fondo azul."""
    colored_print(f"\n{'='*60}", Colors.BLUE, Colors.BOLD)
    colored_print(f"🏦 {text}", Colors.WHITE, Colors.BOLD + Colors.BG_BLUE)
    colored_print(f"{'='*60}\n", Colors.BLUE, Colors.BOLD)

def print_step(step, text):
    """Imprime paso numerado."""
    colored_print(f"📝 Paso {step}: {text}", Colors.CYAN, Colors.BOLD)

def print_loading(text):
    """Imprime texto de carga con animación."""
    import time
    for i in range(3):
        colored_print(f"⏳ {text}{'.' * (i + 1)}", Colors.YELLOW, Colors.BOLD, end='\r')
        time.sleep(0.5)
    print()  # Nueva línea

def print_json(data, title="JSON"):
    """Imprime JSON formateado con colores."""
    import json
    colored_print(f"\n📄 {title}:", Colors.BLUE, Colors.BOLD)
    try:
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        colored_print(formatted, Colors.WHITE, Colors.DIM)
    except Exception as e:
        colored_print(f"Error formateando JSON: {e}", Colors.RED, Colors.BOLD)

def print_table(data, headers=None):
    """Imprime tabla con colores."""
    if not data:
        return
    
    # Calcular anchos de columna
    if headers:
        col_widths = [len(str(header)) for header in headers]
    else:
        col_widths = [len(str(item)) for item in data[0]]
    
    for row in data:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(item)))
    
    # Imprimir encabezados
    if headers:
        colored_print("┌" + "┬".join("─" * (width + 2) for width in col_widths) + "┐", Colors.BLUE)
        header_row = "│"
        for i, header in enumerate(headers):
            header_row += f" {str(header):<{col_widths[i]}} │"
        colored_print(header_row, Colors.BLUE, Colors.BOLD)
        colored_print("├" + "┼".join("─" * (width + 2) for width in col_widths) + "┤", Colors.BLUE)
    
    # Imprimir filas
    for row in data:
        row_str = "│"
        for i, item in enumerate(row):
            row_str += f" {str(item):<{col_widths[i]}} │"
        colored_print(row_str, Colors.WHITE)
    
    colored_print("└" + "┴".join("─" * (width + 2) for width in col_widths) + "┘", Colors.BLUE)

# Función para deshabilitar colores si es necesario
def disable_colors():
    """Deshabilita todos los colores."""
    global Colors
    for attr in dir(Colors):
        if not attr.startswith('_'):
            setattr(Colors, attr, '')

# Verificar si los colores están soportados
def colors_supported():
    """Verifica si los colores están soportados en la terminal."""
    return (
        hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
        os.environ.get('TERM') != 'dumb' and
        os.name != 'nt' or 'ANSICON' in os.environ
    )

# Auto-detectar soporte de colores
if not colors_supported():
    disable_colors()

def print_comprehend(message: str):
    """Print Comprehend-related message."""
    colored_print(f"🧠 [Comprehend] {message}", Colors.MAGENTA, Colors.BOLD)

def print_timer(message: str):
    """Print timer-related message."""
    colored_print(f"⏰ [Timer] {message}", Colors.CYAN, Colors.BOLD)
