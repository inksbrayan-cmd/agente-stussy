import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Alcances (Scopes) requeridos para leer correos en Gmail (lectura únicamente)
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def autenticar_gmail():
    """Maneja la autenticación OAuth 2.0 para la API de Gmail."""
    creds = None
    token_path = "token.json"
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

    return build("gmail", "v1", credentials=creds)


def obtener_resumen_correos(max_resultados=5):
    """Consulta y muestra un resumen de los últimos correos no leídos."""
    print("\n" + "=" * 55)
    print("📬 STUSSY - RESUMEN INTELIGENTE DE CORREOS (GMAIL)")
    print("=" * 55)

    service = autenticar_gmail()
    if not service:
        print("❌ No se pudo conectar con el servicio de Gmail.")
        return

    try:
        # Consultar correos no leídos en la bandeja de entrada
        results = (
            service.users()
            .messages()
            .list(
                userId="me", q="is:unread category:primary", maxResults=max_resultados
            )
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            print(
                "\n✨ ¡Excelente! No tienes correos no leídos en tu bandeja principal."
            )
            print("=" * 55)
            return

        print(f"\n📨 Mostrando los últimos {len(messages)} correos no leídos:\n")

        for idx, msg in enumerate(messages, 1):
            msg_data = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])

            asunto = "Sin Asunto"
            remitente = "Desconocido"
            fecha = ""

            for header in headers:
                name = header.get("name", "").lower()
                if name == "subject":
                    asunto = header.get("value", "")
                elif name == "from":
                    remitente = header.get("value", "")
                elif name == "date":
                    fecha = header.get("value", "")[:16]

            # Recortar fragmento del mensaje si existe
            snippet = msg_data.get("snippet", "Sin vista previa")

            print(f"  {idx}. 📌 Asunto: {asunto}")
            print(f"     👤 De: {remitente}")
            print(f"     📅 Fecha: {fecha}")
            print(
                f"     💬 Vista previa: {snippet[:80]}...\n"
                if len(snippet) > 80
                else f"     💬 Vista previa: {snippet}\n"
            )

        print("=" * 55)

    except Exception as e:
        print(f"⚠️ Error al consultar los correos: {e}")


def menu_correos():
    """Submenú interactivo para el resumen de correos."""
    while True:
        print("\n" + "=" * 40)
        print("📬 STUSSY - RESUMEN DE CORREOS")
        print("=" * 40)
        print("1. 📥 Ver correos no leídos recientes")
        print("2. 🔙 Volver al menú principal")
        print("=" * 40)

        opcion = input("Selecciona una opción (1-2): ").strip()

        if opcion == "1":
            obtener_resumen_correos()
        elif opcion == "2":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_correos()
