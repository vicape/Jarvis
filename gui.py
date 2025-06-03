import tkinter as tk
from tkinter import scrolledtext, messagebox

class JarvisGUI:
    def __init__(self, on_send_message):
        self.on_send_message = on_send_message

        self.root = tk.Tk()
        self.root.title("🧠 Jarvis con Contexto")
        self.root.geometry("800x600")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Courier New", 11))
        self.text_area.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        self.context_label = tk.Label(self.root, text="Tu mensaje:", font=("Arial", 10))
        self.context_label.pack(anchor='w', padx=10)

        self.entry = tk.Entry(self.root, font=("Arial", 12))
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Enviar", command=self.send_message, font=("Arial", 11))
        self.send_button.pack(pady=(0, 10))

        self.entry.focus()

    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.display_message("🧑 Tú", user_input)

        try:
            response = self.on_send_message(user_input)
            self.display_message("🤖 Jarvis", response)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar el mensaje:\n{e}")

        self.entry.delete(0, tk.END)

    def display_message(self, sender, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"{sender}:\n{message}\n\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)

    def run(self):
        self.root.mainloop()
