import customtkinter as ctk
from llm import generate_response
import threading

class ModernJarvisUI:
    def __init__(self):
        # Configuración del tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Ventana principal
        self.window = ctk.CTk()
        self.window.title("Jarvis AI Assistant")
        self.window.geometry("1400x900")
        self.window.configure(fg_color="#1A1A1A")
        
        # Grid layout para mejor control
        self.window.grid_rowconfigure(1, weight=1)  # Chat area expands
        self.window.grid_columnconfigure(0, weight=1)
        
        # Crear el layout
        self.create_widgets()
        
    def create_widgets(self):
        # Header minimalista
        header = ctk.CTkLabel(
            self.window,
            text="JARVIS AI",
            font=("Segoe UI", 24, "bold"),  # Reduced font size
            text_color="#00A3FF"
        )
        header.grid(row=0, column=0, pady=5, sticky="ew")  # Minimal padding
        
        # Frame principal que contiene el chat (eliminamos el status_label para ahorrar espacio)
        main_frame = ctk.CTkFrame(self.window, fg_color="#2D2D2D", corner_radius=15)
        main_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")  # Moved up, reduced padding
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Área de chat con scroll
        self.chat_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent",
            corner_radius=15
        )
        self.chat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame inferior para controles
        controls_container = ctk.CTkFrame(self.window, fg_color="transparent")
        controls_container.grid(row=2, column=0, padx=20, pady=10, sticky="ew")  # Adjusted padding
        controls_container.grid_columnconfigure(1, weight=1)  # Input area expands
        
        # Frame para los botones de tema
        topics_frame = ctk.CTkFrame(controls_container, fg_color="transparent")
        topics_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")
        
        topics = ["🎵 Música", "🎬 Películas", "💻 Tecnología", "✈️ Viajes", "⚽ Deportes"]
        for i, topic in enumerate(topics):
            btn = ctk.CTkButton(
                topics_frame,
                text=topic,
                width=120,
                height=32,
                corner_radius=8,
                font=("Segoe UI", 13),
                fg_color="#404040",
                hover_color="#505050",
                command=lambda t=topic: self.insert_topic(t)
            )
            btn.pack(side="left", padx=5)
        
        # Área de entrada de texto
        self.input_text = ctk.CTkTextbox(
            controls_container,
            height=60,
            font=("Segoe UI", 15),
            fg_color="#404040",
            text_color="#FFFFFF",
            corner_radius=8,
            wrap="word",
            activate_scrollbars=False
        )
        self.input_text.grid(row=1, column=0, columnspan=1, padx=(0, 10), sticky="ew")
        
        # Botón de enviar
        send_button = ctk.CTkButton(
            controls_container,
            text="Enviar 🚀",
            width=100,
            height=60,
            corner_radius=8,
            font=("Segoe UI", 15, "bold"),
            fg_color="#00A3FF",
            hover_color="#0086D4",
            command=self.send_message
        )
        send_button.grid(row=1, column=1, sticky="e")
        
        # Configurar el grid del container
        controls_container.grid_columnconfigure(0, weight=1)
        
        # Mensaje inicial
        self.add_message("¡Hola! 👋 Soy Jarvis, tu asistente AI. ¿En qué puedo ayudarte?", "assistant")
        
        # Bindings
        self.input_text.bind("<Return>", self.handle_return)
        self.input_text.bind("<Shift-Return>", self.handle_shift_return)
        
        # Foco inicial
        self.input_text.focus()

    def update_status(self, message):
        # Método mantenido por compatibilidad pero sin funcionalidad
        pass

    def add_message(self, message, sender):
        # Contenedor para el mensaje
        container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        container.pack(fill="x", pady=5)
        
        # Frame del mensaje
        frame = ctk.CTkFrame(
            container,
            fg_color="#404040" if sender == "assistant" else "#00A3FF",
            corner_radius=12
        )
        frame.pack(
            side="left" if sender == "assistant" else "right",
            padx=20,
            anchor="w" if sender == "assistant" else "e"
        )
        
        # Texto del mensaje
        msg = ctk.CTkLabel(
            frame,
            text=message,
            justify="left",
            font=("Segoe UI", 14),
            text_color="#FFFFFF"
        )
        msg.pack(padx=15, pady=10)
        
        def update_wraplength(event=None):
            if event is not None:  # Solo actualizar si el evento es de resize
                window_width = self.window.winfo_width()
                max_width = min(int(window_width * 0.6), 800)  # 60% del ancho, máximo 800px
                msg.configure(wraplength=max_width)
        
        # Aplicar wrapping inicial y vincular al resize
        update_wraplength()
        self.window.bind('<Configure>', update_wraplength)
        
        # Auto-scroll
        self.window.after(10, self.chat_frame._parent_canvas.yview_moveto, 1.0)

    def send_message(self):
        message = self.input_text.get("1.0", "end-1c").strip()
        if not message:
            return
            
        # Limpiar el texto antes de procesar
        self.input_text.delete("1.0", "end")
        self.input_text.configure(state="disabled")
        
        # Mostrar mensaje del usuario
        self.add_message(message, "user")
        
        # Procesar en thread separado
        def process():
            try:
                response = generate_response(message)
                self.add_message(response, "assistant")
            except Exception as e:
                self.add_message(f"❌ Lo siento, ocurrió un error: {str(e)}", "error")
            finally:
                self.input_text.configure(state="normal")
                self.input_text.focus()
        
        threading.Thread(target=process).start()

    def insert_topic(self, topic):
        current = self.input_text.get("1.0", "end-1c")
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", current + topic.split(" ", 1)[1] + " ")
        self.input_text.focus()

    def handle_return(self, event):
        if not event.state & 0x1:  # No Shift pressed
            self.send_message()
            return "break"
            
    def handle_shift_return(self, event):
        return None  # Allow default behavior (new line)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ModernJarvisUI()
    app.run()
