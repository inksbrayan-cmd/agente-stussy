import os
import shutil

CATEGORIAS = {
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
    "Archivos_Comprimidos": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Programas_y_Binarios": [".deb", ".sh", ".iso", ".exe", ".bin"],
    "Codigo_y_Proyectos": [".py", ".c", ".cpp", ".h", ".ino", ".json", ".sql"],
}


def organizar_descargas():
    ruta_descargas = os.path.expanduser("~/Descargas")

    if not os.path.exists(ruta_descargas):
        print("❌ No se encontró la carpeta Descargas.")
        return

    archivos_movidos = 0

    for elemento in os.listdir(ruta_descargas):
        ruta_elemento = os.path.join(ruta_descargas, elemento)

        if os.path.isdir(ruta_elemento):
            continue

        nombre, extension = os.path.splitext(elemento)
        extension = extension.lower()

        for carpeta, extensiones in CATEGORIAS.items():
            if extension in extensiones:
                destino_carpeta = os.path.join(ruta_descargas, carpeta)
                os.makedirs(destino_carpeta, exist_ok=True)

                shutil.move(ruta_elemento, os.path.join(destino_carpeta, elemento))
                print(f"📦 Movido: {elemento} -> Descargas/{carpeta}/")
                archivos_movidos += 1
                break

    if archivos_movidos == 0:
        print("✨ ¡La carpeta Descargas ya está limpia y organizada!")
    else:
        print(f"✅ Se organizaron {archivos_movidos} archivos con éxito.")


if __name__ == "__main__":
    organizar_descargas()
