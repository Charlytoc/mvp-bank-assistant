# 🏦 Asistente Bancario Banesco Panamá

Asistente bancario inteligente con integración AWS Bedrock y CRM.

## 🚀 Inicio Rápido

### 1. Configurar credenciales
```bash
# Crear archivo .env
echo "AWS_ACCESS_KEY_ID=tu_access_key" > .env
echo "AWS_SECRET_ACCESS_KEY=tu_secret_key" >> .env
echo "AWS_REGION=us-east-1" >> .env
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Iniciar el bot
```bash
# Modo real con AWS Bedrock
python start_bot.py

# Modo mock para desarrollo
python start_bot.py --mock
```

### 4. Acceder a la interfaz
Abre tu navegador en: http://localhost:5000

## 🛠️ Configuración

### Variables de Entorno
- `AWS_ACCESS_KEY_ID`: Tu clave de acceso AWS
- `AWS_SECRET_ACCESS_KEY`: Tu clave secreta AWS  
- `AWS_REGION`: Región AWS (us-east-1)
- `CRM_URL`: URL del CRM (opcional)

### Modelo AI
- **Modelo**: ai21.jamba-1-5-large-v1:0
- **Proveedor**: Amazon Bedrock
- **Idioma**: Español

## 📁 Estructura del Proyecto

```
mvp-bank-assistant/
├── src/
│   ├── agent.py              # Lógica del asistente
│   ├── web_server.py         # Servidor FastAPI
│   ├── config.py             # Configuración
│   ├── colors.py             # Colores para consola
│   ├── memory.py             # Memoria de conversaciones
│   ├── context_loader.py     # Cargador de contexto CSV
│   ├── crm_adapter.py        # Integración CRM
│   ├── comprehend_analyzer.py # Análisis con Comprehend
│   └── timer_manager.py      # Gestión de timers
├── data/
│   ├── banesco_context.csv   # Contexto de productos
│   └── faq.csv              # Preguntas frecuentes
├── lambda/
│   └── handler.py            # Handler para AWS Lambda
├── start_bot.py             # Script principal
├── view_cases.py            # Ver casos del CRM
├── view_analysis.py         # Ver análisis de Comprehend
├── manage_faq.py            # Gestión de FAQ
├── test_comprehend.py       # Probar integración Comprehend
├── requirements.txt         # Dependencias
└── .env                     # Variables de entorno
```

## 🎯 Funcionalidades

- ✅ Chat inteligente con IA (Bedrock)
- ✅ Memoria de conversaciones (20 mensajes)
- ✅ Contexto de productos bancarios
- ✅ Detección de intenciones
- ✅ CRM local con CSV
- ✅ Interfaz web moderna estilo Banesco
- ✅ Soporte para apertura de cuentas
- ✅ Respuestas en español
- ✅ Agent loop con tool calls
- ✅ **Análisis de sentimientos en tiempo real**
- ✅ **Análisis de conversaciones con Amazon Comprehend**
- ✅ **Extracción de entidades y frases clave**
- ✅ **Insights automáticos de conversaciones**

## 🔧 Desarrollo

### Modo Mock
Para desarrollo sin AWS:
```bash
python start_bot.py --mock
```

### Modo Real
Para usar AWS Bedrock:
```bash
python start_bot.py
```

### Ver Casos del CRM
Para ver los casos registrados:
```bash
python view_cases.py
```

## 🧠 **Integración Amazon Comprehend**

### **Análisis en Tiempo Real**
- Analiza el sentimiento de cada mensaje del usuario
- Proporciona puntuaciones de confianza
- Almacena historial de sentimientos para análisis de tendencias

### **Análisis por Inactividad**
- Analiza conversaciones automáticamente después de 1 minuto de inactividad
- Extrae entidades, frases clave e insights
- Genera inteligencia de negocio accionable

### **Endpoints de Análisis**
- `GET /api/analysis/sentiment` - Resumen de sentimientos
- `GET /api/analysis/conversation/{session_id}` - Análisis de conversación
- `GET /api/analysis/timers` - Timers activos
- `POST /api/analysis/analyze/{session_id}` - Forzar análisis

### **Ver Resultados de Análisis**
```bash
# Ver resultados de análisis
python view_analysis.py

# Probar integración Comprehend
python test_comprehend.py
```

## ❓ **Sistema de FAQ (Preguntas Frecuentes)**

### **Gestión de FAQ**
```bash
# Listar todas las FAQ
python manage_faq.py list

# Buscar FAQ por consulta
python manage_faq.py search "horarios de atención"

# Mostrar categorías disponibles
python manage_faq.py categories

# Agregar nueva FAQ (interactivo)
python manage_faq.py add
```

### **Archivo FAQ**
- **Ubicación**: `data/faq.csv`
- **Formato**: pregunta, respuesta, categoria
- **Integración**: Se incluye automáticamente en el system prompt de la IA

## 📁 Archivos CSV

- `data/banesco_context.csv` - Contexto de productos bancarios
- `data/crm_cases.csv` - Casos del CRM (se crea automáticamente)

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto.