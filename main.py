import os
import customtkinter as ctk
from PIL import Image, ImageDraw

# Configuración de apariencia
ctk.set_appearance_mode("Light") 

class AppKalico(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KALICO - Gestión Psicológica")
        self.geometry("1100x750")

        # Paleta de colores corporativa
        self.bg_color = "#FFFFFF"
        self.card_color = "#F0F7F6"
        self.accent_color = "#7FB7B2"
        self.hover_color = "#FADADD"
        self.text_color = "#2F2F2F"

        self.configure(fg_color=self.bg_color)

        # Rutas de imágenes
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(base_dir, "Imagen", "marcaDeAgua.jpeg")
        ruta_foto_dra = os.path.join(base_dir, "Imagen", "doctora.jpeg") # El nombre de tu archivo

        # --- 1. CONTENEDOR PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

       # --- 2. HEADER (LOGO )
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.place(relx=0.02, rely=0.02, anchor="nw")

        if os.path.exists(ruta_logo):
            img_logo = Image.open(ruta_logo).resize((120, 120)).convert("RGBA")
            
            mask_logo = Image.new("L", (120, 120), 0)
            draw_logo = ImageDraw.Draw(mask_logo)
            draw_logo.ellipse((0, 0, 120, 120), fill=255)
            img_logo.putalpha(mask_logo)

            self.logo_img = ctk.CTkImage(light_image=img_logo, size=(120, 120))
            
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_img, text="")
            self.logo_label.pack(side="left", padx=(0, 15))

        self.logo_text = ctk.CTkLabel(
            self.header_frame,
            text="KALICO",
            font=ctk.CTkFont(size=30, weight="bold"), 
            text_color=self.accent_color
        )
        self.logo_text.pack(side="left")

        # 3. ESPACIO PARA LA FOTO DE LA DOCTORA

        self.foto_perfil = ctk.CTkFrame(
            self.main_frame, 
            width=150, 
            height=150, 
            corner_radius=75, 
            fg_color="transparent", # <-- ¡CAMBIADO A TRANSPARENTE! Adiós círculo gris.
            border_width=3,
            border_color=self.accent_color 
        )
        self.foto_perfil.pack(pady=(80, 15))
        
        # Tamaño para la imagen dentro del círculo
        size = (144, 144)

        if os.path.exists(ruta_foto_dra):
            # Abrir y procesar la imagen de la Dra.
            img_dra = Image.open(ruta_foto_dra).convert("RGBA")
            img_dra = img_dra.resize(size, Image.LANCZOS)

            # Crear máscara circular
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            # Aplicar máscara
            img_dra.putalpha(mask)

            self.foto_dra_img = ctk.CTkImage(light_image=img_dra, size=size)
            self.lbl_foto = ctk.CTkLabel(self.foto_perfil, image=self.foto_dra_img, text="")
            self.lbl_foto.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Fallback elegante si no hay foto: silueta blanca sobre fondo azul corporativo
            self.foto_perfil.configure(fg_color=self.accent_color) # Fondo azul temporal
            self.lbl_placeholder = ctk.CTkLabel(
                self.foto_perfil, 
                text="👤", 
                font=("Arial", 60),
                text_color="white"
            )
            self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # --- 4. SALUDO PRINCIPAL ---
        self.welcome_label = ctk.CTkLabel(
            self.main_frame, 
            text="¡Bienvenida, Dra. Karen!", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=self.accent_color,
            fg_color="transparent"
        )
        self.welcome_label.pack(pady=(10, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame, 
            text="¿Qué gestionaremos hoy?", 
            font=ctk.CTkFont(size=18),
            text_color="gray",
            fg_color="transparent"
        )
        self.subtitle_label.pack(pady=(0, 40))

        # --- 5. CONTENEDOR DE TARJETAS ---
        self.cards_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_container.pack(pady=10)

        self.crear_tarjeta("Pacientes", "👥", 0, self.click_pacientes)
        self.crear_tarjeta("Agenda", "📅", 1, self.click_citas)
        self.crear_tarjeta("Estadísticas", "📊", 2, self.click_stats)

    def crear_tarjeta(self, titulo, icono, columna, comando):
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
        card.grid_propagate(False)

        lbl_icon = ctk.CTkLabel(card, text=icono, font=ctk.CTkFont(size=65))
        lbl_icon.pack(pady=(50, 10))

        lbl_title = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=22, weight="bold"), text_color=self.text_color)
        lbl_title.pack(pady=12)

        btn = ctk.CTkButton(
            card, text="Ingresar", 
            fg_color=self.accent_color,
            hover_color=self.hover_color,
            text_color="white",
            corner_radius=15,
            width=160,
            command=comando
        )
        btn.pack(pady=(25, 0))

    def click_pacientes(self): print("Abriendo Módulo de Pacientes...")
    def click_citas(self): print("Abriendo Agenda...")
    def click_stats(self): print("Abriendo Estadísticas...")

if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()