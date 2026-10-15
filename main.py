import os
import sys
from datetime import datetime


def saludar():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "¡Buenos días, Brayan!"
    elif 12 <= hora < 18:
        return "¡Buenas tardes, Brayan!"
    else:
        return "¡Buenas noches, Brayan!"


def menu():
    print("=" * 55)
    print("🤖  STUSSY - Agente Personal & Asistente de Desarrollo")
    print("=" * 55)
    print(f"{saludar()}\n")
    print("1. 📂 Organizar carpeta Descargas")
    print("2. 🚀 Crear nuevo proyecto con estructura estándar")
    print("3. 📊 Ver estado del sistema")
    print("4. ❌ Salir")
    print("=" * 55)


if __name__ == "__main__":
    menu()
