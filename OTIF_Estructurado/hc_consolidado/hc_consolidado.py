# consolidador_ultra_simple.py
import pandas as pd
from pathlib import Path

# Configuración
CARPETA_1 = Path(r"C:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Planeamientos de Rutas - Reportes de Disponibilidad de Personal\RURAL") 
CARPETA_2 = Path(r"C:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Planeamientos de Rutas - Reportes de Disponibilidad de Personal\MACROZONAS") 
SALIDA = "Consolidado.xlsx"

def consolidar_simple():
    print("🔍 Buscando archivos HC*.xlsm...")
    
    archivos = []
    for carpeta in [CARPETA_1, CARPETA_2]:
        if carpeta.exists():
            archivos.extend(carpeta.glob("HC*.xlsm"))
    
    print(f"📁 Encontrados: {len(archivos)} archivos")
    
    with pd.ExcelWriter(SALIDA, engine='openpyxl') as writer:
        for i, archivo in enumerate(archivos, 1):
            try:
                df = pd.read_excel(archivo, sheet_name='Registro')
                df['Origen'] = archivo.name
                
                nombre_hoja = f"Reg_{i}"
                df.to_excel(writer, sheet_name=nombre_hoja, index=False)
                
                print(f"✅ {archivo.name} -> {len(df)} filas")
                
            except Exception as e:
                print(f"❌ {archivo.name} - Error: {e}")
    
    print(f"\n🎉 Consolidado guardado como: {SALIDA}")

if __name__ == "__main__":
    consolidar_simple()