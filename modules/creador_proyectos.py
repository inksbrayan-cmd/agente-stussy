import os
import subprocess

ESTRUCTURAS = {
    "1": {
        "nombre": "Python (Estándar)",
        "carpetas": ["src", "tests", "docs"],
        "archivos": ["main.py", "requirements.txt", "README.md", ".gitignore"],
    },
    "2": {
        "nombre": "C / C++ / Embedded (Arduino / ESP32)",
        "carpetas": ["src", "include", "lib", "docs"],
        "archivos": ["src/main.cpp", "README.md", ".gitignore"],
    },
    "3": {
        "nombre": "Proyecto Genérico / Universidad",
        "carpetas": ["documentos", "codigo", "esquemas", "recursos"],
        "archivos": ["README.md"],
    },
}

GITIGNORE_PYTHON = "venv/\n__pycache__/\n*.pyc\nlogs/\n.vscode/\n"
GITIGNORE_CPP = "build/\nbin/\n*.o\n*.out\n.vscode/\n.pio/\n"


def crear_proyecto():
    print("\n--- 🛠️ Creador Automático de Proyectos ---")
    print("1. Python (Estándar)")
    print("2. C / C++ / Embedded (Arduino / ESP32)")
    print("3. Proyecto Genérico / Universidad")

    tipo = input("Selecciona el tipo de proyecto (1-3): ").strip()

    if tipo not in ESTRUCTURAS:
        print("❌ Tipo de proyecto no válido.")
        return

    nombre_proyecto = input(
        "Ingresa el nombre del nuevo proyecto (ej. Control_Motor_CAN): "
    ).strip()
    if not nombre_proyecto:
        print("❌ El nombre no puede estar vacío.")
        return

    # Ruta de destino (~/Proyectos/)
    ruta_base = os.path.expanduser("~/Proyectos")
    ruta_proyecto = os.path.join(ruta_base, nombre_proyecto)

    if os.path.exists(ruta_proyecto):
        print(f"⚠️ El proyecto '{nombre_proyecto}' ya existe en {ruta_base}.")
        return

    # Crear carpetas
    os.makedirs(ruta_proyecto, exist_ok=True)
    plantilla = ESTRUCTURAS[tipo]

    for carpeta in plantilla["carpetas"]:
        os.makedirs(os.path.join(ruta_proyecto, carpeta), exist_ok=True)

    # Crear archivos base
    for archivo in plantilla["archivos"]:
        ruta_archivo = os.path.join(ruta_proyecto, archivo)
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            if archivo == "README.md":
                f.write(
                    f"# {nombre_proyecto}\n\nProyecto creado con el agente **STUSSY**.\n"
                )
            elif archivo == ".gitignore":
                if tipo == "1":
                    f.write(GITIGNORE_PYTHON)
                elif tipo == "2":
                    f.write(GITIGNORE_CPP)
            elif archivo == "main.py":
                f.write(
                    'def main():\n    print("¡Proyecto iniciado!")\n\nif __name__ == "__main__":\n    main()\n'
                )

    # Inicializar Git en el nuevo proyecto
    try:
        subprocess.run(
            ["git", "init"],
            cwd=ruta_proyecto,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(" Git inicializado en el nuevo proyecto.")
    except Exception:
        pass

    print(
        f"\n✅ ¡Proyecto '{nombre_proyecto}' creado exitosamente en: {ruta_proyecto}!"
    )


if __name__ == "__main__":
    crear_proyecto()
