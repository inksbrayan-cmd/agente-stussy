import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def autenticar_google(cuenta_personalizada=None):
    """Autenticación unificada para Gmail y Drive."""
    creds = None
    token_path = (
        f"token_{cuenta_personalizada}.json" if cuenta_personalizada else "token.json"
    )
    creds_path = "credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            if not os.path.exists(creds_path):
                print(f"\n⚠️ No se encontró el archivo '{creds_path}'.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds), build(
        "drive", "v3", credentials=creds
    )


def gestionar_adjuntos_correo(cuenta_personalizada=None):
    """Busca correos con archivos adjuntos y permite guardarlos en Google Drive."""
    nombre_cuenta = (
        "TEINCO (Universidad)" if cuenta_personalizada == "teinco" else "Personal"
    )

    print("\n" + "=" * 60)
    print(f"📎 STUSSY - GESTOR DE ADJUNTOS Y GOOGLE DRIVE ({nombre_cuenta.upper()})")
    print("=" * 60)

    gmail_service, drive_service = autenticar_google(
        cuenta_personalizada=cuenta_personalizada
    )
    if not gmail_service or not drive_service:
        print("❌ No se pudo conectar con los servicios de Google.")
        return

    try:
        results = (
            gmail_service.users()
            .messages()
            .list(userId="me", q="has:attachment", maxResults=5)
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            print(
                f"\n✨ No se encontraron correos con archivos adjuntos recientes en {nombre_cuenta}."
            )
            print("=" * 60)
            return

        print(f"\n📨 Encontrados {len(messages)} correos con archivos adjuntos:\n")

        adjuntos_encontrados = []

        for idx, msg in enumerate(messages, 1):
            msg_data = (
                gmail_service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])

            asunto = "Sin Asunto"
            remitente = "Desconocido"
            for header in headers:
                if header.get("name", "").lower() == "subject":
                    asunto = header.get("value", "")
                elif header.get("name", "").lower() == "from":
                    remitente = header.get("value", "")

            parts = msg_data.get("payload", {}).get("parts", [])
            for part in parts:
                filename = part.get("filename")
                if filename:
                    attachment_id = part.get("body", {}).get("attachmentId")
                    if attachment_id:
                        print(f"  {idx}. 📄 Archivo: {filename}")
                        print(f"     📌 Asunto: {asunto}")
                        print(f"     👤 De: {remitente}\n")

                        adjuntos_encontrados.append(
                            {
                                "msg_id": msg["id"],
                                "attachment_id": attachment_id,
                                "filename": filename,
                                "asunto": asunto,
                            }
                        )

        if not adjuntos_encontrados:
            print(
                "✨ Los correos tienen etiquetas de adjuntos pero no archivos descargables directos."
            )
            print("=" * 60)
            return

        print("-" * 60)
        confirmacion = (
            input(
                "¿Deseas descargar estos archivos y subirlos automáticamente a Google Drive? (S/N): "
            )
            .strip()
            .lower()
        )

        if confirmacion == "s":
            temp_dir = "temp_adjuntos"
            os.makedirs(temp_dir, exist_ok=True)

            print("\n☁️ Procesando y subiendo archivos a Google Drive...")
            for item in adjuntos_encontrados:
                attachment = (
                    gmail_service.users()
                    .messages()
                    .attachments()
                    .get(
                        userId="me", messageId=item["msg_id"], id=item["attachment_id"]
                    )
                    .execute()
                )

                file_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
                file_path = os.path.join(temp_dir, item["filename"])

                with open(file_path, "wb") as f:
                    f.write(file_data)

                from googleapiclient.http import MediaFileUpload

                file_metadata = {"name": item["filename"]}
                media = MediaFileUpload(file_path, resumable=True)

                uploaded_file = (
                    drive_service.files()
                    .create(body=file_metadata, media_body=media, fields="id")
                    .execute()
                )

                print(
                    f"   ✔ Subido a Drive: {item['filename']} (ID: {uploaded_file.get('id')})"
                )
                os.remove(file_path)

            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

            print(
                "\n✨ ¡Todos los adjuntos seleccionados fueron sincronizados a Google Drive con éxito!"
            )
        else:
            print("\n❌ Operación cancelada por el usuario.")

        print("=" * 60)

    except Exception as e:
        print(f"⚠️ Error al procesar los archivos adjuntos: {e}")


def menu_adjuntos():
    """Submenú interactivo para gestionar adjuntos según la cuenta."""
    while True:
        print("\n" + "=" * 50)
        print("📎 STUSSY - GESTOR DE ADJUNTOS Y GOOGLE DRIVE")
        print("=" * 50)
        print("1. 📂 Sincronizar adjuntos (Cuenta Personal)")
        print("2. 🎓 Sincronizar adjuntos (Cuenta TEINCO)")
        print("3. 🔙 Volver al menú principal")
        print("=" * 50)

        opcion = input("Selecciona una opción (1-3): ").strip()

        if opcion == "1":
            gestionar_adjuntos_correo(cuenta_personalizada=None)
        elif opcion == "2":
            gestionar_adjuntos_correo(cuenta_personalizada="teinco")
        elif opcion == "3":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_adjuntos()
