import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.modify",  # Necesario para crear etiquetas y modificar mensajes
]

# Diccionario de reglas y palabras clave para categorizar correos
REGLAS_CATEGORIAS = {
    "TEINCO_Academico": [
        "teinco",
        "parcial",
        "semestre",
        "matricula",
        "campus",
        "nota",
        "profesor",
    ],
    "Trabajo_CIJAD": ["cijad", "staff 360", "empleo", "contrato", "nomina", "cargo"],
    "Circuitos_Proyectos": [
        "circuitos",
        "arduino",
        "python",
        "onshape",
        "robot",
        "terreneitor",
        "pcb",
    ],
    "Promociones_Spam": [
        "descuento",
        "oferta",
        "gana",
        "premio",
        "casino",
        "loan",
        "credito inmediato",
    ],
}


def autenticar_gmail(cuenta_personalizada=None):
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
                print(f"\n⚠️ No se encontró '{creds_path}'.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def obtener_o_crear_etiqueta(service, nombre_etiqueta):
    """Verifica si la etiqueta existe en Gmail; si no existe, la crea automáticamente."""
    try:
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"].lower() == nombre_etiqueta.lower():
                return label["id"]

        # Si no existe, la creamos
        label_object = {
            "name": nombre_etiqueta,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        nueva_etiqueta = (
            service.users().labels().create(userId="me", body=label_object).execute()
        )
        print(f"   🏷️ Etiqueta creada en tu Gmail: '{nombre_etiqueta}'")
        return nueva_etiqueta["id"]
    except Exception as e:
        print(f"⚠️ Error gestionando etiqueta {nombre_etiqueta}: {e}")
        return None


def clasificar_y_organizar_bandeja(cuenta_personalizada=None):
    """Escanea todos los correos recientes, los categoriza y aplica etiquetas con confirmación S/N."""
    nombre_cuenta = (
        "TEINCO (Universidad)" if cuenta_personalizada == "teinco" else "Personal"
    )

    print("\n" + "=" * 65)
    print(
        f"🏷️ STUSSY - ORGANIZADOR Y CATEGORIZADOR DE CORREOS ({nombre_cuenta.upper()})"
    )
    print("=" * 65)

    service = autenticar_gmail(cuenta_personalizada=cuenta_personalizada)
    if not service:
        print("❌ No se pudo conectar con el servicio de Gmail.")
        return

    try:
        # Consultar los últimos 15 correos de la bandeja
        results = service.users().messages().list(userId="me", maxResults=15).execute()
        messages = results.get("messages", [])

        if not messages:
            print("✨ Tu bandeja de entrada está vacía.")
            return

        print(f"\n🔍 Analizando y clasificando {len(messages)} correos recientes...\n")
        propuestas = []

        for msg in messages:
            msg_data = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])

            asunto = "Sin Asunto"
            remitente = "Desconocido"
            for h in headers:
                name = h.get("name", "").lower()
                if name == "subject":
                    asunto = h.get("value", "")
                elif name == "from":
                    remitente = h.get("value", "")

            texto_analisis = (asunto + " " + remitente).lower()
            categoria_asignada = "General"

            # Evaluar reglas temáticas
            for cat, keywords in REGLAS_CATEGORIAS.items():
                if any(kw in texto_analisis for kw in keywords):
                    categoria_asignada = cat
                    break

            propuestas.append(
                {
                    "id": msg["id"],
                    "asunto": asunto,
                    "remitente": remitente,
                    "categoria": categoria_asignada,
                }
            )

        # Mostrar vista previa de la categorización propuesta
        for idx, p in enumerate(propuestas, 1):
            print(f"  {idx}. 📌 {p['asunto'][:50]}")
            print(f"     👤 De: {p['remitente'][:40]}")
            print(f"     🎯 Categoría sugerida: [{p['categoria']}]\n")

        print("-" * 65)
        confirmacion = (
            input(
                "🛡️ ¿Deseas aplicar estas categorías creando/asignando las etiquetas en tu Gmail? (S/N): "
            )
            .strip()
            .lower()
        )

        if confirmacion == "s":
            print("\n🔄 Aplicando etiquetas en Gmail...")
            for p in propuestas:
                if p["categoria"] != "General":
                    label_id = obtener_o_crear_etiqueta(service, p["categoria"])
                    if label_id:
                        # Añadir la etiqueta al correo
                        body = {"addLabelIds": [label_id]}
                        service.users().messages().batchModify(
                            userId="me",
                            body={"ids": [p["id"]], "addLabelIds": [label_id]},
                        ).execute()
            print(
                "\n✨ ¡Correos categorizados y etiquetas sincronizadas con éxito en tu cuenta!"
            )
        else:
            print("\n❌ Operación cancelada. No se modificó ninguna etiqueta.")

        print("=" * 65)

    except Exception as e:
        print(f"⚠️ Error durante la categorización: {e}")


def menu_organizador_correos():
    while True:
        print("\n" + "=" * 50)
        print("🏷️ STUSSY - MENÚ ORGANIZADOR DE CORREOS")
        print("=" * 50)
        print("1. 📂 Categorizar y etiquetar cuenta Personal")
        print("2. 📂 Categorizar y etiquetar cuenta TEINCO")
        print("3. 🔙 Volver al menú principal")
        print("=" * 50)

        opcion = input("Selecciona una opción (1-3): ").strip()
        if opcion == "1":
            clasificar_y_organizar_bandeja(cuenta_personalizada=None)
        elif opcion == "2":
            clasificar_y_organizar_bandeja(cuenta_personalizada="teinco")
        elif opcion == "3":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_organizador_correos()
