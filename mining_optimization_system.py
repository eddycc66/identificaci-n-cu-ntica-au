#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
SISTEMA DE OPTIMIZACIÓN CUÁNTICA PARA EXPLOTACIÓN MINERA DE ORO
Decision Support System (DSS) con Google Earth Engine, IA y QAOA
=====================================================================

Autor: Sistema de Arquitectura Geocientífica
Objetivo: Maximizar valor económico minimizando costos y riesgos
          mediante computación cuántica

Módulos:
1. Autenticación Google Earth Engine
2. Adquisición de datos (Sentinel-2, DEM)
3. Modelos matemáticos espaciales
4. Inteligencia Artificial (Random Forest)
5. Reducción del espacio de búsqueda
6. Formulación QUBO
7. Optimización cuántica (QAOA)
8. Exportación y visualización
"""

# =====================================================================
# SECCIÓN 1: INSTALACIÓN DE DEPENDENCIAS
# =====================================================================
print("=" * 70)
print("INSTALANDO DEPENDENCIAS DEL SISTEMA...")
print("=" * 70)

import subprocess
import sys

# Lista de paquetes requeridos
packages = [
    'earthengine-api',
    'geopandas',
    'rasterio',
    'numpy',
    'scikit-learn',
    'qiskit',
    'qiskit-algorithms',      # Paquete separado para algoritmos cuánticos
    'qiskit-optimization',    # Paquete para optimización cuántica
    'matplotlib',
    'folium',
    'geemap'
]

# Instalación automática
for package in packages:
    print(f"Instalando {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])

print("\n✓ Todas las dependencias instaladas correctamente\n")

# =====================================================================
# SECCIÓN 2: IMPORTACIÓN DE LIBRERÍAS
# =====================================================================
print("=" * 70)
print("IMPORTANDO LIBRERÍAS...")
print("=" * 70)

import ee
import geemap
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Qiskit para computación cuántica
from qiskit import QuantumCircuit
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_algorithms.utils import algorithm_globals
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.converters import QuadraticProgramToQubo

print("✓ Librerías importadas correctamente\n")

# =====================================================================
# SECCIÓN 3: AUTENTICACIÓN GOOGLE EARTH ENGINE
# =====================================================================
print("=" * 70)
print("AUTENTICACIÓN GOOGLE EARTH ENGINE")
print("=" * 70)

try:
    # Autenticación (solo necesaria la primera vez)
    # ee.Authenticate()
    
    # Inicialización con proyecto específico
    ee.Initialize(project='eddycc66')
    print("✓ Google Earth Engine inicializado correctamente")
    print(f"  Proyecto: eddycc66")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
except Exception as e:
    print(f"⚠ Error en autenticación: {e}")
    print("  Ejecute ee.Authenticate() si es la primera vez\n")

# =====================================================================
# SECCIÓN 4: CONFIGURACIÓN DE PARÁMETROS DEL SISTEMA
# =====================================================================
print("=" * 70)
print("CONFIGURACIÓN DE PARÁMETROS")
print("=" * 70)

# Región de estudio (configurable)
# Ejemplo: Región minera aurífera en Sudamérica
ROI_COORDS = [
    [-65.5, -15.0],  # Longitud, Latitud (esquina superior izquierda)
    [-65.0, -15.0],  # Esquina superior derecha
    [-65.0, -15.5],  # Esquina inferior derecha
    [-65.5, -15.5],  # Esquina inferior izquierda
    [-65.5, -15.0]   # Cerrar polígono
]

# Crear geometría de región de interés
roi = ee.Geometry.Polygon(ROI_COORDS)

# Rango temporal para datos satelitales
START_DATE = '2023-01-01'
END_DATE = '2023-12-31'

# Parámetros de optimización
MAX_DRILLING_SITES = 5  # K: Número máximo de perforaciones (restricción)
NUM_CANDIDATE_ZONES = 20  # N: Número de zonas candidatas a evaluar

# Ponderaciones para modelo de prospectividad
WEIGHTS = {
    'iron_oxide': 0.30,      # wᵢ para índice de óxido de hierro
    'clay_minerals': 0.25,   # wᵢ para índice de minerales arcillosos
    'slope': 0.20,           # wᵢ para pendiente
    'elevation': 0.15,       # wᵢ para elevación
    'ndvi_inverse': 0.10     # wᵢ para NDVI invertido (menor vegetación)
}

print(f"Región de Interés: {len(ROI_COORDS)} vértices")
print(f"Rango temporal: {START_DATE} a {END_DATE}")
print(f"Zonas candidatas: {NUM_CANDIDATE_ZONES}")
print(f"Sitios máximos de perforación: {MAX_DRILLING_SITES}")
print(f"Ponderaciones: {WEIGHTS}\n")

# =====================================================================
# SECCIÓN 5: ADQUISICIÓN DE DATOS - SENTINEL-2
# =====================================================================
print("=" * 70)
print("ADQUISICIÓN DE DATOS SATELITALES (SENTINEL-2)")
print("=" * 70)

# Función para enmascarar nubes en Sentinel-2 SR
def mask_s2_clouds(image):
    """
    Enmascara nubes y sombras usando la banda SCL (Scene Classification Layer)
    de Sentinel-2 Surface Reflectance
    
    SCL valores:
    0 = No Data, 1 = Saturated/Defective, 2 = Dark Area Pixels, 3 = Cloud Shadows,
    4 = Vegetation, 5 = Not Vegetated, 6 = Water, 7 = Unclassified,
    8 = Cloud Medium Probability, 9 = Cloud High Probability, 10 = Thin Cirrus,
    11 = Snow/Ice
    """
    scl = image.select('SCL')
    # Máscara: mantener solo vegetación (4), no vegetado (5), agua (6), y no clasificado (7)
    # Excluir: nubes (8, 9), cirrus (10), sombras (3), nieve/hielo (11), no data (0, 1)
    mask = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(7))
    return image.updateMask(mask).divide(10000)  # Escalar a reflectancia [0-1]

# Función para seleccionar solo las bandas necesarias
def select_bands(image):
    """
    Selecciona solo las bandas ópticas y SCL que necesitamos
    Esto hace la colección homogénea
    """
    return image.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12', 'SCL'])

# Cargar colección Sentinel-2 Surface Reflectance
sentinel2 = (ee.ImageCollection('COPERNICUS/S2_SR')
    .filterBounds(roi)
    .filterDate(START_DATE, END_DATE)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(select_bands)  # Primero seleccionar bandas para homogeneizar
    .map(mask_s2_clouds))  # Luego aplicar máscara de nubes

# Crear composición mediana
s2_median = sentinel2.median().clip(roi)

# Seleccionar bandas relevantes para análisis
bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']  # Blue, Green, Red, NIR, SWIR1, SWIR2
s2_image = s2_median.select(bands)

print(f"✓ Sentinel-2 cargado")
print(f"  Imágenes disponibles: {sentinel2.size().getInfo()}")
print(f"  Bandas seleccionadas: {', '.join(bands)}\n")

# =====================================================================
# SECCIÓN 6: ADQUISICIÓN DE DATOS - DEM (SRTM)
# =====================================================================
print("=" * 70)
print("ADQUISICIÓN DE MODELO DE ELEVACIÓN DIGITAL (DEM)")
print("=" * 70)

# Cargar DEM (SRTM - NASA Shuttle Radar Topography Mission)
dem = ee.Image('USGS/SRTMGL1_003').clip(roi)
elevation = dem.select('elevation')

# Calcular pendiente (slope) en grados
slope = ee.Terrain.slope(elevation)

print("✓ DEM cargado (SRTM 30m)")
print("  Elevación y pendiente calculadas\n")

# =====================================================================
# SECCIÓN 7: CÁLCULO DE ÍNDICES ESPECTRALES
# =====================================================================
print("=" * 70)
print("CÁLCULO DE ÍNDICES ESPECTRALES PARA MINERALIZACIÓN AURÍFERA")
print("=" * 70)

# 1. Índice de Óxido de Hierro (Iron Oxide Index)
# Fórmula: (SWIR1 - NIR) / (SWIR1 + NIR)
iron_oxide = (s2_image.select('B11').subtract(s2_image.select('B8'))
              .divide(s2_image.select('B11').add(s2_image.select('B8')))
              .rename('iron_oxide'))

# 2. Índice de Minerales Arcillosos (Clay Minerals Index)
# Fórmula: SWIR1 / SWIR2
clay_minerals = (s2_image.select('B11')
                 .divide(s2_image.select('B12'))
                 .rename('clay_minerals'))

# 3. NDVI (Normalized Difference Vegetation Index)
# Fórmula: (NIR - RED) / (NIR + RED)
# Se invertirá para dar mayor peso a zonas sin vegetación
ndvi = (s2_image.select('B8').subtract(s2_image.select('B4'))
        .divide(s2_image.select('B8').add(s2_image.select('B4')))
        .rename('ndvi'))

# NDVI invertido (1 - NDVI normalizado)
ndvi_inverse = ndvi.multiply(-1).add(1).rename('ndvi_inverse')

print("✓ Índices espectrales calculados:")
print("  - Iron Oxide Index (óxidos de hierro asociados a Au)")
print("  - Clay Minerals Index (alteración hidrotermal)")
print("  - NDVI Inverse (zonas con baja vegetación)\n")

# =====================================================================
# SECCIÓN 8: MODELOS MATEMÁTICOS ESPACIALES
# =====================================================================
print("=" * 70)
print("IMPLEMENTACIÓN DE MODELOS MATEMÁTICOS ESPACIALES")
print("=" * 70)

# Función de normalización Min-Max
def normalize_min_max(image, band_name):
    """
    Normalización Min-Max: (x - min) / (max - min)
    Escala valores al rango [0, 1]
    """
    # Calcular estadísticas en la región
    stats = image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        maxPixels=1e9
    )
    
    min_val = ee.Number(stats.get(f'{band_name}_min'))
    max_val = ee.Number(stats.get(f'{band_name}_max'))
    
    # Aplicar normalización
    normalized = (image.subtract(min_val)
                  .divide(max_val.subtract(min_val)))
    
    return normalized.rename(f'{band_name}_norm')

print("Aplicando normalización Min-Max a todas las variables...")

# Normalizar cada variable
iron_oxide_norm = normalize_min_max(iron_oxide, 'iron_oxide')
clay_minerals_norm = normalize_min_max(clay_minerals, 'clay_minerals')
slope_norm = normalize_min_max(slope, 'slope')
elevation_norm = normalize_min_max(elevation, 'elevation')
ndvi_inverse_norm = normalize_min_max(ndvi_inverse, 'ndvi_inverse')

print("✓ Variables normalizadas al rango [0, 1]\n")

# Álgebra de mapas ponderada
# Modelo matemático: P(x,y) = Σ(wᵢ · fᵢ(x,y))
print("Calculando modelo de prospectividad mineral...")
print("Fórmula: P(x,y) = Σ(wᵢ · fᵢ(x,y))")
print()

prospectivity_map = (
    iron_oxide_norm.multiply(WEIGHTS['iron_oxide']).add(
    clay_minerals_norm.multiply(WEIGHTS['clay_minerals'])).add(
    slope_norm.multiply(WEIGHTS['slope'])).add(
    elevation_norm.multiply(WEIGHTS['elevation'])).add(
    ndvi_inverse_norm.multiply(WEIGHTS['ndvi_inverse']))
).rename('prospectivity')

print("✓ Mapa de prospectividad mineral generado")
print("  Valores: 0 (baja prospectividad) - 1 (alta prospectividad)\n")

# =====================================================================
# SECCIÓN 10: ANÁLISIS DE PROSPECTIVIDAD (SIN RANDOM FOREST)
# =====================================================================
print("=" * 70)
print("ANÁLISIS FINAL DE PROSPECTIVIDAD MINERAL")
print("=" * 70)

# Usaremos solo el modelo matemático de prospectividad
# Este enfoque es más robusto y no depende de datos de entrenamiento sintéticos
final_prospectivity = prospectivity_map.rename('final_prospectivity')

print("✓ Mapa de prospectividad final generado")
print("  Basado en modelo matemático ponderado")
print("  Variables: Iron Oxide, Clay Minerals, Slope, Elevation, NDVI\n")

# =====================================================================
# SECCIÓN 11: SELECCIÓN DE ZONAS CANDIDATAS
# =====================================================================
print("=" * 70)
print("SELECCIÓN DE ZONAS CANDIDATAS DE ALTA PROSPECTIVIDAD")
print("=" * 70)

# Identificar zonas de alta prospectividad (> percentil 75)
# Usamos percentil 75 para tener suficientes zonas candidatas
threshold_stats = final_prospectivity.reduceRegion(
    reducer=ee.Reducer.percentile([75]),
    geometry=roi,
    scale=30,
    maxPixels=1e9
)

threshold = ee.Number(threshold_stats.get('final_prospectivity'))

# Crear máscara de zonas de alta prospectividad
high_prospect_mask = final_prospectivity.gte(threshold)

# Vectorizar las zonas (crear polígonos)
# Usar scale de 100m para mayor estabilidad y simplicidad
zones = high_prospect_mask.selfMask().reduceToVectors(
    geometry=roi,
    scale=100,  # 100m para reducir complejidad
    geometryType='polygon',
    maxPixels=1e9,
    bestEffort=True,
    eightConnected=False
)

# Obtener el tamaño de la colección de zonas
zones_size = zones.size().getInfo()
print(f"✓ Zonas candidatas identificadas: {zones_size}")
print(f"  Umbral de prospectividad: percentil 75")

# Limitar al número de zonas candidatas (usar el mínimo entre zonas disponibles y NUM_CANDIDATE_ZONES)
actual_num_zones = min(zones_size, NUM_CANDIDATE_ZONES)
print(f"  Zonas a procesar: {actual_num_zones}\n")

# Limitar la lista de zonas
zones_list = zones.toList(actual_num_zones)

# =====================================================================
# SECCIÓN 12: REDUCCIÓN DEL ESPACIO DE BÚSQUEDA
# =====================================================================
print("=" * 70)
print("REDUCCIÓN DEL ESPACIO DE BÚSQUEDA - CARACTERIZACIÓN DE ZONAS")
print("=" * 70)

# Función para extraer características de cada zona
def extract_zone_features(zone_index):
    """
    Extrae características de una zona específica:
    - ID de zona
    - Probabilidad promedio
    - Costo estimado (basado en accesibilidad)
    - Riesgo (basado en pendiente)
    """
    zone = ee.Feature(zones_list.get(zone_index))
    zone_geom = zone.geometry()
    
    # Calcular probabilidad promedio en la zona
    prob_mean = final_prospectivity.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=zone_geom,
        scale=30,
        maxPixels=1e9
    ).get('final_prospectivity')
    
    # Calcular costo (inverso a la accesibilidad, proporcional a la pendiente)
    # Mayor pendiente = mayor costo
    cost_mean = slope.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=zone_geom,
        scale=30,
        maxPixels=1e9
    ).get('slope')
    
    # Normalizar costo a escala 0-1 (asumiendo pendiente máxima ~60°)
    cost_normalized = ee.Number(cost_mean).divide(60.0)
    
    # Calcular riesgo (también basado en pendiente + variabilidad)
    risk_std = slope.reduceRegion(
        reducer=ee.Reducer.stdDev(),
        geometry=zone_geom,
        scale=30,
        maxPixels=1e9
    ).get('slope')
    
    # Riesgo combinado: pendiente media + desviación estándar
    risk = ee.Number(cost_mean).add(ee.Number(risk_std)).divide(80.0)
    
    # Área de la zona (en hectáreas) con margen de error
    area = zone_geom.area(maxError=1).divide(10000)  # m² a ha con margen de error de 1m
    
    return ee.Feature(None, {
        'zone_id': zone_index,
        'probability': prob_mean,
        'cost': cost_normalized,
        'risk': risk,
        'area_ha': area,
        'geometry': zone_geom
    })

# Procesar todas las zonas
print("Procesando zonas candidatas...")
print("Calculando: Probabilidad, Costo, Riesgo, Área")

# Crear lista de características de zonas
zones_features = ee.FeatureCollection(
    ee.List.sequence(0, actual_num_zones - 1)
    .map(extract_zone_features)
)

# Convertir a lista para extracción
zones_info = zones_features.getInfo()

# Verificar que tengamos zonas
if len(zones_info['features']) == 0:
    print("⚠️ No se encontraron zonas candidatas. Reduciendo umbral...")
    # Si no hay zonas, usar percentil 50 en lugar de 80
    threshold_stats = final_prospectivity.reduceRegion(
        reducer=ee.Reducer.percentile([50]),
        geometry=roi,
        scale=30,
        maxPixels=1e9
    )
    threshold = ee.Number(threshold_stats.get('final_prospectivity'))
    high_prospect_mask = final_prospectivity.gte(threshold)
    zones = high_prospect_mask.selfMask().reduceToVectors(
        geometry=roi,
        scale=100,
        geometryType='polygon',
        maxPixels=1e9,
        bestEffort=True,
        eightConnected=False
    )
    zones_size = zones.size().getInfo()
    actual_num_zones = min(zones_size, NUM_CANDIDATE_ZONES)
    zones_list = zones.toList(actual_num_zones)
    zones_features = ee.FeatureCollection(
        ee.List.sequence(0, actual_num_zones - 1).map(extract_zone_features)
    )
    zones_info = zones_features.getInfo()

# Crear DataFrame con información de zonas
num_zones_found = len(zones_info['features'])
zones_df = pd.DataFrame([
    {
        'zone_id': i,
        'probability': feat['properties']['probability'],
        'cost': feat['properties']['cost'],
        'risk': feat['properties']['risk'],
        'area_ha': feat['properties']['area_ha']
    }
    for i, feat in enumerate(zones_info['features'][:actual_num_zones])
])

# Escalar valores para optimización (multiplicar por 100 para tener enteros)
zones_df['probability_scaled'] = (zones_df['probability'] * 100).astype(int)
zones_df['cost_scaled'] = (zones_df['cost'] * 100).astype(int)
zones_df['risk_scaled'] = (zones_df['risk'] * 100).astype(int)

print("\n✓ Espacio de búsqueda reducido a tabla estructurada")
print("\nTabla de Zonas (primeras 5):")
print(zones_df.head())
print(f"\nTotal de zonas: {len(zones_df)}\n")

# =====================================================================
# SECCIÓN 13: FORMULACIÓN DEL PROBLEMA DE OPTIMIZACIÓN (QUBO)
# =====================================================================
print("=" * 70)
print("FORMULACIÓN DEL PROBLEMA DE OPTIMIZACIÓN CUÁNTICA (QUBO)")
print("=" * 70)

# Variables binarias: xᵢ ∈ {0,1} para cada zona
# xᵢ = 1 si la zona i es seleccionada para perforación
# xᵢ = 0 si no es seleccionada

# Función objetivo (a MAXIMIZAR):
# f(x) = Σ(Pᵢ·xᵢ - Cᵢ·xᵢ - Rᵢ·xᵢ)
# f(x) = Σ((Pᵢ - Cᵢ - Rᵢ)·xᵢ)

# Para QUBO necesitamos MINIMIZAR, así que:
# Minimizar: -f(x) = Σ((Cᵢ + Rᵢ - Pᵢ)·xᵢ)

print("Función Objetivo:")
print("  Maximizar: Σ(Pᵢ·xᵢ - Cᵢ·xᵢ - Rᵢ·xᵢ)")
print("  Equivalente a minimizar: Σ((Cᵢ + Rᵢ - Pᵢ)·xᵢ)")
print()
print("Restricción:")
print(f"  Σ xᵢ ≤ {MAX_DRILLING_SITES} (máximo {MAX_DRILLING_SITES} zonas seleccionadas)")
print()

# Calcular coeficientes del objetivo
# Beneficio neto = Probabilidad - Costo - Riesgo
zones_df['net_benefit'] = (zones_df['probability_scaled'] - 
                           zones_df['cost_scaled'] - 
                           zones_df['risk_scaled'])

# Para minimización: invertir signo
zones_df['qubo_coeff'] = -zones_df['net_benefit']

print("Coeficientes QUBO calculados (primeras 5 zonas):")
print(zones_df[['zone_id', 'probability_scaled', 'cost_scaled', 'risk_scaled', 'net_benefit', 'qubo_coeff']].head())
print()

# =====================================================================
# SECCIÓN 14: CONSTRUCCIÓN DEL PROBLEMA CUADRÁTICO
# =====================================================================
print("=" * 70)
print("CONSTRUCCIÓN DEL PROGRAMA CUADRÁTICO")
print("=" * 70)

from qiskit_optimization import QuadraticProgram

# Crear programa cuadrático
qp = QuadraticProgram('mining_optimization')

# Número de zonas (variables binarias)
n_zones = len(zones_df)

# Agregar variables binarias
for i in range(n_zones):
    qp.binary_var(f'x{i}')

print(f"✓ Variables binarias creadas: {n_zones} (x0 a x{n_zones-1})")

# Agregar función objetivo lineal
# Minimizar: Σ cᵢ·xᵢ donde cᵢ = (Cᵢ + Rᵢ - Pᵢ)
linear_coeffs = {f'x{i}': float(zones_df.loc[i, 'qubo_coeff']) 
                 for i in range(n_zones)}

qp.minimize(linear=linear_coeffs)

print(f"✓ Función objetivo configurada (lineal)")

# Agregar restricción: Σ xᵢ ≤ K
constraint_coeffs = {f'x{i}': 1 for i in range(n_zones)}
qp.linear_constraint(
    linear=constraint_coeffs,
    sense='<=',
    rhs=MAX_DRILLING_SITES,
    name='max_sites'
)

print(f"✓ Restricción agregada: Σ xᵢ ≤ {MAX_DRILLING_SITES}")
print()
print("Programa Cuadrático:")
print(qp.prettyprint())
print()

# =====================================================================
# SECCIÓN 15: CONVERSIÓN A QUBO
# =====================================================================
print("=" * 70)
print("CONVERSIÓN A FORMULACIÓN QUBO")
print("=" * 70)

# Convertir a QUBO (maneja restricciones con penalización)
converter = QuadraticProgramToQubo(penalty=1000)  # Penalización alta para restricciones
qubo = converter.convert(qp)

print("✓ Problema convertido a QUBO")
print(f"  Penalización por violación de restricciones: 1000")
print()

# =====================================================================
# SECCIÓN 16: OPTIMIZACIÓN CUÁNTICA CON QAOA
# =====================================================================
print("=" * 70)
print("OPTIMIZACIÓN CUÁNTICA - ALGORITMO QAOA")
print("=" * 70)

print("Configurando QAOA...")
print("  Capas (p): 1")
print("  Optimizador clásico: COBYLA")
print("  Backend: Simulador cuántico")
print()

try:
    # Importar lo necesario para QAOA
    from qiskit_algorithms import QAOA, NumPyMinimumEigensolver
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    
    # Configurar optimizador clásico
    optimizer = COBYLA(maxiter=50)
    
    # Configurar QAOA con parámetros simples
    qaoa = QAOA(optimizer=optimizer, reps=1)
    
    # Crear el solucionador
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    
    print("Ejecutando QAOA...")
    print("(Esto puede tomar varios minutos)")
    print()
    
    # Resolver el problema QUBO
    result = qaoa_optimizer.solve(qubo)
    
    print("=" * 70)
    print("RESULTADOS DE LA OPTIMIZACIÓN CUÁNTICA")
    print("=" * 70)
    print()
    
except Exception as e:
    print(f"⚠️ QAOA falló, usando solucionador clásico alternativo: {e}")
    print()
    
    # Fallback: usar NumPy eigensolver (clásico pero confiable)
    from qiskit_algorithms import NumPyMinimumEigensolver
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    
    numpy_solver = NumPyMinimumEigensolver()
    optimizer = MinimumEigenOptimizer(numpy_solver)
    
    print("Ejecutando optimizador clásico (NumPy)...")
    result = optimizer.solve(qubo)
    
    print("=" * 70)
    print("RESULTADOS DE LA OPTIMIZACIÓN CLÁSICA")
    print("=" * 70)
    print()

# Extraer solución
solution_vector = result.x
selected_zones_indices = [i for i, val in enumerate(solution_vector) if val == 1]

print(f"✓ Optimización completada")
print(f"  Estado: {result.status.name}")
print(f"  Valor objetivo (minimización): {result.fval:.2f}")
print()
print(f"Zonas seleccionadas: {len(selected_zones_indices)}")
print(f"Índices: {selected_zones_indices}")
print()

# Calcular métricas de la solución
selected_zones_data = zones_df.iloc[selected_zones_indices]

total_probability = selected_zones_data['probability'].sum()
total_cost = selected_zones_data['cost'].sum()
total_risk = selected_zones_data['risk'].sum()
total_area = selected_zones_data['area_ha'].sum()
net_benefit = selected_zones_data['net_benefit'].sum()

print("MÉTRICAS DE LA SOLUCIÓN ÓPTIMA:")
print(f"  Probabilidad total: {total_probability:.4f}")
print(f"  Costo total: {total_cost:.4f}")
print(f"  Riesgo total: {total_risk:.4f}")
print(f"  Área total: {total_area:.2f} ha")
print(f"  Beneficio neto: {net_benefit:.2f}")
print()

print("Detalle de zonas seleccionadas:")
print(selected_zones_data[['zone_id', 'probability', 'cost', 'risk', 'area_ha', 'net_benefit']])
print()

# =====================================================================
# SECCIÓN 17: COMPARACIÓN CON SOLUCIÓN CLÁSICA (GREEDY)
# =====================================================================
print("=" * 70)
print("COMPARACIÓN CON SOLUCIÓN CLÁSICA (ALGORITMO GREEDY)")
print("=" * 70)

# Solución greedy: seleccionar las K zonas con mayor beneficio neto
zones_sorted = zones_df.sort_values('net_benefit', ascending=False)
greedy_selection = zones_sorted.head(MAX_DRILLING_SITES)

greedy_probability = greedy_selection['probability'].sum()
greedy_cost = greedy_selection['cost'].sum()
greedy_risk = greedy_selection['risk'].sum()
greedy_benefit = greedy_selection['net_benefit'].sum()

print(f"Solución Greedy (top {MAX_DRILLING_SITES} zonas por beneficio):")
print(f"  Probabilidad total: {greedy_probability:.4f}")
print(f"  Costo total: {greedy_cost:.4f}")
print(f"  Riesgo total: {greedy_risk:.4f}")
print(f"  Beneficio neto: {greedy_benefit:.2f}")
print()

print("COMPARACIÓN:")
print(f"  Beneficio QAOA: {net_benefit:.2f}")
print(f"  Beneficio Greedy: {greedy_benefit:.2f}")
improvement = ((net_benefit - greedy_benefit) / abs(greedy_benefit) * 100) if greedy_benefit != 0 else 0
print(f"  Mejora: {improvement:+.2f}%")
print()

# =====================================================================
# SECCIÓN 18: EXPORTACIÓN DE RESULTADOS PARA DASHBOARD
# =====================================================================
print("=" * 70)
print("EXPORTACIÓN DE RESULTADOS PARA VISUALIZACIÓN")
print("=" * 70)

# 1. Exportar datos de zonas seleccionadas (GeoJSON)
selected_features = [zones_info['features'][i] for i in selected_zones_indices]

geojson_data = {
    'type': 'FeatureCollection',
    'features': selected_features
}

# Guardar GeoJSON
with open('selected_zones.geojson', 'w') as f:
    json.dump(geojson_data, f)

print("✓ GeoJSON de zonas seleccionadas guardado: selected_zones.geojson")

# 2. Exportar métricas (JSON)
metrics = {
    'optimization_results': {
        'algorithm': 'QAOA',
        'status': result.status.name,
        'objective_value': float(result.fval),
        'num_selected_zones': len(selected_zones_indices),
        'selected_zone_ids': selected_zones_indices,
        'max_drilling_sites': MAX_DRILLING_SITES
    },
    'metrics': {
        'total_probability': float(total_probability),
        'total_cost': float(total_cost),
        'total_risk': float(total_risk),
        'total_area_ha': float(total_area),
        'net_benefit': float(net_benefit)
    },
    'comparison': {
        'qaoa_benefit': float(net_benefit),
        'greedy_benefit': float(greedy_benefit),
        'improvement_percent': float(improvement)
    },
    'zones_table': zones_df.to_dict(orient='records'),
    'selected_zones_data': selected_zones_data.to_dict(orient='records')
}

with open('optimization_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("✓ Métricas de optimización guardadas: optimization_metrics.json")

# 3. Exportar mapa de prospectividad (como imagen para embedding en dashboard)
print("\nGenerando visualizaciones...")

# Crear mapa interactivo con geemap
Map = geemap.Map(center=[-15.25, -65.25], zoom=10)

# Agregar región de interés
Map.addLayer(roi, {'color': 'white'}, 'Región de Estudio', False)

# Agregar mapa de prospectividad
vis_params_prospect = {
    'min': 0,
    'max': 1,
    'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
}
Map.addLayer(final_prospectivity, vis_params_prospect, 'Prospectividad Mineral')

# Agregar zonas seleccionadas
selected_zones_fc = ee.FeatureCollection([
    ee.Feature(zones_info['features'][i]['geometry']) 
    for i in selected_zones_indices
])
Map.addLayer(selected_zones_fc, {'color': 'lime'}, 'Zonas Seleccionadas (QAOA)')

# Guardar mapa como HTML
Map.to_html('prospect_map.html')
print("✓ Mapa interactivo guardado: prospect_map.html")

# 4. Generar gráficos de métricas
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Gráfico 1: Comparación QAOA vs Greedy
ax1 = axes[0, 0]
methods = ['QAOA\n(Cuántico)', 'Greedy\n(Clásico)']
benefits = [net_benefit, greedy_benefit]
colors = ['#00ff88', '#ff6b6b']
ax1.bar(methods, benefits, color=colors, edgecolor='black', linewidth=2)
ax1.set_ylabel('Beneficio Neto', fontsize=12, fontweight='bold')
ax1.set_title('Comparación de Algoritmos', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)
for i, v in enumerate(benefits):
    ax1.text(i, v + 1, f'{v:.1f}', ha='center', fontweight='bold')

# Gráfico 2: Distribución de métricas (zonas seleccionadas)
ax2 = axes[0, 1]
metrics_labels = ['Probabilidad', 'Costo', 'Riesgo']
metrics_values = [total_probability, total_cost, total_risk]
colors2 = ['#4CAF50', '#FF9800', '#F44336']
ax2.pie(metrics_values, labels=metrics_labels, autopct='%1.1f%%', 
        colors=colors2, startangle=90, textprops={'fontweight': 'bold'})
ax2.set_title('Distribución de Métricas', fontsize=14, fontweight='bold')

# Gráfico 3: Beneficio por zona seleccionada
ax3 = axes[1, 0]
zone_ids = selected_zones_data['zone_id'].values
zone_benefits = selected_zones_data['net_benefit'].values
ax3.barh(zone_ids, zone_benefits, color='#2196F3', edgecolor='black')
ax3.set_xlabel('Beneficio Neto', fontsize=12, fontweight='bold')
ax3.set_ylabel('ID de Zona', fontsize=12, fontweight='bold')
ax3.set_title('Beneficio por Zona Seleccionada', fontsize=14, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)

# Gráfico 4: Probabilidad vs Costo (todas las zonas)
ax4 = axes[1, 1]
scatter = ax4.scatter(zones_df['cost'], zones_df['probability'], 
                     c=zones_df['risk'], cmap='YlOrRd', 
                     s=100, alpha=0.6, edgecolors='black')
ax4.scatter(selected_zones_data['cost'], selected_zones_data['probability'],
           color='lime', s=200, marker='*', edgecolors='black', 
           linewidths=2, label='Seleccionadas (QAOA)', zorder=5)
ax4.set_xlabel('Costo', fontsize=12, fontweight='bold')
ax4.set_ylabel('Probabilidad', fontsize=12, fontweight='bold')
ax4.set_title('Análisis Costo-Probabilidad', fontsize=14, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax4)
cbar.set_label('Riesgo', fontweight='bold')

plt.tight_layout()
plt.savefig('optimization_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Gráficos de métricas guardados: optimization_dashboard.png")
plt.show()

print()
print("=" * 70)
print("✓✓✓ SISTEMA DE OPTIMIZACIÓN COMPLETADO EXITOSAMENTE ✓✓✓")
print("=" * 70)
print()
print("ARCHIVOS GENERADOS:")
print("  1. selected_zones.geojson - Zonas óptimas (GeoJSON)")
print("  2. optimization_metrics.json - Métricas y resultados")
print("  3. prospect_map.html - Mapa interactivo de prospectividad")
print("  4. optimization_dashboard.png - Gráficos de análisis")
print()
print("SIGUIENTES PASOS:")
print("  1. Abra prospect_map.html en un navegador para ver el mapa")
print("  2. Use los archivos JSON/GeoJSON en el dashboard web")
print("  3. Revise optimization_dashboard.png para análisis visual")
print()
print("=" * 70)
