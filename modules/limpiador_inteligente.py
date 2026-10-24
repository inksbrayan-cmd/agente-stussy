import os
import subprocess
import shutil


def limpiar_sistema():
    """Ejecuta tareas de limpieza de archivos temporales y caché del sistema."""
    reporte = []

    # 1. Limpiar caché del usuario (~/.cache) de carpetas temporales conocidas
    user_cache = os.path.expanduser("~/.cache")
    carpetas_limpiar = ["thumbnails", "pip", "tmp"]

    bytes_liberados = 0
    for carpeta in carpetas_limpiar:
        ruta = os.path.join(user_cache, carpeta)
        if os.path.exists(ruta):
            try:
                for root, dirs, files in os.walk(ruta):
                    for f in files:
                        fp = os.path.join(root, f)
                        bytes_liberados += os.path.getsize(fp)
                shutil.rmtree(ruta)
                os.makedirs(ruta, exist_ok=True)
            except Exception as e:
                print(f"No se pudo limpiar {ruta}: {e}")

    mb_liberados = round(bytes_liberados / (1024 * 1024), 2)
    reporte.append(f"🧹 Caché de usuario: ~{mb_liberados} MB liberados")

    # 2. Limpiar paquetes huérfanos y caché de APT (requiere privilegios o autoclean de usuario)
    try:
        cmd = ["sudo", "apt-get", "autoclean", "-y"]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        reporte.append("📦 Caché de paquetes APT limpiada")
    except Exception:
        pass

    return "\n".join(reporte)


def obtener_espacio_disco():
    """Retorna el espacio libre y total del disco principal."""
    try:
        total, used, free = shutil.disk_usage("/")
        gb_libre = round(free / (1024**3), 2)
        gb_total = round(total / (1024**3), 2)
        return f"Espacio libre: {gb_libre} GB de {gb_total} GB"
    except Exception:
        return "No se pudo obtener la información del disco."
