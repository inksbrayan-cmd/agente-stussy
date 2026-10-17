import os
import shutil
import sqlite3
import webbrowser
from datetime import datetime
from googleapiclient.http import MediaFileUpload
from modules.gestor_adjuntos import autenticar_google

JERARQUIA_ESTUDIOS_GLOBAL = {
    "circuitos": "TEINCO_Actual_Semestre_3/01_Circuitos_y_Electricidad",
    "programacion": "TEINCO_Actual_Semestre_3/02_Programacion_y_Sistemas",
    "c++": "TEINCO_Actual_Semestre_3/02_Programacion_y_Sistemas",
    "python": "TEINCO_Actual_Semestre_3/02_Programacion_y_Sistemas",
    "cad": "TEINCO_Actual_Semestre_3/03_Mecanica_y_CAD",
    "onshape": "TEINCO_Actual_Semestre_3/03_Mecanica_y_CAD",
    "mecanica": "TEINCO_Actual_Semestre_3/03_Mecanica_y_CAD",
    "laboratorio": "TEINCO_Actual_Semestre_3/04_Laboratorios_e_Informes",
    "informe": "TEINCO_Actual_Semestre_3/04_Laboratorios_e_Informes",
    "robot": "TEINCO_Actual_Semestre_3/05_Proyectos_y_Robotica",
    "terreneitor": "TEINCO_Actual_Semestre_3/05_Proyectos_y_Robotica",
    "arduino": "TEINCO_Actual_Semestre_3/05_Proyectos_y_Robotica",
    "triangulo": "Universidades_Anteriores_Y_Formacion/Instituto_Triangulo",
    "mantenimiento": "Universidades_Anteriores_Y_Formacion/Instituto_Triangulo",
    "certificado": "Certificados_Y_Credenciales",
    "diploma": "Certificados_Y_Credenciales",
    "curso": "Universidades_Anteriores_Y_Formacion/Cursos_Y_Seminarios",
}


def inicializar_base_datos_global():
    conn = sqlite3.connect("estudio_index.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos_global (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT,
            institucion_categoria TEXT,
            origen TEXT,
            ruta_local TEXT,
            fecha_registro TEXT
        )
    """)
    conn.commit()
    conn.close()


def clasificar_documento(nombre_archivo):
    nombre_lower = nombre_archivo.lower()
    for keyword, ruta_relativa in JERARQUIA_ESTUDIOS_GLOBAL.items():
        if keyword in nombre_lower:
            return ruta_relativa
    return "Historico_General_Academico"


def obtener_o_crear_carpeta_drive(drive_service, nombre_carpeta, parent_id=None):
    query = f"name = '{nombre_carpeta}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])
    if items:
        return items[0]["id"]
    else:
        file_metadata = {
            "name": nombre_carpeta,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]
        folder = drive_service.files().create(body=file_metadata, fields="id").execute()
        return folder.get("id")


def subir_subir_a_drive_estructurado(ruta_archivo, subruta_categoria, cuenta="teinco"):
    print(f"\n☁️ Sincronizando con Google Drive ({cuenta.upper()})...")
    _, drive_service = autenticar_google(
        cuenta_personalizada=cuenta if cuenta == "teinco" else None
    )
    if not drive_service:
        print("⚠️ No se pudo conectar a Google Drive.")
        return False
    try:
        folder_id = obtener_o_crear_carpeta_drive(
            drive_service, "HISTORIAL_ACADEMICO_STUSSY"
        )
        partes = subruta_categoria.split("/")
        for parte in partes:
            folder_id = obtener_o_crear_carpeta_drive(
                drive_service, parte, parent_id=folder_id
            )
        nombre_archivo = os.path.basename(ruta_archivo)
        file_metadata = {"name": nombre_archivo, "parents": [folder_id]}
        media = MediaFileUpload(ruta_archivo, resumable=True)
        drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        print(
            f"  ✔ Respaldo en Google Drive exitoso en: HISTORIAL_ACADEMICO_STUSSY/{subruta_categoria}"
        )
        return True
    except Exception as e:
        print(f"⚠️ Error al subir a Drive: {e}")
        return False


def auditar_y_organizar_local():
    inicializar_base_datos_global()
    directorio_base = os.path.expanduser("~/Documentos/HISTORIAL_ACADEMICO")
    os.makedirs(directorio_base, exist_ok=True)
    for subruta in set(JERARQUIA_ESTUDIOS_GLOBAL.values()):
        os.makedirs(os.path.join(directorio_base, subruta), exist_ok=True)

    print("\n" + "=" * 65)
    print("🏛️ STUSSY - GESTIÓN Y AUDITORÍA DE HISTORIAL ACADÉMICO GLOBAL")
    print("=" * 65)
    carpeta_descargas = os.path.expanduser("~/Descargas")
    if not os.path.exists(carpeta_descargas):
        print("⚠️ No se encontró la carpeta Descargas.")
        return

    conn = sqlite3.connect("estudio_index.db")
    cursor = conn.cursor()
    encontrados = 0

    for archivo in os.listdir(carpeta_descargas):
        ruta_origen = os.path.join(carpeta_descargas, archivo)
        if os.path.isfile(ruta_origen):
            if archivo.lower().endswith(
                (".pdf", ".docx", ".xlsx", ".txt", ".py", ".ino", ".zip")
            ):
                categoria_destino = clasificar_documento(archivo)
                carpeta_destino = os.path.join(directorio_base, categoria_destino)
                os.makedirs(carpeta_destino, exist_ok=True)
                ruta_destino = os.path.join(carpeta_destino, archivo)

                print(f"  📄 Archivo detectado: {archivo}")
                print(f"     🎯 Categoría asignada: {categoria_destino}")

                confirmacion = (
                    input(
                        "     ¿Mover, indexar y unificar este documento en tu historial? (S/N): "
                    )
                    .strip()
                    .lower()
                )
                if confirmacion == "s":
                    shutil.move(ruta_origen, ruta_destino)
                    cursor.execute(
                        """
                        INSERT INTO documentos_global (nombre_archivo, institucion_categoria, origen, ruta_local, fecha_registro)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            archivo,
                            categoria_destino,
                            "Local/Descargas",
                            ruta_destino,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                    conn.commit()
                    print(f"     ✔ Documento integrado localmente.")

                    respaldo = (
                        input(
                            "     ☁️ ¿Deseas subir una copia de respaldo a Google Drive TEINCO? (S/N): "
                        )
                        .strip()
                        .lower()
                    )
                    if respaldo == "s":
                        subir_subir_a_drive_estructurado(
                            ruta_destino, categoria_destino, cuenta="teinco"
                        )

                    print("")
                    encontrados += 1
                else:
                    print(f"     ⏭️ Omitido por el usuario.\n")

    conn.close()
    print("=" * 65)
    print(
        f"✨ Auditoría finalizada. {encontrados} documentos añadidos a tu registro absoluto."
    )
    print("=" * 65)


def consultar_registro_global():
    if not os.path.exists("estudio_index.db"):
        print("\n⚠️ Aún no hay registros en la base de datos.")
        return
    conn = sqlite3.connect("estudio_index.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre_archivo, institucion_categoria, origen, fecha_registro FROM documentos_global"
    )
    registros = cursor.fetchall()
    conn.close()

    print("\n" + "=" * 75)
    print("📊 INVENTARIO ABSOLUTO - HISTORIAL ACADÉMICO GLOBAL")
    print("=" * 75)
    if not registros:
        print("✨ El registro está vacío.")
    else:
        for reg in registros:
            print(f"  ID: {reg[0]} | 📂 {reg[2]}")
            print(f"     📄 Archivo: {reg[1]}")
            print(f"     📍 Origen: {reg[3]} | 📅 Fecha: {reg[4]}\n")
    print("=" * 75)


def buscar_documentos_global():
    if not os.path.exists("estudio_index.db"):
        print("\n⚠️ Aún no hay registros en la base de datos.")
        return
    query = (
        input(
            "\n🔍 Ingresa la palabra clave a buscar (ej. circuitos, python, informe): "
        )
        .strip()
        .lower()
    )
    if not query:
        print("⚠️ La búsqueda no puede estar vacía.")
        return
    conn = sqlite3.connect("estudio_index.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nombre_archivo, institucion_categoria, origen, ruta_local, fecha_registro
        FROM documentos_global
        WHERE LOWER(nombre_archivo) LIKE ? OR LOWER(institucion_categoria) LIKE ?
    """,
        (f"%{query}%", f"%{query}%"),
    )
    resultados = cursor.fetchall()
    conn.close()

    print("\n" + "=" * 75)
    print(f"🔎 RESULTADOS DE BÚSQUEDA PARA: '{query.upper()}'")
    print("=" * 75)
    if not resultados:
        print("✨ No se encontraron documentos que coincidan con la búsqueda.")
    else:
        for reg in resultados:
            print(f"  ID: {reg[0]} | 📂 {reg[2]}")
            print(f"     📄 Archivo: {reg[1]}")
            print(f"     📍 Ruta: {reg[4]}")
            print(f"     📅 Fecha: {reg[5]}\n")
    print("=" * 75)


def generar_reporte_html():
    if not os.path.exists("estudio_index.db"):
        print("\n⚠️ Aún no hay registros en la base de datos para generar un reporte.")
        return
    conn = sqlite3.connect("estudio_index.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre_archivo, institucion_categoria, origen, ruta_local, fecha_registro FROM documentos_global"
    )
    registros = cursor.fetchall()
    conn.close()

    if not registros:
        print("\n✨ La base de datos está vacía, no hay nada que exportar.")
        return

    nombre_reporte = (
        f"reporte_academico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    )
    filas_html = ""
    for reg in registros:
        filas_html += f"""
        <tr>
            <td>{reg[0]}</td>
            <td><strong>{reg[1]}</strong></td>
            <td><span class="badge">{reg[2]}</span></td>
            <td>{reg[3]}</td>
            <td><code>{reg[4]}</code></td>
            <td>{reg[5]}</td>
        </tr>
        """

    contenido_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>STUSSY - Reporte Académico Global</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; }}
            .container {{ max-width: 1100px; margin: 0 auto; background-color: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h1 {{ color: #38bdf8; text-align: center; border-bottom: 2px solid #334155; padding-bottom: 15px; }}
            p.sub {{ text-align: center; color: #94a3b8; font-size: 0.9em; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #334155; }}
            th {{ background-color: #0f172a; color: #38bdf8; }}
            tr:hover {{ background-color: #334155; }}
            .badge {{ background-color: #0284c7; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.85em; }}
            code {{ color: #a5f3fc; font-size: 0.85em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ STUSSY - Reporte de Control Académico Global</h1>
            <p class="sub">Fecha de Generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Usuario: Brayan Martínez</p>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Documento</th>
                        <th>Categoría / Jerarquía</th>
                        <th>Origen</th>
                        <th>Ruta Local</th>
                        <th>Fecha Registro</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    with open(nombre_reporte, "w", encoding="utf-8") as f:
        f.write(contenido_html)

    print("\n" + "=" * 65)
    print(f"📄 Reporte generado con éxito: {nombre_reporte}")
    abrir = (
        input("¿Deseas abrir el reporte en tu navegador web? (S/N): ").strip().lower()
    )
    if abrir == "s":
        webbrowser.open("file://" + os.path.realpath(nombre_reporte))
    print("=" * 65)


def mostrar_estadisticas_globales():
    """Genera y despliega estadísticas analíticas del inventario académico."""
    if not os.path.exists("estudio_index.db"):
        print(
            "\n⚠️ Aún no hay registros en la base de datos para calcular estadísticas."
        )
        return

    conn = sqlite3.connect("estudio_index.db")
    cursor = conn.cursor()

    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM documentos_global")
    total_docs = cursor.fetchone()[0]

    if total_docs == 0:
        print("\n✨ La base de datos está vacía. Indexa archivos para ver métricas.")
        conn.close()
        return

    # Conteo por categoría
    cursor.execute(
        "SELECT institucion_categoria, COUNT(*) FROM documentos_global GROUP BY institucion_categoria"
    )
    categorias_counts = cursor.fetchall()

    # Fechas límite
    cursor.execute(
        "SELECT MIN(fecha_registro), MAX(fecha_registro) FROM documentos_global"
    )
    fecha_min, fecha_max = cursor.fetchone()

    # Calcular espacio total de los archivos registrados
    cursor.execute("SELECT ruta_local FROM documentos_global")
    rutas = cursor.fetchall()
    espacio_total_bytes = 0
    archivos_existentes = 0

    for (ruta,) in rutas:
        if os.path.exists(ruta):
            espacio_total_bytes += os.path.getsize(ruta)
            archivos_existentes += 1

    espacio_mb = espacio_total_bytes / (1024 * 1024)
    conn.close()

    print("\n" + "=" * 65)
    print("📈 STUSSY - ANALÍTICA Y ESTADÍSTICAS DEL HISTORIAL ACADÉMICO")
    print("=" * 65)
    print(f"  📄 Total de documentos indexados : {total_docs}")
    print(f"  💾 Archivos verificados en disco  : {archivos_existentes} / {total_docs}")
    print(f"  📦 Almacenamiento total utilizado: {espacio_mb:.2f} MB")
    print(f"  📅 Primer registro               : {fecha_min}")
    print(f"  🕒 Último registro               : {fecha_max}")
    print("-" * 65)
    print("  📂 DISTRIBUCIÓN POR CATEGORÍA:")
    for cat, count in categorias_counts:
        porcentaje = (count / total_docs) * 100
        barras = "█" * int(porcentaje // 5)
        print(f"     ▪ {cat}")
        print(f"       [{barras:<20}] {count} doc(s) ({porcentaje:.1f}%)")
    print("=" * 65)


def menu_estudio_global():
    while True:
        print("\n" + "=" * 55)
        print("🏛️ STUSSY - CONTROL TOTAL DE ESTUDIO Y HISTORIAL")
        print("=" * 55)
        print("1. 📂 Auditar y unificar archivos locales (Jerarquía Global)")
        print("2. 📊 Ver inventario absoluto de documentos (Base de Datos)")
        print("3. 🔍 Buscar documentos por palabra clave")
        print("4. 📄 Generar reporte visual HTML de historial")
        print("5. 📈 Ver estadísticas y analítica del agente")
        print("6. 🔙 Volver al menú principal")
        print("=" * 55)

        opcion = input("Selecciona una opción (1-6): ").strip()
        if opcion == "1":
            auditar_y_organizar_local()
        elif opcion == "2":
            consultar_registro_global()
        elif opcion == "3":
            buscar_documentos_global()
        elif opcion == "4":
            generar_reporte_html()
        elif opcion == "5":
            mostrar_estadisticas_globales()
        elif opcion == "6":
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    menu_estudio_global()
