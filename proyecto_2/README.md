# AstroNight AI — Proyecto II

**Predicción de nubosidad y apoyo a la observación astronómica mediante aprendizaje automático e inteligencia artificial generativa.**

## 1. Descripción y motivación

Proyecto desarrollado en Python cuyo objetivo es ayudar a interpretar las condiciones meteorológicas para la observación del cielo nocturno.

El sistema combina:

- Previsiones meteorológicas obtenidas mediante Open-Meteo.
- Un modelo Random Forest entrenado localmente con scikit-learn para estimar la nubosidad.
- Datos de radiancia nocturna del satélite VIIRS, como información complementaria sobre iluminación artificial.
- Cálculos astronómicos con Astral para identificar si existe noche astronómica.
- Un modelo generativo NVIDIA Nemotron, mediante API, para producir explicaciones comprensibles de los resultados.

La motivación del proyecto es comprobar si un modelo de aprendizaje automático puede mejorar las previsiones originales de nubosidad y presentar sus resultados de manera útil para una persona interesada en la astronomía.

El Proyecto II constituye la base técnica del Proyecto III, en el que se ampliará el sistema hacia una aplicación o API de extremo a extremo.

## 2. Fuentes de datos

### 2.1. Open-Meteo Previous Runs API

Se utiliza para obtener previsiones meteorológicas históricas con distintos horizontes de antelación, de uno a siete días.

Variables de entrada:

- Temperatura a 2 metros.
- Velocidad del viento a 10 metros.
- Precipitación.
- Humedad relativa a 2 metros.
- Punto de rocío a 2 metros.
- Nubosidad prevista por Open-Meteo.
- Horizonte de predicción (`lead_days`).

Documentación: https://open-meteo.com/en/docs/previous-runs-api
Fecha de descarga: 11/11/2026

### 2.2. Open-Meteo Historical Weather API / ERA5

Se utiliza como referencia histórica de nubosidad (`cloud_cover_actual`) para entrenar y evaluar el modelo.

ERA5 proporciona datos de reanálisis meteorológico. En este proyecto se emplean como referencia para comparar las previsiones, no como observaciones instrumentales directas de cada localidad.

Documentación: https://open-meteo.com/en/docs/historical-weather-api
Fecha de descarga: 11/11/2026

### 2.3. Open-Meteo Forecast API y Geocoding API

Durante la inferencia operativa se utilizan para:

- Localizar una ciudad o municipio.
- Obtener coordenadas y zona horaria.
- Descargar las previsiones meteorológicas actuales.

Documentación:

- https://open-meteo.com/en/docs
- https://open-meteo.com/en/docs/geocoding-api

### 2.4. Datos satelitales VIIRS: preparación y cobertura

Para incorporar información sobre contaminación lumínica se ha utilizado el producto anual **VIIRS Nighttime Lights de 2025**, proporcionado por el Earth Observation Group (EOG).

Se ha trabajado con el raster de radiancia nocturna media anual, enmascarado para reducir determinadas fuentes de iluminación no representativas.

**Preparación del raster**

Debido al tamaño del producto original, se ha utilizado **QGIS** para generar un GeoTIFF reducido al área de interés del proyecto.

El procedimiento seguido ha sido:

1. Descargar el raster VIIRS anual de 2025 desde el EOG.
2. Abrir el archivo raster en QGIS.
3. Recortar el raster mediante una extensión geográfica que abarcase España, incluyendo las Islas Canarias y las Islas Baleares.
4. Utilizar los siguientes límites geográficos aproximados:
   - Longitud mínima: -19°.
   - Longitud máxima: 5°.
   - Latitud mínima: 27°.
   - Latitud máxima: 45°.
5. Guardar el raster resultante en formato GeoTIFF, con sistema de coordenadas EPSG:4326, en:

   `data/viirs/espana_viirs.tif`

**Cobertura y limitaciones**

El raster se ha preparado para cubrir España, incluyendo los territorios insulares. Por tanto, esta es la zona de interés para la consulta de contaminación lumínica en la versión actual de AstroNight.

El recorte es rectangular y se define mediante coordenadas geográficas, por lo que también puede incluir zonas de países vecinos. La presencia de un valor válido depende de la cobertura del raster y de los píxeles disponibles.

Los valores consultados representan **radiancia nocturna en nW/cm²/sr**. No son predicciones de iluminación futura, ni mediciones directas del brillo del cielo desde el suelo, ni equivalencias automáticas con la escala Bortle.

Para ampliar la cobertura geográfica sería necesario preparar otros recortes o disponer de una fuente de datos alternativa.

Fuente: https://eogdata.mines.edu/products/vnl/

### 2.5. Licencias y condiciones de uso

**Open-Meteo — Datos meteorológicos**

Las previsiones meteorológicas históricas y actuales utilizadas se han obtenido mediante las APIs de Open-Meteo.

Los datos proporcionados por Open-Meteo se distribuyen bajo la licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**, que permite su reutilización y transformación siempre que se reconozca la fuente y se indiquen las modificaciones realizadas.

- **Fuente:** [Open-Meteo](https://open-meteo.com/)
- **Licencia:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Condiciones oficiales:** [Licencia de Open-Meteo](https://open-meteo.com/en/license)

**Atribución:** Datos meteorológicos proporcionados por [Open-Meteo.com](https://open-meteo.com/).

**Referencia bibliográfica:**

Zippenfenig, P. (2023). *Open-Meteo.com Weather API* [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.7970649

Los datos históricos de referencia se han obtenido mediante la Historical Weather API de Open-Meteo, sin realizar descargas directas desde Copernicus Climate Data Store.

**Earth Observation Group (EOG) — VIIRS Nighttime Lights**

Los datos de radiancia nocturna utilizados en AstroNight AI proceden del producto **VIIRS Nighttime Lights (VNL)** del Earth Observation Group (EOG), Payne Institute for Public Policy, Colorado School of Mines.

El EOG incluye VIIRS Nighttime Lights entre los productos distribuidos bajo la licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**, que permite copiar, modificar y redistribuir los datos siempre que se reconozca su procedencia y se indiquen las modificaciones realizadas.

Para este proyecto se ha utilizado un producto anual de 2025, recortado geográficamente mediante QGIS para generar el archivo `data/viirs/espana_viirs.tif`.

- **Fuente:** [Earth Observation Group — VIIRS Nighttime Lights](https://eogdata.mines.edu/products/vnl/)
- **Licencia:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Documento oficial de licencias:** [EOG Products — Data Access and Licensing](https://eogdata.mines.edu/files/EOG_products_CC_License.pdf)

**Atribución del producto derivado:**

Este producto se ha elaborado utilizando datos VIIRS Nighttime Lights (VNL) producidos por el Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines. El raster original se ha recortado mediante QGIS para su utilización en AstroNight AI.

**Referencia bibliográfica:**

Elvidge, C. D., Baugh, K., Zhizhin, M., Hsu, F. C., & Ghosh, T. (2017). *VIIRS night-time lights*. International Journal of Remote Sensing, 38, 5860–5879.

## 3. Arquitectura y pipeline

El sistema separa la preparación de datos, el entrenamiento, la inferencia y la explicación generativa.

```text
Open-Meteo Previous Runs + ERA5
               |
               v
      descargar_datos.py
               |
               v
       procesar_datos.py
               |
               v
 data/processed/datos_ml.csv
               |
       +-------+--------+
       |                |
       v                v
 evaluar_modelo.py  entrenar_modelo.py
       |                |
 Validación CV          v
                 Random Forest
                 + metadata.json
                        |
                        v
Geocoding + Forecast API --> predecir.py
                                  |
                                  v
                          Predicciones CSV
                                  |
                VIIRS + Astral    |
                       |          |
                       v          v
                        recomendador.py
                                  |
                                  v
                        explicar_predicciones.py
                                  |
                                  v
                    cliente_nvidia.py
                    (mock / API real)
                                  |
                                  v
                      Explicación al usuario
```

Los componentes incluyen registros de ejecución mediante `logging`.

## 4. Instalación y configuración

AstroNight AI utiliza **Python 3.12** y las dependencias especificadas en `requirements.txt`.

Los siguientes comandos están preparados para Windows utilizando Git Bash y deben ejecutarse desde la carpeta `proyecto_2`.

### 4.1. Crear el entorno virtual

```bash
python -m venv .venv
```

### 4.2. Activar el entorno virtual

```bash
source .venv/Scripts/activate
```

### 4.3. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```
### 4.4. Configurar las variables de entorno

Crear un archivo `.env` en la raíz de `proyecto_2` tomando como referencia `.env.example`.

```dotenv
NVIDIA_API_KEY=
NVIDIA_MODEL=nvidia/nemotron-3.5-super-vl-120b-a12b
```

La variable `NVIDIA_API_KEY` solo es necesaria para utilizar el modo real de la API de NVIDIA. Para ejecutar el modo simulado (`mock`) no se necesita una clave.

El archivo `.env` contiene información privada y está excluido de Git mediante `.gitignore`.

### 4.5. Requisitos de datos y modelo

Para realizar predicciones es necesario disponer de los siguientes archivos, incluidos en el repositorio:

- `models/random_forest.joblib`
- `models/metadata.json`

El modelo Random Forest ya está entrenado y guardado, por lo que no es necesario volver a entrenarlo para realizar predicciones.

Para consultar información de radiancia nocturna también se utiliza el archivo `data/viirs/espana_viirs.tif`, preparado a partir del producto satelital original mediante QGIS e incluido en el repositorio.

El conjunto de datos históricos completo no es necesario para ejecutar predicciones con el modelo guardado, pero sí para reproducir el proceso de entrenamiento y evaluación.

## 5. Configuración de la API de IA

AstroNight AI utiliza **NVIDIA** como proveedor de IA generativa, una alternativa a Hugging Face permitida por el enunciado.

- **Proveedor:** NVIDIA.
- **Modelo:** `nvidia/nemotron-3.5-super-vl-120b-a12b`.
- **Tarea:** generación de explicaciones en lenguaje natural mediante *chat completions*.
- **Cliente:** `cliente_nvidia.py`.
- **SDK:** `openai`, configurado para utilizar el endpoint de NVIDIA.

El sistema dispone de dos modos de funcionamiento:

- **Modo `mock`:** genera una respuesta simulada sin consultar la API de NVIDIA ni requerir una clave privada.
- **Modo `real`:** utiliza la API de NVIDIA para generar explicaciones a partir de los resultados calculados por AstroNight.

La configuración de las credenciales se explica en el **apartado 4.4**.

Las llamadas a la API real de NVIDIA incluyen un control de errores de comunicación, como problemas de conexión, tiempos de espera o respuestas HTTP fallidas. Estos errores se gestionan mediante la excepción `AIClientError`, permitiendo identificar los fallos del servicio externo.

Para la generación de explicaciones se utiliza `temperature=0.3`, con el objetivo de favorecer respuestas más consistentes y ajustadas a los datos meteorológicos y astronómicos proporcionados. Esta configuración no garantiza por sí sola la ausencia de información incorrecta.

El modelo generativo NVIDIA no calcula la nubosidad ni sustituye al Random Forest. Su función es explicar en lenguaje natural los resultados meteorológicos y astronómicos obtenidos por el sistema.

## 6. Preparación de datos y entrenamiento

### 6.1. Descargar los datos históricos

```bash
python descargar_datos.py historicos --inicio 2024-01-26 --fin 2026-10-31
```

Los datos se obtienen para siete localidades:

- A Coruña.
- Madrid.
- León.
- Barcelona.
- Almería.
- Granada.
- Santa Cruz de Tenerife.

Las descargas históricas se guardan en `data/raw/`.

La disponibilidad y los límites de las APIs pueden requerir repetir o completar las descargas.

### 6.2. Procesar los datos

```bash
python procesar_datos.py
```

El script prepara las variables meteorológicas, normaliza las fechas y combina las previsiones históricas con los datos de referencia.

El resultado es:

```text
data/processed/datos_ml.csv
```

El conjunto construido contiene aproximadamente 1,18 millones de registros, correspondientes a distintos horizontes de predicción.

### 6.3. División de los datos: entrenamiento, validación y test

Para evaluar la capacidad de generalización del modelo Random Forest, se ha realizado una separación temporal y geográfica de los datos.

El conjunto original contiene información meteorológica de siete localidades: A Coruña, Madrid, León, Barcelona, Almería, Granada y Santa Cruz de Tenerife, con previsiones históricas correspondientes a horizontes de uno a siete días.

La división se ha realizado de la siguiente manera:

| Conjunto | Localidades | Período | Finalidad |
|---|---|---|---|
| Entrenamiento y validación | A Coruña, Madrid, León, Almería y Santa Cruz de Tenerife | Antes del 01/01/2026 | Entrenar el modelo y seleccionar hiperparámetros |
| Test temporal | Las cinco localidades de entrenamiento | Desde el 01/01/2026 | Comprobar la generalización a fechas no utilizadas durante el entrenamiento |
| Test geográfico | Barcelona y Granada | Antes del 01/01/2026 | Comprobar la generalización a localidades no utilizadas durante el entrenamiento |
| Test combinado | Barcelona y Granada | Desde el 01/01/2026 | Comprobar la generalización simultánea a nuevas localidades y fechas |

Los datos de Barcelona y Granada, así como los registros de 2026, se han reservado para la evaluación final y no se han utilizado para ajustar los hiperparámetros.

Dentro del conjunto de desarrollo se ha aplicado validación cruzada temporal para seleccionar la configuración del Random Forest.

Esta estrategia permite analizar por separado la generalización temporal y geográfica del modelo, evitando utilizar los conjuntos de test final durante su selección.

### 6.4. Validación y selección de hiperparámetros

```bash
python evaluar_modelo.py
```

La selección de hiperparámetros se realiza únicamente con los datos de desarrollo: las cinco localidades de entrenamiento y fechas anteriores a 2026.

Se utiliza `TimeSeriesSplit` con cuatro particiones temporales y una separación de 168 horas entre entrenamiento y validación. La división se efectúa sobre las marcas temporales únicas para mantener agrupados los registros correspondientes a una misma hora, incluidos los distintos horizontes de predicción.

Se comparan diferentes combinaciones de parámetros de `RandomForestRegressor`, utilizando como referencia (*baseline*) las previsiones originales de nubosidad de Open-Meteo.

Para cada configuración se calculan las métricas MSE, MAE, RMSE y R².

La selección del modelo se basa en el menor MSE medio de validación. La configuración finalmente seleccionada fue:

| Hiperparámetro | Valor |
|---|---|
| `n_estimators` | 100 |
| `max_depth` | 8 |
| `min_samples_leaf` | 20 |

Una vez seleccionados los hiperparámetros, el modelo definitivo se entrena con todos los registros del conjunto de entrenamiento y desarrollo.

Los conjuntos de test temporal, geográfico y combinado permanecen reservados hasta la evaluación final del modelo.

#### 6.4.1  Justificación de la métrica principal: MSE

Se ha seleccionado el **error cuadrático medio (MSE)** como métrica principal para comparar los modelos y elegir los hiperparámetros del Random Forest.

Esta elección se debe al objetivo: proporcionar estimaciones de nubosidad útiles para planificar la observación astronómica. En este contexto, se considera especialmente importante reducir los errores de predicción de gran magnitud, ya que una diferencia elevada entre la nubosidad prevista y la real puede llevar al usuario a interpretar incorrectamente las condiciones del cielo.

El MSE eleva los errores al cuadrado, por lo que penaliza proporcionalmente más los errores grandes que los pequeños. Así, se prioriza un modelo que reduzca los errores cuadráticos, aunque pueda presentar un error absoluto medio ligeramente superior.

No obstante, también se calculan el MAE, el RMSE y el R² para ofrecer una evaluación más completa y evitar que la selección dependa de una única métrica.


### 6.5. Entrenar el modelo definitivo

```bash
python entrenar_modelo.py
```

Configuración seleccionada:

| Parámetro | Valor |
|---|---|
| Algoritmo | `RandomForestRegressor` |
| `n_estimators` | 100 |
| `max_depth` | 8 |
| `min_samples_leaf` | 20 |
| `random_state` | 42 |

Se utilizan 593.040 registros de entrenamiento, correspondientes a cinco localidades y fechas anteriores a 2026.

Los archivos generados son:

```text
models/random_forest.joblib
models/metadata.json
```

El modelo se carga mediante `joblib` durante la inferencia.

## 7. Evaluación final del modelo

La evaluación final se ejecuta por separado de los tests unitarios:

```bash
python evaluacion_final.py
```

Se utilizan tres escenarios de prueba:

1. **Temporal:** fechas de 2026 de las cinco localidades utilizadas en entrenamiento.
2. **Geográfico:** Barcelona y Granada, con fechas anteriores a 2026.
3. **Combinado:** Barcelona y Granada, con fechas de 2026.

Los conjuntos de evaluación final no se utilizan para seleccionar los hiperparámetros.

### 7.1. Resultados globales

| Escenario | Modelo | MSE | MAE | RMSE | R² |
|---|---|---:|---:|---:|---:|
| Temporal | Open-Meteo | 1337,74 | 24,24 | 36,58 | 0,1491 |
| Temporal | Random Forest | 1013,96 | 25,72 | 31,84 | 0,3551 |
| Geográfico | Open-Meteo | 1425,71 | 25,23 | 37,76 | 0,1223 |
| Geográfico | Random Forest | 1049,70 | 26,68 | 32,40 | 0,3538 |
| Combinado | Open-Meteo | 1395,74 | 24,72 | 37,36 | 0,1524 |
| Combinado | Random Forest | 1048,62 | 26,58 | 32,38 | 0,3632 |

#### 7.2 Interpretación de los resultados

El Random Forest consigue reducir el MSE respecto a Open-Meteo en los tres escenarios de evaluación, con mejoras aproximadas del 24 % al 26 %. También presenta valores más bajos de RMSE y mayores de R².
Los resultados también muestran que el error aumenta con el horizonte de predicción. Random Forest obtiene un MSE inferior al de Open-Meteo en los siete horizontes evaluados.
Sin embargo, el MAE es ligeramente superior al de Open-Meteo en los tres escenarios globales. Esto indica que, aunque el modelo reduce el error cuadrático, no mejora el error absoluto medio.

Por tanto, **la elección del Random Forest se justifica por el objetivo de priorizar la reducción de errores grandes de nubosidad, y no porque supere a Open-Meteo en todas las métricas**.

Como limitación, el MSE penaliza los errores grandes independientemente de su dirección. En futuras versiones podría estudiarse específicamente la frecuencia de predicciones que indican poca nubosidad cuando las condiciones reales son mucho más desfavorables.

El modelo no elimina la incertidumbre meteorológica y no garantiza predicciones exactas.

### 7.3 Archivos de resultados disponibles

Los resultados completos de la evaluación se encuentran en el archivo [`resultados_finales.xlsx`](data/processed/evaluacion_final/resultados_finales.xlsx).

Este Excel permite consultar las métricas **MSE, MAE, RMSE y R²** del modelo Random Forest y compararlas con las previsiones originales de Open-Meteo en los tres escenarios de evaluación: temporal, geográfico y combinado.

De esta forma, los resultados presentados en este README pueden consultarse directamente en el archivo generado por el pipeline de evaluación.


## 8. Predicciones operativas

Para generar predicciones de una localidad:

```bash
python predecir.py --ubicacion "La Hiruela"
```

También puede indicarse el país:

```bash
python predecir.py --ubicacion Lisboa --pais PT
```

El sistema busca las coordenadas de la localidad, descarga las previsiones y aplica el Random Forest guardado.

Las predicciones se almacenan en un archivo CSV dentro de `data/processed/`.

Entre sus columnas se incluyen:

- `time`: fecha y hora en UTC.
- `lead_days`: horizonte aproximado de predicción.
- `cloud_cover_forecast`: nubosidad original de Open-Meteo.
- `cloud_cover_predicted`: nubosidad utilizada por AstroNight.
- `metodo`: `random_forest` u `open_meteo`.
- `zona_horaria`: zona horaria local.
- `latitud` y `longitud`: coordenadas de la localidad.

El horizonte operativo `lead_days` se aproxima a partir de las horas restantes hasta la fecha prevista. Puede no representar exactamente el mismo horizonte que los datos históricos de Previous Runs.

### 8.1. Cobertura geográfica

Las predicciones meteorológicas se generan mediante la API de Open-Meteo y el modelo Random Forest, por lo que no dependen directamente del raster VIIRS.

Sin embargo, **la información adicional sobre radiancia nocturna está limitada al área cubierta por el archivo `espana_viirs.tif`**, preparado principalmente para España, incluidas las Islas Canarias y Baleares.

Para localidades fuera de dicha cobertura, AstroNight no puede obtener un valor de VIIRS a partir del raster actual. Esta limitación afecta al componente de contaminación lumínica, no necesariamente a la generación de la predicción meteorológica.

La consulta del raster no debe utilizar valores inventados para localidades sin datos disponibles.

## 9. Explicaciones mediante NVIDIA

Una vez generado el CSV, es posible solicitar una explicación simulada:

```bash
python explicar_predicciones.py --ubicacion "La Hiruela" --lead-days 3 --mock
```

Para usar la API real de NVIDIA:

```bash
python explicar_predicciones.py --ubicacion "La Hiruela" --lead-days 3 --real
```

El sistema puede incorporar información adicional procedente de:

- **VIIRS:** radiancia nocturna asociada a la ubicación.
- **Astral:** altura del Sol para identificar si existe noche astronómica.
- **Recomendador:** reglas que interpretan la nubosidad y las condiciones disponibles.

La explicación generativa debe basarse en los resultados calculados por el sistema y no en valores meteorológicos inventados.

El modo `mock` evita la petición a NVIDIA, pero no sustituye las peticiones de Open-Meteo necesarias para generar previamente un CSV actualizado.

El parámetro `--lead-days` indica el **horizonte de predicción**, es decir, con cuántos días de antelación se realiza la previsión meteorológica que queremos consultar.

Por ejemplo, `--lead-days 3` selecciona las predicciones correspondientes al horizonte aproximado de tres días. El sistema utiliza la nubosidad de ese horizonte para elaborar la recomendación astronómica y generar la explicación.

Se pueden consultar los horizontes disponibles en el CSV generado previamente.

### 9.1. Consulta por fecha y hora

Además de seleccionar una predicción mediante `--lead-days`, AstroNight permite consultar una **fecha y hora concretas**, utilizando la zona horaria local de la ubicación.

Por ejemplo, para consultar las condiciones de observación astronómica en La Hiruela el **26 de noviembre de 2026 a las 23:00**:

```bash
python explicar_predicciones.py --ubicacion "La Hiruela" --fecha 2026-11-26 --hora 23 --real
```

También es posible utilizar el modo simulado:

```bash
python explicar_predicciones.py --ubicacion "La Hiruela" --fecha 2026-11-26 --hora 23 --mock
```

El sistema selecciona la predicción correspondiente a esa fecha y hora del CSV generado previamente, teniendo en cuenta la zona horaria de la localidad.

De esta forma, el usuario no necesita calcular manualmente el horizonte `lead_days` cuando desea consultar una hora concreta.

Para ambas opciones es necesario haber generado previamente el CSV de predicciones mediante predecir.py.

### 9.2. Integración de VIIRS y Astral

El módulo `cliente_viirs.py` utiliza la biblioteca `rasterio` para abrir el archivo `data/viirs/espana_viirs.tif` y consultar el valor del píxel correspondiente a las coordenadas geográficas de la localidad.

Se realiza la transformación de coordenadas necesaria para utilizar el sistema de referencia del raster.

El módulo `recomendador.py` combina la nubosidad predicha con la información astronómica obtenida mediante Astral.

Astral permite calcular la altura del Sol. Se considera noche astronómica cuando el Sol está a **18 grados o más por debajo del horizonte**.

La radiancia VIIRS se incorpora como información complementaria y se muestra junto con su fuente, unidad y año. Actualmente no se transforma en una clasificación Bortle ni se utiliza para calcular una puntuación numérica de calidad del cielo.

Finalmente, `cliente_nvidia.py` puede generar una explicación en lenguaje natural a partir de estos resultados, sin sustituir los cálculos realizados por los módulos anteriores.



## 10. Pruebas automatizadas

Se utiliza `pytest` para comprobar el funcionamiento de los distintos componentes. Se han implementado pruebas unitarias, pruebas de integración con servicios simulados y pruebas específicas de carga e inferencia del modelo Random Forest.

| Archivo | Función |
|---|---|
| `tests/test_descargar_datos.py` | Comprueba los reintentos ante errores HTTP temporales y la propagación de errores no reintentables, sin realizar peticiones reales |
| `tests/test_predecir.py` | Carga del modelo sklearn e inferencia |
| `tests/test_integracion_API_simulada.py` | Flujo de predicción con servicios externos simulados |
| `tests/test_metricas.py` | Comprobación del cálculo de las métricas |
| `tests/test_nvidia.py` | Comprueba la generación de prompts, el modo mock, las validaciones, la integración con CSV, las respuestas simuladas de NVIDIA y la gestión de errores de la API |
| `tests/test_viirs.py` | Lectura de VIIRS y comprobaciones del recomendador |

### 10.1. Ejecutar todos los tests

Desde la raíz del proyecto:

```bash
python -m pytest -v
```

### 10.2. Ejecutar los tests unitarios

Para ejecutar las pruebas de métricas y las comprobaciones unitarias de NVIDIA y VIIRS, excluyendo las pruebas de integración y las de carga e inferencia del modelo:

```bash
python -m pytest tests/test_metricas.py tests/test_nvidia.py tests/test_viirs.py -k "not integracion and not cliente_nvidia_simulado" -v
```

Esta selección comprueba las métricas y las pruebas unitarias seleccionadas de NVIDIA y VIIRS, excluyendo los casos identificados por el filtro indicado.

### 10.3. Ejecutar los tests de integración

Para ejecutar el flujo de predicción con Open-Meteo simulado:

```bash
python -m pytest tests/test_integracion_API_simulada.py -v
```

También se puede ejecutar específicamente mediante su marcador `integracion`:

```bash
python -m pytest -m integracion -v
```

Este último se puede realizar porque tiene aplicado `@pytest.mark.integracion`.

La prueba utiliza `monkeypatch` para simular las respuestas de geocodificación y previsión de Open-Meteo, y `tmp_path` para comprobar la generación del CSV sin modificar los archivos habituales del proyecto.

### 10.4. Ejecutar los tests de carga e inferencia del modelo sklearn

```bash
python -m pytest tests/test_predecir.py -v
```

Este archivo incluye dos pruebas principales:

- `test_modelo_guardado_carga`: comprueba que el modelo Random Forest guardado en formato `joblib` puede cargarse correctamente.
- `test_inferencia_con_modelo_real`: comprueba que el modelo realiza predicciones válidas y que se utiliza para los horizontes correspondientes, manteniendo la previsión de Open-Meteo en el horizonte 0.

### 10.5. Simulación de servicios externos

Las pruebas automatizadas utilizan respuestas simuladas y `monkeypatch` para evitar peticiones reales a los servicios externos.

Esto permite ejecutar los tests sin consumir créditos de NVIDIA ni depender de la disponibilidad de las APIs.

La evaluación científica completa del Random Forest se realiza por separado mediante:

```bash
python evaluacion_final.py
```

Este script calcula MSE, MAE, RMSE y R² en los conjuntos de test temporal, geográfico y combinado. No forma parte de la batería habitual de pytest.

## 11. Integración continua

El proyecto utiliza GitHub Actions para comprobar automáticamente que las pruebas del proyecto siguen funcionando cuando se suben cambios al repositorio.

El workflow de integración continua está definido en el archivo .github/workflows/tests_proyecto_2.yml, situado en la raíz del repositorio GitHub. Se ejecuta automáticamente cuando se suben cambios del Proyecto II a la rama main, en las solicitudes de incorporación de cambios correspondientes, y también permite su ejecución manual.
El workflow utiliza Python 3.12 y pytest, instala las dependencias desde requirements.txt y ejecuta las pruebas descritas en el apartado 10, sin necesidad de utilizar credenciales privadas ni consultar las APIs reales.

- Enlace directo al workflow de GitHub Actions.
https://github.com/saramartindelbarrio/dsia-26-27-martin-sara/actions/workflows/tests_proyecto_2.yml

- Badge que muestre el estado de la última ejecución.
[![Tests AstroNight Proyecto II](https://github.com/saramartindelbarrio/dsia-26-27-martin-sara/actions/workflows/tests_proyecto_2.yml/badge.svg)](https://github.com/saramartindelbarrio/dsia-26-27-martin-sara/actions/workflows/tests_proyecto_2.yml)

La evaluación final del modelo, que requiere el conjunto de datos históricos completo, se ejecuta de manera independiente mediante evaluacion_final.py y no forma parte de las pruebas automáticas de GitHub Actions.

### 11.1. Uso del modo mock en CI

Las pruebas automatizadas ejecutadas en GitHub Actions utilizan el modo `mock` para comprobar la integración con NVIDIA sin realizar peticiones reales a su API ni necesitar credenciales.

Las pruebas que simulan el cliente de NVIDIA mediante `monkeypatch` tampoco realizan conexiones externas. El modo real queda reservado para ejecuciones con una clave de API válida.

## 12. Limitaciones

El proyecto presenta las siguientes limitaciones:

- La precisión meteorológica es limitada y las predicciones contienen errores.
- Random Forest mejora el MSE global frente a Open-Meteo, pero empeora el MAE global.
- Las localidades de prueba permiten estudiar la generalización, pero no garantizan la precisión en cualquier municipio.
- La variable `lead_days` operativa es una aproximación al horizonte histórico.
- ERA5 es una referencia de reanálisis, no una medición directa de nubosidad en cada emplazamiento.
- VIIRS mide radiancia observada desde satélite; no proporciona directamente una clase Bortle.
- Las explicaciones de NVIDIA pueden variar y no deben considerarse mediciones adicionales.
- Los servicios externos pueden presentar errores de conexión, límites de uso o cambios de disponibilidad.

## 13. Continuidad hacia el Proyecto III

El Proyecto II proporciona la base reutilizable del Trabajo Final:

- Pipeline de preparación y procesamiento de datos.
- Modelo Random Forest entrenado y persistido.
- Inferencia meteorológica mediante CLI.
- Cliente de IA con modos `mock` y `real`.
- Integración de información VIIRS y cálculos astronómicos.
- Pruebas automatizadas y configuración de entorno.

En el Proyecto III se prevé ampliar esta base mediante una API o aplicación, integrar un flujo de análisis completo, mejorar la selección de horarios adecuados para observación, añadir mecanismos de despliegue y monitorización y preparar la presentación final.

### 13.1 Integración futura de Light Pollution Map

Como ampliación del Proyecto III, se plantea integrar la API de **Light Pollution Map** para obtener información adicional sobre contaminación lumínica a partir de las coordenadas de la localidad seleccionada.

Durante el Proyecto II se ha contactado con el responsable del servicio para solicitar acceso a la API y estudiar su posible integración.

Esta funcionalidad complementaría los datos satelitales VIIRS utilizados actualmente y permitiría mejorar la información ofrecida al usuario sobre las condiciones de observación astronómica.

La integración dependerá de las condiciones de acceso y uso de la API, y requerirá validar los datos obtenidos antes de incorporarlos a las recomendaciones del sistema.

## 14. Uso de IA durante el desarrollo

La utilización de herramientas de IA para apoyar el desarrollo y la documentación, así como la descripción del proveedor y el modelo generativo integrados en AstroNight, se detallan en:

`AI_USAGE.md`

## 15. Referencias

- Open-Meteo: https://open-meteo.com/ 
- Open-Meteo Previous Runs: https://open-meteo.com/en/docs/previous-runs-api
- Open-Meteo Historical Weather: https://open-meteo.com/en/docs/historical-weather-api
- Copernicus Climate Data Store / ERA5: https://cds.climate.copernicus.eu/ 
#Referencia de origen para los datos históricos de nubosidad utilizados como objetivo de entrenamiento y evaluación del Random Forest. Estos datos se obtienen mediante la Historical Weather API de Open-Meteo, sin necesidad de descargar directamente archivos desde Copernicus Climate Data Store.
- Earth Observation Group — VIIRS: https://eogdata.mines.edu/products/vnl/
- scikit-learn: https://scikit-learn.org/
- NVIDIA Build: https://build.nvidia.com/
- Astral: https://astral.readthedocs.io/
- pytest: https://docs.pytest.org/
