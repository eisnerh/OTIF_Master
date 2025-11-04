# Script PowerShell para configurar la tarea programada en Windows
# Este script crea una tarea que ejecuta el script cada hora

param(
    [string]$HoraInicio = "14:00",
    [string]$HoraFin = "22:00",
    [switch]$SoloHorarioLaboral = $true
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CONFIGURACION DE TAREA PROGRAMADA" -ForegroundColor Cyan
Write-Host "   Monitor Guías - Ejecución Cada Hora" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Obtener la ruta del script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFile = Join-Path $ScriptDir "ejecutar_monitor_guias.bat"
$TaskName = "OTIF_Monitor_Guias_Hourly"

# Verificar que existe el archivo batch
if (-not (Test-Path $BatchFile)) {
    Write-Host "ERROR: No se encontró el archivo ejecutar_monitor_guias.bat" -ForegroundColor Red
    Write-Host "Ubicación esperada: $BatchFile" -ForegroundColor Red
    exit 1
}

Write-Host "Archivo batch encontrado: $BatchFile" -ForegroundColor Green
Write-Host ""

# Eliminar la tarea si ya existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Eliminando tarea existente: $TaskName" -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Crear la acción (ejecutar el batch)
$Action = New-ScheduledTaskAction -Execute $BatchFile -WorkingDirectory $ScriptDir

# Crear el trigger (cada hora)
if ($SoloHorarioLaboral) {
    # Crear múltiples triggers para cada hora entre HoraInicio y HoraFin
    $StartTime = Get-Date $HoraInicio
    $EndTime = Get-Date $HoraFin
    
    Write-Host "Configurando ejecución cada hora entre $HoraInicio y $HoraFin" -ForegroundColor Yellow
    
    $Triggers = @()
    $CurrentTime = $StartTime
    
    while ($CurrentTime -le $EndTime) {
        $Trigger = New-ScheduledTaskTrigger -Daily -At $CurrentTime.ToString("HH:mm")
        $Triggers += $Trigger
        Write-Host "  - Trigger configurado para: $($CurrentTime.ToString('HH:mm'))" -ForegroundColor Gray
        $CurrentTime = $CurrentTime.AddHours(1)
    }
    
    # Crear la tarea con múltiples triggers
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Settings $Settings -Principal $Principal -Description "Ejecuta Monitor Guías cada hora entre $HoraInicio y $HoraFin" -Force | Out-Null
} else {
    # Crear trigger para cada hora (24 horas)
    Write-Host "Configurando ejecución cada hora (24 horas)" -ForegroundColor Yellow
    
    $Triggers = @()
    for ($hour = 0; $hour -lt 24; $hour++) {
        $Trigger = New-ScheduledTaskTrigger -Daily -At "$($hour.ToString('00')):00"
        $Triggers += $Trigger
    }
    
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Settings $Settings -Principal $Principal -Description "Ejecuta Monitor Guías cada hora (24 horas)" -Force | Out-Null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   TAREA PROGRAMADA CREADA EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nombre de la tarea: $TaskName" -ForegroundColor Cyan
Write-Host "Archivo ejecutado: $BatchFile" -ForegroundColor Cyan
Write-Host ""

# Mostrar información de la tarea
$Task = Get-ScheduledTask -TaskName $TaskName
Write-Host "Estado: $($Task.State)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para ver la tarea en el Programador de Tareas:" -ForegroundColor White
Write-Host "  1. Abre 'Programador de Tareas' desde el menú Inicio" -ForegroundColor White
Write-Host "  2. Busca la tarea: $TaskName" -ForegroundColor White
Write-Host ""
Write-Host "Para ejecutar manualmente:" -ForegroundColor White
Write-Host "  .\ejecutar_monitor_guias.bat" -ForegroundColor White
Write-Host ""
Write-Host "Para eliminar la tarea:" -ForegroundColor White
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor White

