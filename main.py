import os
import customtkinter as ctk
from PIL import Image, ImageDraw
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONFIGURACIÓN DE SUPABASE ---
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

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
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ruta_logo = os.path.join(self.base_dir, "Imagen", "marcaDeAgua.jpeg")
        self.ruta_foto_dra = os.path.join(self.base_dir, "Imagen", "doctora.jpeg")

        # --- 1. CONTENEDOR PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Iniciar mostrando el menú principal
        self.mostrar_menu_principal()

    def limpiar_pantalla(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_menu_principal(self):
        self.limpiar_pantalla()

        # --- 2. HEADER (LOGO GRANDE) ---
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.place(relx=0.02, rely=0.02, anchor="nw")

        if os.path.exists(self.ruta_logo):
            img_logo = Image.open(self.ruta_logo).resize((120, 120)).convert("RGBA")
            mask_logo = Image.new("L", (120, 120), 0)
            draw_logo = ImageDraw.Draw(mask_logo)
            draw_logo.ellipse((0, 0, 120, 120), fill=255)
            img_logo.putalpha(mask_logo)
            self.logo_img = ctk.CTkImage(light_image=img_logo, size=(120, 120))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_img, text="")
            self.logo_label.pack(side="left", padx=(0, 15))

        self.logo_text = ctk.CTkLabel(self.header_frame, text="KALICO", font=ctk.CTkFont(size=30, weight="bold"), text_color=self.accent_color)
        self.logo_text.pack(side="left")

        # --- 3. FOTO DE LA DOCTORA ---
        self.foto_perfil = ctk.CTkFrame(self.main_frame, width=150, height=150, corner_radius=75, fg_color="transparent", border_width=3, border_color=self.accent_color)
        self.foto_perfil.pack(pady=(80, 15))
        
        size = (144, 144)
        if os.path.exists(self.ruta_foto_dra):
            img_dra = Image.open(self.ruta_foto_dra).convert("RGBA").resize(size, Image.LANCZOS)
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img_dra.putalpha(mask)
            self.foto_dra_img = ctk.CTkImage(light_image=img_dra, size=size)
            ctk.CTkLabel(self.foto_perfil, image=self.foto_dra_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.foto_perfil.configure(fg_color=self.accent_color)
            ctk.CTkLabel(self.foto_perfil, text="👤", font=("Arial", 60), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # --- 4. SALUDOS ---
        ctk.CTkLabel(self.main_frame, text="¡Bienvenida, Dra. Karen!", font=ctk.CTkFont(size=36, weight="bold"), text_color=self.accent_color).pack(pady=(10, 5))
        ctk.CTkLabel(self.main_frame, text="¿Qué gestionaremos hoy?", font=ctk.CTkFont(size=18), text_color="gray").pack(pady=(0, 40))

        # --- 5. TARJETAS ---
        self.cards_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_container.pack(pady=10)
        self.crear_tarjeta("Pacientes", "👥", 0, self.click_pacientes)
        self.crear_tarjeta("Agenda", "📅", 1, self.click_citas)
        self.crear_tarjeta("Estadísticas", "📊", 2, self.click_stats)

    def crear_tarjeta(self, titulo, icono, columna, comando):
        card = ctk.CTkFrame(self.cards_container, width=240, height=300, fg_color=self.card_color, corner_radius=25, border_width=2, border_color="#E0E0E0")
        card.grid(row=0, column=columna, padx=25, pady=10)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=icono, font=ctk.CTkFont(size=65)).pack(pady=(50, 10))
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=22, weight="bold"), text_color=self.text_color).pack(pady=12)
        ctk.CTkButton(card, text="Ingresar", fg_color=self.accent_color, hover_color=self.hover_color, corner_radius=15, width=160, command=comando).pack(pady=(25, 0))

    # --- MÓDULO DE REGISTRO DE PACIENTES ---
    def click_pacientes(self):
        self.limpiar_pantalla()
        ctk.CTkButton(self.main_frame, text="← Volver", fg_color="transparent", text_color="gray", command=self.mostrar_menu_principal).pack(anchor="nw", padx=20, pady=10)
        ctk.CTkLabel(self.main_frame, text="Registro de Pacientes", font=ctk.CTkFont(size=30, weight="bold"), text_color=self.accent_color).pack(pady=10)

        form_frame = ctk.CTkFrame(self.main_frame, fg_color=self.card_color, corner_radius=20)
        form_frame.pack(pady=10, padx=50, fill="both", expand=True)

        self.entry_nombre = self.crear_campo(form_frame, "Nombre Completo:", 0, 0)
        self.entry_documento = self.crear_campo(form_frame, "Cédula / Documento:", 1, 0)
        self.entry_fecha = self.crear_campo(form_frame, "Fecha Nacimiento (AAAA-MM-DD):", 2, 0)
        
        self.entry_tel = self.crear_campo(form_frame, "Teléfono:", 0, 1)
        self.entry_email = self.crear_campo(form_frame, "Email:", 1, 1)
        self.entry_ocupacion = self.crear_campo(form_frame, "Ocupación:", 2, 1)

        ctk.CTkButton(self.main_frame, text="Confirmar y Guardar", fg_color=self.accent_color, height=45, width=300, corner_radius=15, command=self.guardar_paciente).pack(pady=30)

    def crear_campo(self, parent, texto, fila, col):
        ctk.CTkLabel(parent, text=texto, text_color=self.text_color).grid(row=fila*2, column=col, padx=40, pady=(15,0), sticky="w")
        entry = ctk.CTkEntry(parent, width=280, height=35)
        entry.grid(row=fila*2 + 1, column=col, padx=40, pady=(0,10), sticky="w")
        return entry

    def guardar_paciente(self):
        nombre = self.entry_nombre.get()
        doc = self.entry_documento.get()
        
        if not nombre or not doc:
            from tkinter import messagebox
            messagebox.showwarning("Atención", "Por favor llena al menos Nombre y Documento.")
            return

        try:
            nuevo = {
                "nombre_completo": nombre,
                "documento_identidad": doc,
                "fecha_nacimiento": self.entry_fecha.get(),
                "telefono": self.entry_tel.get(),
                "email": self.entry_email.get(),
                "ocupacion": self.entry_ocupacion.get()
            }
            supabase.table("pacientes").insert(nuevo).execute()
            from tkinter import messagebox
            messagebox.showinfo("¡Éxito!", f"El paciente {nombre} ha sido registrado correctamente.")
            self.mostrar_menu_principal()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def click_citas(self): print("Abriendo Agenda...")
    def click_stats(self): print("Abriendo Estadísticas...")

if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()