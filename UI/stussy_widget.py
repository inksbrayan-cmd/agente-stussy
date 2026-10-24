import os
import sys
import psutil
import subprocess
import sqlite3
import base64

# Forzar el backend de X11 para asegurar el posicionamiento exacto
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

# Asegurar la ruta absoluta del proyecto e importar módulos de forma segura
project_path = os.path.expanduser("~/agente-stussy")
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Importar funciones de correo de Gmail
try:
    from modules.organizador_correos import (
        autenticar_google,
        REGLAS_CATEGORIAS,
        obtener_o_crear_etiqueta,
    )
except Exception as e:
    print(f"⚠️ Advertencia al importar organizador_correos: {e}")
    autenticar_google = None
    REGLAS_CATEGORIAS = {}
    obtener_o_crear_etiqueta = None

# Importar módulo de respaldo a Google Drive
try:
    from modules.respaldo_drive import hacer_respaldo_drive
except Exception as e:
    print(f"⚠️ Advertencia al importar respaldo_drive: {e}")
    hacer_respaldo_drive = None

# Importar módulo creador de proyectos de ingeniería
try:
    from modules.creador_proyectos import crear_proyecto_ingenieria
except Exception as e:
    print(f"⚠️ Advertencia al importar creador_proyectos: {e}")
    crear_proyecto_ingenieria = None

# Importar módulo limpiador inteligente del sistema
try:
    from modules.limpiador_inteligente import limpiar_sistema, obtener_espacio_disco
except Exception as e:
    print(f"⚠️ Advertencia al importar limpiador_inteligente: {e}")
    limpiar_sistema = None
    obtener_espacio_disco = None

DB_PATH = os.path.expanduser("~/agente-stussy/tasks.db")


class DashboardPanel(QWidget):
    """Centro de control gráfico con tareas, hardware, multimedia y automatización"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(360, 560)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 18, 22, 0.96);
                border: 1px solid rgba(0, 255, 204, 0.3);
                border-radius: 16px;
            }
            QLabel {
                color: white;
                font-family: sans-serif;
                border: none;
                background: transparent;
            }
            QPushButton {
                background-color: rgba(0, 255, 204, 0.15);
                color: #00ffcc;
                border: 1px solid rgba(0, 255, 204, 0.4);
                border-radius: 8px;
                padding: 6px 10px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 204, 0.3);
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 4px 8px;
            }
            QListWidget {
                background-color: rgba(0, 0, 0, 0.3);
                color: #00ffcc;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                font-size: 11px;
            }
        """)

        inner_layout = QVBoxLayout(container)

        title_label = QLabel("🚀 STUSSY - CENTRO DE CONTROL INTEGRAL")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #00ffcc;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(title_label)

        # Lista de tareas
        self.task_list = QListWidget()
        inner_layout.addWidget(self.task_list)

        # Input y botón para nueva tarea
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nueva tarea...")
        btn_add = QPushButton("➕")
        btn_add.setFixedWidth(40)
        btn_add.clicked.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(btn_add)
        inner_layout.addLayout(input_layout)

        # Botones de automatización (Correo, Drive, Respaldo, Proyectos y Limpieza)
        mail_layout = QVBoxLayout()

        row1_layout = QHBoxLayout()
        self.btn_categorize = QPushButton("🏷️ Categorizar Correos")
        self.btn_categorize.clicked.connect(self.run_categorize_mail)
        self.btn_sync = QPushButton("📎 Sincronizar Adjuntos")
        self.btn_sync.clicked.connect(self.run_sync_drive)
        row1_layout.addWidget(self.btn_categorize)
        row1_layout.addWidget(self.btn_sync)
        mail_layout.addLayout(row1_layout)

        self.btn_backup = QPushButton("💾 Respaldar Base de Datos a Drive")
        self.btn_backup.clicked.connect(self.run_drive_backup)
        mail_layout.addWidget(self.btn_backup)

        self.btn_project = QPushButton("📁 Nuevo Proyecto de Ingeniería")
        self.btn_project.clicked.connect(self.run_project_generator)
        mail_layout.addWidget(self.btn_project)

        self.btn_clean = QPushButton("🧹 Limpiador Inteligente del Sistema")
        self.btn_clean.clicked.connect(self.run_system_cleaner)
        mail_layout.addWidget(self.btn_clean)

        inner_layout.addLayout(mail_layout)

        # Botones de control general
        btn_layout = QHBoxLayout()
        self.btn_media = QPushButton("⏯️ Play/Pause")
        self.btn_media.clicked.connect(self.toggle_media)

        self.btn_close = QPushButton("❌ Cerrar")
        self.btn_close.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_media)
        btn_layout.addWidget(self.btn_close)
        inner_layout.addLayout(btn_layout)

        layout.addWidget(container)
        self.setLayout(layout)
        self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        try:
            if os.path.exists(DB_PATH):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT id, title FROM tasks WHERE status='pendiente'")
                tasks = c.fetchall()
                conn.close()
                for task in tasks:
                    self.task_list.addItem(f"📌 [{task[0]}] {task[1]}")
            else:
                self.task_list.addItem("No hay tareas registradas")
        except Exception as e:
            self.task_list.addItem(f"Error al cargar: {e}")

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO tasks (title) VALUES (?)", (text,))
                conn.commit()
                conn.close()
                self.task_input.clear()
                self.load_tasks()
            except Exception:
                pass

    def run_categorize_mail(self):
        if not autenticar_google:
            QMessageBox.warning(
                self, "Error", "Módulo de organización de correos no disponible."
            )
            return

        reply = QMessageBox.question(
            self,
            "Categorizar Correos",
            "¿Deseas que Stussy escanee y etiquete tus correos recientes de Gmail?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                gmail_service, _ = autenticar_google(cuenta_personalizada=None)
                if gmail_service:
                    results = (
                        gmail_service.users()
                        .messages()
                        .list(userId="me", maxResults=10)
                        .execute()
                    )
                    messages = results.get("messages", [])
                    for msg in messages:
                        msg_data = (
                            gmail_service.users()
                            .messages()
                            .get(userId="me", id=msg["id"], format="full")
                            .execute()
                        )
                        headers = msg_data.get("payload", {}).get("headers", [])
                        asunto = ""
                        for h in headers:
                            if h.get("name", "").lower() == "subject":
                                asunto = h.get("value", "").lower()

                        for cat, keywords in REGLAS_CATEGORIAS.items():
                            if any(kw in asunto for kw in keywords):
                                label_id = obtener_o_crear_etiqueta(gmail_service, cat)
                                if label_id:
                                    gmail_service.users().messages().batchModify(
                                        userId="me",
                                        body={
                                            "ids": [msg["id"]],
                                            "addLabelIds": [label_id],
                                        },
                                    ).execute()
                                break
                    QMessageBox.information(
                        self,
                        "Éxito",
                        "✨ ¡Correos categorizados y etiquetados con éxito!",
                    )
                else:
                    QMessageBox.warning(self, "Error", "No se pudo conectar con Gmail.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error: {e}")

    def run_sync_drive(self):
        if not autenticar_google:
            QMessageBox.warning(self, "Error", "Módulo de Google Drive no disponible.")
            return

        reply = QMessageBox.question(
            self,
            "Sincronizar Adjuntos",
            "¿Deseas buscar archivos adjuntos en tus correos y subirlos a Google Drive?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "En proceso",
                "Stussy está procesando los adjuntos en segundo plano...",
            )
            try:
                gmail_service, drive_service = autenticar_google(
                    cuenta_personalizada=None
                )
                if gmail_service and drive_service:
                    results = (
                        gmail_service.users()
                        .messages()
                        .list(userId="me", q="has:attachment", maxResults=3)
                        .execute()
                    )
                    messages = results.get("messages", [])
                    subidos = 0
                    temp_dir = "temp_adjuntos"
                    os.makedirs(temp_dir, exist_ok=True)

                    for msg in messages:
                        msg_data = (
                            gmail_service.users()
                            .messages()
                            .get(userId="me", id=msg["id"], format="full")
                            .execute()
                        )
                        parts = msg_data.get("payload", {}).get("parts", [])
                        for part in parts:
                            filename = part.get("filename")
                            attachment_id = part.get("body", {}).get("attachmentId")
                            if filename and attachment_id:
                                attachment = (
                                    gmail_service.users()
                                    .messages()
                                    .attachments()
                                    .get(
                                        userId="me",
                                        messageId=msg["id"],
                                        id=attachment_id,
                                    )
                                    .execute()
                                )
                                file_data = base64.urlsafe_b64decode(
                                    attachment["data"].encode("UTF-8")
                                )
                                file_path = os.path.join(temp_dir, filename)
                                with open(file_path, "wb") as f:
                                    f.write(file_data)

                                from googleapiclient.http import MediaFileUpload

                                file_metadata = {"name": filename}
                                media = MediaFileUpload(file_path, resumable=True)
                                drive_service.files().create(
                                    body=file_metadata, media_body=media, fields="id"
                                ).execute()
                                os.remove(file_path)
                                subidos += 1

                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)

                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"✨ ¡{subidos} archivos adjuntos sincronizados a Google Drive!",
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "No se pudo conectar con Google."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error al sincronizar adjuntos: {e}"
                )

    def run_drive_backup(self):
        if not hacer_respaldo_drive:
            QMessageBox.warning(self, "Error", "Módulo de respaldo no disponible.")
            return

        reply = QMessageBox.question(
            self,
            "Respaldo en Google Drive",
            "¿Deseas subir una copia de seguridad de tu base de datos (tasks.db) a Google Drive?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                exito = hacer_respaldo_drive()
                if exito:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        "✨ ¡Base de datos respaldada en Google Drive con éxito!",
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "No se pudo completar el respaldo en Drive."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error: {e}")

    def run_project_generator(self):
        """Abre un diálogo para crear un nuevo proyecto de ingeniería con enfoque de ventana"""
        if not crear_proyecto_ingenieria:
            QMessageBox.warning(
                self, "Error", "Módulo creador de proyectos no disponible."
            )
            return

        dialog = QInputDialog(self)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        dialog.setWindowTitle("Nuevo Proyecto de Ingeniería")
        dialog.setLabelText("Ingresa el nombre del proyecto:")

        if dialog.exec() == QInputDialog.DialogCode.Accepted:
            nombre = dialog.textValue().strip()
            if nombre:
                nombre_limpio = nombre.replace(" ", "_")
                ruta = crear_proyecto_ingenieria(nombre_limpio)
                if ruta:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"✨ ¡Proyecto '{nombre_limpio}' creado con éxito!\n\nRuta: {ruta}",
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "No se pudo crear la estructura del proyecto."
                    )

    def run_system_cleaner(self):
        """Ejecuta la limpieza del sistema y muestra el espacio disponible"""
        if not limpiar_sistema:
            QMessageBox.warning(
                self, "Error", "Módulo limpiador inteligente no disponible."
            )
            return

        info_disco = obtener_espacio_disco()
        reply = QMessageBox.question(
            self,
            "Limpiador Inteligente",
            f"📊 Estado actual del disco:\n{info_disco}\n\n¿Deseas ejecutar la limpieza de temporales y caché?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                res = limpiar_sistema()
                info_post = obtener_espacio_disco()
                QMessageBox.information(
                    self,
                    "Limpieza Completada",
                    f"✨ ¡Limpieza ejecutada con éxito!\n\n{res}\n\n📊 Estado actualizado:\n{info_post}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error al limpiar: {e}")

    def toggle_media(self):
        try:
            subprocess.run(["playerctl", "play-pause"], capture_output=True)
        except Exception:
            pass


class StussyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("🤖 Iniciando Stussy...", self)
        self.label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; "
            "background: rgba(0, 0, 0, 0.85); padding: 8px 15px; border-radius: 14px;"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.resize(300, 45)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_widget_info)
        self.timer.start(3000)

        self.update_widget_info()
        self.dashboard = None
        self.alert_sent = False

    def get_pending_tasks_count(self):
        try:
            if os.path.exists(DB_PATH):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM tasks WHERE status='pendiente'")
                count = c.fetchone()[0]
                conn.close()
                return count
        except Exception:
            pass
        return 0

    def get_hardware_stats(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent

            if (cpu > 85.0 or ram > 85.0) and not self.alert_sent:
                self.send_desktop_notification(
                    "⚠️ Alerta de Stussy", f"¡Alto consumo! CPU: {cpu}% | RAM: {ram}%"
                )
                self.alert_sent = True
            elif cpu < 75.0 and ram < 75.0:
                self.alert_sent = False

            temp_str = ""
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        temp_str = f" | 🌡️ {entries[0].current}°C"
                        break

            tasks_count = self.get_pending_tasks_count()
            task_str = f" | 📝 {tasks_count}" if tasks_count > 0 else ""

            avatar = "🔥" if cpu > 70 else ("🤖" if cpu < 30 else "⚡")

            return f"{avatar} C:{cpu}% R:{ram}%{temp_str}{task_str}"
        except Exception:
            return f"🤖 CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"

    def send_desktop_notification(self, title, message):
        try:
            subprocess.run(
                ["notify-send", title, message, "-i", "dialog-warning"],
                capture_output=True,
            )
        except Exception:
            pass

    def get_media_info(self):
        try:
            status = subprocess.run(
                ["playerctl", "status"], capture_output=True, text=True, timeout=0.5
            )
            if status.returncode == 0 and "Playing" in status.stdout:
                artist = subprocess.run(
                    ["playerctl", "artist"], capture_output=True, text=True, timeout=0.5
                ).stdout.strip()
                title = subprocess.run(
                    ["playerctl", "title"], capture_output=True, text=True, timeout=0.5
                ).stdout.strip()
                if title:
                    return f"🎶 {artist} - {title}" if artist else f"🎶 {title}"
        except Exception:
            pass
        return None

    def update_widget_info(self):
        media_text = self.get_media_info()
        if media_text:
            self.label.setText(media_text)
        else:
            self.label.setText(self.get_hardware_stats())

    def showEvent(self, event):
        super().showEvent(event)
        screen = QApplication.primaryScreen().geometry()
        widget_width = self.width()
        widget_height = self.height()

        x = (screen.width() - widget_width) // 2
        y = 35
        self.setGeometry(x, y, widget_width, widget_height)

    def mousePressEvent(self, event):
        if self.dashboard is None or not self.dashboard.isVisible():
            self.dashboard = DashboardPanel()

            screen = QApplication.primaryScreen().geometry()
            panel_x = (screen.width() - self.dashboard.width()) // 2
            panel_y = 85
            self.dashboard.setGeometry(
                panel_x, panel_y, self.dashboard.width(), self.dashboard.height()
            )
            self.dashboard.show()
        else:
            self.dashboard.close()
            self.dashboard = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = StussyWidget()
    widget.show()
    sys.exit(app.exec())
