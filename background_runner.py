import time
from modules.organizador import organizar_descargas

if __name__ == "__main__":
    print("Iniciando STUSSY en segundo plano...")
    while True:
        try:
            organizar_descargas()
        except Exception as e:
            print(f"Error en segundo plano: {e}")
        # Espera 1 hora (3600 segundos) antes de volver a organizar
        time.sleep(3600)
