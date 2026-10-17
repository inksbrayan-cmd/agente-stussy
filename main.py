from datetime import datetime
from modules.organizador import organizar_descargas
from modules.creador_proyectos import crear_proyecto
from modules.monitor import mostrar_estado_sistema
from modules.tareas import menu_tareas
from modules.drive_organizer import menu_drive
from modules.correo_resumen import menu_correos


def saludar():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "¡Buenos días, Brayan!"
    elif 12 <= hora < 18:
        return "¡Buenas tardes, Brayan!"
    else:
        return "¡Buenas noches, Brayan!"


def menu():
    while True:
        print("\n" + "=" * 55)
        print("🤖 STUSSY - Agente Personal & Asistente de Desarrollo")
        print("=" * 55)
        print(f"{saludar()}\n")
        print("1. 📂 Organizar carpeta Descargas")
        print("2. 🚀 Crear nuevo proyecto con estructura estándar")
        print("3. 📊 Ver estado del sistema")
        print("4. 📌 Gestionar tareas y pendientes")
        print("5. ☁️ Gestionar y organizar Google Drive")
        print("6. 📬 Resumen inteligente de correos")
        print("7. ❌ Salir")
        print("=" * 55)

        opcion = input("Selecciona una opción (1-7): ").strip()

        if opcion == "1":
            print("\n📂 Ejecutando organizador de archivos...")
            organizar_descargas()
        elif opcion == "2":
            print("\n🚀 Ejecutando Creador de Proyectos...")
            crear_proyecto()
        elif opcion == "3":
            print("\n📊 Ejecutando Monitor del Sistema...")
            mostrar_estado_sistema()
        elif opcion == "4":
            menu_tareas()
        elif opcion == "5":
            menu_drive()
        elif opcion == "6":
            menu_correos()
        elif opcion == "7":
            print("\n👋 ¡Hasta luego, Brayan! STUSSY se despide.")
            break
        else:
            print("\n⚠️ Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()
