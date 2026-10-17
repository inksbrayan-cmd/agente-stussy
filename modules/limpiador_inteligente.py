import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.modify",  # Requerido para mover a la papelera o modificar etiquetas
]


def autenticar_gmail(cuenta_personalizada=None):
    """Maneja la autenticación OAuth 2.0 con permisos de modificación para Gmail."""
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

    return build("gmail", "v1", credentials=creds)


def limpiar_spam_y_promociones(cuenta_personalizada=None):
    """Busca correos de promociones, spam o sospechosos y pide confirmación S/N antes de borrarlos."""
    nombre_cuenta = (
        "TEINCO (Universidad)" if cuenta_personalizada == "teinco" else "Personal"
    )

    print("\n" + "=" * 60)
    print(
        f"🧹 STUSSY - LIMPIEZA SEGURA DE SPAM Y PROMOCIONES ({nombre_cuenta.upper()})"
    )
    print("=" * 60)

    service = autenticar_gmail(cuenta_personalizada=cuenta_personalizada)
    if not service:
        print("❌ No se pudo conectar con el servicio de Gmail.")
        return

    try:
        # Consulta para buscar correos en categorías de promociones o con términos sospechosos comunes
        query = "category:promotions OR label:spam"
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=10)
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            print(
                f"\n✨ ¡Excelente! No se encontraron correos de spam o promociones masivas en {nombre_cuenta}."
            )
            print("=" * 60)
            return

        print(f"\n🔍 Se encontraron {len(messages)} correos candidatos a limpieza:\n")

        mensajes_a_procesar = []

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

            for header in headers:
                name = header.get("name", "").lower()
                if name == "subject":
                    asunto = header.get("value", "")
                elif name == "from":
                    remitente = header.get("value", "")

            snippet = msg_data.get("snippet", "Sin vista previa")

            print(f"  {idx}. 📌 Asunto: {asunto}")
            print(f"     👤 De: {remitente}")
            print(f"     💬 Vista previa: {snippet[:75]}...\n")

            mensajes_a_procesar.append(
                {"id": msg["id"], "asunto": asunto, "remitente": remitente}
            )

        print("-" * 60)
        print("🛡️ MODO DE SEGURIDAD ACTIVADO: STUSSY NUNCA ELIMINA AUTOMÁTICAMENTE.")

        confirmacion = (
            input("¿Deseas enviar estos correos listados a la papelera? (S/N): ")
            .strip()
            .lower()
        )

        if confirmacion == "s":
            print("\n🗑️ Moviendo correos seleccionados a la papelera...")
            for item in mensajes_a_procesar:
                # Mover a la papelera (trash) en lugar de borrar permanentemente (delete)
                service.users().messages().trash(userId="me", id=item["id"]).execute()
                print(f"   ✔ Enviado a papelera: {item['asunto'][:40]}...")
            print("\n✨ ¡Limpieza completada de forma segura!")
        else:
            print(
                "\n❌ Operación cancelada por el usuario. Ningún correo fue modificado."
            )

        print("=" * 60)

    except Exception as e:
        print(f"⚠️ Error durante el proceso de limpieza: {e}")


def menu_limpieza():
    """Submenú interactivo para elegir la cuenta a limpiar."""
    while True:
        print("\n" + "=" * 50)
        print("🧹 STUSSY - GESTIÓN DE LIMPIEZA Y SEGURIDAD")
        print("=" * 50)
        print("1. 🧹 Limpiar Spam y Promociones (Cuenta Personal)")
        print("2. 🧹 Limpiar Spam y Promociones (Cuenta TEINCO)")
        print("3. 🔙 Volver al menú principal")
        print("=" * 50)

        opcion = input("Selecciona una opción (1-3): ").strip()

        if opcion == "1":
            limpiar_spam_y_promociones(cuenta_personalizada=None)
        elif opcion == "2":
            limpiar_spam_y_promociones(cuenta_personalizada="teinco")
        elif opcion == "3":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_limpieza()
