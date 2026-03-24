import os
import customtkinter as ctk
from PIL import Image

# Configuración de apariencia
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class AppKalico(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KALICO - Gestión Psicológica")
        self.geometry("900x600")

        # Colores personalizados (basados en tu logo)
        self.bg_color = "#F5F7FA"
        self.sidebar_color = "#E8F3F1"
        self.button_color = "#7FB7B2"
        self.button_hover = "#6AA39E"
        self.text_color = "#2F2F2F"

        self.configure(fg_color=self.bg_color)

        # Configurar el sistema de cuadrícula (layout)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- MENU LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="KALICO", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.text_color
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Botones del menú
        self.btn_pacientes = ctk.CTkButton(
            self.sidebar_frame, 
            text="Pacientes",
            fg_color=self.button_color,
            hover_color=self.button_hover,
            command=self.click_pacientes
        )
        self.btn_pacientes.grid(row=1, column=0, padx=20, pady=10)

        self.btn_citas = ctk.CTkButton(
            self.sidebar_frame, 
            text="Agenda de Citas",
            fg_color=self.button_color,
            hover_color=self.button_hover,
            command=self.click_citas
        )
        self.btn_citas.grid(row=2, column=0, padx=20, pady=10)

        self.btn_stats = ctk.CTkButton(
            self.sidebar_frame, 
            text="Estadísticas",
            fg_color=self.button_color,
            hover_color=self.button_hover,
            command=self.click_stats
        )
        self.btn_stats.grid(row=3, column=0, padx=20, pady=10)

        # --- CONTENIDO PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # Texto principal
        self.main_content = ctk.CTkLabel(
            self.main_frame, 
            text="Bienvenido al Sistema KALICO",
            font=ctk.CTkFont(size=20),
            text_color=self.text_color
        )
        self.main_content.pack(pady=20)

        # =========================
        # MARCA DE AGUA
        # =========================
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_imagen = os.path.join(base_dir, "Imagen", "marcaDeAgua.jpeg")

        if os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            imagen = imagen.resize((350, 350))  # tamaño de la marca de agua

            self.bg_image = ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(350, 350))

            self.bg_label = ctk.CTkLabel(
                self.main_frame,
                text="",
                image=self.bg_image
            )

            # Centrar la marca de agua
            self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

        # =========================

    def click_pacientes(self):
        self.main_content.configure(text="Módulo de Pacientes Seleccionado")

    def click_citas(self):
        self.main_content.configure(text="Módulo de Agenda Seleccionado")

    def click_stats(self):
        self.main_content.configure(text="Módulo de Estadísticas Seleccionado")


if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()