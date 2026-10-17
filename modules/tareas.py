import sqlite3
import subprocess
from datetime import datetime
import os

# Ruta de la base de datos dentro del proyecto
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tareas.db")


def inicializar_db():
    """Crea la tabla de tareas si no existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT DEFAULT 'General',
            fecha_limite TEXT,
            prioridad TEXT DEFAULT 'Media',
            completada INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def notificar_zorin(titulo, mensaje):
    """Envía una notificación emergente nativa al escritorio de Zorin OS."""
    try:
        subprocess.run(
            ["notify-send", "-i", "dialog-information", titulo, mensaje], check=False
        )
    except Exception:
        pass


def agregar_tarea():
    """Permite registrar una nueva tarea."""
    inicializar_db()
    print("\n" + "=" * 50)
    print("📝 STUSSY - REGISTRAR NUEVA TAREA")
    print("=" * 50)

    titulo = input("📌 Título de la tarea: ").strip()
    if not titulo:
        print("⚠️ El título no puede estar vacío.")
        return

    print("\nSelecciona la categoría:")
    print("1. 🎓 Universidad (TEINCO)")
    print("2. 💼 Trabajo (CIJAD S.A.S.)")
    print("3. 👤 Personal")
    cat_opcion = input("Opción (1-3, por defecto 3): ").strip()

    categorias = {"1": "TEINCO", "2": "Trabajo", "3": "Personal"}
    categoria = categorias.get(cat_opcion, "Personal")

    fecha = input(
        "📅 Fecha límite (AAAA-MM-DD) [Opcional - Presiona Enter para omitir]: "
    ).strip()

    print("\nPrioridad:")
    print("1. Alta 🔴 | 2. Media 🟡 | 3. Baja 🟢")
    prio_opcion = input("Opción (1-3, por defecto 2): ").strip()
    prioridades = {"1": "Alta", "2": "Media", "3": "Baja"}
    prioridad = prioridades.get(prio_opcion, "Media")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tareas (titulo, categoria, fecha_limite, prioridad)
        VALUES (?, ?, ?, ?)
    """,
        (titulo, categoria, fecha if fecha else "Sin fecha", prioridad),
    )
    conn.commit()
    conn.close()

    print(f"\n✅ ¡Tarea '{titulo}' guardada exitosamente en categoría [{categoria}]!")
    notificar_zorin("STUSSY - Tarea Registrada", f"[{categoria}] {titulo}")


def listar_tareas():
    """Muestra todas las tareas pendientes."""
    inicializar_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, categoria, fecha_limite, prioridad
        FROM tareas
        WHERE completada = 0
        ORDER BY CASE prioridad WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 ELSE 3 END
    """)
    tareas = cursor.fetchall()
    conn.close()

    print("\n" + "=" * 50)
    print("📋 STUSSY - TAREAS PENDIENTES")
    print("=" * 50)

    if not tareas:
        print("🎉 ¡No tienes tareas pendientes! Todo al día.")
        print("=" * 50)
        return

    for t in tareas:
        t_id, titulo, cat, fecha, prio = t
        icon_prio = "🔴" if prio == "Alta" else ("🟡" if prio == "Media" else "🟢")
        print(f"[{t_id}] {icon_prio} ({cat}) {titulo} | 📅 Límite: {fecha}")

    print("=" * 50)


def completar_tarea():
    """Marca una tarea como realizada."""
    listar_tareas()
    t_id = input(
        "\nIngrese el número (ID) de la tarea a marcar como completada: "
    ).strip()
    if not t_id.isdigit():
        print("⚠️ ID no válido.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (int(t_id),))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados > 0:
        print(f"🎉 ¡Excelente trabajo! Tarea #{t_id} completada.")
        notificar_zorin(
            "STUSSY - Tarea Completada", f"¡Felicidades, completaste la tarea #{t_id}!"
        )
    else:
        print("⚠️ No se encontró ninguna tarea pendiente con ese ID.")


def menu_tareas():
    """Submenú interactivo para gestionar tareas."""
    while True:
        print("\n" + "=" * 40)
        print("📌 STUSSY - GESTOR DE TAREAS")
        print("=" * 40)
        print("1. ➕ Agregar nueva tarea")
        print("2. 📋 Ver tareas pendientes")
        print("3. ✅ Marcar tarea como completada")
        print("4. 🔙 Volver al menú principal")
        print("=" * 40)

        opcion = input("Selecciona una opción (1-4): ").strip()

        if opcion == "1":
            agregar_tarea()
        elif opcion == "2":
            listar_tareas()
        elif opcion == "3":
            completar_tarea()
        elif opcion == "4":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_tareas()
