import os
import sys
from datetime import datetime
from modules.organizador import organizar_descargas


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
        print("🤖  STUSSY - Agente Personal & Asistente de Desarrollo")
        print("=" * 55)
        print(f"{saludar()}\n")
        print("1. 📂 Organizar carpeta Descargas")
        print("2. 🚀 Crear nuevo proyecto con estructura estándar")
        print("3. 📊 Ver estado del sistema")
        print("4. ❌ Salir")
        print("=" * 55)

        opcion = input("Selecciona una opción (1-4): ").strip()

        if opcion == "1":
            print("\n🧹 Ejecutando organizador de archivos...")
            organizar_descargas()
        elif opcion == "2":
            print("\n🚀 Próximamente: Creador de proyectos...")
        elif opcion == "3":
            print("\n📊 Próximamente: Monitor de sistema...")
        elif opcion == "4":
            print("\n👋 ¡Hasta luego, Brayan! STUSSY se despide.")
            break
        else:
            print("\n⚠️ Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    menu()
