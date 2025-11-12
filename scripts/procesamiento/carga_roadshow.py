import os
import ftplib
import shutil
from datetime import datetime
###
# --- Configuración ---
# Directorios
DIRECTORIO_TRABAJO = r"C:\SAP\CARGARS"
DIRECTORIO_MOVIDOS = os.path.join(DIRECTORIO_TRABAJO, "Movidos")
ARCHIVO_ULTIMO_CENTRO = os.path.join(DIRECTORIO_TRABAJO, "ultimo_centro.txt")

# Configuración FTP (puedes sobrescribir con variables de entorno)
FTP_HOST = "fifjumpftp-prd.cloud.fifco.com"
FTP_USER_DEFAULT = "usaim"   # ⚠️ Evita credenciales en claro en producción
FTP_PASS_DEFAULT = "usaim"   # ⚠️ Usa variables de entorno: FTP_USER / FTP_PASS

# Base y centros (subcarpetas dentro de RoadShow)
FTP_BASE_REMOTO = "RoadShow"
CENTROS = [
    "SncaSubeRS",
    "VYDSubeRS",
    "SubeRS",
    "GuapSubeRS",
    "LibeSubeRS",
    "LimoSubeRS",
    "CneiSubeRS",
    "NicoSubeRS",
    "PuntaSubeRS",
    "SnisSubeRS",
]

# --- Utilidades ---
def mostrar_estado(mensaje):
    """Muestra un mensaje de estado en la consola con marca de tiempo."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")

def leer_ultima_seleccion():
    """Lee el último centro guardado, si existe y es válido."""
    try:
        if os.path.exists(ARCHIVO_ULTIMO_CENTRO):
            with open(ARCHIVO_ULTIMO_CENTRO, "r", encoding="utf-8") as f:
                valor = f.read().strip()
                if valor in CENTROS:
                    return valor
    except Exception:
        pass
    return None

def guardar_ultima_seleccion(centro):
    """Guarda el centro elegido para futuras ejecuciones."""
    try:
        with open(ARCHIVO_ULTIMO_CENTRO, "w", encoding="utf-8") as f:
            f.write(centro)
    except Exception as e:
        mostrar_estado(f"[WARN] No se pudo guardar la última selección. Detalles: {e}")

def seleccionar_centro(default_centro=None):
    """Muestra un menú para elegir el centro de destino en el FTP (con recuerdo del último)."""
    # Ajustar default si no es válido
    if default_centro not in CENTROS:
        default_centro = CENTROS[0]

    print("\nSeleccione el centro remoto (carpeta dentro de RoadShow) para guardar los archivos:\n")
    for i, c in enumerate(CENTROS, 1):
        print(f"  {i}. {c}")
    print(f"\nPredeterminado: {default_centro}")

    while True:
        opcion = input(f"Ingrese el número del centro (Enter = {default_centro}): ").strip()
        if opcion == "":
            return default_centro
        if opcion.isdigit():
            idx = int(opcion)
            if 1 <= idx <= len(CENTROS):
                return CENTROS[idx - 1]
        print("Opción inválida. Intente de nuevo.")

def obtener_credenciales():
    """Obtiene credenciales desde variables de entorno o valores por defecto."""
    user = os.getenv("FTP_USER", FTP_USER_DEFAULT)
    password = os.getenv("FTP_PASS", FTP_PASS_DEFAULT)
    return user, password

def ensure_remote_path(ftp, path):
    """
    Asegura que el path remoto exista navegando y creándolo si hace falta.
    path: "RoadShow/SncaSubeRS"
    """
    partes = path.replace("\\", "/").split("/")
    for parte in partes:
        if not parte:
            continue
        try:
            ftp.cwd(parte)
        except ftplib.error_perm:
            # Intentar crear y luego entrar
            try:
                ftp.mkd(parte)
                ftp.cwd(parte)
            except ftplib.error_perm as e:
                raise RuntimeError(f"No se pudo acceder/crear el directorio remoto '{parte}': {e}")

def listar_archivos_dnl(directorio):
    """Lista archivos .DNL (insensible a mayúsculas) en el directorio indicado."""
    return [
        f for f in os.listdir(directorio)
        if os.path.isfile(os.path.join(directorio, f)) and f.lower().endswith(".dnl")
    ]

# --- Flujo principal ---
def main():
    mostrar_estado("Iniciando el proceso de carga de RoadShow a SAP...")

    # 1) Preparación de directorios
    mostrar_estado(f"Cambiando directorio de trabajo a: {DIRECTORIO_TRABAJO}")
    try:
        os.chdir(DIRECTORIO_TRABAJO)
        if not os.path.exists(DIRECTORIO_MOVIDOS):
            os.makedirs(DIRECTORIO_MOVIDOS, exist_ok=True)
            mostrar_estado(f"Carpeta de Movidos creada: {DIRECTORIO_MOVIDOS}")
    except Exception as e:
        mostrar_estado(f"🚨 ERROR: No se pudo preparar el entorno. Detalles: {e}")
        return

    # 2) Selección de centro (con recuerdo de última selección) si hay archivos a subir
    archivos_a_subir = listar_archivos_dnl(DIRECTORIO_TRABAJO)

    if not archivos_a_subir:
        mostrar_estado("[Aviso]: No se encontraron archivos '.DNL' para subir. Se limpiará moviéndolos si aparecieron nuevos.")
    else:
        ultimo_centro = leer_ultima_seleccion()
        centro_elegido = seleccionar_centro(default_centro=ultimo_centro)
        # Guardar inmediatamente la elección para próximas ejecuciones
        guardar_ultima_seleccion(centro_elegido)

        ruta_remota = f"{FTP_BASE_REMOTO}/{centro_elegido}"
        mostrar_estado(f"Conectando a {FTP_HOST} para subir {len(archivos_a_subir)} archivo(s) a '{ruta_remota}'...")
        user, password = obtener_credenciales()

        try:
            with ftplib.FTP(FTP_HOST, timeout=30) as ftp:
                ftp.login(user, password)
                mostrar_estado("[OK] Conexión y login exitosos.")

                # Modo ASCII (como en tu script original). Para binario: ftp.voidcmd('TYPE I')
                ftp.voidcmd('TYPE A')
                # Asegurar y cambiar a directorio remoto
                ensure_remote_path(ftp, ruta_remota)
                mostrar_estado(f"Directorio remoto listo: {ruta_remota}")

                # Subida de archivos
                archivos_subidos_count = 0
                for nombre_archivo in archivos_a_subir:
                    mostrar_estado(f" Subiendo: {nombre_archivo}")
                    with open(nombre_archivo, 'rb') as fp:
                        ftp.storbinary(f'STOR {nombre_archivo}', fp)
                        archivos_subidos_count += 1

                mostrar_estado(f"[OK] Subida FTP completa. Total de archivos subidos: {archivos_subidos_count}")

        except ftplib.all_errors as e:
            mostrar_estado(f"ERROR FATAL: Falló la transferencia FTP. Detalle: {e}")
            return
        except RuntimeError as e:
            mostrar_estado(f"ERROR: {e}")
            return

    # 3) Mover archivos procesados
    mostrar_estado("Moviendo archivos '.DNL' procesados para archivarlos...")
    archivos_movidos = 0
    try:
        # Re-listar para evitar mover si la subida no ocurrió
        archivos_para_mover = listar_archivos_dnl(DIRECTORIO_TRABAJO)

        for archivo in archivos_para_mover:
            origen = os.path.join(DIRECTORIO_TRABAJO, archivo)
            destino = os.path.join(DIRECTORIO_MOVIDOS, archivo)
            shutil.move(origen, destino)
            mostrar_estado(f"    - Movido: {archivo}")
            archivos_movidos += 1

        if archivos_movidos > 0:
            mostrar_estado(f" Éxito: Se movieron {archivos_movidos} archivo(s) a {DIRECTORIO_MOVIDOS}.")
        else:
            mostrar_estado(" Aviso: No se encontraron archivos '.DNL' para mover.")

    except Exception as e:
        mostrar_estado(f"ERROR: Falló el movimiento de archivos. Detalles: {e}")
        return

    # 4) Finalización
    mostrar_estado("[OK] Terminó el proceso RoadShow. Todos los pasos completados con éxito.")

if __name__ == "__main__":
    main()