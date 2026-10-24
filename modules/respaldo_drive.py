import os
import datetime
from googleapiclient.http import MediaFileUpload
from modules.organizador_correos import autenticar_google


def hacer_respaldo_drive():
    """Sube una copia de seguridad de la base de datos tasks.db a Google Drive."""
    print("\n" + "=" * 60)
    print("☁️ STUSSY - RESPALDO AUTOMÁTICO DE BASE DE DATOS A GOOGLE DRIVE")
    print("=" * 60)

    _, drive_service = autenticar_google(cuenta_personalizada=None)
    if not drive_service:
        print("❌ No se pudo conectar con el servicio de Google Drive.")
        return False

    db_path = os.path.expanduser("~/agente-stussy/tasks.db")
    if not os.path.exists(db_path):
        print(f"⚠️ No se encontró la base de datos en {db_path}")
        return False

    try:
        # Buscar o crear la carpeta 'Stussy_Backups' en Google Drive
        folder_name = "Stussy_Backups"
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = (
            drive_service.files()
            .list(q=query, spaces="drive", fields="files(id, name)")
            .execute()
        )
        folders = results.get("files", [])

        if folders:
            folder_id = folders[0]["id"]
            print(f"📁 Carpeta encontrada en Drive: '{folder_name}' (ID: {folder_id})")
        else:
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = (
                drive_service.files()
                .create(body=folder_metadata, fields="id")
                .execute()
            )
            folder_id = folder.get("id")
            print(f"📁 Carpeta creada en Drive: '{folder_name}' (ID: {folder_id})")

        # Generar nombre con la fecha y hora actual
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"tasks_backup_{timestamp}.db"

        # Metadatos del archivo y subida
        file_metadata = {"name": backup_filename, "parents": [folder_id]}

        media = MediaFileUpload(
            db_path, mimetype="application/x-sqlite3", resumable=True
        )

        print(f"🚀 Subiendo '{backup_filename}' a Google Drive...")
        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        print(f"✨ ¡Respaldo completado con éxito! ID en Drive: {file.get('id')}")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"⚠️ Error al realizar el respaldo en Google Drive: {e}")
        return False


if __name__ == "__main__":
    hacer_respaldo_drive()
