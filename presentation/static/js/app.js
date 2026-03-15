/**
 * AGENTE IA - JAVASCRIPT PROFESIONAL
 * Manejo de la interfaz y comunicación con la API
 * Soporte para múltiples sesiones
 */

// ==========================================
// Estado de la Aplicación
// ==========================================

const AppState = {
    sesionActual: null,
    sesiones: [],
    soluciones: [],
    historial: [],
};

// ==========================================
// Elementos del DOM
// ==========================================

const DOM = {
    form: null,
    problemaInput: null,
    problemaError: null,
    btnConsultar: null,
    btnContent: null,
    loading: null,
    respuestaContainer: null,
    contenedorRespuestas: null,
    historialContainer: null,
    sesionesContainer: null,
    sesionActualNombre: null,
    btnNuevaSesion: null,
    welcomeMessage: null,
};

// ==========================================
// Inicialización
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    inicializarElementos();
    configurarEventos();
    cargarSaludo();
    cargarSesiones();
    cargarHistorial();
});

function inicializarElementos() {
    DOM.form = document.getElementById('problemaForm');
    DOM.problemaInput = document.getElementById('problema');
    DOM.problemaError = document.getElementById('problemaError');
    DOM.btnConsultar = document.getElementById('btnConsultar');
    DOM.btnContent = DOM.btnConsultar.querySelector('.btn-content');
    DOM.loading = DOM.btnConsultar.querySelector('.loading');
    DOM.respuestaContainer = document.getElementById('respuestaContainer');
    DOM.contenedorRespuestas = document.getElementById('respuesta');
    DOM.historialContainer = document.getElementById('historialLista');
    DOM.sesionesContainer = document.getElementById('sesionesLista');
    DOM.sesionActualNombre = document.getElementById('sesionActualNombre');
    DOM.btnNuevaSesion = document.getElementById('btnNuevaSesion');
    DOM.btnTerminarSesion = document.getElementById('btnTerminarSesion');
    DOM.welcomeMessage = document.getElementById('welcomeMessage');
}

// ==========================================
// Configuración de Eventos
// ==========================================

function configurarEventos() {
    // Validación en tiempo real
    DOM.problemaInput.addEventListener('input', validarInput);
    DOM.problemaInput.addEventListener('blur', validarInput);
    
    // Envío del formulario
    DOM.form.addEventListener('submit', manejarSubmit);
    
    // Botón nueva sesión
    if (DOM.btnNuevaSesion) {
        DOM.btnNuevaSesion.addEventListener('click', crearNuevaSesion);
    }
    
    // Botón terminar sesión
    if (DOM.btnTerminarSesion) {
        DOM.btnTerminarSesion.addEventListener('click', terminarSesion);
    }
    
    // Despedida al cerrar la pestaña/navegador
    window.addEventListener('beforeunload', manejarCierreSesion);
}

// ==========================================
// Validación
// ==========================================

function validarInput() {
    const valor = DOM.problemaInput.value.trim();
    const esValido = valor.length >= 5 && valor.length <= 500;
    
    if (valor.length > 0 && !esValido) {
        DOM.problemaInput.classList.add('is-invalid');
        DOM.problemaError.classList.add('visible');
        return false;
    } else if (valor.length === 0) {
        DOM.problemaInput.classList.remove('is-invalid');
        DOM.problemaError.classList.remove('visible');
        return false;
    } else {
        DOM.problemaInput.classList.remove('is-invalid');
        DOM.problemaError.classList.remove('visible');
        return true;
    }
}

// ==========================================
// Manejo de Sesiones
// ==========================================

async function cargarSesiones() {
    try {
        const respuesta = await fetch('/api/v1/sesiones');
        const data = await respuesta.json();
        AppState.sesiones = data;
        renderizarSesiones();
        
        // Si no hay sesión activa, crear una
        if (!AppState.sesionActual && data.length > 0) {
            await seleccionarSesion(data[0].id);
        } else if (!AppState.sesionActual) {
            await crearNuevaSesion();
        }
    } catch (error) {
        console.error('Error cargando sesiones:', error);
        await crearNuevaSesion();
    }
}

async function crearNuevaSesion() {
    try {
        const respuesta = await fetch('/api/v1/sesiones', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre: null }),
        });
        const data = await respuesta.json();
        
        AppState.sesiones.unshift(data);
        AppState.sesionActual = data.id;
        
        renderizarSesiones();
        limpiarFormulario();
        
    } catch (error) {
        console.error('Error creando sesión:', error);
    }
}

async function terminarSesion() {
    console.log('Botón terminar sesión cliqueado');
    try {
        const sesionId = AppState.sesionActual;
        console.log('Sesión ID:', sesionId);
        
        // Llamar a la despedida
        const response = await fetch('/api/v1/skills/despedida', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sesion_id: sesionId }),
        });
        
        const data = await response.json();
        console.log('Despedida:', data);
        
        // Mostrar despedida en pantalla
        mostrarDespedida(data);
        
        // Limpiar estado
        AppState.sesionActual = null;
        AppState.soluciones = [];
        limpiarFormulario();
        renderizarSesiones();
        
    } catch (error) {
        console.error('Error terminando sesión:', error);
        alert('Error al terminar sesión: ' + error.message);
    }
}

async function seleccionarSesion(sesionId) {
    AppState.sesionActual = sesionId;
    
    // Cargar datos de la sesión
    try {
        const respuesta = await fetch(`/api/v1/sesiones/${sesionId}`);
        const data = await respuesta.json();
        
        if (data.problema_actual) {
            DOM.problemaInput.value = data.problema_actual;
        }
        
        if (data.soluciones && data.soluciones.length > 0) {
            // Convertir formato de sesión a formato de respuesta
            const respuestaData = {
                problema_original: data.problema_actual,
                timestamp: new Date().toISOString(),
                soluciones: data.soluciones,
                razonamiento: '',
                preguntas_aclaratorias: [],
            };
            AppState.soluciones = data.soluciones;
            mostrarResultados(respuestaData);
        } else {
            limpiarFormulario();
        }
        
    } catch (error) {
        console.error('Error cargando sesión:', error);
    }
    
    renderizarSesiones();
}

async function eliminarSesion(sesionId, event) {
    event.stopPropagation();
    
    if (!confirm('¿Eliminar esta sesión?')) return;
    
    try {
        await fetch(`/api/v1/sesiones/${sesionId}`, {
            method: 'DELETE',
        });
        
        // Recargar sesiones
        await cargarSesiones();
        
    } catch (error) {
        console.error('Error eliminando sesión:', error);
    }
}

function renderizarSesiones() {
    if (!DOM.sesionesContainer) return;
    
    if (AppState.sesiones.length === 0) {
        DOM.sesionesContainer.innerHTML = `
            <p style="color: var(--text-muted); text-align: center; padding: 1rem;">
                No hay sesiones
            </p>
        `;
        return;
    }
    
    DOM.sesionesContainer.innerHTML = AppState.sesiones.map(sesion => `
        <div class="sesion-item ${sesion.id === AppState.sesionActual ? 'active' : ''}" 
             onclick="seleccionarSesion('${sesion.id}')">
            <div class="sesion-info">
                <span class="sesion-nombre">${sesion.nombre}</span>
                ${sesion.problema_actual ? `<span class="sesion-preview">${truncarTexto(sesion.problema_actual, 30)}</span>` : ''}
            </div>
            <button class="sesion-eliminar" onclick="eliminarSesion('${sesion.id}', event)">
                <i class="bi bi-x"></i>
            </button>
        </div>
    `).join('');
    
    // Actualizar nombre en el header
    if (DOM.sesionActualNombre && AppState.sesionActual) {
        const sesion = AppState.sesiones.find(s => s.id === AppState.sesionActual);
        if (sesion) {
            DOM.sesionActualNombre.textContent = sesion.nombre;
        }
    }
}

// ==========================================
// Manejo del Formulario
// ==========================================

async function manejarSubmit(e) {
    e.preventDefault();
    
    if (!validarInput()) {
        DOM.problemaInput.focus();
        return;
    }
    
    const texto = DOM.problemaInput.value.trim();
    
    // Mostrar estado de carga
    DOM.btnContent.style.display = 'none';
    DOM.loading.style.display = 'inline-flex';
    DOM.btnConsultar.disabled = true;
    DOM.respuestaContainer.classList.remove('visible');
    
    try {
        const response = await fetch('/api/v1/analizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sesion_id: AppState.sesionActual,
                texto: texto,
            }),
        });
        
        if (!response.ok) {
            throw new Error('Error en la solicitud');
        }
        
        const data = await response.json();
        
        // Guardar ID de sesión si es nuevo
        if (data.sesion_id && data.sesion_id !== AppState.sesionActual) {
            AppState.sesionActual = data.sesion_id;
            await cargarSesiones();
        }
        
        // Procesar y mostrar resultados
        AppState.soluciones = data.soluciones;
        mostrarResultados(data);
        
    } catch (error) {
        console.error('Error:', error);
        mostrarError();
    } finally {
        DOM.btnContent.style.display = 'inline';
        DOM.loading.style.display = 'none';
        DOM.btnConsultar.disabled = false;
    }
}

function limpiarFormulario() {
    DOM.problemaInput.value = '';
    AppState.soluciones = [];
    DOM.contenedorRespuestas.innerHTML = '';
    DOM.respuestaContainer.classList.remove('visible');
}

// ==========================================
// Renderizado de Resultados
// ==========================================

function mostrarResultados(data) {
    DOM.contenedorRespuestas.innerHTML = '';
    
    // Mostrar preguntas aclaratorias si existen
    if (data.preguntas_aclaratorias && data.preguntas_aclaratorias.length > 0) {
        const preguntasHTML = `
            <div class="preguntas-container">
                <div class="preguntas-title">
                    <i class="bi bi-question-circle"></i>
                    Para mejorar el análisis, considera:
                </div>
                <ul class="preguntas-lista">
                    ${data.preguntas_aclaratorias.map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>
        `;
        DOM.contenedorRespuestas.innerHTML = preguntasHTML;
    }
    
    // Renderizar tarjetas de soluciones
    data.soluciones.forEach((solucion, indice) => {
        const card = crearTarjetaSolucion(solucion, indice);
        DOM.contenedorRespuestas.innerHTML += card;
    });
    
    // Agregar eventos a las tarjetas
    configurarEventosTarjetas();
    
    // Mostrar contenedor
    DOM.respuestaContainer.classList.add('visible');
    
    // Animar entradas
    animateSoluciones();
}

function crearTarjetaSolucion(solucion, indice) {
    const complejidadClase = `complejidad-${solucion.complejidad}`;
    const complejidadLabel = mapearComplejidad(solucion.complejidad);
    
    return `
        <div class="solucion-card" data-indice="${indice}" style="animation-delay: ${indice * 0.1}s">
            <div class="solucion-header" onclick="toggleSolucion(${indice})">
                <span class="solucion-numero">${indice + 1}</span>
                <div class="solucion-info">
                    <div class="solucion-titulo">${solucion.titulo}</div>
                    <div class="solucion-categoria">${solucion.categoria}</div>
                </div>
                <span class="solucion-complejidad ${complejidadClase}">
                    <i class="bi bi-gear"></i>
                    ${complejidadLabel}
                </span>
                <i class="bi bi-chevron-down solucion-toggle"></i>
            </div>
            <div class="solucion-body">
                <p class="solucion-descripcion">${solucion.descripcion}</p>
                
                <div class="solucion-seccion">
                    <div class="solucion-seccion-title ventajas">
                        <i class="bi bi-check-circle"></i> Ventajas
                    </div>
                    <ul class="solucion-lista ventajas">
                        ${solucion.ventajas.map(v => `<li>${v}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="solucion-seccion">
                    <div class="solucion-seccion-title desventajas">
                        <i class="bi bi-x-circle"></i> Desventajas
                    </div>
                    <ul class="solucion-lista desventajas">
                        ${solucion.desventajas.map(d => `<li>${d}</li>`).join('')}
                    </ul>
                </div>
                
                ${solucion.tecnologias && solucion.tecnologias.length > 0 ? `
                    <div class="solucion-seccion">
                        <div class="solucion-seccion-title tecnologias">
                            <i class="bi bi-tools"></i> Tecnologías Recomendadas
                        </div>
                        <div class="solucion-tags">
                            ${solucion.tecnologias.map(t => `<span class="solucion-tag">${t}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="solucion-seccion">
                    <div class="solucion-seccion-title recomendacion">
                        <i class="bi bi-lightbulb"></i> Recomendación
                    </div>
                    <div class="solucion-recomendacion">
                        <i class="bi bi-info-circle"></i>
                        ${solucion.recomendacion}
                    </div>
                </div>
                
                <button class="btn-seleccionar" onclick="seleccionarSolucion(${indice})">
                    <i class="bi bi-check2-circle"></i> Seleccionar esta solución
                </button>
            </div>
        </div>
    `;
}

function mapearComplejidad(complejidad) {
    const map = {
        'baja': 'Complejidad Baja',
        'media': 'Complejidad Media',
        'alta': 'Complejidad Alta',
        'muy_alta': 'Complejidad Muy Alta',
    };
    return map[complejidad] || complejidad;
}

function configurarEventosTarjetas() {
    // Los eventos se manejan mediante onclick en el HTML
}

function toggleSolucion(indice) {
    const card = document.querySelector(`.solucion-card[data-indice="${indice}"]`);
    card.classList.toggle('expanded');
}

function animateSoluciones() {
    const cards = document.querySelectorAll('.solucion-card');
    cards.forEach((card, indice) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateX(0)';
        }, indice * 100);
    });
}

// ==========================================
// Selección de Solución
// ==========================================

async function seleccionarSolucion(indice) {
    const solucion = AppState.soluciones[indice];
    const card = document.querySelector(`.solucion-card[data-indice="${indice}"]`);
    
    // Quitar selección previa
    document.querySelectorAll('.solucion-card').forEach(c => {
        c.classList.remove('selected');
        const btn = c.querySelector('.btn-seleccionar');
        btn.classList.remove('seleccionado');
        btn.innerHTML = '<i class="bi bi-check2-circle"></i> Seleccionar esta solución';
    });
    
    // Marcar como seleccionada
    card.classList.add('selected');
    const btn = card.querySelector('.btn-seleccionar');
    btn.classList.add('seleccionado');
    btn.innerHTML = '<i class="bi bi-check2"></i> Solución seleccionada';
    
    // Guardar en sesión y historial
    try {
        await fetch('/api/v1/decision', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sesion_id: AppState.sesionActual,
                problema: DOM.problemaInput.value.trim(),
                indice_seleccionado: indice,
                notas: null,
            }),
        });
        
        // Recargar sesiones y historial
        cargarSesiones();
        cargarHistorial();
        
    } catch (error) {
        console.error('Error guardando decisión:', error);
    }
}

// ==========================================
// Manejo de Errores
// ==========================================

function mostrarError() {
    DOM.contenedorRespuestas.innerHTML = `
        <div class="alert alert-error">
            <i class="bi bi-exclamation-triangle"></i>
            Error al procesar la solicitud. Por favor, intenta de nuevo.
        </div>
    `;
    DOM.respuestaContainer.classList.add('visible');
}

// ==========================================
// Historial
// ==========================================

async function cargarHistorial() {
    try {
        const respuesta = await fetch('/api/v1/historial?limite=5');
        const data = await respuesta.json();
        
        renderizarHistorial(data);
    } catch (error) {
        console.error('Error cargando historial:', error);
    }
}

function renderizarHistorial(historial) {
    if (!DOM.historialContainer) return;
    
    if (historial.length === 0) {
        DOM.historialContainer.innerHTML = `
            <p style="color: var(--text-muted); text-align: center; padding: 1rem;">
                No hay decisiones en el historial
            </p>
        `;
        return;
    }
    
    DOM.historialContainer.innerHTML = historial.map(item => `
        <div class="historial-item">
            <span class="historial-fecha">${formatearFecha(item.timestamp)}</span>
            <span class="historial-problema">${truncarTexto(item.problema, 40)}</span>
            <span class="historial-solucion">${item.solucion_seleccionada}</span>
        </div>
    `).join('');
}

function formatearFecha(isoString) {
    const fecha = new Date(isoString);
    return fecha.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function truncarTexto(texto, maxLength) {
    if (!texto) return '';
    if (texto.length <= maxLength) return texto;
    return texto.substring(0, maxLength) + '...';
}

async function limpiarHistorial() {
    if (!confirm('¿Estás seguro de que quieres limpiar el historial?')) {
        return;
    }
    
    try {
        await fetch('/api/v1/historial', {
            method: 'DELETE',
        });
        cargarHistorial();
    } catch (error) {
        console.error('Error limpiando historial:', error);
    }
}

// ==========================================
// Utilidades
// ==========================================

function mostrarLoader() {
    DOM.contenedorRespuestas.innerHTML = `
        <div class="loader-container">
            <div class="loader"></div>
            <span class="loader-text">Analizando tu problema...</span>
        </div>
    `;
    DOM.respuestaContainer.classList.add('visible');
}

// ==========================================
// Skills - Saludo y Despedida
// ==========================================

async function cargarSaludo() {
    try {
        const respuesta = await fetch('/api/v1/skills/saludo');
        const data = await respuesta.json();
        mostrarSaludo(data);
    } catch (error) {
        console.error('Error cargando saludo:', error);
    }
}

function mostrarSaludo(data) {
    if (!DOM.welcomeMessage) return;
    
    DOM.welcomeMessage.innerHTML = `
        <div class="welcome-toast">
            <div class="welcome-icon"><i class="bi bi-emoji-smile"></i></div>
            <div class="welcome-text">${data.mensaje}</div>
        </div>
    `;
    
    setTimeout(() => {
        DOM.welcomeMessage.classList.add('visible');
    }, 100);
}

async function manejarCierreSesion(e) {
    try {
        const sesionId = AppState.sesionActual;
        
        await fetch('/api/v1/skills/despedida', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sesion_id: sesionId }),
        });
    } catch (error) {
        console.error('Error en despedida:', error);
    }
}

function mostrarDespedida(data) {
    if (!DOM.welcomeMessage) return;
    
    DOM.welcomeMessage.innerHTML = `
        <div class="welcome-toast farewell">
            <div class="welcome-icon"><i class="bi bi-stars"></i></div>
            <div class="welcome-text">${data.mensaje}</div>
        </div>
    `;
    
    DOM.welcomeMessage.classList.add('visible');
}
