# Jarvis - Personal AI Assistant

Un asistente personal de IA que se ejecuta localmente usando Ollama.

## Requisitos

- Python 3.10 o superior
- [Ollama](https://ollama.ai/) instalado
- Windows 11 (probado en Windows 11, puede funcionar en Windows 10)
- Modelo Mistral instalado en Ollama

## Instalación

1. Clona este repositorio

2. Crea un entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Instala Ollama desde https://ollama.ai/download

5. Instala el modelo Mistral:
```bash
ollama pull mistral:7b-instruct
```

6. Verifica la instalación:
```bash
ollama list
```

Deberías ver `mistral:7b-instruct` en la lista de modelos.

## Uso

1. Activa el entorno virtual:
```bash
.\venv\Scripts\activate
```

2. Ejecuta Jarvis:
```bash
python main.py
```

## Comandos Disponibles

- Preguntas generales: Simplemente escribe tu pregunta
- `INYECTAR <archivo> [descripción]`: Inyecta conocimiento desde un archivo
- `DESINYECTAR <id_fuente>`: Elimina conocimiento inyectado
- `TOKENS <n>`: Establece el máximo de tokens para las respuestas
- `CARGAR <archivo>`: Carga y muestra un archivo de conocimiento
- `RESUMIR <archivo>`: Muestra un resumen de un archivo
- `SALIR`: Cierra el programa

## Estructura del Proyecto

- `main.py`: Programa principal y manejo de comandos
- `knowledge.py`: Módulo de gestión de conocimiento usando FAISS para búsqueda semántica
- `llm.py`: Integración con Ollama y manejo del modelo
- `requirements.txt`: Dependencias del proyecto
- `vector_store/`: Directorio donde se almacenan los vectores de FAISS
- `conocimiento_manual/`: Directorio para archivos de conocimiento

## Desarrollo

- Usa nombres en inglés para variables y funciones
- Sigue las guías de estilo PEP 8
- Agrega docstrings a funciones y clases
- Maneja los errores apropiadamente

## Solución de Problemas

Si encuentras errores:

1. Verifica que Ollama esté instalado y corriendo:
```bash
ollama list
```

2. Asegúrate de tener el modelo correcto:
```bash
ollama pull mistral:7b-instruct
```

3. Revisa los logs en `jarvis.log`

4. Errores comunes:
   - "model not found": Ejecuta `ollama pull mistral:7b-instruct`
   - "connection refused": Inicia el servicio de Ollama
   - "out of memory": Reduce el número de tokens con `TOKENS 256`
   - "vector_store no encontrado": Es normal en la primera ejecución, se creará automáticamente

## Integraciones Futuras

El proyecto está diseñado para extenderse con:
- Integración con Google Drive
- API de Gmail
- API de WhatsApp
- Calendario y recordatorios
- Skills personalizados 