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
│   ├── agent.py          # Lógica del asistente
│   ├── web_server.py     # Servidor FastAPI
│   ├── config.py         # Configuración
│   ├── colors.py         # Colores para consola
│   ├── memory.py         # Memoria de conversaciones
│   ├── context_loader.py # Cargador de contexto CSV
│   └── crm_adapter.py    # Integración CRM
├── data/
│   └── banesco_context.csv # Contexto de productos
├── lambda/
│   └── handler.py        # Handler para AWS Lambda
├── start_bot.py         # Script principal
├── requirements.txt     # Dependencias
└── .env                 # Variables de entorno
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

## 📁 Archivos CSV

- `data/banesco_context.csv` - Contexto de productos bancarios
- `data/crm_cases.csv` - Casos del CRM (se crea automáticamente)

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto.