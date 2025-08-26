/* ===== SISTEMA OTIF - FUNCIONES JAVASCRIPT ===== */

// Variables globales
let processingInterval;
let startTime;
let accionPendiente = null;
let moduloPendiente = null;

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Sistema OTIF inicializado');
    updateStatus();
    loadFiles();
    initializeEventListeners();
});

// ===== EVENT LISTENERS =====
function initializeEventListeners() {
    // Botón iniciar procesamiento
    const btnIniciar = document.getElementById('btnIniciar');
    if (btnIniciar) {
        btnIniciar.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que quieres iniciar el procesamiento? Esto puede tomar varios minutos.')) {
                startProcessing();
            }
        });
    }

    // Botón actualizar estado
    const btnActualizar = document.getElementById('btnActualizar');
    if (btnActualizar) {
        btnActualizar.addEventListener('click', function() {
            updateStatus();
            loadFiles();
        });
    }

    // Botón configuración
    const btnConfiguracion = document.getElementById('btnConfiguracion');
    if (btnConfiguracion) {
        btnConfiguracion.addEventListener('click', function() {
            toggleConfigPanel();
            loadConfiguracion();
        });
    }

    // Botón verificar rutas
    const btnVerificarRutas = document.getElementById('btnVerificarRutas');
    if (btnVerificarRutas) {
        btnVerificarRutas.addEventListener('click', function() {
            verificarRutas();
        });
    }

    // Formulario de configuración
    const configForm = document.getElementById('configForm');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarConfiguracion();
        });
    }
}

// ===== FUNCIONES DE PROCESAMIENTO =====
function startProcessing() {
    showLoading('Iniciando procesamiento...');
    
    fetch('/iniciar_procesamiento', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
        } else {
            startTime = new Date();
            startMonitoring();
            showAlert('Procesamiento iniciado correctamente', 'success');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al iniciar el procesamiento', 'danger');
    });
}

function startMonitoring() {
    if (processingInterval) {
        clearInterval(processingInterval);
    }
    
    processingInterval = setInterval(() => {
        updateStatus();
    }, 2000);
}

function updateStatus() {
    fetch('/estado_procesamiento')
    .then(response => response.json())
    .then(data => {
        updateProgressBar(data.progreso);
        updateStatusIndicator(data);
        updateCurrentStep(data.paso_actual);
        updateLogMessages(data.mensajes);
        
        if (data.completado || data.error) {
            clearInterval(processingInterval);
            loadFiles();
            updateStatistics();
        }
    })
    .catch(error => {
        console.error('Error al obtener estado:', error);
    });
}

// ===== FUNCIONES DE ACTUALIZACIÓN DE UI =====
function updateProgressBar(progress) {
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = progress + '%';
        progressBar.textContent = progress + '%';
    }
}

function updateStatusIndicator(data) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (indicator && statusText) {
        indicator.className = 'status-indicator';
        
        if (data.error) {
            indicator.classList.add('status-error');
            statusText.textContent = 'Error';
        } else if (data.completado) {
            indicator.classList.add('status-completed');
            statusText.textContent = 'Completado';
        } else if (data.en_proceso) {
            indicator.classList.add('status-running');
            statusText.textContent = 'En Proceso';
        } else {
            indicator.classList.add('status-error');
            statusText.textContent = 'Inactivo';
        }
    }
}

function updateCurrentStep(step) {
    const pasoActual = document.getElementById('pasoActual');
    if (pasoActual) {
        pasoActual.textContent = step || 'Esperando inicio...';
    }
}

function updateLogMessages(messages) {
    const logContainer = document.getElementById('logContainer');
    
    if (logContainer && messages && messages.length > 0) {
        logContainer.innerHTML = messages.map(msg => 
            `<div class="mb-1">${msg}</div>`
        ).join('');
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// ===== FUNCIONES DE ARCHIVOS =====
function loadFiles() {
    fetch('/archivos_generados')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('archivosContainer');
        
        if (container) {
            if (data.archivos && data.archivos.length > 0) {
                container.innerHTML = data.archivos.map(file => `
                    <div class="file-item fade-in">
                        <div class="row align-items-center">
                            <div class="col-md-6">
                                <h6><i class="fas fa-file-alt"></i> ${file.nombre}</h6>
                                ${file.error ? 
                                    `<span class="text-danger">Error: ${file.error}</span>` :
                                    `<small class="text-muted">
                                        ${file.filas ? file.filas.toLocaleString() : 'N/A'} filas, 
                                        ${file.columnas || 'N/A'} columnas, 
                                        ${file.tamaño_mb ? file.tamaño_mb.toFixed(2) : 'N/A'} MB
                                    </small>`
                                }
                            </div>
                            <div class="col-md-6 text-end">
                                ${!file.error ? 
                                    `<a href="/descargar_archivo/${file.nombre}" class="btn btn-success btn-sm">
                                        <i class="fas fa-download"></i> Descargar
                                    </a>` : ''
                                }
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-folder-open fa-3x mb-3"></i>
                        <p>No hay archivos generados aún</p>
                    </div>
                `;
            }
        }
    })
    .catch(error => {
        console.error('Error al cargar archivos:', error);
    });
}

function updateStatistics() {
    fetch('/ver_resumen')
    .then(response => response.json())
    .then(data => {
        if (data.archivos_generados) {
            const totalFiles = data.archivos_generados.length;
            const totalRows = data.archivos_generados.reduce((sum, file) => sum + (file.filas || 0), 0);
            const totalSize = data.archivos_generados.reduce((sum, file) => sum + (file.tamaño_mb || 0), 0);
            
            const totalFilesEl = document.getElementById('totalFiles');
            const totalRowsEl = document.getElementById('totalRows');
            const totalSizeEl = document.getElementById('totalSize');
            const processingTimeEl = document.getElementById('processingTime');
            
            if (totalFilesEl) totalFilesEl.textContent = totalFiles;
            if (totalRowsEl) totalRowsEl.textContent = totalRows.toLocaleString();
            if (totalSizeEl) totalSizeEl.textContent = totalSize.toFixed(2) + ' MB';
            
            if (startTime && processingTimeEl) {
                const endTime = new Date();
                const processingTime = Math.round((endTime - startTime) / 1000);
                processingTimeEl.textContent = processingTime + 's';
            }
        }
    })
    .catch(error => {
        console.error('Error al cargar estadísticas:', error);
    });
}

// ===== FUNCIONES DE CONFIGURACIÓN =====
function toggleConfigPanel() {
    const panel = document.getElementById('configPanel');
    if (panel) {
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            panel.classList.add('slide-up');
        } else {
            panel.style.display = 'none';
        }
    }
}

function loadConfiguracion() {
    fetch('/configuracion')
    .then(response => response.json())
    .then(data => {
        const rutaRepPLR = document.getElementById('rutaRepPLR');
        const rutaNoEntregas = document.getElementById('rutaNoEntregas');
        const rutaVolPortafolio = document.getElementById('rutaVolPortafolio');
        const rutaOutputUnificado = document.getElementById('rutaOutputUnificado');
        const rutaOutputFinal = document.getElementById('rutaOutputFinal');
        
        if (rutaRepPLR) rutaRepPLR.value = data.rutas_archivos.rep_plr;
        if (rutaNoEntregas) rutaNoEntregas.value = data.rutas_archivos.no_entregas;
        if (rutaVolPortafolio) rutaVolPortafolio.value = data.rutas_archivos.vol_portafolio;
        if (rutaOutputUnificado) rutaOutputUnificado.value = data.rutas_archivos.output_unificado;
        if (rutaOutputFinal) rutaOutputFinal.value = data.rutas_archivos.output_final;
    })
    .catch(error => {
        console.error('Error al cargar configuración:', error);
        showAlert('Error al cargar la configuración', 'danger');
    });
}

function guardarConfiguracion() {
    const config = {
        rutas_archivos: {
            rep_plr: document.getElementById('rutaRepPLR')?.value || '',
            no_entregas: document.getElementById('rutaNoEntregas')?.value || '',
            vol_portafolio: document.getElementById('rutaVolPortafolio')?.value || '',
            output_unificado: document.getElementById('rutaOutputUnificado')?.value || '',
            output_final: document.getElementById('rutaOutputFinal')?.value || ''
        }
    };

    fetch('/configuracion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
        } else {
            showAlert('Configuración guardada correctamente', 'success');
            toggleConfigPanel();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al guardar la configuración', 'danger');
    });
}

// ===== FUNCIONES DEL MENÚ UNIFICADO =====
function ejecutarModulo(modulo) {
    showLoading(`Ejecutando módulo: ${modulo}`);
    
    fetch(`/ejecutar_modulo/${modulo}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            showAlert('Error: ' + data.error, 'danger');
        } else {
            showAlert('Módulo iniciado correctamente. Revisa el progreso en el panel de control.', 'success');
            startTime = new Date();
            updateStatus();
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al ejecutar el módulo', 'danger');
    });
}

// ===== FUNCIONES DE CONFIRMACIÓN =====
function confirmarAccion(modulo, mensaje) {
    accionPendiente = 'ejecutar';
    moduloPendiente = modulo;
    const mensajeConfirmacion = document.getElementById('mensajeConfirmacion');
    const confirmacionPanel = document.getElementById('confirmacionPanel');
    
    if (mensajeConfirmacion) mensajeConfirmacion.textContent = mensaje;
    if (confirmacionPanel) confirmacionPanel.style.display = 'block';
}

function confirmarLimpiar() {
    accionPendiente = 'limpiar';
    const mensajeConfirmacion = document.getElementById('mensajeConfirmacion');
    const confirmacionPanel = document.getElementById('confirmacionPanel');
    
    if (mensajeConfirmacion) {
        mensajeConfirmacion.textContent = '¿Estás seguro de que quieres limpiar todos los archivos temporales del sistema? Esta acción no se puede deshacer.';
    }
    if (confirmacionPanel) confirmacionPanel.style.display = 'block';
}

function confirmarAccionConfirmada() {
    if (accionPendiente === 'ejecutar' && moduloPendiente) {
        ejecutarModulo(moduloPendiente);
    } else if (accionPendiente === 'limpiar') {
        limpiarArchivosTemporales();
    }
    cancelarAccion();
}

function cancelarAccion() {
    accionPendiente = null;
    moduloPendiente = null;
    const confirmacionPanel = document.getElementById('confirmacionPanel');
    if (confirmacionPanel) confirmacionPanel.style.display = 'none';
}

// ===== FUNCIONES DE VERIFICACIÓN =====
function verificarRutas() {
    showLoading('Verificando rutas...');
    
    fetch('/verificar_rutas')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        const statusDiv = document.getElementById('rutasStatus');
        if (statusDiv) {
            let html = '<h6><i class="fas fa-info-circle"></i> Estado de las Rutas:</h6>';
            
            for (const [nombre, info] of Object.entries(data)) {
                const icon = info.existe ? 'fas fa-check text-success' : 'fas fa-times text-danger';
                const status = info.existe ? 'Existe' : 'No existe';
                html += `<div><i class="${icon}"></i> ${nombre}: ${status} (${info.ruta})</div>`;
            }
            
            statusDiv.innerHTML = html;
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error al verificar rutas:', error);
        showAlert('Error al verificar las rutas', 'danger');
    });
}

function verificarEstructura() {
    showLoading('Verificando estructura...');
    
    fetch('/verificar_estructura')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert('Verificación completada. Revisa la consola para más detalles.', 'success');
            console.log('Verificación de estructura:', data.output);
            if (data.error) {
                console.warn('Advertencias:', data.error);
            }
        } else {
            showAlert('Error en la verificación: ' + (data.error || 'Error desconocido'), 'danger');
            console.error('Error de verificación:', data);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al verificar estructura', 'danger');
    });
}

function verArchivosGenerados() {
    showLoading('Obteniendo archivos...');
    
    fetch('/ver_archivos_generados')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        let mensaje = '📁 ARCHIVOS GENERADOS POR EL SISTEMA:\n\n';
        
        for (const [directorio, info] of Object.entries(data)) {
            mensaje += `${info.descripcion} (${directorio}):\n`;
            if (info.existe) {
                if (info.archivos.length > 0) {
                    info.archivos.forEach(archivo => {
                        mensaje += `   📄 ${archivo.nombre} (${archivo.tamaño_mb.toFixed(2)} MB)\n`;
                    });
                } else {
                    mensaje += `   ⚠️ No hay archivos\n`;
                }
            } else {
                mensaje += `   ❌ Directorio no existe\n`;
            }
            mensaje += '\n';
        }
        
        showAlert(mensaje, 'info');
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al obtener archivos generados', 'danger');
    });
}

function informacionSistema() {
    showLoading('Obteniendo información...');
    
    fetch('/informacion_sistema')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        let mensaje = `📋 INFORMACIÓN DEL SISTEMA OTIF\n\n`;
        mensaje += `🎯 VERSIÓN: ${data.version}\n`;
        mensaje += `📅 FECHA: ${data.fecha}\n\n`;
        
        mensaje += `📁 SCRIPTS DISPONIBLES:\n`;
        if (data.scripts_disponibles.length > 0) {
            data.scripts_disponibles.forEach(script => {
                mensaje += `   ✅ ${script}\n`;
            });
        } else {
            mensaje += `   ❌ Carpeta scripts no encontrada\n`;
        }
        mensaje += '\n';
        
        mensaje += `⚙️ CONFIGURACIÓN:\n`;
        if (data.configuracion.archivo) {
            mensaje += `   ✅ Archivo: ${data.configuracion.archivo}\n`;
            mensaje += `   📅 Última actualización: ${data.configuracion.ultima_actualizacion}\n`;
        } else {
            mensaje += `   ❌ Error al leer configuración\n`;
        }
        mensaje += '\n';
        
        mensaje += `📊 LOGS:\n`;
        if (data.logs.log_principal) {
            mensaje += `   ✅ ${data.logs.log_principal}\n`;
        } else {
            mensaje += `   ❌ Log principal no encontrado\n`;
        }
        
        showAlert(mensaje, 'info');
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al obtener información del sistema', 'danger');
    });
}

function estadisticasRendimiento() {
    showLoading('Obteniendo estadísticas...');
    
    fetch('/estadisticas_rendimiento')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        let mensaje = `📈 ESTADÍSTICAS DE RENDIMIENTO\n\n`;
        
        mensaje += `⏱️ TIEMPOS ESTIMADOS DE PROCESAMIENTO:\n`;
        for (const [modulo, tiempo] of Object.entries(data.tiempos_estimados)) {
            mensaje += `   • ${modulo}: ${tiempo}\n`;
        }
        mensaje += '\n';
        
        mensaje += `💻 REQUISITOS DEL SISTEMA:\n`;
        for (const [requisito, descripcion] of Object.entries(data.requisitos_sistema)) {
            mensaje += `   • ${requisito}: ${descripcion}\n`;
        }
        mensaje += '\n';
        
        mensaje += `📊 ARCHIVOS PRINCIPALES GENERADOS:\n`;
        data.archivos_principales_generados.forEach(archivo => {
            mensaje += `   • ${archivo}\n`;
        });
        
        showAlert(mensaje, 'info');
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al obtener estadísticas de rendimiento', 'danger');
    });
}

// ===== FUNCIONES NUEVAS DEL MENÚ MEJORADO =====
function verificarLogs() {
    showLoading('Verificando logs...');
    
    fetch('/verificar_logs')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        let mensaje = '📄 LOGS DEL SISTEMA:\n\n';
        if (data.logs && data.logs.length > 0) {
            data.logs.forEach(log => {
                mensaje += `📄 ${log.nombre} (${log.tamaño_mb.toFixed(2)} MB)\n`;
                mensaje += `   📅 Última modificación: ${log.fecha_modificacion}\n\n`;
            });
        } else {
            mensaje += '❌ No se encontraron logs del sistema';
        }
        showAlert(mensaje, 'info');
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al verificar logs del sistema', 'danger');
    });
}

function exportarReporte() {
    showLoading('Exportando reporte...');
    
    fetch('/exportar_reporte')
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert('✅ Reporte exportado correctamente\n\n📁 Ubicación: ' + data.ubicacion, 'success');
        } else {
            showAlert('❌ Error al exportar reporte: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al exportar reporte', 'danger');
    });
}

function reiniciarSistema() {
    if (confirm('¿Estás seguro de que quieres reiniciar el sistema? Esto detendrá todos los procesos en curso.')) {
        showLoading('Reiniciando sistema...');
        
        fetch('/reiniciar_sistema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showAlert('✅ Sistema reiniciado correctamente', 'success');
                setTimeout(() => location.reload(), 2000);
            } else {
                showAlert('❌ Error al reiniciar sistema: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showAlert('Error al reiniciar sistema', 'danger');
        });
    }
}

function limpiarArchivosTemporales() {
    showLoading('Limpiando archivos...');
    
    fetch('/limpiar_archivos_temporales', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
        } else {
            showAlert('Error: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error al limpiar archivos temporales', 'danger');
    });
}

// ===== FUNCIONES AUXILIARES =====
function mostrarConfiguracion() {
    toggleConfigPanel();
}

function actualizarEstado() {
    updateStatus();
    loadFiles();
    updateStatistics();
}

function verResumen() {
    updateStatistics();
}

function seleccionarCarpeta(tipoRuta) {
    fetch(`/seleccionar_carpeta/${tipoRuta}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const campoId = getCampoId(tipoRuta);
            if (campoId) {
                const campo = document.getElementById(campoId);
                if (campo) campo.value = data.ruta;
            }
            
            const statusDiv = document.getElementById('rutasStatus');
            if (statusDiv) {
                statusDiv.innerHTML = `<div class="alert alert-success">
                    <i class="fas fa-check"></i> ${data.message}
                </div>`;
                
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 3000);
            }
        } else {
            showAlert(data.message || 'No se seleccionó ninguna carpeta', 'warning');
        }
    })
    .catch(error => {
        console.error('Error al seleccionar carpeta:', error);
        showAlert('Error al seleccionar la carpeta', 'danger');
    });
}

function getCampoId(tipoRuta) {
    const mapeo = {
        'rep_plr': 'rutaRepPLR',
        'no_entregas': 'rutaNoEntregas',
        'vol_portafolio': 'rutaVolPortafolio',
        'output_unificado': 'rutaOutputUnificado',
        'output_final': 'rutaOutputFinal'
    };
    return mapeo[tipoRuta];
}

// ===== FUNCIONES DE UI =====
function showLoading(message = 'Cargando...') {
    // Crear overlay de loading si no existe
    let loadingOverlay = document.getElementById('loadingOverlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loadingOverlay';
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="loading"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function showAlert(message, type = 'info') {
    // Crear alerta personalizada
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insertar al inicio del main-container
    const mainContainer = document.querySelector('.main-container');
    if (mainContainer) {
        mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// ===== EXPORTAR FUNCIONES PARA USO GLOBAL =====
window.OTIFApp = {
    ejecutarModulo,
    confirmarAccion,
    confirmarLimpiar,
    confirmarAccionConfirmada,
    cancelarAccion,
    verificarEstructura,
    verArchivosGenerados,
    informacionSistema,
    estadisticasRendimiento,
    verificarLogs,
    exportarReporte,
    reiniciarSistema,
    limpiarArchivosTemporales,
    mostrarConfiguracion,
    actualizarEstado,
    verResumen,
    verificarRutas,
    seleccionarCarpeta
};
