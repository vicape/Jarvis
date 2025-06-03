from langchain_ollama import ChatOllama
from knowledge import KnowledgeManager
from langchain_community.cache import InMemoryCache
from langchain_core.globals import set_llm_cache
import langchain_core as langchain
import time
import subprocess
import os

# Activar caché para respuestas repetidas
langchain.llm_cache = InMemoryCache()
set_llm_cache(langchain.llm_cache)

# Variables globales
model_instance = None
last_request_time = 0
last_restart_time = 0
REQUEST_TIMEOUT = 120  # aumentado a 2 minutos
RESTART_COOLDOWN = 300  # 5 minutos entre reinicios
STARTUP_WAIT = 10  # segundos de espera tras inicio

def restart_ollama():
    """Reinicia el servicio de Ollama."""
    global last_restart_time
    current_time = time.time()
    
    # Evitar reinicios muy frecuentes
    if current_time - last_restart_time < RESTART_COOLDOWN:
        print("⚠️ Reinicio de Ollama solicitado muy pronto, esperando...")
        return False
        
    try:
        print("\n🔄 Reiniciando servicio Ollama...")
        if os.name == 'nt':  # Windows
            # En Windows, usamos taskkill para forzar el cierre
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            time.sleep(5)  # Más tiempo para asegurar cierre
            # Iniciar Ollama con el comando start
            subprocess.Popen(['ollama', 'start'], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=True)
        else:  # Linux/Mac
            subprocess.run(['ollama', 'stop'], check=True)
            time.sleep(5)
            subprocess.run(['ollama', 'start'], check=True)
        
        time.sleep(STARTUP_WAIT)  # Esperar más tiempo para inicio completo
        last_restart_time = current_time
        print("✅ Servicio Ollama reiniciado")
        return True
    except Exception as e:
        print(f"⚠️ Error al reiniciar Ollama: {str(e)}")
        print("Por favor, reinicia Ollama manualmente con el comando: ollama start")
        return False

def get_model():
    """Obtiene una nueva instancia del modelo."""
    global model_instance
    try:
        model_instance = ChatOllama(
            model="mistral:7b-instruct",
            temperature=0.7,
            num_ctx=2048,
            num_predict=256,
            num_thread=6,
            timeout=30,
            mirostat=2,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.1,
            num_gpu=1
        )
        return model_instance
    except Exception as e:
        print(f"⚠️ Error al crear instancia del modelo: {str(e)}")
        return None

# Cargar gestor de conocimiento
try:
    km = KnowledgeManager()
    model_instance = get_model()
except Exception as e:
    print(f"⚠️ Error al inicializar el gestor de conocimiento: {str(e)}")
    raise

def generate_response(user_input):
    global model_instance, last_request_time
    current_time = time.time()
    
    try:
        if not user_input or not user_input.strip():
            return "Lo siento, no he recibido ninguna pregunta. ¿Podrías reformularla?"

        # Solo reiniciar si el modelo está realmente inactivo
        if current_time - last_request_time > REQUEST_TIMEOUT and model_instance is None:
            print("\n⚠️ Modelo no disponible, intentando reiniciar...")
            if restart_ollama():
                model_instance = get_model()
            else:
                return "El sistema necesita un descanso. Por favor, espera unos minutos antes de intentar de nuevo."

        # Asegurarse de que tenemos una instancia válida del modelo
        if model_instance is None:
            model_instance = get_model()
            if model_instance is None:
                return "No se pudo inicializar el modelo. Por favor, verifica que Ollama esté funcionando."

        # Actualizar tiempo de última petición
        last_request_time = current_time

        # 🔍 Buscar contexto relevante
        print("\n🔍 Buscando información relevante...")
        context_fragments = km.query(user_input, k=2)
        
        if not context_fragments:
            context_text = "No hay información específica sobre esto en mi base de conocimiento."
        else:
            context_text = "\n".join([doc.page_content for doc in context_fragments])
        
        # 🧠 Crear prompt
        prompt = f"""Eres Jarvis, un asistente personal. Estás hablando con Victor (el padre). 
Usa este contexto para responder: {context_text}
Pregunta de Victor: {user_input}
Responde de forma breve y precisa, manteniendo en mente que hablas con Victor, no con sus hijos."""
        
        # 📡 Consultar modelo con timeout
        print("\n🧠 Consultando modelo Mistral...")
        start_time = time.time()
        
        try:
            response = model_instance.invoke(prompt).content
            
            # Verificar timeout
            if time.time() - start_time > REQUEST_TIMEOUT:
                print("\n⚠️ Respuesta demasiado lenta, intentando reiniciar...")
                if restart_ollama():
                    model_instance = get_model()
                return "Lo siento, la respuesta está tardando demasiado. Por favor, intenta de nuevo en unos minutos."
                
            if response and response.strip():
                # 💾 Guardar interacción
                km.add_interaction_to_history(user_input, response)
                return response
            else:
                return "Lo siento, no he podido generar una respuesta coherente. ¿Podrías reformular tu pregunta?"
                
        except Exception as model_error:
            print(f"\n⚠️ Error en el modelo: {str(model_error)}")
            if "timeout" in str(model_error).lower():
                print("Detectado timeout, esperando antes de reiniciar...")
                time.sleep(10)  # Esperar antes de reiniciar
            if restart_ollama():
                model_instance = get_model()
            return "Lo siento, hubo un error al procesar tu pregunta. Por favor, espera unos minutos e intenta de nuevo."
            
    except Exception as e:
        error_msg = f"Lo siento, ha ocurrido un error: {str(e)}"
        print(f"⚠️ Error al generar respuesta: {str(e)}")
        return error_msg
