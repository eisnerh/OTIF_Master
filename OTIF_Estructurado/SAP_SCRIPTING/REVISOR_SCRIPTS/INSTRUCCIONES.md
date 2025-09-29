# 📋 INSTRUCCIONES - REVISOR DE SCRIPTS SAP

## 🎯 Propósito
Este subproyecto está diseñado para revisar y corregir individualmente cada script VBScript de SAP, eliminando la navegación por favoritos y convirtiéndolos al enfoque directo de transacciones.

## 📁 Estructura del Proyecto

```
REVISOR_SCRIPTS/
├── README.md                           # Documentación principal
├── INSTRUCCIONES.md                    # Este archivo
├── RESUMEN_CORRECCIONES.md             # Estado general de correcciones
├── scripts_originales/                 # Backup de scripts originales
├── scripts_corregidos/                 # Scripts corregidos
├── analisis_por_script/                # Análisis individual de cada script
└── herramientas/                       # Utilidades de corrección
    └── corrector_automatico.py         # Herramienta de corrección automática
```

## 🔧 Cómo Usar

### 1. **Revisión Manual**
- Revisar cada análisis en `analisis_por_script/`
- Verificar scripts corregidos en `scripts_corregidos/`
- Comparar con scripts originales

### 2. **Corrección Automática**
```bash
cd herramientas
python corrector_automatico.py
```

### 3. **Aplicar Correcciones**
1. Revisar scripts corregidos
2. Probar cada script individualmente
3. Reemplazar scripts originales si funcionan correctamente

## 📊 Estado Actual

### ✅ Scripts Corregidos:
- `rep_plr_CORREGIDO` - Enfoque directo + fechas dinámicas
- `y_dev_45_CORREGIDO` - Enfoque directo + rutas dinámicas

### 🔄 Scripts Pendientes:
- `y_dev_74` - Requiere corrección de favoritos + fecha
- `y_dev_82` - Requiere corrección de favoritos + fecha  
- `z_devo_alv` - Requiere corrección de favoritos + ruta
- `zhbo` - Requiere corrección de favoritos + fecha

### ✅ Scripts Correctos (No requieren cambios):
- `zred` - Ya usa enfoque directo
- `zsd_incidencias` - Ya usa enfoque directo

## 🎯 Patrón de Corrección

### ❌ ANTES (Incorrecto):
```vbscript
' Navegar por favoritos
session.findById("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode "F00120"
session.findById("wnd[0]/tbar[1]/btn[17]").press
```

### ✅ DESPUÉS (Correcto):
```vbscript
' Ir directamente a transacción
session.findById("wnd[0]/tbar[0]/okcd").text = "NOMBRE_TRANSACCION"
session.findById("wnd[0]").sendVKey 0
session.findById("wnd[0]/tbar[1]/btn[17]").press
```

## 🚀 Próximos Pasos

1. **Completar correcciones pendientes**
2. **Probar todos los scripts corregidos**
3. **Reemplazar scripts originales**
4. **Actualizar documentación**

## 📞 Soporte
Para dudas o problemas, revisar los análisis individuales en `analisis_por_script/`.
