import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Alcances (Scopes) requeridos para administrar archivos y carpetas en Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive"]


def autenticar_drive():
    """Maneja la autenticación OAuth 2.0 para Google Drive."""
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"\n⚠️ No se encontró el archivo '{creds_path}'.")
                print(
                    "📌 Para conectar Drive necesitas colocar 'credentials.json' en la raíz del proyecto."
                )
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def verificar_estructura_drive():
    """Verifica y crea la estructura organizada de carpetas en Google Drive."""
    print("\n" + "=" * 50)
    print("☁️ STUSSY - ORGANIZADOR DE GOOGLE DRIVE")
    print("=" * 50)

    service = autenticar_drive()
    if not service:
        return

    # Estructura maestra a garantizar en Google Drive
    estructura = {
        "TEINCO_Semestre_3": [
            "01_Mecatronica",
            "02_Circuitos_Laboratorios",
            "03_Programacion_C_Python",
            "04_Informes_Tecnicos",
        ],
        "CIJAD_SAS_Trabajo": [
            "Proyectos",
            "Diagnosticos_Automotrices",
            "Documentacion",
        ],
        "Personal_Stussy": ["Respaldo_Codigos", "Certificados_Apuntes"],
    }

    print("\n🔍 Verificando estructura de carpetas en Google Drive...")

    for carpeta_principal, subcarpetas in estructura.items():
        query = f"name = '{carpeta_principal}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = (
            service.files()
            .list(q=query, pageSize=1, fields="files(id, name)")
            .execute()
        )
        items = results.get("files", [])

        if not items:
            file_metadata = {
                "name": carpeta_principal,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = service.files().create(body=file_metadata, fields="id").execute()
            parent_id = folder.get("id")
            print(f"📁 Creada carpeta principal: [{carpeta_principal}]")
        else:
            parent_id = items[0]["id"]
            print(f"📁 Encontrada carpeta principal: [{carpeta_principal}]")

        for sub in subcarpetas:
            sub_query = f"name = '{sub}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            sub_results = (
                service.files()
                .list(q=sub_query, pageSize=1, fields="files(id, name)")
                .execute()
            )
            sub_items = sub_results.get("files", [])

            if not sub_items:
                sub_metadata = {
                    "name": sub,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_id],
                }
                service.files().create(body=sub_metadata, fields="id").execute()
                print(f"   └── 📂 Subcarpeta creada: {sub}")
            else:
                print(f"   └── 📂 Subcarpeta existente: {sub}")

    print("\n✅ ¡Estructura de Google Drive verificada y sincronizada!")
    print("=" * 50)


def menu_drive():
    """Submenú interactivo para Google Drive."""
    while True:
        print("\n" + "=" * 40)
        print("☁️ STUSSY - GOOGLE DRIVE")
        print("=" * 40)
        print("1. 📂 Sincronizar y verificar estructura en la nube")
        print("2. 🔙 Volver al menú principal")
        print("=" * 40)

        opcion = input("Selecciona una opción (1-2): ").strip()

        if opcion == "1":
            verificar_estructura_drive()
        elif opcion == "2":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_drive()
