import psutil
import shutil
import platform


def obtener_uso_disco():
    total, usado, libre = shutil.disk_usage("/")
    total_gb = total / (1024**3)
    usado_gb = usado / (1024**3)
    libre_gb = libre / (1024**3)
    porcentaje = (usado / total) * 100
    return total_gb, usado_gb, libre_gb, porcentaje


def mostrar_estado_sistema():
    print("\n" + "=" * 50)
    print("📊  STUSSY - MONITOR DEL SISTEMA")
    print("=" * 50)

    # Información del Sistema
    print(f"🖥️  Sistema Operativo: {platform.system()} {platform.release()}")

    # Uso de CPU
    uso_cpu = psutil.cpu_percent(interval=1)
    print(f"⚡ Uso de CPU: {uso_cpu}%")

    # Uso de RAM
    ram = psutil.virtual_memory()
    ram_total_gb = ram.total / (1024**3)
    ram_usada_gb = ram.used / (1024**3)
    print(
        f"🧠 Memoria RAM: {ram_usada_gb:.2f} GB / {ram_total_gb:.2f} GB ({ram.percent}%)"
    )

    # Uso de Disco
    total_gb, usado_gb, libre_gb, pct_disco = obtener_uso_disco()
    print(
        f"💾 Almacenamiento: {usado_gb:.2f} GB / {total_gb:.2f} GB usados ({pct_disco:.1f}%)"
    )
    print(f"   Espacio libre: {libre_gb:.2f} GB")

    # Batería (si está disponible)
    bateria = psutil.sensors_battery()
    if bateria:
        conectado = "Cargando 🔌" if bateria.power_plugged else "En batería 🔋"
        print(f"🔋 Batería: {bateria.percent}% ({conectado})")

    print("=" * 50)


if __name__ == "__main__":
    mostrar_estado_sistema()
