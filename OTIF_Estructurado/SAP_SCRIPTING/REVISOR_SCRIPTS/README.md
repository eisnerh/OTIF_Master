# 🔧 REVISOR DE SCRIPTS SAP

Este subproyecto está diseñado para revisar y corregir individualmente cada script VBScript de SAP.

## 📋 Problema Identificado

Los scripts están usando dos enfoques diferentes:
1. **❌ INCORRECTO**: Navegar por favoritos (rep_plr, y_dev_45, y_dev_74, etc.)
2. **✅ CORRECTO**: Ir directamente a transacción (zred)

## 🎯 Objetivo

Convertir todos los scripts para que usen el enfoque directo como `zred`, eliminando la navegación por favoritos.

## 📁 Estructura

```
REVISOR_SCRIPTS/
├── README.md
├── scripts_originales/          # Scripts originales (backup)
├── scripts_corregidos/          # Scripts corregidos
├── analisis_por_script/         # Análisis individual de cada script
└── herramientas/                # Utilidades para revisión
```

## 🔍 Scripts a Revisar

- [ ] rep_plr (usar favoritos → ir directo)
- [ ] y_dev_45 (usar favoritos → ir directo) 
- [ ] y_dev_74 (usar favoritos → ir directo)
- [ ] y_dev_82 (usar favoritos → ir directo)
- [ ] z_devo_alv (usar favoritos → ir directo)
- [ ] zhbo (usar favoritos → ir directo)
- [x] zred (ya correcto)
- [x] zsd_incidencias (ya correcto)
