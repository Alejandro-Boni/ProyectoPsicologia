# 🌸 KALICO — Gestión Psicológica

>** Nota de Desarrollo: ** este es un proyecto acaemico y personal que se encuentra actualmente en **fase activa de desarrollo**. Algunas funcionalidades pueden estar limitadas o en proceso de implementacion.

**KALICO** es una aplicación de escritorio moderna y elegante diseñada para optimizar la gestión de consultas psicológicas. Desarrollada en Python, combina una interfaz de usuario "Premium Pastel" con la potencia de **Supabase** para el manejo de datos en tiempo real.

---

## ✨ Características Principales

* **Panel de Control 3x3:** Interfaz intuitiva con acceso directo a 9 módulos clave.
* **Gestión de Pacientes:** Registro completo, edición y búsqueda avanzada por nombre o documento.
* **Agenda Inteligente:** Sistema de citas vinculado directamente a la base de datos de pacientes.
* **Arquitectura en la Nube:** Integración total con Supabase para persistencia de datos segura.
* **Diseño Custom:** Interfaz personalizada utilizando `CustomTkinter` y procesamiento de imágenes con `PIL` para una experiencia visual única.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.13+
* **Interfaz Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Base de Datos:** [Supabase](https://supabase.com/) (PostgreSQL)
* **Manejo de Imágenes:** Pillow (PIL)
* **Variables de Entorno:** Python-dotenv

---

## 🚀 Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/kalico.git](https://github.com/tu-usuario/kalico.git)
    cd kalico
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto y añade tus credenciales de Supabase:
    ```env
    SUPABASE_URL=tu_url_de_supabase
    SUPABASE_KEY=tu_anon_key_de_supabase
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    python main.py
    ```

---

## 📂 Estructura del Proyecto

* `main.py`: Archivo principal con la lógica de la aplicación y la clase `AppKalico`.
* `Imagen/`: Directorio que contiene los recursos visuales (`marcaDeAgua.jpeg`, `doctora.jpeg`).
* `.env`: Configuración segura de claves (no incluido en el repositorio).
* `requirements.txt`: Lista de librerías necesarias.


---
> *Este proyecto fue desarrollado pensando en la eficiencia y la calidez que requiere la práctica de la psicología clínica.*
> *Este software se desarrolla con el objetivo de brindar una herramienta tecnologica eficiente para el sector de la salud mental.*
