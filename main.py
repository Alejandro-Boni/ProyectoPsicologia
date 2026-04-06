import os
from datetime import datetime
from tkinter import messagebox
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONFIGURACIÓN DE SUPABASE ---
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan variables SUPABASE_URL o SUPABASE_KEY en el archivo .env")

supabase: Client = create_client(url, key)

ctk.set_appearance_mode("Light")


# ─────────────────────────────────────────────
#  PALETA PASTEL PREMIUM (inspirada en el logo)
# ─────────────────────────────────────────────
PALETTE = {
    "bg":           "#FDF8F6",       # Blanco crema cálido
    "bg2":          "#F9F1EE",       # Crema rosada secundaria
    "card":         "#FFFFFF",       # Tarjetas blancas puras
    "card_border":  "#F2E4E1",       # Borde rosado muy suave
    "teal":         "#7EC8C8",       # Teal pastel (del logo)
    "teal_dark":    "#5AACAC",       # Teal más profundo (hover)
    "teal_light":   "#B8E4E4",       # Teal muy claro
    "rose":         "#F4B8C1",       # Rosa pastel suave
    "rose_dark":    "#E896A4",       # Rosa hover
    "rose_light":   "#FDE8EC",       # Rosa muy claro
    "lavender":     "#C9B8E8",       # Lavanda suave
    "gold":         "#E8C97A",       # Dorado pastel premium
    "text":         "#3D3044",       # Texto principal (ciruela oscuro)
    "text_soft":    "#8A7A8F",       # Texto secundario
    "text_light":   "#B8A8BF",       # Texto muy suave
    "white":        "#FFFFFF",
    "shadow":       "#EDD8D5",       # Sombra rosada
}


def make_gradient_image(w, h, color1, color2, vertical=True):
    """Crea imagen PIL con gradiente entre dos colores hex."""
    img = Image.new("RGB", (w, h))
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    for i in range(h if vertical else w):
        t = i / (h - 1 if vertical else w - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        if vertical:
            for x in range(w):
                img.putpixel((x, i), (r, g, b))
        else:
            for y in range(h):
                img.putpixel((i, y), (r, g, b))
    return img


def make_circle_image(pil_img, size, border_color_hex=None, border_width=4):
    """Recorta imagen en círculo con borde opcional."""
    pil_img = pil_img.convert("RGBA").resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size[0]-1, size[1]-1), fill=255)
    result = Image.new("RGBA", size, (0, 0, 0, 0))
    result.paste(pil_img, mask=mask)

    if border_color_hex:
        border_img = Image.new("RGBA", size, (0, 0, 0, 0))
        r, g, b = int(border_color_hex[1:3], 16), int(border_color_hex[3:5], 16), int(border_color_hex[5:7], 16)
        ImageDraw.Draw(border_img).ellipse(
            (0, 0, size[0]-1, size[1]-1),
            outline=(r, g, b, 255), width=border_width
        )
        result = Image.alpha_composite(result, border_img)
    return result


def make_pill_button_image(w, h, color_hex, hover=False):
    """Imagen para botón redondeado con efecto de brillo."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
    draw.rounded_rectangle([0, 0, w-1, h-1], radius=h//2, fill=(r, g, b, 255))
    # Brillo superior
    shine_h = h // 3
    for i in range(shine_h):
        alpha = int(80 * (1 - i / shine_h))
        draw.line([(10, i+2), (w-10, i+2)], fill=(255, 255, 255, alpha))
    return img


# ════════════════════════════════════════════════════════
#  POPUP BUSCAR PACIENTE
# ════════════════════════════════════════════════════════

class PopupBuscarPaciente(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        self.title("🔍 Buscar Paciente — KALICO")
        self.geometry("920x620")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["bg"])
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        # Título decorativo
        title_frame = ctk.CTkFrame(self, fg_color=PALETTE["teal_light"], corner_radius=0, height=70)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="✦  Buscar Paciente  ✦",
                     font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
                     text_color=PALETTE["teal_dark"]).place(relx=0.5, rely=0.5, anchor="center")

        # Barra de búsqueda
        search_card = ctk.CTkFrame(self, fg_color=PALETTE["card"],
                                   corner_radius=18, border_width=1,
                                   border_color=PALETTE["card_border"])
        search_card.pack(padx=30, pady=18, fill="x")

        ctk.CTkLabel(search_card, text="Buscar por nombre o número de documento",
                     font=ctk.CTkFont(size=13), text_color=PALETTE["text_soft"]).pack(
            anchor="w", padx=22, pady=(14, 4))

        row = ctk.CTkFrame(search_card, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(0, 14))

        self.entry_busqueda = ctk.CTkEntry(
            row, placeholder_text="🔎  Ej: Karen López  ó  10234567",
            height=42, corner_radius=21,
            fg_color=PALETTE["bg2"], border_color=PALETTE["teal_light"],
            text_color=PALETTE["text"],
            placeholder_text_color=PALETTE["text_light"],
            font=ctk.CTkFont(size=14)
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.entry_busqueda.bind("<Return>", lambda e: self.buscar())

        ctk.CTkButton(row, text="Buscar", width=130, height=42,
                      corner_radius=21,
                      fg_color=PALETTE["teal"], hover_color=PALETTE["teal_dark"],
                      text_color="white",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.buscar).pack(side="left")

        # Encabezado tabla
        headers_frame = ctk.CTkFrame(self, fg_color=PALETTE["rose_light"],
                                     corner_radius=12, height=40)
        headers_frame.pack(padx=30, fill="x")
        headers_frame.pack_propagate(False)
        for texto, ancho in [("Nombre", 220), ("Documento", 130),
                              ("Teléfono", 110), ("Email", 170), ("Acciones", 200)]:
            ctk.CTkLabel(headers_frame, text=texto, width=ancho,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=PALETTE["rose_dark"]).pack(side="left", padx=8, pady=8)

        # Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(padx=30, fill="both", expand=True, pady=(6, 0))

        self.lbl_estado = ctk.CTkLabel(self, text="Ingresa un nombre o documento para buscar.",
                                       text_color=PALETTE["text_light"],
                                       font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_estado.pack(pady=8)

    def buscar(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        termino = self.entry_busqueda.get().strip()
        if not termino:
            self.lbl_estado.configure(text="⚠️  Escribe algo para buscar.")
            return
        try:
            r1 = supabase.table("pacientes").select("*").ilike("nombre_completo", f"%{termino}%").execute()
            r2 = supabase.table("pacientes").select("*").ilike("documento_identidad", f"%{termino}%").execute()
            ids, pacientes = set(), []
            for p in (r1.data or []) + (r2.data or []):
                if p["id"] not in ids:
                    ids.add(p["id"]); pacientes.append(p)
            if not pacientes:
                self.lbl_estado.configure(text="❌  No se encontraron pacientes.")
                return
            self.lbl_estado.configure(text=f"✅  {len(pacientes)} paciente(s) encontrado(s).")
            for p in pacientes:
                self._fila(p)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _fila(self, p):
        fila = ctk.CTkFrame(self.scroll, fg_color=PALETTE["card"],
                            corner_radius=12, border_width=1,
                            border_color=PALETTE["card_border"])
        fila.pack(fill="x", pady=4)
        for texto, ancho in [
            (p.get("nombre_completo", "—"), 220),
            (p.get("documento_identidad", "—"), 130),
            (p.get("telefono") or "—", 110),
            (p.get("email") or "—", 170),
        ]:
            ctk.CTkLabel(fila, text=texto, width=ancho,
                         text_color=PALETTE["text"],
                         font=ctk.CTkFont(size=13),
                         wraplength=ancho - 10).pack(side="left", padx=6, pady=10)

        acc = ctk.CTkFrame(fila, fg_color="transparent")
        acc.pack(side="left", padx=4)

        btn_cfg = [
            ("👁", PALETTE["teal_light"],  PALETTE["teal"],      self._ver),
            ("✏️", PALETTE["rose_light"],  PALETTE["rose_dark"], self._editar),
            ("🗑", "#FADADD",              "#E88080",            self._eliminar),
            ("📋", "#EDE8F8",              PALETTE["lavender"],  self._historial),
        ]
        for emoji, bg, hover, fn in btn_cfg:
            ctk.CTkButton(acc, text=emoji, width=36, height=32,
                          corner_radius=10, fg_color=bg, hover_color=hover,
                          text_color=PALETTE["text"],
                          font=ctk.CTkFont(size=15),
                          command=lambda f=fn, pac=p, fw=fila: f(pac, fw) if f == self._eliminar else f(pac)
                          ).pack(side="left", padx=3)

    # ── Acciones ──────────────────────────────────────────

    def _ver(self, p):
        win = ctk.CTkToplevel(self)
        win.title("Detalle"); win.geometry("430x390")
        win.configure(fg_color=PALETTE["bg"]); win.grab_set()

        h = ctk.CTkFrame(win, fg_color=PALETTE["teal_light"], corner_radius=0, height=55)
        h.pack(fill="x"); h.pack_propagate(False)
        ctk.CTkLabel(h, text="👤  Datos del Paciente",
                     font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
                     text_color=PALETTE["teal_dark"]).place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(win, fg_color=PALETTE["card"], corner_radius=16,
                            border_width=1, border_color=PALETTE["card_border"])
        card.pack(padx=22, pady=14, fill="both", expand=True)

        for label, val in [
            ("Nombre completo",  p.get("nombre_completo")),
            ("Documento",        p.get("documento_identidad")),
            ("Fecha nacimiento", p.get("fecha_nacimiento")),
            ("Teléfono",         p.get("telefono")),
            ("Email",            p.get("email")),
            ("Ocupación",        p.get("ocupacion")),
        ]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row, text=f"{label}:", width=155,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=PALETTE["teal_dark"], anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val or "—",
                         font=ctk.CTkFont(size=13),
                         text_color=PALETTE["text_soft"]).pack(side="left")

        ctk.CTkButton(win, text="Cerrar", height=38, width=140, corner_radius=19,
                      fg_color=PALETTE["teal"], hover_color=PALETTE["teal_dark"],
                      text_color="white", command=win.destroy).pack(pady=10)

    def _editar(self, p):
        win = ctk.CTkToplevel(self)
        win.title("Editar Paciente"); win.geometry("490x490")
        win.configure(fg_color=PALETTE["bg"]); win.grab_set()

        h = ctk.CTkFrame(win, fg_color=PALETTE["rose_light"], corner_radius=0, height=55)
        h.pack(fill="x"); h.pack_propagate(False)
        ctk.CTkLabel(h, text="✏️  Editar Paciente",
                     font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
                     text_color=PALETTE["rose_dark"]).place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(win, fg_color=PALETTE["card"], corner_radius=16,
                            border_width=1, border_color=PALETTE["card_border"])
        card.pack(padx=22, pady=12, fill="both", expand=True)

        campos = [
            ("Nombre completo",    "nombre_completo"),
            ("Documento",          "documento_identidad"),
            ("Fecha (AAAA-MM-DD)", "fecha_nacimiento"),
            ("Teléfono",           "telefono"),
            ("Email",              "email"),
            ("Ocupación",          "ocupacion"),
        ]
        entries = {}
        for i, (label, key) in enumerate(campos):
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
                         text_color=PALETTE["text_soft"]).grid(
                row=i*2, column=0, padx=24, pady=(10, 0), sticky="w")
            e = ctk.CTkEntry(card, width=390, height=33, corner_radius=10,
                             fg_color=PALETTE["bg2"], border_color=PALETTE["teal_light"],
                             text_color=PALETTE["text"])
            e.insert(0, p.get(key) or "")
            e.grid(row=i*2+1, column=0, padx=24, pady=(2, 0), sticky="w")
            entries[key] = e

        def guardar():
            fs = entries["fecha_nacimiento"].get().strip()
            if fs:
                try: datetime.strptime(fs, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Formato", "Fecha debe ser AAAA-MM-DD", parent=win); return
            try:
                datos = {k: (entries[k].get().strip() or None) for k in entries}
                supabase.table("pacientes").update(datos).eq("id", p["id"]).execute()
                messagebox.showinfo("¡Éxito!", "Paciente actualizado.", parent=win)
                win.destroy(); self.buscar()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=win)

        ctk.CTkButton(win, text="💾  Guardar cambios", height=40, width=200,
                      corner_radius=20, fg_color=PALETTE["teal"],
                      hover_color=PALETTE["teal_dark"], text_color="white",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=guardar).pack(pady=12)

    def _eliminar(self, p, fila_widget):
        if messagebox.askyesno("Eliminar",
                               f"¿Eliminar a {p.get('nombre_completo')}?\nEsta acción no se puede deshacer.",
                               parent=self):
            try:
                supabase.table("pacientes").delete().eq("id", p["id"]).execute()
                fila_widget.destroy()
                messagebox.showinfo("Eliminado", "Paciente eliminado.", parent=self)
                self.buscar()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self)

    def _historial(self, p):
        win = ctk.CTkToplevel(self)
        win.title("Historial"); win.geometry("500x340")
        win.configure(fg_color=PALETTE["bg"]); win.grab_set()

        h = ctk.CTkFrame(win, fg_color="#EDE8F8", corner_radius=0, height=55)
        h.pack(fill="x"); h.pack_propagate(False)
        ctk.CTkLabel(h, text=f"📋  Historial — {p.get('nombre_completo','')}",
                     font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
                     text_color=PALETTE["lavender"]).place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(win, fg_color=PALETTE["card"], corner_radius=16,
                            border_width=1, border_color=PALETTE["card_border"])
        card.pack(padx=22, pady=14, fill="both", expand=True)
        ctk.CTkLabel(card,
                     text="🚧\n\nEl módulo de historial y citas\nestará disponible próximamente.",
                     font=ctk.CTkFont(size=15), text_color=PALETTE["text_light"]
                     ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(win, text="Cerrar", height=36, width=120, corner_radius=18,
                      fg_color=PALETTE["lavender"], hover_color=PALETTE["teal"],
                      text_color="white", command=win.destroy).pack(pady=8)


# ════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ════════════════════════════════════════════════════════

class AppKalico(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KALICO — Gestión Psicológica")
        self.geometry("1100x760")
        self.configure(fg_color=PALETTE["bg"])
        self.resizable(True, True)

        # Para compatibilidad con PopupBuscarPaciente
        self.accent_color = PALETTE["teal"]
        self.card_color   = PALETTE["card"]
        self.text_color   = PALETTE["text"]
        self.hover_color  = PALETTE["teal_dark"]

        self.base_dir      = os.path.dirname(os.path.abspath(__file__))
        self.ruta_logo     = os.path.join(self.base_dir, "Imagen", "marcaDeAgua.jpeg")
        self.ruta_foto_dra = os.path.join(self.base_dir, "Imagen", "doctora.jpeg")

        self.main_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        self.mostrar_menu_principal()

    # ── Utilidades ────────────────────────────────────────

    def limpiar_pantalla(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    # ── Menú principal ────────────────────────────────────

    def mostrar_menu_principal(self):
        self.limpiar_pantalla()

        # ── Franja superior decorativa con gradiente simulado ──
        top_band = ctk.CTkFrame(self.main_frame, fg_color=PALETTE["teal_light"],
                                corner_radius=0, height=90)
        top_band.pack(fill="x")
        top_band.pack_propagate(False)

        # Línea decorativa inferior de la franja
        accent_line = ctk.CTkFrame(self.main_frame, fg_color=PALETTE["rose"],
                                   corner_radius=0, height=4)
        accent_line.pack(fill="x")

        # Logo + nombre KALICO en la franja
        logo_area = ctk.CTkFrame(top_band, fg_color="transparent")
        logo_area.place(x=28, rely=0.5, anchor="w")

        if os.path.exists(self.ruta_logo):
            img = Image.open(self.ruta_logo)
            img_circ = make_circle_image(img, (72, 72),
                                         border_color_hex=PALETTE["white"], border_width=3)
            self.logo_img = ctk.CTkImage(light_image=img_circ, size=(72, 72))
            ctk.CTkLabel(logo_area, image=self.logo_img, text="").pack(side="left", padx=(0, 12))

        # KALICO con estilo premium
        kalico_frame = ctk.CTkFrame(logo_area, fg_color="transparent")
        kalico_frame.pack(side="left")
        ctk.CTkLabel(kalico_frame, text="KALICO",
                     font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
                     text_color=PALETTE["teal_dark"]).pack(anchor="w")
        ctk.CTkLabel(kalico_frame, text="Gestión Psicológica",
                     font=ctk.CTkFont(size=11),
                     text_color=PALETTE["text_soft"]).pack(anchor="w")

        # Decoración floral derecha (caracteres unicode)
        ctk.CTkLabel(top_band, text="✿  ✦  ✿",
                     font=ctk.CTkFont(size=18),
                     text_color=PALETTE["rose"]).place(relx=0.98, rely=0.5,
                                                       anchor="e")

        # ── Foto doctora con anillo decorativo ──
        photo_outer = ctk.CTkFrame(self.main_frame, fg_color=PALETTE["rose_light"],
                                   width=176, height=176, corner_radius=88)
        photo_outer.pack(pady=(32, 0))
        photo_outer.pack_propagate(False)

        photo_mid = ctk.CTkFrame(photo_outer, fg_color=PALETTE["gold"],
                                 width=162, height=162, corner_radius=81)
        photo_mid.place(relx=0.5, rely=0.5, anchor="center")
        photo_mid.pack_propagate(False)

        size = (152, 152)
        if os.path.exists(self.ruta_foto_dra):
            img_dra = Image.open(self.ruta_foto_dra)
            img_circ = make_circle_image(img_dra, size)
            self.foto_img = ctk.CTkImage(light_image=img_circ, size=size)
            ctk.CTkLabel(photo_mid, image=self.foto_img, text="").place(
                relx=0.5, rely=0.5, anchor="center")
        else:
            photo_mid.configure(fg_color=PALETTE["teal"])
            ctk.CTkLabel(photo_mid, text="👤", font=("Arial", 58),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # ── Saludo ──
        ctk.CTkLabel(self.main_frame, text="¡Bienvenida, Dra. Karen!",
                     font=ctk.CTkFont(family="Georgia", size=34, weight="bold"),
                     text_color=PALETTE["text"]).pack(pady=(18, 4))

        ctk.CTkLabel(self.main_frame,
                     text="✦   ¿Qué gestionaremos hoy?   ✦",
                     font=ctk.CTkFont(size=14),
                     text_color=PALETTE["rose_dark"]).pack(pady=(0, 30))

        # ── Tarjetas ──
        cards_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_row.pack(pady=6)

        tarjetas = [
            ("Pacientes",    "👥", PALETTE["teal"],     PALETTE["teal_dark"],    self.click_pacientes),
            ("Agenda",       "📅", PALETTE["rose"],     PALETTE["rose_dark"],    self.click_citas),
            ("Estadísticas", "📊", PALETTE["lavender"], "#A090D0",               self.click_stats),
        ]
        for titulo, icono, color, hover, cmd in tarjetas:
            self._crear_tarjeta(cards_row, titulo, icono, color, hover, cmd)

    def _crear_tarjeta(self, parent, titulo, icono, color, hover, cmd):
        # Sombra simulada
        shadow = ctk.CTkFrame(parent, fg_color=PALETTE["shadow"],
                              width=246, height=304, corner_radius=26)
        shadow.grid(row=0, column=len(parent.winfo_children()), padx=24, pady=10)
        shadow.grid_propagate(False)

        card = ctk.CTkFrame(shadow, fg_color=PALETTE["card"],
                            width=240, height=298, corner_radius=24,
                            border_width=1, border_color=PALETTE["card_border"])
        card.place(x=2, y=0)
        card.pack_propagate(False)

        # Franja de color superior en tarjeta
        top_strip = ctk.CTkFrame(card, fg_color=color, height=8, corner_radius=0)
        top_strip.pack(fill="x", padx=0, pady=0)

        # Círculo del ícono (colores pastel sólidos, tkinter no soporta hex con alpha)
        icon_bg = ctk.CTkFrame(card, fg_color=PALETTE["bg2"],
                               width=90, height=90, corner_radius=45)
        icon_bg.pack(pady=(28, 4))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=icono,
                     font=ctk.CTkFont(size=42)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=titulo,
                     font=ctk.CTkFont(family="Georgia", size=21, weight="bold"),
                     text_color=PALETTE["text"]).pack(pady=(8, 4))

        ctk.CTkLabel(card, text="─────",
                     text_color=color,
                     font=ctk.CTkFont(size=10)).pack()

        ctk.CTkButton(card, text="Ingresar  →",
                      fg_color=color, hover_color=hover,
                      text_color="white",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      height=38, width=165, corner_radius=19,
                      command=cmd).pack(pady=(14, 0))

    # ── Módulo Pacientes ──────────────────────────────────

    def click_pacientes(self):
        self.limpiar_pantalla()
        self._header_secundario("👥  Gestión de Pacientes",
                                PALETTE["teal_light"], PALETTE["teal_dark"])

        btn_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_row.pack(pady=14)

        ctk.CTkButton(btn_row, text="➕  Registrar paciente",
                      fg_color=PALETTE["teal"], hover_color=PALETTE["teal_dark"],
                      text_color="white", height=42, width=240, corner_radius=21,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._mostrar_form_registro).pack(side="left", padx=10)

        ctk.CTkButton(btn_row, text="🔍  Buscar paciente",
                      fg_color=PALETTE["rose"], hover_color=PALETTE["rose_dark"],
                      text_color="white", height=42, width=220, corner_radius=21,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._abrir_busqueda).pack(side="left", padx=10)

        self.form_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True)
        self._mostrar_form_registro()

    def _header_secundario(self, titulo, bg, fg):
        band = ctk.CTkFrame(self.main_frame, fg_color=bg, height=64, corner_radius=0)
        band.pack(fill="x")
        band.pack_propagate(False)

        ctk.CTkButton(band, text="←  Volver",
                      fg_color="transparent", hover_color=PALETTE["card_border"],
                      text_color=fg, font=ctk.CTkFont(size=13),
                      command=self.mostrar_menu_principal).place(x=16, rely=0.5, anchor="w")

        ctk.CTkLabel(band, text=titulo,
                     font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
                     text_color=fg).place(relx=0.5, rely=0.5, anchor="center")

        # Línea decorativa
        ctk.CTkFrame(self.main_frame, fg_color=PALETTE["rose"],
                     height=3, corner_radius=0).pack(fill="x")

    def _abrir_busqueda(self):
        PopupBuscarPaciente(self)

    def _mostrar_form_registro(self):
        for w in self.form_container.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(self.form_container, fg_color=PALETTE["card"],
                            corner_radius=20, border_width=1,
                            border_color=PALETTE["card_border"])
        card.pack(pady=10, padx=50, fill="both", expand=True)

        ctk.CTkLabel(card, text="Nuevo Paciente",
                     font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
                     text_color=PALETTE["teal_dark"]).grid(
            row=0, column=0, columnspan=2, pady=(16, 6), padx=30, sticky="w")

        self.entry_nombre    = self._campo(card, "Nombre Completo", 1, 0)
        self.entry_documento = self._campo(card, "Cédula / Documento", 2, 0)
        self.entry_fecha     = self._campo(card, "Fecha Nacimiento (AAAA-MM-DD)", 3, 0)
        self.entry_tel       = self._campo(card, "Teléfono", 1, 1)
        self.entry_email     = self._campo(card, "Email", 2, 1)
        self.entry_ocupacion = self._campo(card, "Ocupación", 3, 1)

        ctk.CTkButton(self.form_container,
                      text="✓  Confirmar y Guardar",
                      fg_color=PALETTE["teal"], hover_color=PALETTE["teal_dark"],
                      text_color="white", height=46, width=280, corner_radius=23,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      command=self.guardar_paciente).pack(pady=18)

    def _campo(self, parent, texto, fila, col):
        ctk.CTkLabel(parent, text=texto,
                     font=ctk.CTkFont(size=12),
                     text_color=PALETTE["text_soft"]).grid(
            row=fila*2-1, column=col, padx=30, pady=(12, 2), sticky="w")
        e = ctk.CTkEntry(parent, width=290, height=36, corner_radius=12,
                         fg_color=PALETTE["bg2"],
                         border_color=PALETTE["teal_light"],
                         text_color=PALETTE["text"],
                         font=ctk.CTkFont(size=13))
        e.grid(row=fila*2, column=col, padx=30, pady=(0, 4), sticky="w")
        return e

    def guardar_paciente(self):
        nombre = self.entry_nombre.get().strip()
        doc    = self.entry_documento.get().strip()
        if not nombre or not doc:
            messagebox.showwarning("Atención", "Por favor llena al menos Nombre y Documento.")
            return
        fecha_str = self.entry_fecha.get().strip()
        fecha_valida = None
        if fecha_str:
            try:
                datetime.strptime(fecha_str, "%Y-%m-%d"); fecha_valida = fecha_str
            except ValueError:
                messagebox.showwarning("Formato", "La fecha debe ser AAAA-MM-DD."); return
        try:
            supabase.table("pacientes").insert({
                "nombre_completo":     nombre,
                "documento_identidad": doc,
                "fecha_nacimiento":    fecha_valida,
                "telefono":            self.entry_tel.get().strip() or None,
                "email":               self.entry_email.get().strip() or None,
                "ocupacion":           self.entry_ocupacion.get().strip() or None,
            }).execute()
            messagebox.showinfo("¡Éxito!", f"{nombre} ha sido registrado correctamente.")
            self.mostrar_menu_principal()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def click_citas(self):
        messagebox.showinfo("Próximamente", "El módulo de Agenda está en desarrollo. 📅")

    def click_stats(self):
        messagebox.showinfo("Próximamente", "El módulo de Estadísticas está en desarrollo. 📊")


if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()