# Jarvis - Asistente Personal AI de VIC - ja!

## Descripción
Jarvis es un asistente personal AI que combina la potencia de los modelos de lenguaje locales con una interfaz gráfica moderna y un sistema de gestión de conocimiento. Está diseñado para ser fácil de usar, eficiente y capaz de aprender de nuevas fuentes de información.

## Tecnologías Utilizadas

### Modelos de IA
- **Ollama**: Motor de modelos de lenguaje local
  - Modelo principal: `mistral:7b-instruct`
  - Modelo de embeddings: `nomic-embed-text`
- **LangChain**: Framework para aplicaciones de IA
  - `langchain-ollama`: Integración con Ollama
  - `langchain-community`: Componentes comunitarios

### Base de Datos Vectorial
- **FAISS**: Base de datos vectorial de Facebook AI para almacenamiento y búsqueda semántica
  - Almacenamiento persistente en `vector_store/`
  - Optimizado para embeddings de HuggingFace
  - Alto rendimiento en búsquedas de similitud

### Interfaz Gráfica
- **CustomTkinter**: Framework moderno para interfaces gráficas
  - Tema oscuro personalizado
  - Diseño responsive
  - Manejo asíncrono de eventos

### Dependencias Principales
```
requests>=2.31.0
customtkinter>=5.2.2
langchain>=0.1.9
langchain-community>=0.0.24
langchain-ollama>=0.0.3
```

## Arquitectura

### 1. Componente LLM (`llm.py`)
```python
class OllamaManager:
    def __init__(self):
        self.api_base = "http://localhost:11434/api"
        self.model_name = "mistral:7b-instruct"
```
- Maneja la comunicación con Ollama
- Verifica la conexión y disponibilidad del modelo
- Procesa prompts y genera respuestas
- Manejo especial de respuestas en streaming:
  * Reconstrucción de mensajes fragmentados
  * Procesamiento línea por línea de respuestas JSON
  * Tolerancia a fallos en líneas individuales

### 2. Sistema de Conocimiento (`knowledge.py`)
```python
class KnowledgeManager:
    def __init__(self):
        self.vectorstore = FAISS(
            persist_directory="vector_store",
            embedding_function=self.embeddings
        )
```
- Gestiona la base de conocimiento vectorial con FAISS
- Procesa y almacena documentos
- Realiza búsquedas semánticas para contexto
- Optimizado para búsquedas rápidas y eficientes

### 3. Interfaz Gráfica (`gui.py`)
```python
class JarvisGUI:
    def __init__(self, on_send_message):
        self.root = ctk.CTk()
        self.message_queue = queue.Queue()
```
- Interfaz moderna y responsive
- Manejo asíncrono de mensajes
- Sistema de estado y notificaciones

### 4. Controlador Principal (`main.py`)
```python
class Jarvis:
    def __init__(self):
        self.gui = JarvisGUI(on_send_message=self.handle_message)
        self.llm = OllamaManager()
        self.knowledge = KnowledgeManager()
```
- Coordina todos los componentes
- Maneja el flujo de mensajes
- Gestiona errores y estados

## Prompt del Sistema

El prompt base utilizado para las interacciones con el modelo es:

```
Eres Jarvis, un asistente personal AI. Responde de manera clara y concisa.

[Contexto relevante si existe]

Pregunta: [mensaje del usuario]
```

## Características Principales

### 1. Procesamiento de Mensajes
- Manejo asíncrono de solicitudes
- Sistema de cola para mensajes
- Respuestas en tiempo real

### 2. Gestión de Conocimiento
- Carga de archivos de texto y JSON
- Búsqueda semántica de contexto relevante usando FAISS
- Persistencia de datos en vector_store

### 3. Comandos del Sistema
```
/ayuda   - Muestra la ayuda disponible
/cargar  - Carga un archivo de conocimiento
/limpiar - Limpia la base de conocimiento
/estado  - Muestra el estado de los servicios
```

### 4. Manejo de Errores
- Verificación de conexión con Ollama
- Modo limitado cuando no hay conexión
- Logging detallado de errores

## Instalación y Uso

### Requisitos Previos
1. Python 3.8 o superior
2. Ollama instalado y configurado
3. Modelos necesarios descargados:
   ```bash
   ollama pull mistral:7b-instruct
   ollama pull nomic-embed-text
   ```

### Instalación
1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Uso
1. Iniciar el servicio de Ollama:
   ```bash
   ollama serve
   ```

2. En otra terminal, iniciar Jarvis:
   ```bash
   python main.py
   ```

## Mejores Prácticas

### Gestión de Conocimiento
- Dividir documentos grandes en chunks manejables
- Mantener la base de conocimiento actualizada
- Usar tags para organizar la información

### Rendimiento
- Monitorear el uso de memoria de FAISS
- Mantener un tamaño razonable de contexto
- Limpiar la base de conocimiento periódicamente

### Seguridad
- No almacenar información sensible
- Verificar archivos antes de cargarlos
- Mantener Ollama y dependencias actualizadas

## Troubleshooting

### Problemas Comunes
1. **Ollama no responde**
   - Verificar que el servicio esté corriendo
   - Comprobar el puerto 11434
   - Revisar logs de Ollama
   - Verificar que no hay problemas de red

2. **Errores de memoria**
   - Reducir el tamaño de chunks
   - Limpiar la base de conocimiento
   - Monitorear uso de RAM

3. **GUI no responde**
   - Verificar hilos de procesamiento
   - Revisar cola de mensajes
   - Comprobar logs de la aplicación

4. **Respuestas incompletas**
   - Verificar el timeout de la conexión (default 60s)
   - Comprobar que la reconstrucción de mensajes es correcta
   - Revisar los logs por errores de parsing

## Desarrollo Futuro

### Mejoras Planificadas
1. Soporte para más formatos de archivo
2. Interfaz web opcional
3. Sistema de plugins
4. Mejoras en el manejo de contexto
5. Integración con más modelos de Ollama 