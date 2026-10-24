import os


def crear_proyecto_ingenieria(nombre_proyecto):
    """Crea una estructura estándar de carpetas y archivos para un proyecto de ingeniería."""
    base_dir = os.path.expanduser("~/agente-stussy/proyectos")
    project_path = os.path.join(base_dir, nombre_proyecto)

    carpetas = [
        "src",  # Código fuente
        "firmware",  # Microcontroladores (Arduino, ESP32)
        "cad",  # Diseños 3D / PCB
        "docs",  # Datasheets y manuales
        "tests",  # Pruebas y validaciones
    ]

    try:
        os.makedirs(project_path, exist_ok=True)
        for carpeta in carpetas:
            os.makedirs(os.path.join(project_path, carpeta), exist_ok=True)

        readme_path = os.path.join(project_path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# Proyecto: {nombre_proyecto}\n\n")
                f.write(
                    "Generado automáticamente por **Stussy Asistente Inteligente** para Zorin OS.\n\n"
                )
                f.write(
                    "## 📂 Estructura:\n- `src/`\n- `firmware/`\n- `cad/`\n- `docs/`\n- `tests/`\n"
                )

        return project_path
    except Exception as e:
        print(f"❌ Error al crear el proyecto de ingeniería: {e}")
        return None
