import os
import customtkinter as ctk
from PIL import Image, ImageDraw

# Configuración de apariencia
ctk.set_appearance_mode("Light") 

class AppKalico(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KALICO - Gestión Psicológica")
        self.geometry("1100x750") # Un poco más amplia para que luzca el fondo

        # Paleta de colores extraída del logo
        self.bg_color = "#FFFFFF" # Fondo blanco puro
        self.card_color = "#F0F7F6" # Un verde/azul muy tenue para las tarjetas
        self.accent_color = "#7FB7B2" # El azul principal del logo
        self.hover_color = "#FADADD"  # Rosa pastel del logo para el hover
        self.text_color = "#2F2F2F"

        self.configure(fg_color=self.bg_color)

        # Ruta de imagen
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_imagen = os.path.join(base_dir, "Imagen", "marcaDeAgua.jpeg")

        # 1. MARCA DE AGUA REAL (FONDO)
        if os.path.exists(ruta_imagen):
            img_original = Image.open(ruta_imagen).convert("RGBA")

            # Tamaño grande tipo fondo
            img_original = img_original.resize((800, 800))

            # Opacidad visible
            alpha = img_original.split()[3]
            alpha = alpha.point(lambda p: 60)
            img_original.putalpha(alpha)

            self.bg_image = ctk.CTkImage(
                light_image=img_original,
                size=(800, 800)
            )

            self.bg_label = ctk.CTkLabel(
                self,   # 👈 CLAVE: usar la ventana
                image=self.bg_image,
                text=""
            )

            self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
            self.bg_label.lower()

        else:
            print(f"⚠️ No se encontró la imagen en: {ruta_imagen}")

        # --- CONTENIDO PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

       

        #  HEADER (LOGO + TEXTO)
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.place(relx=0.02, rely=0.02, anchor="nw")

        if os.path.exists(ruta_imagen):
            img_logo = Image.open(ruta_imagen).resize((60, 60)).convert("RGBA")

            # Máscara circular
            mask = Image.new("L", (60, 60), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 60, 60), fill=255)

            img_logo.putalpha(mask)

            self.logo_img = ctk.CTkImage(light_image=img_logo, size=(60, 60))

            self.logo_label = ctk.CTkLabel(
                self.header_frame,
                image=self.logo_img,
                text=""
            )
            self.logo_label.pack(side="left", padx=(0, 10))

        self.logo_text = ctk.CTkLabel(
            self.header_frame,
            text="KALICO",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.accent_color
        )
        self.logo_text.pack(side="left")


        
        # 2. ELEMENTOS SUPERIORES (Dibujados sobre el logo)
        
        # --- TÍTULO DE BIENVENIDA ---
        self.welcome_label = ctk.CTkLabel(
            self.main_frame, 
            text="¡Bienvenida, Dra. Karen!", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.accent_color,
            fg_color="transparent" # Para que se vea el logo detrás
        )
        self.welcome_label.pack(pady=(60, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame, 
            text="¿Qué gestionaremos hoy?", 
            font=ctk.CTkFont(size=18),
            text_color="gray",
            fg_color="transparent"
        )
        self.subtitle_label.pack(pady=(0, 50))

        # --- CONTENEDOR DE TARJETAS (Cards) ---
        self.cards_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_container.pack(pady=20)

        # Crear las 3 tarjetas principales 
        self.crear_tarjeta("Pacientes", "👥", 0, self.click_pacientes)
        self.crear_tarjeta("Agenda", "📅", 1, self.click_citas)
        self.crear_tarjeta("Estadísticas", "📊", 2, self.click_stats)

    def crear_tarjeta(self, titulo, icono, columna, comando):
        """Función para crear tarjetas interactivas"""
        card = ctk.CTkFrame(
            self.cards_container, 
            width=240, 
            height=300, 
            fg_color=self.card_color,
            corner_radius=25,
            border_width=2,
            border_color="#E0E0E0"
        )
        card.grid(row=0, column=columna, padx=25, pady=10)
        card.grid_propagate(False) # Mantener el tamaño fijo

        # Icono (usando texto por ahora, luego pondremos imágenes)
        lbl_icon = ctk.CTkLabel(card, text=icono, font=ctk.CTkFont(size=65))
        lbl_icon.pack(pady=(50, 10))

        # Título de la tarjeta
        lbl_title = ctk.CTkLabel(
            card, 
            text=titulo, 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.text_color
        )
        lbl_title.pack(pady=12)

        # Botón de acción dentro de la tarjeta
        btn = ctk.CTkButton(
            card, 
            text="Ingresar", 
            fg_color=self.accent_color,
            hover_color=self.hover_color,
            text_color="white",
            corner_radius=15,
            width=160,
            command=comando
        )
        btn.pack(pady=(25, 0))

    # --- FUNCIONES DE BOTONES (Se mantienen) ---
    def click_pacientes(self):
        print("Abriendo Módulo de Pacientes...")

    def click_citas(self):
        print("Abriendo Agenda...")

    def click_stats(self):
        print("Abriendo Estadísticas...")

if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()