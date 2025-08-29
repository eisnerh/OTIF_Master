/* ===== SISTEMA OTIF - FUNCIONES JAVASCRIPT ===== */

// Variables globales
let processingInterval;
let startTime;
let currentAction = null;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 OTIF Master - Aplicación inicializada');
    updateStatus();
    loadFiles();
    
    // Inicializar el menú hamburguesa
    initializeHamburgerMenu();
    
    // Agregar event listeners para los botones principales
    document.getElementById('btnIniciar').addEventListener('click', ejecutarProcesamientoCompleto);
    document.getElementById('btnActualizar').addEventListener('click', actualizarEstado);
    document.getElementById('btnConfiguracion').addEventListener('click', mostrarConfiguracion);
});

// ===== FUNCIONES DEL MENÚ HAMBURGUESA =====

function initializeHamburgerMenu() {
    const hamburgerToggle = document.getElementById('hamburgerToggle');
    const hamburgerContent = document.getElementById('hamburgerContent');
    
    if (hamburgerToggle && hamburgerContent) {
        hamburgerToggle.addEventListener('click', function() {
            toggleHamburgerMenu();
        });
        
        // Expandir el menú por defecto en pantallas grandes
        if (window.innerWidth > 768) {
            hamburgerContent.classList.add('expanded');
            hamburgerToggle.classList.add('active');
        }
    }
}

function toggleHamburgerMenu() {
    const hamburgerToggle = document.getElementById('hamburgerToggle');
    const hamburgerContent = document.getElementById('hamburgerContent');
    
    if (hamburgerToggle && hamburgerContent) {
        hamburgerToggle.classList.toggle('active');
        hamburgerContent.classList.toggle('expanded');
        
        // Agregar efecto de sonido (opcional)
        if (hamburgerContent.classList.contains('expanded')) {
            console.log('🍔 Menú expandido');
        } else {
            console.log('🍔 Menú contraído');
        }
    }
}

function toggleCategory(categoryName) {
    const content = document.getElementById(`content-${categoryName}`);
    const icon = document.getElementById(`icon-${categoryName}`);
    const header = content.previousElementSibling;
    
    if (content && icon) {
        // Toggle la clase expanded
        content.classList.toggle('expanded');
        icon.classList.toggle('rotated');
        header.classList.toggle('active');
        
        // Efecto visual adicional
        if (content.classList.contains('expanded')) {
            content.style.maxHeight = content.scrollHeight + 'px';
            console.log(`📂 Categoría ${categoryName} expandida`);
        } else {
            content.style.maxHeight = '0';
            console.log(`📂 Categoría ${categoryName} contraída`);
        }
    }
}

// Función para expandir todas las categorías
function expandAllCategories() {
    const categories = ['procesamiento', 'modulos', 'verificacion', 'configuracion', 'analisis', 'herramientas'];
    
    categories.forEach(category => {
        const content = document.getElementById(`content-${category}`);
        const icon = document.getElementById(`icon-${category}`);
        const header = content?.previousElementSibling;
        
        if (content && icon && header) {
            content.classList.add('expanded');
            icon.classList.add('rotated');
            header.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    });
    
    console.log('📂 Todas las categorías expandidas');
}

// Función para contraer todas las categorías
function collapseAllCategories() {
    const categories = ['procesamiento', 'modulos', 'verificacion', 'configuracion', 'analisis', 'herramientas'];
    
    categories.forEach(category => {
        const content = document.getElementById(`content-${category}`);
        const icon = document.getElementById(`icon-${category}`);
        const header = content?.previousElementSibling;
        
        if (content && icon && header) {
            content.classList.remove('expanded');
            icon.classList.remove('rotated');
            header.classList.remove('active');
            content.style.maxHeight = '0';
        }
    });
    
    console.log('📂 Todas las categorías contraídas');
}

// Función para agregar efectos de hover a las categorías del menú
function addMenuHoverEffects() {
    const menuCategories = document.querySelectorAll('.menu-category');
    menuCategories.forEach(category => {
        category.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        category.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// ===== FUNCIONES DEL MENÚ PRINCIPAL =====

// 🚀 PROCESAMIENTO PRINCIPAL
function confirmarAccion(modulo, mensaje) {
    currentAction = modulo;
    document.getElementById('mensajeConfirmacion').textContent = mensaje;
    document.getElementById('confirmacionPanel').style.display = 'block';
}

function confirmarAccionConfirmada() {
    if (currentAction === 'todo') {
        ejecutarProcesamientoCompleto();
    }
    document.getElementById('confirmacionPanel').style.display = 'none';
    currentAction = null;
}

function cancelarAccion() {
    document.getElementById('confirmacionPanel').style.display = 'none';
    currentAction = null;
}

function ejecutarProcesamientoCompleto() {
    fetch('/iniciar_procesamiento', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            mostrarAlerta('Error: ' + data.error, 'danger');
        } else {
            startTime = new Date();
            startMonitoring();
            mostrarAlerta('🚀 Procesamiento iniciado correctamente', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al iniciar el procesamiento', 'danger');
    });
}

// 📊 MÓDULOS INDIVIDUALES
function ejecutarModulo(modulo) {
    const modulos = {
        'no_entregas': 'Agrupación de datos NO ENTREGAS',
        'rep_plr': 'Agrupación de datos REP PLR',
        'vol_portafolio': 'Agrupación de datos VOL PORTAFOLIO',
        'unificar': 'Unificación de todos los datos'
    };
    
    const mensaje = `¿Ejecutar: ${modulos[modulo]}?`;
    confirmarAccion(modulo, mensaje);
}

// 🔍 VERIFICACIÓN Y MONITOREO
function verificarRutas() {
    fetch('/verificar_rutas')
    .then(response => response.json())
    .then(data => {
        mostrarResultadoVerificacion(data);
    })
    .catch(error => {
        console.error('Error al verificar rutas:', error);
        mostrarAlerta('Error al verificar las rutas', 'danger');
    });
}

function verResumen() {
    fetch('/ver_resumen')
    .then(response => response.json())
    .then(data => {
        mostrarResumen(data);
    })
    .catch(error => {
        console.error('Error al obtener resumen:', error);
        mostrarAlerta('Error al obtener el resumen', 'danger');
    });
}

function verificarEstructura() {
    fetch('/verificar_estructura')
    .then(response => response.json())
    .then(data => {
        mostrarResultadoEstructura(data);
    })
    .catch(error => {
        console.error('Error al verificar estructura:', error);
        mostrarAlerta('Error al verificar la estructura', 'danger');
    });
}

function verArchivosGenerados() {
    fetch('/ver_archivos_generados')
    .then(response => response.json())
    .then(data => {
        mostrarArchivosGenerados(data);
    })
    .catch(error => {
        console.error('Error al obtener archivos:', error);
        mostrarAlerta('Error al obtener archivos generados', 'danger');
    });
}

// ⚙️ CONFIGURACIÓN Y MANTENIMIENTO
function mostrarConfiguracion() {
    const panel = document.getElementById('configPanel');
    // Verificar si el panel está oculto (puede ser por CSS o por style)
    if (panel.style.display === 'none' || getComputedStyle(panel).display === 'none') {
        panel.style.display = 'block';
        loadConfiguracion();
    } else {
        panel.style.display = 'none';
    }
}

function actualizarEstado() {
    updateStatus();
    loadFiles();
    mostrarAlerta('🔄 Estado actualizado', 'info');
}

function confirmarLimpiar() {
    confirmarAccion('limpiar', '¿Estás seguro de que quieres LIMPIAR todos los archivos temporales? Esta acción no se puede deshacer.');
}

// 📈 ANÁLISIS Y REPORTES
function estadisticasRendimiento() {
    fetch('/estadisticas_rendimiento')
    .then(response => response.json())
    .then(data => {
        mostrarEstadisticasRendimiento(data);
    })
    .catch(error => {
        console.error('Error al obtener estadísticas:', error);
        mostrarAlerta('Error al obtener estadísticas', 'danger');
    });
}

function exportarReporte() {
    mostrarAlerta('📊 Función de exportación en desarrollo', 'info');
}

function informacionSistema() {
    fetch('/informacion_sistema')
    .then(response => response.json())
    .then(data => {
        mostrarInformacionSistema(data);
    })
    .catch(error => {
        console.error('Error al obtener información:', error);
        mostrarAlerta('Error al obtener información del sistema', 'danger');
    });
}

// 🛠️ HERRAMIENTAS AVANZADAS
function verificarLogs() {
    mostrarAlerta('📄 Función de logs en desarrollo', 'info');
}

function reiniciarSistema() {
    confirmarAccion('reiniciar', '¿Estás seguro de que quieres reiniciar el sistema?');
}

// ===== FUNCIONES DE UTILIDAD =====

function mostrarAlerta(mensaje, tipo) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.main-container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function mostrarResultadoVerificacion(data) {
    let html = '<div class="alert alert-info"><h6>🗺️ Estado de las Rutas:</h6>';
    
    for (const [nombre, info] of Object.entries(data)) {
        const icon = info.existe ? 'fas fa-check text-success' : 'fas fa-times text-danger';
        const status = info.existe ? 'Existe' : 'No existe';
        html += `<div><i class="${icon}"></i> ${nombre}: ${status} (${info.ruta})</div>`;
    }
    
    html += '</div>';
    
    const container = document.querySelector('.main-container');
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    container.insertBefore(alertDiv, container.firstChild);
}

function mostrarResumen(data) {
    let html = '<div class="alert alert-success"><h6>📊 Resumen del Procesamiento:</h6>';
    
    if (data.archivos_generados) {
        html += `<p><strong>Archivos generados:</strong> ${data.archivos_generados.length}</p>`;
        data.archivos_generados.forEach(archivo => {
            html += `<div>📄 ${archivo.nombre} - ${archivo.filas} filas, ${archivo.tamaño_mb.toFixed(2)} MB</div>`;
        });
    }
    
    html += '</div>';
    
    const container = document.querySelector('.main-container');
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    container.insertBefore(alertDiv, container.firstChild);
}

function mostrarResultadoEstructura(data) {
    let html = '<div class="alert alert-info"><h6>✅ Verificación de Estructura:</h6>';
    
    if (data.success) {
        html += '<div class="text-success">✅ Estructura del sistema correcta</div>';
        if (data.output) {
            html += `<pre class="mt-2">${data.output}</pre>`;
        }
    } else {
        html += '<div class="text-danger">❌ Problemas en la estructura del sistema</div>';
        if (data.error) {
            html += `<div class="text-danger">Error: ${data.error}</div>`;
        }
    }
    
    html += '</div>';
    
    const container = document.querySelector('.main-container');
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    container.insertBefore(alertDiv, container.firstChild);
}

function mostrarArchivosGenerados(data) {
    let html = '<div class="alert alert-info"><h6>📁 Archivos Generados:</h6>';
    
    for (const [directorio, info] of Object.entries(data)) {
        html += `<div class="mb-2"><strong>${info.descripcion}:</strong>`;
        if (info.existe) {
            if (info.archivos.length > 0) {
                info.archivos.forEach(archivo => {
                    html += `<div class="ms-3">📄 ${archivo.nombre} (${archivo.tamaño_mb.toFixed(2)} MB)</div>`;
                });
            } else {
                html += '<div class="ms-3 text-muted">No hay archivos</div>';
            }
        } else {
            html += '<div class="ms-3 text-danger">Directorio no existe</div>';
        }
        html += '</div>';
    }
    
    html += '</div>';
    
    const container = document.querySelector('.main-container');
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    container.insertBefore(alertDiv, container.firstChild);
}

function mostrarEstadisticasRendimiento(data) {
    let html = '<div class="alert alert-primary"><h6>📈 Estadísticas de Rendimiento:</h6>';
    
    if (data.tiempos_estimados) {
        html += '<div class="mb-2"><strong>Tiempos estimados:</strong></div>';
        for (const [modulo, tiempo] of Object.entries(data.tiempos_estimados)) {
            html += `<div class="ms-3">⏱️ ${modulo}: ${tiempo}</div>`;
        }
    }
    
    if (data.requisitos_sistema) {
        html += '<div class="mb-2 mt-3"><strong>Requisitos del sistema:</strong></div>';
        for (const [requisito, valor] of Object.entries(data.requisitos_sistema)) {
            html += `<div class="ms-3">💻 ${requisito}: ${valor}</div>`;
        }
    }
    
    html += '</div>';
    
    const container = document.querySelector('.main-container');
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    container.insertBefore(alertDiv, container.firstChild);
}

function mostrarInformacionSistema(data) {
    let html = '<div class="alert alert-secondary"><h6>ℹ️ Información del Sistema:</h6>';
    
    html += `<div><strong>Versión:</strong> ${data.version}</div>`;
    html += `<div><strong>Fecha:</strong> ${data.fecha}</div>`;
    
    if (data.scripts_disponibles && data.scripts_disponibles.length > 0) {
        html += '<div class="mb-2 mt-2"><strong>Scripts disponibles:</strong></div>';
        data.scripts_disponibles.forEach(script => {
            html += `<div class="ms-3">📜 ${script}</div>`;
        });
    }
    
    html += '</div>';
    
    const container = document.querySelector('.main-container');
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    container.insertBefore(alertDiv, container.firstChild);
}

// ===== FUNCIONES DE MONITOREO =====

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
        
        // Actualizar paso actual y mostrar información detallada del archivo en proceso
        if (data.archivo_actual && data.total_lineas > 0) {
            const porcentajeArchivo = data.total_lineas > 0 ? Math.round((data.lineas_procesadas / data.total_lineas) * 100) : 0;
            
            // Actualizar paso actual
            const pasoActual = document.getElementById('pasoActual');
            if (pasoActual) {
                pasoActual.innerHTML = `${data.paso_actual || 'Procesando...'}`;
            }
            
            // Mostrar sección de detalle de archivo
            const detalleArchivo = document.getElementById('detalleArchivo');
            if (detalleArchivo) {
                detalleArchivo.style.display = 'block';
                
                // Actualizar nombre del archivo
                const nombreArchivo = document.getElementById('nombreArchivo');
                if (nombreArchivo) {
                    nombreArchivo.textContent = data.archivo_actual;
                }
                
                // Actualizar progreso del archivo
                const progresoArchivo = document.getElementById('progresoArchivo');
                if (progresoArchivo) {
                    progresoArchivo.textContent = `${data.lineas_procesadas.toLocaleString()} de ${data.total_lineas.toLocaleString()} líneas (${porcentajeArchivo}%)`;
                }
                
                // Actualizar barra de progreso del archivo
                const progressBarArchivo = document.getElementById('progressBarArchivo');
                if (progressBarArchivo) {
                    progressBarArchivo.style.width = porcentajeArchivo + '%';
                    progressBarArchivo.setAttribute('aria-valuenow', porcentajeArchivo);
                }
            }
        } else {
            // Ocultar sección de detalle de archivo si no hay archivo en proceso
            const detalleArchivo = document.getElementById('detalleArchivo');
            if (detalleArchivo) {
                detalleArchivo.style.display = 'none';
            }
            
            updateCurrentStep(data.paso_actual);
        }
        
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
        logContainer.innerHTML = messages.map(msg => {
            // Determinar el tipo de mensaje para aplicar la clase CSS adecuada
            let messageClass = 'log-message';
            
            if (msg.includes('ERROR') || msg.includes('Error')) {
                messageClass = 'log-error';
            } else if (msg.includes('ADVERTENCIA') || msg.includes('Advertencia')) {
                messageClass = 'log-warning';
            } else if (msg.includes('ÉXITO') || msg.includes('Completado')) {
                messageClass = 'log-success';
            } else if (msg.includes('Leyendo archivo') || msg.includes('Iniciando lectura')) {
                messageClass = 'log-reading';
            } else if (msg.includes('Progreso') || msg.includes('líneas procesadas')) {
                messageClass = 'log-progress';
            } else if (msg.includes('INFO')) {
                messageClass = 'log-info';
            }
            
            return `<div class="mb-1 ${messageClass}">${msg}</div>`;
        }).join('');
        
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

function loadFiles() {
    fetch('/archivos_generados')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('archivosContainer');
        
        if (container) {
            if (data.archivos && data.archivos.length > 0) {
                container.innerHTML = data.archivos.map(file => `
                    <div class="file-item">
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
            
            const totalFilesElement = document.getElementById('totalFiles');
            const totalRowsElement = document.getElementById('totalRows');
            const totalSizeElement = document.getElementById('totalSize');
            const processingTimeElement = document.getElementById('processingTime');
            
            if (totalFilesElement) totalFilesElement.textContent = totalFiles;
            if (totalRowsElement) totalRowsElement.textContent = totalRows.toLocaleString();
            if (totalSizeElement) totalSizeElement.textContent = totalSize.toFixed(2) + ' MB';
            
            if (startTime && processingTimeElement) {
                const endTime = new Date();
                const processingTime = Math.round((endTime - startTime) / 1000);
                processingTimeElement.textContent = processingTime + 's';
            }
        }
    })
    .catch(error => {
        console.error('Error al cargar estadísticas:', error);
    });
}

// ===== FUNCIONES DE CONFIGURACIÓN =====

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
        mostrarAlerta('Error al cargar la configuración', 'danger');
    });
}

// Event listeners para el formulario de configuración
document.addEventListener('DOMContentLoaded', function() {
    const configForm = document.getElementById('configForm');
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarConfiguracion();
        });
    }
    
    const btnVerificarRutas = document.getElementById('btnVerificarRutas');
    if (btnVerificarRutas) {
        btnVerificarRutas.addEventListener('click', function() {
            verificarRutas();
        });
    }
});

function guardarConfiguracion() {
    const config = {
        rutas_archivos: {
            rep_plr: document.getElementById('rutaRepPLR').value,
            no_entregas: document.getElementById('rutaNoEntregas').value,
            vol_portafolio: document.getElementById('rutaVolPortafolio').value,
            output_unificado: document.getElementById('rutaOutputUnificado').value,
            output_final: document.getElementById('rutaOutputFinal').value
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
            mostrarAlerta('Error: ' + data.error, 'danger');
        } else {
            mostrarAlerta('✅ Configuración guardada correctamente', 'success');
            mostrarConfiguracion(); // Ocultar panel
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar la configuración', 'danger');
    });
}

// Función para seleccionar carpetas
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
                document.getElementById(campoId).value = data.ruta;
            }
            
            mostrarAlerta(`✅ ${data.message}`, 'success');
        } else {
            mostrarAlerta(data.message || 'No se seleccionó ninguna carpeta', 'warning');
        }
    })
    .catch(error => {
        console.error('Error al seleccionar carpeta:', error);
        mostrarAlerta('Error al seleccionar la carpeta', 'danger');
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
