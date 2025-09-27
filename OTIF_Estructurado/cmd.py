import os
import time
import ftplib
import shutil

# Paso 1: Cambiar al directorio de trabajo
os.chdir(r'C:\SAP\CARGARS')
time.sleep(2)

# Paso 2: Conectarse al servidor FTP
ftp_server = 'fifjumpftp-prd.cloud.fifco.com'
ftp_user = 'usaim'
ftp_password = 'usaim'

ftp = ftplib.FTP(ftp_server)
ftp.login(user=ftp_user, passwd=ftp_password)
ftp.set_pasv(True)
ftp.sendcmd("TYPE A")  # Modo ASCII
ftp.cwd('RoadShow')
ftp.cwd('SncaSubeRS')
time.sleep(2)

# Paso 3: Subir archivos .dnl
for filename in os.listdir():
    if filename.endswith('.dnl'):
        with open(filename, 'rb') as file:
            ftp.storbinary(f'STOR {filename}', file)
        time.sleep(2)

ftp.quit()

# Paso 4: Mover archivos a carpeta 'Movidos'
destination_dir = r'C:\SAP\CARGARS\Movidos'
os.makedirs(destination_dir, exist_ok=True)

for filename in os.listdir():
    if filename.endswith('.dnl'):
        shutil.move(filename, os.path.join(destination_dir, filename))
        time.sleep(2)

print("Proceso terminado.")
