#!/usr/bin/env python3
"""
Script de demostración para mostrar cómo funcionan las fechas dinámicas
"""

from datetime import datetime, timedelta

def get_dynamic_date():
    """
    Obtiene la fecha dinámica según la lógica de negocio:
    - Si es lunes: ejecutar sábado y domingo (fecha del sábado)
    - Para otros días: un día atrás
    """
    today = datetime.now()
    weekday = today.weekday()  # 0=Lunes, 1=Martes, ..., 6=Domingo
    
    if weekday == 0:  # Lunes
        # Si es lunes, ejecutar sábado (2 días atrás)
        target_date = today - timedelta(days=2)
        print("📅 Es lunes - ejecutando reporte del sábado")
    else:
        # Para otros días, un día atrás
        target_date = today - timedelta(days=1)
        print(f"📅 Día {today.strftime('%A')} - ejecutando reporte de ayer")
    
    return target_date.strftime("%d.%m.%Y")

def demo_fechas_semana():
    """
    Demuestra cómo funcionarían las fechas para cada día de la semana
    """
    print("🗓️  DEMOSTRACIÓN DE FECHAS DINÁMICAS")
    print("=" * 60)
    
    # Simular cada día de la semana
    dias_semana = [
        "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
    ]
    
    # Fecha base (hoy)
    hoy = datetime.now()
    
    for i, dia in enumerate(dias_semana):
        # Simular que hoy es ese día
        fecha_simulada = hoy - timedelta(days=hoy.weekday() - i)
        
        print(f"\n📅 Si hoy fuera {dia} ({fecha_simulada.strftime('%d.%m.%Y')}):")
        
        if i == 0:  # Lunes
            fecha_reporte = fecha_simulada - timedelta(days=2)  # Sábado
            print(f"   🎯 Ejecutaría reporte del: {fecha_reporte.strftime('%A %d.%m.%Y')} (sábado)")
        else:
            fecha_reporte = fecha_simulada - timedelta(days=1)  # Día anterior
            print(f"   🎯 Ejecutaría reporte del: {fecha_reporte.strftime('%A %d.%m.%Y')} (ayer)")

def main():
    """
    Función principal
    """
    print("🚀 DEMOSTRACIÓN DE LÓGICA DE FECHAS DINÁMICAS")
    print("=" * 80)
    print(f"⏰ Fecha actual: {datetime.now().strftime('%A %d.%m.%Y %H:%M:%S')}")
    print("=" * 80)
    
    # Mostrar fecha dinámica actual
    print("\n📊 FECHA DINÁMICA ACTUAL:")
    fecha_dinamica = get_dynamic_date()
    print(f"   🎯 Fecha que se ejecutaría: {fecha_dinamica}")
    
    # Demostrar para toda la semana
    demo_fechas_semana()
    
    print("\n" + "=" * 80)
    print("💡 RESUMEN DE LA LÓGICA:")
    print("=" * 80)
    print("✅ Lunes → Ejecuta reporte del sábado (2 días atrás)")
    print("✅ Martes → Ejecuta reporte del lunes (1 día atrás)")
    print("✅ Miércoles → Ejecuta reporte del martes (1 día atrás)")
    print("✅ Jueves → Ejecuta reporte del miércoles (1 día atrás)")
    print("✅ Viernes → Ejecuta reporte del jueves (1 día atrás)")
    print("✅ Sábado → Ejecuta reporte del viernes (1 día atrás)")
    print("✅ Domingo → Ejecuta reporte del sábado (1 día atrás)")
    print("\n🎯 Esta lógica se aplica automáticamente en todos los scripts SAP")
    print("=" * 80)

if __name__ == "__main__":
    main()
