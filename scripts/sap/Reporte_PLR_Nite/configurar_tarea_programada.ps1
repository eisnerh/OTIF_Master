# Script PowerShell para configurar tarea programada del Reporte PLR
# Ejecutar con permisos de administrador

param(
    [string]$HoraInicio = "14:00",
    [string]$HoraFin = "22:00",
    [switch]$SoloHorarioLaboral = $true
)

$TaskName = "OTIF_Reporte_PLR_Nite_Hourly"
$ScriptPath = Join-Path $PSScriptRoot "ejecutar_rep_plr.bat"
$WorkingDirectory = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configurando Tarea Programada" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que existe el archivo batch
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: No se encontró el archivo ejecutar_rep_plr.bat" -ForegroundColor Red
    Write-Host "Ruta esperada: $ScriptPath" -ForegroundColor Red
    exit 1
}

# Verificar que existe el archivo de credenciales
$CredsPath = Join-Path $PSScriptRoot "credentials.ini"
if (-not (Test-Path $CredsPath)) {
    Write-Host "ADVERTENCIA: No se encontró credentials.ini" -ForegroundColor Yellow
    Write-Host "Por favor, crea este archivo antes de ejecutar la tarea programada" -ForegroundColor Yellow
    Write-Host ""
}

# Eliminar tarea si ya existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Eliminando tarea programada existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Crear acción
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDirectory

# Crear trigger
if ($SoloHorarioLaboral) {
    # Calcular duración en horas
    $StartTime = [DateTime]::ParseExact($HoraInicio, "HH:mm", $null)
    $EndTime = [DateTime]::ParseExact($HoraFin, "HH:mm", $null)
    $Duration = $EndTime - $StartTime
    
    $Trigger = New-ScheduledTaskTrigger -Daily -At $HoraInicio
    $Trigger.Repetition = $(New-ScheduledTaskTrigger -Once -At $HoraInicio -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration $Duration).Repetition
} else {
    # Ejecutar cada hora, 24 horas al día
    $Trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
    $Trigger.Repetition = $(New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 1)).Repetition
}

# Configuración de la tarea
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Crear principal (ejecutar con el usuario actual)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Registrar la tarea
Write-Host "Registrando tarea programada..." -ForegroundColor Green
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Ejecuta el Reporte PLR NITE automáticamente cada hora"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Tarea Programada Configurada" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nombre de la tarea: $TaskName" -ForegroundColor Cyan
Write-Host "Horario de inicio: $HoraInicio" -ForegroundColor Cyan
if ($SoloHorarioLaboral) {
    Write-Host "Horario de fin: $HoraFin" -ForegroundColor Cyan
} else {
    Write-Host "Frecuencia: 24 horas al día" -ForegroundColor Cyan
}
Write-Host "Intervalo: Cada 1 hora" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar la tarea, ejecuta:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para eliminar la tarea, ejecuta:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Yellow
Write-Host ""

