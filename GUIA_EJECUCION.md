# GUÍA DE EJECUCIÓN - Sistema de Optimización Cuántica Minera

## 📋 Tabla de Contenidos
1. [Pre-requisitos](#pre-requisitos)
2. [Configuración de Google Earth Engine](#configuración-de-google-earth-engine)
3. [Ejecución del Código Python (Google Colab)](#ejecución-del-código-python)
4. [Configuración del Dashboard Web](#configuración-del-dashboard-web)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Troubleshooting](#troubleshooting)

---

## 📌 Pre-requisitos

### Cuentas Necesarias
- **Cuenta Google**: Para acceso a Google Colab y Google Earth Engine
- **Proyecto Google Earth Engine**: ID `eddycc66` (o crear uno nuevo)

### Conocimientos Recomendados
- Python básico
- Conceptos de optimización
- Fundamentos de GIS (opcional pero útil)

### Navegadores Compatibles
- Google Chrome (recomendado)
- Firefox
- Microsoft Edge

---

## 🌍 Configuración de Google Earth Engine

### Paso 1: Registro en Earth Engine

1. Visite: https://earthengine.google.com/
2. Haga clic en "Sign Up"
3. Complete el formulario con su información
4. Seleccione el tipo de uso: **Investigación/Educación**
5. Espere la aprobación (usualmente 1-2 días)

### Paso 2: Verificar Acceso

1. Vaya a: https://code.earthengine.google.com/
2. Debería ver la interfaz de Earth Engine Code Editor
3. Confirme que puede ejecutar código de prueba

### Paso 3: Configurar Proyecto

Si necesita crear un nuevo proyecto:

1. Vaya a: https://console.cloud.google.com/
2. Seleccione "Nuevo Proyecto"
3. Nombre el proyecto (ej: `mining-optimization`)
4. Anote el ID del proyecto
5. Actualice el código Python en la línea de inicialización:
   ```python
   ee.Initialize(project='SU-PROYECTO-ID')
   ```

---

## 🐍 Ejecución del Código Python (Google Colab)

### Paso 1: Abrir Google Colab

1. Visite: https://colab.research.google.com/
2. Inicie sesión con su cuenta Google

### Paso 2: Cargar el Script Python

**Opción A: Desde archivo local**
1. Haga clic en "Archivo" → "Cargar notebook"
2. Seleccione `mining_optimization_system.py`
3. El notebook se abrirá automáticamente

**Opción B: Crear notebook nuevo**
1. Haga clic en "Archivo" → "Nuevo notebook"
2. Copie y pegue todo el contenido de `mining_optimization_system.py`
3. Guarde el notebook

### Paso 3: Autenticación de Earth Engine (Primera vez)

Si es la primera vez que usa Earth Engine en Colab:

1. Descomente la línea:
   ```python
   ee.Authenticate()
   ```
2. Ejecute solo esa celda
3. Siga el enlace que aparece
4. Seleccione su cuenta Google
5. Copie el código de autorización
6. Péguelo en el campo correspondiente
7. Presione Enter
8. **Importante**: Vuelva a comentar la línea después de autenticar:
   ```python
   # ee.Authenticate()  # Solo necesario la primera vez
   ```

### Paso 4: Configurar Parámetros del Sistema

Antes de ejecutar, revise y configure estos parámetros (sección 4 del código):

```python
# Región de estudio - MODIFIQUE ESTAS COORDENADAS
ROI_COORDS = [
    [-65.5, -15.0],  # Longitud, Latitud (esquina superior izquierda)
    [-65.0, -15.0],  # Esquina superior derecha
    [-65.0, -15.5],  # Esquina inferior derecha
    [-65.5, -15.5],  # Esquina inferior izquierda
    [-65.5, -15.0]   # Cerrar polígono
]

# Rango temporal - AJUSTE SEGÚN SUS NECESIDADES
START_DATE = '2023-01-01'
END_DATE = '2023-12-31'

# Parámetros de optimización
MAX_DRILLING_SITES = 5  # Número máximo de perforaciones
NUM_CANDIDATE_ZONES = 20  # Zonas candidatas a evaluar
```

**Cómo obtener coordenadas de su región:**
1. Vaya a: https://www.google.com/maps
2. Haga clic derecho en el mapa
3. Seleccione las coordenadas que aparecen (se copian al portapapeles)
4. Formato: Latitud, Longitud
5. Defina las 4 esquinas de su región de interés

### Paso 5: Ejecutar el Sistema Completo

**Opción A: Ejecución completa (recomendado para primera vez)**
1. Haga clic en "Entorno de ejecución" → "Ejecutar todas"
2. Espere a que se completen todas las secciones (15-30 minutos)
3. Observe los mensajes de progreso

**Opción B: Ejecución por secciones**
1. Ejecute cada sección secuencialmente con `Shift + Enter`
2. Espere a que cada sección termine antes de continuar
3. Útil para debugging o ajustes

### Paso 6: Monitorear la Ejecución

Durante la ejecución verá:
- ✓ Checkmarks verdes: Sección completada
- ⚠️ Warnings amarillos: Advertencias (no críticas)
- ❌ Errores rojos: Problemas que requieren atención

**Tiempos aproximados por sección:**
- Sección 1-3: 2-5 minutos (instalación)
- Sección 4-7: 5-10 minutos (adquisición de datos)
- Sección 8-14: 5-10 minutos (modelos y IA)
- Sección 15-17: 10-15 minutos (optimización cuántica)
- Sección 18: 2-5 minutos (exportación)

### Paso 7: Descargar Resultados

Al finalizar, el sistema generará 4 archivos:

1. **selected_zones.geojson**: Zonas óptimas seleccionadas
2. **optimization_metrics.json**: Métricas y resultados
3. **prospect_map.html**: Mapa interactivo de prospectividad
4. **optimization_dashboard.png**: Gráficos de análisis

**Para descargar:**
1. En el panel izquierdo de Colab, haga clic en 📁 (Archivos)
2. Verá los archivos generados
3. Haga clic derecho en cada archivo → "Descargar"
4. Guarde todos los archivos en la misma carpeta del dashboard

**Ubicación recomendada:**
```
modelo matematico cuantico/
├── mining_optimization_system.py
├── dashboard.html
├── dashboard.css
├── dashboard.js
├── selected_zones.geojson          ← Descargado
├── optimization_metrics.json        ← Descargado
├── prospect_map.html                ← Descargado
└── optimization_dashboard.png       ← Descargado
```

---

## 🌐 Configuración del Dashboard Web

### Paso 1: Verificar Archivos

Asegúrese de tener todos estos archivos en la misma carpeta:
- ✅ `dashboard.html`
- ✅ `dashboard.css`
- ✅ `dashboard.js`
- ✅ `selected_zones.geojson` (descargado de Colab)
- ✅ `optimization_metrics.json` (descargado de Colab)

### Paso 2: Abrir el Dashboard

**Método Simple:**
1. Navegue a la carpeta con los archivos
2. Haga doble clic en `dashboard.html`
3. El dashboard se abrirá en su navegador predeterminado

**Método Alternativo (servidor local - recomendado):**

Si el dashboard no carga los datos correctamente debido a restricciones CORS:

**Opción A: Usar Python Simple HTTP Server**
```bash
# Abra PowerShell o CMD en la carpeta del proyecto
cd "d:\DOCENCIA UNIVERSITARIA\Siglo XX\Módulo 11\modelo matematico cuantico"

# Python 3
python -m http.server 8000

# Abra el navegador en: http://localhost:8000/dashboard.html
```

**Opción B: Usar extensión de VSCode**
1. Instale "Live Server" en Visual Studio Code
2. Abra la carpeta del proyecto en VSCode
3. Haga clic derecho en `dashboard.html` → "Open with Live Server"

### Paso 3: Verificar Carga de Datos

El dashboard mostrará:
1. **Overlay de carga**: Aparece inicialmente mientras carga datos
2. **Métricas principales**: 5 tarjetas en la parte superior
3. **Mapa interactivo**: Debe mostrar zonas seleccionadas
4. **Gráficos**: 3 visualizaciones (comparación, distribución, beneficio)
5. **Tabla**: Lista de zonas seleccionadas

**Si los datos no cargan:**
- Verifique que los archivos JSON/GeoJSON estén en la carpeta correcta
- Abra la consola del navegador (F12) y busque errores
- El sistema usará datos de demostración si no encuentra los archivos reales

---

## 📊 Interpretación de Resultados

### Métricas Principales

**1. Beneficio Neto**
- Valor optimizado que combina probabilidad, costo y riesgo
- Valor más alto = mejor selección
- Compare con el algoritmo greedy para ver la mejora

**2. Probabilidad Total**
- Suma de probabilidades de mineralización de zonas seleccionadas
- Rango: 0-1 (valores más altos indican mayor prospectividad)

**3. Costo Total**
- Costo acumulado de explotar las zonas seleccionadas
- Basado en accesibilidad (pendiente del terreno)
- Valores más bajos son preferibles

**4. Riesgo Agregado**
- Riesgo total de las operaciones en zonas seleccionadas
- Considera pendiente y variabilidad del terreno
- Valores más bajos indican menor riesgo

**5. Zonas Seleccionadas**
- Número de sitios de perforación óptimos
- No excederá el límite MAX_DRILLING_SITES

### Gráficos

**Comparación de Algoritmos**
- Compara QAOA (cuántico) vs Greedy (clásico)
- Muestra el beneficio neto de cada enfoque
- Porcentaje de mejora del algoritmo cuántico

**Distribución de Métricas**
- Pie chart que muestra la proporción de probabilidad, costo y riesgo
- Útil para entender el balance de la solución

**Beneficio por Zona**
- Desglosa la contribución de cada zona seleccionada
- Identifica las zonas más valiosas

### Mapa Interactivo

**Elementos del Mapa:**
- **Zonas verdes (★)**: Zonas seleccionadas por QAOA
- **Polígono cyan**: Región de estudio
- **Capas adicionales**: Prospectividad mineral (si disponible)

**Interacción:**
- **Zoom**: Rueda del mouse o controles +/-
- **Pan**: Arrastrar con el mouse
- **Popup**: Click en una zona para ver detalles
- **Capas**: Botones superiores para mostrar/ocultar

### Detalles de Optimización Cuántica

**Estado del Algoritmo**
- `OPTIMAL`: Solución óptima encontrada ✓
- `FEASIBLE`: Solución válida pero no necesariamente óptima
- `INFEASIBLE`: No se encontró solución (revisar restricciones)

**Variables QUBO**
- Número de variables binarias en el problema
- Igual al número de zonas candidatas

**Capas QAOA**
- Profundidad del circuito cuántico variacional
- Más capas = potencialmente mejor solución (pero más lento)

---

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Autenticación Google Earth Engine

**Síntoma:**
```
Error: Please authorize access to your Earth Engine account
```

**Solución:**
1. Descomente `ee.Authenticate()` en el código
2. Ejecute solo esa celda
3. Complete el proceso de autenticación
4. Vuelva a comentar la línea
5. Ejecute `ee.Initialize(project='eddycc66')`

#### 2. Error: "No images found in collection"

**Síntoma:**
```
Imágenes disponibles: 0
```

**Causas posibles:**
- Región fuera de cobertura Sentinel-2
- Rango de fechas sin datos
- Filtro de nubes demasiado estricto

**Solución:**
1. Verifique las coordenadas de ROI_COORDS
2. Amplíe el rango de fechas
3. Aumente CLOUDY_PIXEL_PERCENTAGE a 30-50%:
   ```python
   .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50))
   ```

#### 3. Error de Memoria en Earth Engine

**Síntoma:**
```
Error: User memory limit exceeded
```

**Solución:**
1. Reduzca el tamaño de la región de estudio
2. Disminuya NUM_CANDIDATE_ZONES
3. Use una escala espacial mayor (ej: scale=60 en lugar de 30)

#### 4. QAOA No Converge

**Síntoma:**
```
Status: INFEASIBLE
```

**Solución:**
1. Aumente MAX_DRILLING_SITES si es muy restrictivo
2. Reduzca NUM_CANDIDATE_ZONES para simplificar el problema
3. Ajuste la penalización en la conversión QUBO:
   ```python
   converter = QuadraticProgramToQubo(penalty=500)  # En lugar de 1000
   ```

#### 5. Dashboard No Carga Datos

**Síntoma:**
- Mapa muestra datos de demostración
- Métricas muestran "--"

**Solución:**
1. Verifique que los archivos JSON/GeoJSON están en la misma carpeta
2. Use un servidor local (ver "Método Alternativo" arriba)
3. Abra consola del navegador (F12) y revise errores CORS

#### 6. Instalación de Paquetes Falla

**Síntoma:**
```
ERROR: Could not install packages
```

**Solución:**
1. Reinicie el runtime de Colab: "Entorno de ejecución" → "Reiniciar entorno de ejecución"
2. Ejecute la instalación manualmente:
   ```python
   !pip install --upgrade earthengine-api qiskit qiskit-optimization
   ```

### Contacto y Soporte

Para problemas técnicos adicionales:
1. Revise la documentación oficial de Qiskit: https://qiskit.org/documentation/
2. Consulte la guía de Earth Engine: https://developers.google.com/earth-engine
3. Verifique issues en GitHub de las librerías

---

## 📝 Notas Importantes

### Limitaciones del Sistema

1. **Simulador Cuántico**: QAOA ejecuta en simulador clásico, no hardware cuántico real
2. **Escalabilidad**: Para >50 zonas candidatas, el tiempo de cómputo aumenta significativamente
3. **Datos Sintéticos**: El entrenamiento del Random Forest usa datos sintéticos; idealmente use datos de campo reales

### Mejoras Recomendadas

1. **Datos de Entrenamiento Reales**:
   - Reemplace los puntos de entrenamiento sintéticos con datos de perforaciones reales
   - Use un shapefile con ubicaciones conocidas de mineralización

2. **Validación Geológica**:
   - Consulte con geólogos expertos sobre los ponderamientos
   - Ajuste WEIGHTS basándose en conocimiento del área

3. **Hardware Cuántico Real**:
   - Configure credenciales de IBM Quantum
   - Use `IBMProvider()` en lugar del simulador

4. **Restricciones Adicionales**:
   - Agregue restricciones de presupuesto
   - Incluya restricciones de distancia mínima entre zonas
   - Considere restricciones ambientales o sociales

### Recomendaciones de Uso

1. **Primera Ejecución**: Use parámetros por defecto para familiarizarse
2. **Producción**: Ajuste parámetros según su región específica
3. **Validación**: Compare resultados con conocimiento geológico local
4. **Iteración**: Refine ponderamientos basándose en resultados de campo

---

## ✅ Checklist de Ejecución

Antes de ejecutar, verifique:

- [ ] Cuenta Google Earth Engine activa
- [ ] Proyecto EE configurado
- [ ] Autenticación completada (si es primera vez)
- [ ] Coordenadas ROI_COORDS configuradas para su región
- [ ] Rango de fechas apropiado para el área
- [ ] Parámetros de optimización revisados
- [ ] Archivos del dashboard en la misma carpeta
- [ ] Navegador actualizado (Chrome/Firefox/Edge)

Durante la ejecución:

- [ ] Instalación de paquetes completada sin errores
- [ ] Datos satelitales cargados (imágenes > 0)
- [ ] Índices espectrales calculados
- [ ] Random Forest entrenado exitosamente
- [ ] QAOA convergió a solución óptima
- [ ] 4 archivos de salida generados
- [ ] Archivos descargados de Colab

Al visualizar dashboard:

- [ ] Métricas principales muestran valores (no "--")
- [ ] Mapa muestra zonas seleccionadas
- [ ] 3 gráficos se renderizan correctamente
- [ ] Tabla muestra zonas con datos
- [ ] Interacción del mapa funciona (zoom, click)

---

## 🎯 Resultado Final Esperado

Al completar exitosamente todos los pasos, tendrá:

1. ✅ **Mapa de Prospectividad Mineral**: Generado con datos Sentinel-2 y DEM
2. ✅ **Clasificación con IA**: Random Forest entrenado con 11 variables
3. ✅ **Solución Cuántica Óptima**: 5 zonas seleccionadas maximizando beneficio
4. ✅ **Dashboard Interactivo**: Visualización completa con mapas y gráficos
5. ✅ **Comparación de Algoritmos**: Demostración de mejora cuántica vs clásica
6. ✅ **Datos Exportables**: GeoJSON y JSON para integración con otros sistemas

**¡Éxito! Su Sistema de Optimización Cuántica Minera está completo y operacional.**

---

*Documento actualizado: 2026-01-08*  
*Versión: 1.0*  
*Sistema: Quantum Mining Optimization DSS*
