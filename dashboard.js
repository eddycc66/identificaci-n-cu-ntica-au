/* ===================================================================
   QUANTUM MINING OPTIMIZATION DASHBOARD - JAVASCRIPT
   Sistema de Optimización Cuántica para Explotación Minera
   =================================================================== */

// =====================================================================
// CONFIGURACIÓN GLOBAL Y VARIABLES
// =====================================================================

let map = null;
let prospectivityLayer = null;
let selectedZonesLayer = null;
let metricsData = null;

// Colores para gráficos
const CHART_COLORS = {
    quantum: '#00fff2',
    classical: '#ff6b6b',
    probability: '#a78bfa',
    cost: '#ff8c00',
    risk: '#ff4757',
    benefit: '#00ff88',
    purple: '#667eea',
    blue: '#2196F3'
};

// =====================================================================
// INICIALIZACIÓN DEL DASHBOARD
// =====================================================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Inicializando Dashboard de Optimización Cuántica...');

    // Inicializar mapa
    initializeMap();

    // Cargar datos
    loadOptimizationData();

    // Configurar event listeners
    setupEventListeners();
});

// =====================================================================
// INICIALIZACIÓN DEL MAPA (LEAFLET.JS)
// =====================================================================

function initializeMap() {
    console.log('🗺️ Inicializando mapa Leaflet...');

    // Crear mapa centrado en la región de estudio
    map = L.map('map', {
        center: [-15.25, -65.25],
        zoom: 11,
        zoomControl: true,
        attributionControl: true
    });

    // Definir capas base
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    });

    const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        maxZoom: 18
    });

    const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
        maxZoom: 17
    });

    // Agregar capa OSM por defecto
    osmLayer.addTo(map);

    // Crear control de capas base
    const baseMaps = {
        "🗺️ OpenStreetMap": osmLayer,
        "🛰️ Satélite (Esri)": satelliteLayer,
        "🏔️ Topográfico": topoLayer
    };

    // Agregar control de capas
    L.control.layers(baseMaps, null, {
        position: 'topright',
        collapsed: false
    }).addTo(map);

    console.log('✓ Mapa inicializado correctamente con selector de capas');
}

// =====================================================================
// CARGA DE DATOS DE OPTIMIZACIÓN
// =====================================================================

async function loadOptimizationData() {
    console.log('📊 Cargando datos de optimización...');

    try {
        // Intentar cargar desde archivo JSON local
        const response = await fetch('optimization_metrics.json');

        if (response.ok) {
            metricsData = await response.json();
            console.log('✓ Datos cargados desde optimization_metrics.json');
            processData(metricsData);
        } else {
            console.warn('⚠ No se encontró optimization_metrics.json');
            // Cargar datos de ejemplo para demostración
            loadDemoData();
        }

        // Cargar zonas seleccionadas (GeoJSON)
        await loadSelectedZones();

    } catch (error) {
        console.error('❌ Error al cargar datos:', error);
        // Cargar datos de ejemplo
        loadDemoData();
    }
}

// =====================================================================
// CARGA DE DATOS DE DEMOSTRACIÓN
// =====================================================================

function loadDemoData() {
    console.log('📋 Cargando datos de demostración...');

    // Datos de ejemplo para demostración
    metricsData = {
        optimization_results: {
            algorithm: 'QAOA',
            status: 'OPTIMAL',
            objective_value: -285.5,
            num_selected_zones: 5,
            selected_zone_ids: [0, 3, 7, 11, 15],
            max_drilling_sites: 5
        },
        metrics: {
            total_probability: 4.35,
            total_cost: 0.85,
            total_risk: 0.62,
            total_area_ha: 125.5,
            net_benefit: 287.5
        },
        comparison: {
            qaoa_benefit: 287.5,
            greedy_benefit: 265.3,
            improvement_percent: 8.37
        },
        zones_table: [
            { zone_id: 0, probability: 0.92, cost: 0.15, risk: 0.08, area_ha: 25.3, net_benefit: 69.0 },
            { zone_id: 1, probability: 0.78, cost: 0.22, risk: 0.18, area_ha: 18.7, net_benefit: 38.0 },
            { zone_id: 2, probability: 0.85, cost: 0.19, risk: 0.12, area_ha: 22.1, net_benefit: 54.0 },
            { zone_id: 3, probability: 0.88, cost: 0.17, risk: 0.10, area_ha: 28.5, net_benefit: 61.0 },
            { zone_id: 4, probability: 0.72, cost: 0.28, risk: 0.25, area_ha: 15.2, net_benefit: 19.0 },
            { zone_id: 5, probability: 0.81, cost: 0.20, risk: 0.14, area_ha: 20.8, net_benefit: 47.0 },
            { zone_id: 6, probability: 0.76, cost: 0.24, risk: 0.20, area_ha: 17.3, net_benefit: 32.0 },
            { zone_id: 7, probability: 0.90, cost: 0.16, risk: 0.09, area_ha: 26.7, net_benefit: 65.0 },
            { zone_id: 8, probability: 0.74, cost: 0.26, risk: 0.22, area_ha: 16.5, net_benefit: 26.0 },
            { zone_id: 9, probability: 0.79, cost: 0.21, risk: 0.16, area_ha: 19.4, net_benefit: 42.0 },
            { zone_id: 10, probability: 0.83, cost: 0.18, risk: 0.11, area_ha: 24.2, net_benefit: 54.0 },
            { zone_id: 11, probability: 0.87, cost: 0.17, risk: 0.10, area_ha: 27.1, net_benefit: 60.0 },
            { zone_id: 12, probability: 0.77, cost: 0.23, risk: 0.19, area_ha: 18.0, net_benefit: 35.0 },
            { zone_id: 13, probability: 0.80, cost: 0.21, risk: 0.15, area_ha: 21.3, net_benefit: 44.0 },
            { zone_id: 14, probability: 0.75, cost: 0.25, risk: 0.21, area_ha: 16.8, net_benefit: 29.0 },
            { zone_id: 15, probability: 0.89, cost: 0.16, risk: 0.09, area_ha: 27.8, net_benefit: 64.0 },
            { zone_id: 16, probability: 0.73, cost: 0.27, risk: 0.23, area_ha: 15.9, net_benefit: 23.0 },
            { zone_id: 17, probability: 0.82, cost: 0.19, risk: 0.13, area_ha: 23.5, net_benefit: 50.0 },
            { zone_id: 18, probability: 0.78, cost: 0.22, risk: 0.17, area_ha: 19.1, net_benefit: 39.0 },
            { zone_id: 19, probability: 0.84, cost: 0.18, risk: 0.12, area_ha: 25.0, net_benefit: 54.0 }
        ],
        selected_zones_data: [
            { zone_id: 0, probability: 0.92, cost: 0.15, risk: 0.08, area_ha: 25.3, net_benefit: 69.0 },
            { zone_id: 3, probability: 0.88, cost: 0.17, risk: 0.10, area_ha: 28.5, net_benefit: 61.0 },
            { zone_id: 7, probability: 0.90, cost: 0.16, risk: 0.09, area_ha: 26.7, net_benefit: 65.0 },
            { zone_id: 11, probability: 0.87, cost: 0.17, risk: 0.10, area_ha: 27.1, net_benefit: 60.0 },
            { zone_id: 15, probability: 0.89, cost: 0.16, risk: 0.09, area_ha: 27.8, net_benefit: 64.0 }
        ]
    };

    processData(metricsData);
}

// =====================================================================
// PROCESAMIENTO Y VISUALIZACIÓN DE DATOS
// =====================================================================

function processData(data) {
    console.log('⚙️ Procesando datos de optimización...');

    // Actualizar métricas principales
    updateMetrics(data);

    // Generar gráficos
    createComparisonChart(data);
    createMetricsChart(data);
    createZoneBenefitChart(data);

    // Poblar tabla
    populateZonesTable(data);

    // Actualizar detalles de optimización
    updateOptimizationDetails(data);

    // Ocultar overlay de carga
    setTimeout(() => {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }, 1500);

    console.log('✓ Datos procesados y visualizados correctamente');
}

// =====================================================================
// ACTUALIZACIÓN DE MÉTRICAS PRINCIPALES
// =====================================================================

function updateMetrics(data) {
    const metrics = data.metrics;
    const comparison = data.comparison;
    const optimization = data.optimization_results;

    // Beneficio neto
    document.getElementById('netBenefit').textContent = metrics.net_benefit.toFixed(2);

    // Mejora porcentual
    const improvementPercent = comparison.improvement_percent >= 0 ?
        `+${comparison.improvement_percent.toFixed(2)}%` :
        `${comparison.improvement_percent.toFixed(2)}%`;
    document.getElementById('improvement').textContent = improvementPercent;

    // Probabilidad total
    document.getElementById('totalProbability').textContent = metrics.total_probability.toFixed(3);

    // Costo total
    document.getElementById('totalCost').textContent = metrics.total_cost.toFixed(3);

    // Riesgo total
    document.getElementById('totalRisk').textContent = metrics.total_risk.toFixed(3);

    // Número de zonas
    document.getElementById('numZones').textContent = optimization.num_selected_zones;
    document.getElementById('maxZones').textContent = optimization.max_drilling_sites;
}

// =====================================================================
// GRÁFICO 1: COMPARACIÓN DE ALGORITMOS (BAR CHART)
// =====================================================================

function createComparisonChart(data) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['QAOA\n(Cuántico)', 'Greedy\n(Clásico)'],
            datasets: [{
                label: 'Beneficio Neto',
                data: [data.comparison.qaoa_benefit, data.comparison.greedy_benefit],
                backgroundColor: [
                    CHART_COLORS.quantum,
                    CHART_COLORS.classical
                ],
                borderColor: [
                    CHART_COLORS.quantum,
                    CHART_COLORS.classical
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#00fff2',
                    bodyColor: '#ffffff',
                    borderColor: '#00fff2',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// =====================================================================
// GRÁFICO 2: DISTRIBUCIÓN DE MÉTRICAS (PIE CHART)
// =====================================================================

function createMetricsChart(data) {
    const ctx = document.getElementById('metricsChart').getContext('2d');

    const metrics = data.metrics;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Probabilidad', 'Costo', 'Riesgo'],
            datasets: [{
                data: [
                    metrics.total_probability,
                    metrics.total_cost,
                    metrics.total_risk
                ],
                backgroundColor: [
                    CHART_COLORS.probability,
                    CHART_COLORS.cost,
                    CHART_COLORS.risk
                ],
                borderColor: '#0a0e27',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#00fff2',
                    bodyColor: '#ffffff',
                    borderColor: '#00fff2',
                    borderWidth: 1
                }
            }
        }
    });
}

// =====================================================================
// GRÁFICO 3: BENEFICIO POR ZONA (HORIZONTAL BAR)
// =====================================================================

function createZoneBenefitChart(data) {
    const ctx = document.getElementById('zoneChart').getContext('2d');

    const selectedZones = data.selected_zones_data;
    const labels = selectedZones.map(z => `Zona ${z.zone_id}`);
    const benefits = selectedZones.map(z => z.net_benefit);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Beneficio Neto',
                data: benefits,
                backgroundColor: CHART_COLORS.benefit,
                borderColor: CHART_COLORS.benefit,
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#00fff2',
                    bodyColor: '#ffffff',
                    borderColor: '#00fff2',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// =====================================================================
// POBLAR TABLA DE ZONAS SELECCIONADAS
// =====================================================================

function populateZonesTable(data) {
    const tbody = document.getElementById('zonesTableBody');
    tbody.innerHTML = '';

    const selectedZones = data.selected_zones_data;

    selectedZones.forEach(zone => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>Zona ${zone.zone_id}</strong></td>
            <td>${(zone.probability * 100).toFixed(1)}%</td>
            <td>${zone.cost.toFixed(3)}</td>
            <td>${zone.risk.toFixed(3)}</td>
            <td>${zone.area_ha.toFixed(2)}</td>
            <td><strong style="color: #00ff88;">${zone.net_benefit.toFixed(2)}</strong></td>
        `;
        tbody.appendChild(row);
    });
}

// =====================================================================
// ACTUALIZAR DETALLES DE OPTIMIZACIÓN
// =====================================================================

function updateOptimizationDetails(data) {
    const optimization = data.optimization_results;

    document.getElementById('optStatus').textContent = optimization.status;
    document.getElementById('numVariables').textContent = data.zones_table.length;
}

// =====================================================================
// CARGAR ZONAS SELECCIONADAS (GEOJSON)
// =====================================================================

async function loadSelectedZones() {
    try {
        const response = await fetch('selected_zones.geojson');

        if (response.ok) {
            const geojson = await response.json();
            console.log('✓ GeoJSON cargado correctamente');

            // Agregar capa de zonas seleccionadas al mapa
            selectedZonesLayer = L.geoJSON(geojson, {
                style: {
                    fillColor: '#00ff88',
                    weight: 3,
                    opacity: 1,
                    color: '#00ff88',
                    fillOpacity: 0.3
                },
                onEachFeature: function (feature, layer) {
                    // Agregar popup con información
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div style="font-family: Inter, sans-serif; color: #0a0e27;">
                                <h4 style="margin: 0 0 8px 0; color: #667eea;">Zona Seleccionada</h4>
                                <p style="margin: 4px 0;"><strong>ID:</strong> ${props.zone_id || 'N/A'}</p>
                                <p style="margin: 4px 0;"><strong>Probabilidad:</strong> ${props.probability ? (props.probability * 100).toFixed(1) + '%' : 'N/A'}</p>
                                <p style="margin: 4px 0;"><strong>Área:</strong> ${props.area_ha ? props.area_ha.toFixed(2) + ' ha' : 'N/A'}</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(map);

            // Ajustar vista del mapa a las zonas
            map.fitBounds(selectedZonesLayer.getBounds(), { padding: [50, 50] });

            // Intentar cargar el mapa de prospectividad desde prospect_map.html
            loadProspectivityLayer();

        } else {
            console.warn('⚠ No se encontró selected_zones.geojson');
            // Crear zonas de ejemplo
            createDemoZones();
        }

    } catch (error) {
        console.error('❌ Error al cargar GeoJSON:', error);
        createDemoZones();
    }
}

// =====================================================================
// CARGAR CAPA DE PROSPECTIVIDAD
// =====================================================================

function loadProspectivityLayer() {
    console.log('📊 Intentando cargar capa de prospectividad...');

    // Nota: La capa de prospectividad de Earth Engine requiere tiles específicos
    // Por ahora, agregamos un mensaje informativo

    // Si existe prospect_map.html, el usuario puede verlo separadamente
    const prospectInfo = L.control({ position: 'bottomleft' });
    prospectInfo.onAdd = function () {
        const div = L.DomUtil.create('div', 'info-box');
        div.innerHTML = `
            <div style="background: rgba(10,14,39,0.9); padding: 10px; border-radius: 8px; color: white; font-size: 0.75rem;">
                <strong>ℹ️ Mapa de Prospectividad</strong><br>
                Para ver el mapa de prospectividad completo,<br>
                abra el archivo <code>prospect_map.html</code>
            </div>
        `;
        return div;
    };
    prospectInfo.addTo(map);
}

// =====================================================================
// CREAR ZONAS DE DEMOSTRACIÓN
// =====================================================================

function createDemoZones() {
    console.log('📍 Creando zonas de demostración...');

    // Coordenadas de ejemplo alrededor del centro del mapa
    const centerLat = -15.25;
    const centerLng = -65.25;
    const offset = 0.02;

    const selectedZoneIds = metricsData.optimization_results.selected_zone_ids;

    selectedZoneIds.forEach((zoneId, index) => {
        // Crear polígono de ejemplo para cada zona
        const lat = centerLat + (Math.random() - 0.5) * offset * 3;
        const lng = centerLng + (Math.random() - 0.5) * offset * 3;
        const size = offset * 0.5;

        const polygon = L.polygon([
            [lat - size, lng - size],
            [lat - size, lng + size],
            [lat + size, lng + size],
            [lat + size, lng - size]
        ], {
            fillColor: '#00ff88',
            weight: 3,
            opacity: 1,
            color: '#00ff88',
            fillOpacity: 0.3
        }).addTo(map);

        // Agregar popup
        const zoneData = metricsData.selected_zones_data.find(z => z.zone_id === zoneId);
        if (zoneData) {
            const popupContent = `
                <div style="font-family: Inter, sans-serif; color: #0a0e27;">
                    <h4 style="margin: 0 0 8px 0; color: #667eea;">Zona ${zoneId}</h4>
                    <p style="margin: 4px 0;"><strong>Probabilidad:</strong> ${(zoneData.probability * 100).toFixed(1)}%</p>
                    <p style="margin: 4px 0;"><strong>Costo:</strong> ${zoneData.cost.toFixed(3)}</p>
                    <p style="margin: 4px 0;"><strong>Riesgo:</strong> ${zoneData.risk.toFixed(3)}</p>
                    <p style="margin: 4px 0;"><strong>Área:</strong> ${zoneData.area_ha.toFixed(2)} ha</p>
                    <p style="margin: 4px 0;"><strong>Beneficio:</strong> ${zoneData.net_benefit.toFixed(2)}</p>
                </div>
            `;
            polygon.bindPopup(popupContent);
        }
    });

    // Agregar región de estudio (rectángulo)
    const roiBounds = [
        [centerLat - offset * 2, centerLng - offset * 2],
        [centerLat + offset * 2, centerLng + offset * 2]
    ];

    L.rectangle(roiBounds, {
        color: '#00fff2',
        weight: 2,
        fillOpacity: 0,
        dashArray: '5, 10'
    }).addTo(map).bindPopup('<b>Región de Estudio</b>');

    // Ajustar vista
    map.fitBounds(roiBounds, { padding: [50, 50] });
}

// =====================================================================
// EVENT LISTENERS
// =====================================================================

function setupEventListeners() {
    // Toggle de capa de prospectividad
    document.getElementById('toggleProspect')?.addEventListener('click', function () {
        if (prospectivityLayer) {
            if (map.hasLayer(prospectivityLayer)) {
                map.removeLayer(prospectivityLayer);
                this.style.opacity = '0.5';
            } else {
                map.addLayer(prospectivityLayer);
                this.style.opacity = '1';
            }
        }
    });

    // Toggle de zonas seleccionadas
    document.getElementById('toggleZones')?.addEventListener('click', function () {
        if (selectedZonesLayer) {
            if (map.hasLayer(selectedZonesLayer)) {
                map.removeLayer(selectedZonesLayer);
                this.style.opacity = '0.5';
            } else {
                map.addLayer(selectedZonesLayer);
                this.style.opacity = '1';
            }
        }
    });

    // Exportar CSV
    document.getElementById('exportCSV')?.addEventListener('click', function () {
        exportTableToCSV('zonas_seleccionadas.csv');
    });
}

// =====================================================================
// EXPORTAR TABLA A CSV
// =====================================================================

function exportTableToCSV(filename) {
    if (!metricsData) return;

    const data = metricsData.selected_zones_data;

    // Crear contenido CSV
    let csv = 'ID Zona,Probabilidad,Costo,Riesgo,Área (ha),Beneficio Neto\n';

    data.forEach(zone => {
        csv += `${zone.zone_id},${zone.probability},${zone.cost},${zone.risk},${zone.area_ha},${zone.net_benefit}\n`;
    });

    // Crear blob y descargar
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    console.log(`✓ Tabla exportada como ${filename}`);
}

// =====================================================================
// UTILIDADES
// =====================================================================

// Formatear números
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Log de diagnóstico
console.log('✓ Dashboard JavaScript cargado correctamente');
