from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import os
import time
from functools import lru_cache
from typing import List
from datetime import datetime
import threading

class KnowledgeManager:
    def __init__(self, 
                 docs_path: str = "conocimiento_manual",
                 vectorstore_path: str = "vector_store",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):

        self.docs_path = docs_path
        self.vectorstore_path = vectorstore_path
        self.embedding_model = embedding_model
        self.conversation_history_file = os.path.join(docs_path, "conversacion_historial.txt")
        self._lock = threading.Lock()
        self._last_check = 0
        self._check_interval = 5  # segundos entre verificaciones
        
        # Asegurar que los directorios existan
        os.makedirs(self.docs_path, exist_ok=True)
        os.makedirs(self.vectorstore_path, exist_ok=True)
        
        print(f"🤖 Inicializando modelo de embeddings {self.embedding_model}...")
        print("⚠️ La primera vez puede tardar unos minutos en descargar el modelo...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Modelo de embeddings cargado correctamente")

        # Inicializar vectorstore
        self.load_or_create_vectorstore()

    def check_for_updates(self):
        """Verifica si hay actualizaciones en los archivos de conocimiento."""
        current_time = time.time()
        if current_time - self._last_check < self._check_interval:
            return False

        self._last_check = current_time
        try:
            files = []
            for root, _, filenames in os.walk(self.docs_path):
                for filename in filenames:
                    if filename.endswith('.txt'):
                        file_path = os.path.join(root, filename)
                        files.append((file_path, os.path.getmtime(file_path)))
            
            if not hasattr(self, '_last_files'):
                self._last_files = files
                return False

            if files != self._last_files:
                self._last_files = files
                return True
                
            return False
        except Exception as e:
            print(f"⚠️ Error al verificar actualizaciones: {str(e)}")
            return False

    def load_or_create_vectorstore(self):
        """Carga o crea el vectorstore."""
        with self._lock:
            try:
                if os.path.exists(os.path.join(self.vectorstore_path, "index.faiss")):
                    print("📥 Cargando vectorstore desde disco...")
                    self.vectorstore = FAISS.load_local(
                        self.vectorstore_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    print("✅ Vectorstore cargado correctamente")
                else:
                    print("🆕 Creando nuevo vectorstore...")
                    self.vectorstore = self._create_vectorstore()
                    self.save_vectorstore()
                    print("✅ Vectorstore creado y guardado correctamente")
            except Exception as e:
                print(f"⚠️ Error al cargar/crear vectorstore: {str(e)}")
                print("🔄 Intentando crear nuevo vectorstore...")
                self.vectorstore = self._create_vectorstore()
                self.save_vectorstore()

    def save_vectorstore(self):
        """Guarda el vectorstore en disco."""
        with self._lock:
            try:
                print("💾 Guardando vectorstore en disco...")
                self.vectorstore.save_local(self.vectorstore_path)
                print("✅ Vectorstore guardado correctamente")
            except Exception as e:
                print(f"⚠️ Error al guardar vectorstore: {str(e)}")

    def reload_knowledge(self):
        """Recarga la base de conocimiento."""
        with self._lock:
            try:
                print("🔄 Recargando base de conocimiento...")
                new_vectorstore = self._create_vectorstore()
                self.vectorstore = new_vectorstore
                self.save_vectorstore()
                print("✅ Base de conocimiento actualizada")
            except Exception as e:
                print(f"⚠️ Error al recargar base de conocimiento: {str(e)}")

    def add_interaction_to_history(self, user_input: str, response: str):
        """Agrega una interacción a la historia y actualiza la base de conocimiento."""
        with self._lock:
            try:
                # Crear el texto de la interacción
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                interaction = f"\n--- Interacción {timestamp} ---\nPregunta: {user_input}\nRespuesta: {response}\n"
                
                # Guardar en archivo de historia
                os.makedirs(self.docs_path, exist_ok=True)
                with open(self.conversation_history_file, "a", encoding="utf-8") as f:
                    f.write(interaction)
                
                # Actualizar vectorstore con la nueva interacción
                doc = Document(page_content=interaction)
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=200,
                    chunk_overlap=20,
                    separators=["\n\n", "\n", ".", "!", "?", ",", " "],
                )
                docs = splitter.split_documents([doc])
                self.vectorstore.add_documents(docs)
                print("✨ Nueva interacción agregada a la base de conocimiento")
            except Exception as e:
                print(f"⚠️ Error al agregar interacción: {str(e)}")

    def _create_vectorstore(self) -> FAISS:
        print(f"📂 Cargando documentos desde: {self.docs_path}")
        
        try:
            loader = DirectoryLoader(
                self.docs_path,
                glob="**/*.txt",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"}
            )
            raw_docs = loader.load()

            if not raw_docs:
                print("⚠️ No se encontraron documentos. Creando vectorstore vacío...")
                return FAISS.from_texts(["Bienvenido a Jarvis"], embedding=self.embeddings)

            print(f"✂️ Dividiendo {len(raw_docs)} documentos...")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=200,
                chunk_overlap=20,
                separators=["\n\n", "\n", ".", "!", "?", ",", " "],
                length_function=len,
                is_separator_regex=False
            )
            docs = splitter.split_documents(raw_docs)
            print(f"✅ {len(docs)} fragmentos generados.")

            return FAISS.from_documents(docs, self.embeddings)
        except Exception as e:
            print(f"⚠️ Error al crear vectorstore: {str(e)}")
            return FAISS.from_texts(["Error al cargar documentos"], embedding=self.embeddings)

    def query(self, question: str, k: int = 4) -> List[Document]:
        """Busca los fragmentos más relevantes para una pregunta."""
        try:
            # Verificar actualizaciones antes de cada consulta
            if self.check_for_updates():
                self.reload_knowledge()
                
            print(f"🔎 Buscando respuesta para: {question}")
            with self._lock:
                return self.vectorstore.similarity_search(question, k=k)
        except Exception as e:
            print(f"⚠️ Error en la búsqueda: {str(e)}")
            return []
