import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.modify",
]

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
        "pcb",
    ],
    "Promociones_Spam": [
        "descuento",
        "oferta",
        "gana",
        "premio",
        "casino",
        "credito inmediato",
        "loan",
    ],
}


def autenticar_google(cuenta_personalizada=None):
    """Autenticación unificada para Gmail y Drive con rutas absolutas."""
    creds = None
    base_dir = os.path.expanduser("~/agente-stussy")
    token_filename = (
        f"token_{cuenta_personalizada}.json" if cuenta_personalizada else "token.json"
    )
    token_path = os.path.join(base_dir, token_filename)
    creds_path = os.path.join(base_dir, "credentials.json")

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
                return None, None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds), build(
        "drive", "v3", credentials=creds
    )


def obtener_o_crear_etiqueta(service, nombre_etiqueta):
    """Verifica si la etiqueta existe en Gmail; si no, la crea automáticamente."""
    try:
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        for label in labels:
            if label["name"].lower() == nombre_etiqueta.lower():
                return label["id"]

        label_object = {
            "name": nombre_etiqueta,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        nueva_etiqueta = (
            service.users().labels().create(userId="me", body=label_object).execute()
        )
        return nueva_etiqueta["id"]
    except Exception:
        return None
