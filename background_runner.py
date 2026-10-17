import time
import os
from datetime import datetime
from modules.organizador import organizar_descargas
from modules.monitor import mostrar_estado_sistema


def tarea_automatica():
    """Ejecuta rutinas automáticas en segundo plano."""
    print(
        f"\n[BACKGROUND] Ejecutando rutina automática de STUSSY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # 1. Organizar descargas automáticamente
    try:
        organizar_descargas()
        print("[BACKGROUND] Carpeta Descargas optimizada correctamente.")
    except Exception as e:
        print(f"[BACKGROUND] Error al organizar descargas: {e}")


def main():
    print("🤖 STUSSY Background Runner iniciado en segundo plano.")
    # Intervalo en segundos (ej. cada 1 hora = 3600 segundos. Para pruebas puedes poner 300 para 5 mins)
    INTERVALO = 3600

    while True:
        tarea_automatica()
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
