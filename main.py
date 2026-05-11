import os
import re
from datetime import datetime
from tkinter import messagebox
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw
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
#  PALETA PASTEL PREMIUM
# ─────────────────────────────────────────────
PALETTE = {
    "bg":          "#FDF8F6",
    "bg2":         "#F9F1EE",
    "card":        "#FFFFFF",
    "card_border": "#F2E4E1",
    "teal":        "#7EC8C8",
    "teal_dark":   "#5AACAC",
    "teal_light":  "#D6F0F0",
    "rose":        "#F4B8C1",
    "rose_dark":   "#E896A4",
    "rose_light":  "#FDE8EC",
    "lavender":    "#C9B8E8",
    "lav_dark":    "#A090D0",
    "gold":        "#E8C97A",
    "text":        "#3D3044",
    "text_soft":   "#8A7A8F",
    "text_light":  "#B8A8BF",
    "white":       "#FFFFFF",
    "shadow":      "#EDD8D5",
}


def make_circle_image(pil_img, size, border_color_hex=None, border_width=4):
    pil_img = pil_img.convert("RGBA").resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size[0]-1, size[1]-1), fill=255)
    result = Image.new("RGBA", size, (0, 0, 0, 0))
    result.paste(pil_img, mask=mask)
    if border_color_hex:
        border_img = Image.new("RGBA", size, (0, 0, 0, 0))
        r = int(border_color_hex[1:3], 16)
        g = int(border_color_hex[3:5], 16)
        b = int(border_color_hex[5:7], 16)
        ImageDraw.Draw(border_img).ellipse(
            (0, 0, size[0]-1, size[1]-1),
            outline=(r, g, b, 255), width=border_width
        )
        result = Image.alpha_composite(result, border_img)
    return result


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
        title_frame = ctk.CTkFrame(self, fg_color=PALETTE["teal_light"], corner_radius=0, height=70)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="✦  Buscar Paciente  ✦",
                     font=ctk.CTkFont(family="Georgia", size=22, weight="bold"),
                     text_color=PALETTE["teal_dark"]).place(relx=0.5, rely=0.5, anchor="center")

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

        headers_frame = ctk.CTkFrame(self, fg_color=PALETTE["rose_light"],
                                     corner_radius=12, height=40)
        headers_frame.pack(padx=30, fill="x")
        headers_frame.pack_propagate(False)
        for texto, ancho in [("Nombre", 220), ("Documento", 130),
                              ("Teléfono", 110), ("Email", 170), ("Acciones", 200)]:
            ctk.CTkLabel(headers_frame, text=texto, width=ancho,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=PALETTE["rose_dark"]).pack(side="left", padx=8, pady=8)

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
            ("👁", PALETTE["teal_light"], PALETTE["teal"],      self._ver),
            ("✏️", PALETTE["rose_light"], PALETTE["rose_dark"], self._editar),
            ("🗑", "#FADADD",             "#E88080",             self._eliminar),
            ("📋", "#EDE8F8",             PALETTE["lavender"],  self._historial),
        ]
        for emoji, bg, hover, fn in btn_cfg:
            ctk.CTkButton(acc, text=emoji, width=36, height=32,
                          corner_radius=10, fg_color=bg, hover_color=hover,
                          text_color=PALETTE["text"],
                          font=ctk.CTkFont(size=15),
                          command=lambda f=fn, pac=p, fw=fila: f(pac, fw) if f == self._eliminar else f(pac)
                          ).pack(side="left", padx=3)

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
        self.geometry("1100x820")
        self.minsize(1000, 780)
        self.configure(fg_color=PALETTE["bg"])
        self.resizable(True, True)

        self.accent_color = PALETTE["teal"]
        self.card_color   = PALETTE["card"]
        self.text_color   = PALETTE["text"]
        self.hover_color  = PALETTE["teal_dark"]

        self.base_dir      = os.path.dirname(os.path.abspath(__file__))
        self.ruta_logo     = os.path.join(self.base_dir, "Imagen", "marcaDeAgua.jpeg")
        self.ruta_foto_dra = os.path.join(self.base_dir, "Imagen", "doctora.jpeg")

        # ── Estructura con scroll para pantallas pequeñas ──
        self._root_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg"], corner_radius=0)
        self._root_frame.pack(fill="both", expand=True)

        self._scroll_container = ctk.CTkScrollableFrame(
            self._root_frame,
            fg_color=PALETTE["bg"],
            corner_radius=0,
            scrollbar_button_color=PALETTE["teal_light"],
            scrollbar_button_hover_color=PALETTE["teal"],
        )
        self._scroll_container.pack(fill="both", expand=True)

        self.main_frame = ctk.CTkFrame(
            self._scroll_container, fg_color=PALETTE["bg"], corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)

        self.mostrar_menu_principal()

    def limpiar_pantalla(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    # ────────────────────────────────────────────────────
    #  MENÚ PRINCIPAL
    # ────────────────────────────────────────────────────

    def mostrar_menu_principal(self):
        self.limpiar_pantalla()

        # ── Header con logo CENTRADO y protagonismo ──────
        top_band = ctk.CTkFrame(self.main_frame, fg_color=PALETTE["teal_light"],
                                corner_radius=0, height=130)
        top_band.pack(fill="x")
        top_band.pack_propagate(False)

        # Decoraciones florales a los lados
        ctk.CTkLabel(top_band, text="✿  ✦  ✿",
                     font=ctk.CTkFont(size=16),
                     text_color=PALETTE["rose"]).place(x=24, rely=0.5, anchor="w")
        ctk.CTkLabel(top_band, text="✿  ✦  ✿",
                     font=ctk.CTkFont(size=16),
                     text_color=PALETTE["rose"]).place(relx=0.98, rely=0.5, anchor="e")

        # Bloque central: logo + KALICO + subtítulo
        center_header = ctk.CTkFrame(top_band, fg_color="transparent")
        center_header.place(relx=0.5, rely=0.5, anchor="center")

        if os.path.exists(self.ruta_logo):
            img = Image.open(self.ruta_logo)
            img_circ = make_circle_image(img, (100, 100),
                                         border_color_hex=PALETTE["white"], border_width=4)
            self.logo_img = ctk.CTkImage(light_image=img_circ, size=(100, 100))
            ctk.CTkLabel(center_header, image=self.logo_img, text="").pack(side="left", padx=(0, 18))

        texto_header = ctk.CTkFrame(center_header, fg_color="transparent")
        texto_header.pack(side="left")
        ctk.CTkLabel(texto_header, text="KALICO",
                     font=ctk.CTkFont(family="Georgia", size=38, weight="bold"),
                     text_color=PALETTE["teal_dark"]).pack(anchor="w")
        ctk.CTkLabel(texto_header, text="Gestión Psicológica",
                     font=ctk.CTkFont(size=14),
                     text_color=PALETTE["text_soft"]).pack(anchor="w")

        # Línea decorativa rosa
        ctk.CTkFrame(self.main_frame, fg_color=PALETTE["rose"],
                     corner_radius=0, height=4).pack(fill="x")

        # ── Foto doctora + saludo ────────────────────────
        center_block = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_block.pack(pady=(16, 4))

        # Foto circular limpia con borde teal (sin fondo dorado)
        size = (128, 128)
        if os.path.exists(self.ruta_foto_dra):
            img_dra = Image.open(self.ruta_foto_dra)
            img_circ = make_circle_image(img_dra, size,
                                         border_color_hex=PALETTE["teal"], border_width=4)
            self.foto_img = ctk.CTkImage(light_image=img_circ, size=size)
            ctk.CTkLabel(center_block, image=self.foto_img, text="",
                         fg_color="transparent").pack(side="left", padx=(0, 20))
        else:
            placeholder = ctk.CTkFrame(center_block, fg_color=PALETTE["teal"],
                                       width=128, height=128, corner_radius=64)
            placeholder.pack(side="left", padx=(0, 20))
            placeholder.pack_propagate(False)
            ctk.CTkLabel(placeholder, text="👤", font=("Arial", 48),
                         text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        saludo_frame = ctk.CTkFrame(center_block, fg_color="transparent")
        saludo_frame.pack(side="left")
        ctk.CTkLabel(saludo_frame, text="¡Bienvenida, Dra. Karen!",
                     font=ctk.CTkFont(family="Georgia", size=30, weight="bold"),
                     text_color=PALETTE["text"]).pack(anchor="w")
        ctk.CTkLabel(saludo_frame, text="✦   Panel de Gestión Integral   ✦",
                     font=ctk.CTkFont(size=13),
                     text_color=PALETTE["rose_dark"]).pack(anchor="w", pady=(4, 0))

        # ── Cuadrícula 3×3 de tarjetas ───────────────────
        grid_outer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        grid_outer.pack(pady=(12, 10))

        tarjetas = [
            ("Pacientes",     "👥", PALETTE["teal"],     PALETTE["teal_dark"], self.click_pacientes),
            ("Agenda",        "📅", PALETTE["rose"],     PALETTE["rose_dark"], self.click_citas),
            ("Historias",     "🧠", PALETTE["lavender"], PALETTE["lav_dark"],  self.click_historias),
            ("Tratamientos",  "💊", PALETTE["teal"],     PALETTE["teal_dark"], self.click_tratamientos),
            ("Notas",         "📝", PALETTE["rose"],     PALETTE["rose_dark"], self.click_notas),
            ("Pagos",         "💳", PALETTE["lavender"], PALETTE["lav_dark"],  self.click_pagos),
            ("Progreso",      "📈", PALETTE["teal"],     PALETTE["teal_dark"], self.click_progreso),
            ("Estadísticas",  "📊", PALETTE["rose"],     PALETTE["rose_dark"], self.click_stats),
            ("Configuración", "⚙️", PALETTE["lavender"], PALETTE["lav_dark"],  self.click_config),
        ]

        for idx, (titulo, icono, color, hover, cmd) in enumerate(tarjetas):
            self._crear_tarjeta(grid_outer, titulo, icono, color, hover, cmd,
                                idx // 3, idx % 3)

    # ── Tarjeta compacta ─────────────────────────────────

    def _crear_tarjeta(self, parent, titulo, icono, color, hover, cmd, fila, col):
        shadow = ctk.CTkFrame(parent, fg_color=PALETTE["shadow"],
                              width=298, height=170, corner_radius=20)
        shadow.grid(row=fila, column=col, padx=14, pady=10)
        shadow.grid_propagate(False)

        card = ctk.CTkFrame(shadow, fg_color=PALETTE["card"],
                            width=293, height=166, corner_radius=18,
                            border_width=1, border_color=PALETTE["card_border"])
        card.place(x=2, y=0)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        icon_frame = ctk.CTkFrame(inner, fg_color=PALETTE["bg2"],
                                  width=72, height=72, corner_radius=36)
        icon_frame.pack(side="left", padx=(0, 14))
        icon_frame.pack_propagate(False)
        ctk.CTkFrame(icon_frame, fg_color=color, width=5, height=72,
                     corner_radius=3).place(x=0, y=0)
        ctk.CTkLabel(icon_frame, text=icono,
                     font=ctk.CTkFont(size=34)).place(relx=0.55, rely=0.5, anchor="center")

        text_col = ctk.CTkFrame(inner, fg_color="transparent")
        text_col.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(text_col, text=titulo,
                     font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
                     text_color=PALETTE["text"], anchor="w").pack(anchor="w", pady=(6, 2))
        ctk.CTkLabel(text_col, text="─────",
                     text_color=color, font=ctk.CTkFont(size=9)).pack(anchor="w")
        ctk.CTkButton(text_col, text="Ingresar  →",
                      fg_color=color, hover_color=hover, text_color="white",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=32, width=140, corner_radius=16,
                      command=cmd).pack(anchor="w", pady=(8, 0))

    # ── Header secundario ────────────────────────────────

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
        ctk.CTkFrame(self.main_frame, fg_color=PALETTE["rose"],
                     height=3, corner_radius=0).pack(fill="x")

    # ── Módulo Pacientes ─────────────────────────────────

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
        ctk.CTkButton(self.form_container, text="✓  Confirmar y Guardar",
                      fg_color=PALETTE["teal"], hover_color=PALETTE["teal_dark"],
                      text_color="white", height=46, width=280, corner_radius=23,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      command=self.guardar_paciente).pack(pady=18)

    def _campo(self, parent, texto, fila, col):
        ctk.CTkLabel(parent, text=texto, font=ctk.CTkFont(size=12),
                     text_color=PALETTE["text_soft"]).grid(
            row=fila*2-1, column=col, padx=30, pady=(12, 2), sticky="w")
        e = ctk.CTkEntry(parent, width=290, height=36, corner_radius=12,
                         fg_color=PALETTE["bg2"], border_color=PALETTE["teal_light"],
                         text_color=PALETTE["text"], font=ctk.CTkFont(size=13))
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

    # ── Módulo Agenda (MEJORADO) ──────────────────────────

    def click_citas(self):
        self.limpiar_pantalla()
        self._header_secundario("📅  Agenda de Citas",
                                PALETTE["rose_light"], PALETTE["rose_dark"])

        cuerpo_agenda = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cuerpo_agenda.pack(fill="both", expand=True, padx=40, pady=20)

        # ── IZQUIERDA: Calendario ────────────────────────
        frame_izq = ctk.CTkFrame(cuerpo_agenda, fg_color=PALETTE["card"], corner_radius=20)
        frame_izq.pack(side="left", fill="both", expand=True, padx=(0, 20))

        ctk.CTkLabel(frame_izq, text="Seleccione el día",
                     font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
                     text_color=PALETTE["teal_dark"]).pack(pady=(18, 6))

        # Calendario con fallback si es_ES no está instalado en Windows
        try:
            from tkcalendar import Calendar
            self.cal = Calendar(
                frame_izq, selectmode="day", locale="es_ES",
                background=PALETTE["rose_light"],
                headersbackground=PALETTE["rose_dark"],
                headersforeground="white",
                selectbackground=PALETTE["teal"],
                selectforeground="white",
                normalbackground="white",
                weekendbackground=PALETTE["bg2"],
                othermonthbackground=PALETTE["bg"],
                font=("Georgia", 11),
            )
        except Exception:
            from tkcalendar import Calendar
            self.cal = Calendar(
                frame_izq, selectmode="day",
                background=PALETTE["rose_light"],
                headersbackground=PALETTE["rose_dark"],
                selectbackground=PALETTE["teal"],
                normalbackground="white",
            )
        self.cal.pack(padx=20, pady=10, fill="both", expand=True)

        # Lista de citas del día seleccionado
        ctk.CTkLabel(frame_izq, text="Citas del día seleccionado:",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=PALETTE["text_soft"]).pack(anchor="w", padx=20, pady=(10, 2))

        self.frame_citas_dia = ctk.CTkScrollableFrame(
            frame_izq, fg_color=PALETTE["bg2"], corner_radius=12, height=130
        )
        self.frame_citas_dia.pack(fill="x", padx=20, pady=(0, 14))

        self.cal.bind("<<CalendarSelected>>", lambda e: self._cargar_citas_dia())
        self._cargar_citas_dia()

        # ── DERECHA: Formulario ───────────────────────────
        frame_der = ctk.CTkFrame(cuerpo_agenda, fg_color=PALETTE["card"],
                                 width=350, corner_radius=20)
        frame_der.pack(side="right", fill="y")
        frame_der.pack_propagate(False)

        ctk.CTkLabel(frame_der, text="Detalles del Agendamiento",
                     font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
                     text_color=PALETTE["rose_dark"]).pack(pady=(22, 10))

        ctk.CTkLabel(frame_der, text="Paciente:",
                     text_color=PALETTE["text_soft"],
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=25)
        self.combo_pacientes = ctk.CTkComboBox(
            frame_der, width=300, corner_radius=15,
            fg_color=PALETTE["bg2"], border_color=PALETTE["teal_light"],
            button_color=PALETTE["teal"], button_hover_color=PALETTE["teal_dark"],
            text_color=PALETTE["text"]
        )
        self.combo_pacientes.pack(pady=(5, 18), padx=25)

        try:
            res = supabase.table("pacientes").select("id,nombre_completo").execute()
            self.pacientes_data = res.data or []
            if self.pacientes_data:
                self.combo_pacientes.configure(
                    values=[p["nombre_completo"] for p in self.pacientes_data])
                self.combo_pacientes.set(self.pacientes_data[0]["nombre_completo"])
            else:
                self.combo_pacientes.configure(values=["Sin pacientes registrados"])
        except Exception as e:
            messagebox.showwarning("Advertencia",
                                   f"No se pudieron cargar los pacientes:\n{e}")

        ctk.CTkLabel(frame_der, text="Hora (HH:MM):",
                     text_color=PALETTE["text_soft"],
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=25)
        self.entry_hora_cita = ctk.CTkEntry(
            frame_der, placeholder_text="Ej: 10:00",
            width=300, corner_radius=15,
            fg_color=PALETTE["bg2"], border_color=PALETTE["teal_light"],
            text_color=PALETTE["text"]
        )
        self.entry_hora_cita.pack(pady=(5, 8), padx=25)

        ctk.CTkLabel(frame_der, text="ⓘ  La fecha se toma del calendario",
                     font=ctk.CTkFont(size=11, slant="italic"),
                     text_color=PALETTE["text_light"]).pack(anchor="w", padx=25, pady=(0, 20))

        ctk.CTkFrame(frame_der, fg_color=PALETTE["card_border"],
                     height=1).pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkButton(frame_der, text="✓  Agendar Cita",
                      fg_color=PALETTE["rose"], hover_color=PALETTE["rose_dark"],
                      text_color="white", height=42, corner_radius=21,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.guardar_cita).pack(pady=0, padx=25, fill="x")

    def _cargar_citas_dia(self):
        """Muestra las citas del día seleccionado con opción de eliminar."""
        for w in self.frame_citas_dia.winfo_children():
            w.destroy()
        try:
            # Usamos selection_get para evitar errores de formato de texto
            fecha_obj = self.cal.selection_get()
            fecha_db  = fecha_obj.strftime("%Y-%m-%d")

            # Traemos el 'id' (importante para el delete) y los datos de tu DB
            res = supabase.table("citas").select(
                "id, hora_cita, pacientes(nombre_completo)"
            ).eq("fecha_cita", fecha_db).order("hora_cita").execute()

            citas = res.data or []
            if not citas:
                ctk.CTkLabel(self.frame_citas_dia, text="Sin citas para este día.",
                             text_color=PALETTE["text_light"],
                             font=ctk.CTkFont(size=12, slant="italic")).pack(pady=8)
            else:
                for c in citas:
                    nombre = c.get("pacientes", {}).get("nombre_completo", "—")
                    hora   = c.get("hora_cita", "—")
                    cita_id = c.get("id")

                    fila = ctk.CTkFrame(self.frame_citas_dia, fg_color=PALETTE["card"], corner_radius=8)
                    fila.pack(fill="x", pady=3, padx=4)
                    
                    ctk.CTkLabel(fila, text=f"🕐 {hora}",
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 text_color=PALETTE["teal_dark"],
                                 width=70).pack(side="left", padx=8, pady=6)
                    
                    ctk.CTkLabel(fila, text=nombre,
                                 font=ctk.CTkFont(size=12),
                                 text_color=PALETTE["text"]).pack(side="left", padx=4, expand=True, anchor="w")

                    # BOTÓN ELIMINAR ESTÉTICO
                    ctk.CTkButton(fila, text="✕", width=28, height=28,
                                  fg_color="#FADADD", hover_color="#E88080",
                                  text_color="#E88080", corner_radius=6,
                                  font=ctk.CTkFont(size=12, weight="bold"),
                                  command=lambda cid=cita_id: self.eliminar_cita(cid)).pack(side="right", padx=8)
        except Exception as e:
            print(f"Error al cargar citas: {e}")

    def eliminar_cita(self, cita_id):
        """Borra una cita de Supabase tras confirmar con el usuario."""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas cancelar esta cita?"):
            try:
                # Ejecuta el delete en Supabase usando el ID único
                supabase.table("citas").delete().eq("id", cita_id).execute()
                
                messagebox.showinfo("Éxito", "La cita ha sido eliminada.")
                self._cargar_citas_dia() # Refresca la lista automáticamente
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la cita:\n{e}")

    def guardar_cita(self):
        """Valida y guarda la cita en Supabase."""
        nombre = self.combo_pacientes.get().strip()
        hora   = self.entry_hora_cita.get().strip()

        if not nombre or not hora or nombre == "Sin pacientes registrados":
            messagebox.showwarning("Atención", "Selecciona un paciente e ingresa la hora.")
            return

        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", hora):
            messagebox.showwarning("Formato incorrecto",
                                   "La hora debe estar en formato HH:MM\nEj: 09:30 o 14:00")
            return

        try:
            fecha_obj = self.cal.selection_get()
            fecha_db  = fecha_obj.strftime("%Y-%m-%d")
        except Exception:
            messagebox.showwarning("Error", "No se pudo leer la fecha del calendario.")
            return

        paciente = next(
            (p for p in self.pacientes_data if p["nombre_completo"] == nombre), None)
        if not paciente:
            messagebox.showwarning("Error", "Paciente no válido.")
            return

        try:
            supabase.table("citas").insert({
                "paciente_id": paciente["id"],
                "fecha_cita":      fecha_db,
                "hora_cita":       hora,
                "estado":          "programada",
            }).execute()
            messagebox.showinfo("¡Éxito!", f"Cita agendada:\n👤 {nombre}\n📅 {fecha_db}  🕐 {hora}")
            self.entry_hora_cita.delete(0, "end")
            self._cargar_citas_dia()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la cita:\n{e}")

    # ── Módulos genéricos ────────────────────────────────

    def _modulo_generico(self, titulo, bg=None, fg=None):
        self.limpiar_pantalla()
        bg = bg or PALETTE["teal_light"]
        fg = fg or PALETTE["teal_dark"]
        self._header_secundario(titulo, bg, fg)
        ctk.CTkLabel(self.main_frame,
                     text="🚧\n\nMódulo en desarrollo.\nEstará disponible próximamente.",
                     font=ctk.CTkFont(size=18),
                     text_color=PALETTE["text_soft"]).pack(pady=80)

    def click_historias(self):
        self._modulo_generico("🧠  Historias Clínicas", "#EDE8F8", PALETTE["lav_dark"])

    def click_tratamientos(self):
        self._modulo_generico("💊  Tratamientos", PALETTE["teal_light"], PALETTE["teal_dark"])

    def click_notas(self):
        self._modulo_generico("📝  Notas de Sesión", PALETTE["rose_light"], PALETTE["rose_dark"])

    def click_pagos(self):
        self._modulo_generico("💳  Pagos / Facturación", "#EDE8F8", PALETTE["lav_dark"])

    def click_progreso(self):
        self._modulo_generico("📈  Progreso del Paciente", PALETTE["teal_light"], PALETTE["teal_dark"])

    def click_recordatorios(self):
        self._modulo_generico("🔔  Recordatorios", PALETTE["rose_light"], PALETTE["rose_dark"])

    def click_config(self):
        self._modulo_generico("⚙️  Configuración", "#EDE8F8", PALETTE["lav_dark"])

    def click_stats(self):
        self._modulo_generico("📊  Estadísticas", PALETTE["rose_light"], PALETTE["rose_dark"])


if __name__ == "__main__":
    app = AppKalico()
    app.mainloop()