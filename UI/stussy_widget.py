import os
import sys
import psutil
import subprocess
import sqlite3

# Forzar backend de X11
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
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

DB_PATH = os.path.expanduser("~/agente-stussy/tasks.db")


class DashboardPanel(QWidget):
    """Panel interactivo con tareas SQLite y métricas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(340, 310)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 18, 22, 0.95);
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
                padding: 5px 10px;
                font-weight: bold;
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

        title_label = QLabel("🚀 STUSSY - CENTRO DE CONTROL & TAREAS")
        title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #00ffcc;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(title_label)

        # Lista de tareas desde SQLite
        self.task_list = QListWidget()
        inner_layout.addWidget(self.task_list)

        # Input y botón para nueva tarea
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nueva tarea...")
        btn_add = QPushButton("➕")
        btn_add.clicked.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(btn_add)
        inner_layout.addLayout(input_layout)

        # Botones de control
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
        """Carga tareas pendientes desde SQLite"""
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
        """Guarda una nueva tarea en SQLite"""
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

        self.label = QLabel("🤖 Iniciando hardware...", self)
        self.label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; "
            "background: rgba(0, 0, 0, 0.85); padding: 8px 15px; border-radius: 14px;"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.resize(280, 45)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_widget_info)
        self.timer.start(3000)

        self.update_widget_info()
        self.dashboard = None
        self.alert_sent = False

    def get_pending_tasks_count(self):
        """Consulta número de tareas pendientes"""
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

            return f"🖥️ C:{cpu}% R:{ram}%{temp_str}{task_str}"
        except Exception:
            return f"🖥️ CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"

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
                    return f"🎵 {artist} - {title}" if artist else f"🎵 {title}"
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
