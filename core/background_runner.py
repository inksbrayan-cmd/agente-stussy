import os
import time
import subprocess


def notificar_escritorio(titulo, mensaje):
    """Envía una notificación persistente al centro de notificaciones de Zorin OS."""
    try:
        # Usamos --urgency=normal y un hint de persistencia o categoría para que se guarde
        subprocess.run(
            [
                "notify-send",
                titulo,
                mensaje,
                "--urgency=normal",
                "-h",
                "string:x-canonical-private-synchronous:stussy-alerta",
            ]
        )
    except Exception:
        pass


def verificar_pendientes():
    """Revisa si hay documentos de estudio o archivos para clasificar."""
    carpeta_descargas = os.path.expanduser("~/Descargas")
    extensiones_estudio = (".pdf", ".docx", ".xlsx", ".py", ".ino", ".txt")

    if os.path.exists(carpeta_descargas):
        archivos = [
            f
            for f in os.listdir(carpeta_descargas)
            if f.lower().endswith(extensiones_estudio)
        ]
        if archivos:
            notificar_escritorio(
                "🤖 STUSSY - Control Académico",
                f"Se encontraron {len(archivos)} archivo(s) académico(s) pendientes de clasificar.",
            )


if __name__ == "__main__":
    verificar_pendientes()
