import customtkinter as ctk

# Configuración de apariencia
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class AppKalico(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KALICO - Gestión Psicológica")
        self.geometry("900x600")

        # Configurar el sistema de cuadrícula (layout)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- MENU LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="KALICO", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Botones del menú
        self.btn_pacientes = ctk.CTkButton(self.sidebar_frame, text="Pacientes", command=self.click_pacientes)
        self.btn_pacientes.grid(row=1, column=0, padx=20, pady=10)

        self.btn_citas = ctk.CTkButton(self.sidebar_frame, text="Agenda de Citas", command=self.click_citas)
        self.btn_citas.grid(row=2, column=0, padx=20, pady=10)

        self.btn_stats = ctk.CTkButton(self.sidebar_frame, text="Estadísticas", command=self.click_stats)
        self.btn_stats.grid(row=3, column=0, padx=20, pady=10)

        # --- CONTENIDO PRINCIPAL ---
        self.main_content = ctk.CTkLabel(self, text="Bienvenido al Sistema KALICO", font=ctk.CTkFont(size=20))
        self.main_content.grid(row=0, column=1, padx=20, pady=20)

    def click_pacientes(self):
        self.main_content.configure(text="Módulo de Pacientes Seleccionado")

    def click_citas(self):
        self.main_content.configure(text="Módulo de Agenda Seleccionado")

    def click_stats(self):
        self.main_content.configure(text="Módulo de Estadísticas Seleccionado")

if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()