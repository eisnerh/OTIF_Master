import os
import ftplib
import shutil
from datetime import datetime
import time

# --- Configuración ---
# Directorios
DIRECTORIO_TRABAJO = r"C:\SAP\CARGARS"
DIRECTORIO_MOVIDOS = os.path.join(DIRECTORIO_TRABAJO, "Movidos")

# Configuración FTP (extraída de subeRS.ftp)
FTP_HOST = "fifjumpftp-prd.cloud.fifco.com"
FTP_USER = "usaim"
FTP_PASS = "usaim" # ¡Advertencia: Dejar credenciales en texto plano no es seguro!
FTP_RUTA_REMOTA = "RoadShow/SnisSubeRS" # Combina los comandos 'cd RoadShow' y 'cd SnisSubeRS'

# --- Funciones ---

def mostrar_estado(mensaje):
    """Muestra un mensaje de estado en la consola con marca de tiempo."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")

def main():
    mostrar_estado("🚀 Iniciando el proceso de carga de RoadShow a SAP...")
    
    # 1. Preparación de directorios
    mostrar_estado(f"Cambiando directorio de trabajo a: {DIRECTORIO_TRABAJO}")
    try:
        os.chdir(DIRECTORIO_TRABAJO)
        if not os.path.exists(DIRECTORIO_MOVIDOS):
            os.makedirs(DIRECTORIO_MOVIDOS)
            mostrar_estado(f"Carpeta de Movidos creada: {DIRECTORIO_MOVIDOS}")
    except Exception as e:
        mostrar_estado(f"🚨 ERROR: No se pudo preparar el entorno. Detalles: {e}")
        return

    # 2. Transferencia de archivos vía FTP
    archivos_a_subir = [f for f in os.listdir(DIRECTORIO_TRABAJO) if f.endswith(".DNL") and os.path.isfile(f)]
    
    if not archivos_a_subir:
        mostrar_estado("ℹ️ Aviso: No se encontraron archivos '.dnl' para subir. Saltando paso FTP.")
    else:
        mostrar_estado(f"Conectando a {FTP_HOST} para subir {len(archivos_a_subir)} archivo(s)...")
        try:
            # 1. Conexión y Login
            with ftplib.FTP(FTP_HOST, timeout=30) as ftp:
                ftp.login(FTP_USER, FTP_PASS)
                mostrar_estado("✅ Conexión y login exitosos.")
                
                # 2. Configuración (ascii y cd)
                ftp.voidcmd('TYPE A') # Equivalente a 'ascii'
                ftp.cwd(FTP_RUTA_REMOTA) # Equivalente a 'cd RoadShow' y 'cd SnisSubeRS'
                mostrar_estado(f"Cambiado a directorio remoto: {FTP_RUTA_REMOTA}")
                
                # 3. Subida de archivos (mput *.dnl)
                archivos_subidos_count = 0
                for nombre_archivo in archivos_a_subir:
                    mostrar_estado(f"    - Subiendo: {nombre_archivo}")
                    with open(nombre_archivo, 'rb') as fp:
                        ftp.storbinary(f'STOR {nombre_archivo}', fp)
                        archivos_subidos_count += 1
                
                mostrar_estado(f"✅ Subida FTP completa. Total de archivos subidos: {archivos_subidos_count}")

        except ftplib.all_errors as e:
            mostrar_estado(f"❌ ERROR FATAL: Falló la transferencia FTP. Detalle del error: {e}")
            return
    
    # 3. Mover archivos procesados
    mostrar_estado("Moviendo archivos '.DNL' procesados para archivarlos...")
    archivos_movidos = 0
    try:
        # Volvemos a listar los archivos, ya que si la subida falló, no se deben mover
        archivos_para_mover = [f for f in os.listdir(DIRECTORIO_TRABAJO) if f.endswith(".DNL") and os.path.isfile(f)]

        for archivo in archivos_para_mover:
            origen = os.path.join(DIRECTORIO_TRABAJO, archivo)
            destino = os.path.join(DIRECTORIO_MOVIDOS, archivo)
            
            # Solo mover si fueron subidos, o si la subida fue saltada (lo que implica que deben moverse igual para limpiar)
            if archivo in archivos_a_subir or not archivos_a_subir:
                 shutil.move(origen, destino)
                 mostrar_estado(f"    - Movido: {archivo}")
                 archivos_movidos += 1
        
        if archivos_movidos > 0:
            mostrar_estado(f"✅ Éxito: Se movieron {archivos_movidos} archivo(s) a {DIRECTORIO_MOVIDOS}.")
        elif archivos_a_subir:
             # Este caso ocurre si se intentó subir pero no se encontró nada.
             mostrar_estado("ℹ️ Aviso: No se encontraron archivos '.DNL' para mover.")
            
    except Exception as e:
        mostrar_estado(f"❌ ERROR: Falló el movimiento de archivos. Detalles: {e}")
        return

    # 4. Finalización
    mostrar_estado("🎉 Termino el proceso RoadShow. Todos los pasos completados con éxito.")

if __name__ == "__main__":
    main()