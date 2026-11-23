# Uso de inteligencia artificial — AstroNight AI

## 1. Objetivo

AstroNight AI combina un modelo clásico de aprendizaje automático, entrenado con scikit-learn, y un modelo de inteligencia artificial generativa al que se accede mediante una API externa.

Ambos modelos desempeñan funciones diferentes:

- **Random Forest:** genera predicciones de nubosidad a partir de variables meteorológicas.
- **NVIDIA Nemotron:** genera explicaciones en lenguaje natural a partir de las predicciones y de la información proporcionada por el sistema.

El modelo generativo no sustituye al Random Forest ni se utiliza para entrenarlo.

## 2. Modelo de aprendizaje automático

- **Biblioteca:** scikit-learn.
- **Algoritmo:** `RandomForestRegressor`.
- **Tarea:** regresión de la nubosidad, expresada como porcentaje.
- **Entrenamiento:** local, mediante `entrenar_modelo.py`.
- **Persistencia:** `models/random_forest.joblib`.
- **Inferencia:** integrada en `predecir.py`.

El modelo se entrena con datos meteorológicos históricos y se evalúa por separado frente a la previsión original de Open-Meteo.

## 3. Proveedor de inteligencia artificial generativa

- **Proveedor:** NVIDIA.
- **Servicio:** NVIDIA API.
- **Modelo:** `nvidia/nemotron-3.5-super-vl-120b-a12b`.
- **Tarea:** generación de explicaciones en lenguaje natural mediante chat/completions.
- **Cliente:** `cliente_nvidia.py`.

La API recibe información de las previsiones calculadas por el sistema y devuelve una explicación comprensible para el usuario sobre las condiciones de observación astronómica.

La aplicación utiliza el SDK de OpenAI con un endpoint compatible de NVIDIA. Esto no significa que las peticiones se envíen a los servidores de OpenAI.

## 4. Modos de funcionamiento

**Modo mock**

Permite generar respuestas simuladas sin utilizar una clave de API ni realizar peticiones a NVIDIA. Se utiliza en las pruebas automatizadas para que puedan ejecutarse sin conexión al proveedor externo.

**Modo real**

Realiza una petición a NVIDIA utilizando la variable de entorno `NVIDIA_API_KEY`.

Las credenciales se almacenan en un archivo `.env` local, excluido del control de versiones mediante `.gitignore`.

## 5. Limitaciones

Las explicaciones generativas pueden variar entre ejecuciones y no constituyen una fuente independiente de datos meteorológicos.

El modelo generativo debe interpretar los valores proporcionados por AstroNight y no inventar porcentajes de nubosidad, clases Bortle ni mediciones astronómicas.

Los datos VIIRS representan radiancia nocturna observada por satélite y no deben interpretarse directamente como una medición de brillo del cielo.

## 6. Uso de herramientas de IA durante el desarrollo

Durante el desarrollo de AstroNight AI se ha utilizado **ChatGPT (OpenAI)** como herramienta de apoyo para la programación, la revisión del código, la resolución de errores y la documentación del proyecto.

### 6.1. Tareas en las que se ha utilizado

- **Desarrollo en Python:** apoyo en la elaboración y revisión de funciones y scripts del pipeline de datos, entrenamiento e inferencia.
- **Aprendizaje automático:** apoyo para implementar y comprender el entrenamiento de Random Forest, la validación temporal, la selección de hiperparámetros y las métricas MSE, MAE, RMSE y R².
- **Pruebas automatizadas:** apoyo para diseñar y revisar tests con pytest, incluyendo simulaciones de servicios externos mediante `monkeypatch`.
- **Integración de servicios:** orientación para conectar las previsiones meteorológicas, el modelo sklearn y el cliente de NVIDIA.
- **Documentación:** ayuda para estructurar las instrucciones de ejecución, describir los componentes del sistema e interpretar los resultados obtenidos.

### 6.2. Sugerencias aceptadas y modificadas

Durante el desarrollo de AstroNight AI se han utilizado herramientas de inteligencia artificial como apoyo para la organización modular del proyecto, la implementación de pruebas automatizadas, la integración de servicios externos y la documentación.

Entre las propuestas aceptadas y adaptadas destacan:

- **Organización del proyecto:** separación de los procesos de descarga, preparación de datos, entrenamiento, evaluación e inferencia, así como el uso de `joblib` para guardar y reutilizar el modelo Random Forest.

- **Validación del modelo:** utilización de `TimeSeriesSplit` para la validación temporal, manteniendo separados los datos de 2026 y las localidades de Barcelona y Granada para la evaluación final.

- **Cliente NVIDIA:** revisión de la implementación para eliminar una llamada duplicada a la API, incorporar la gestión de errores mediante `AIClientError` y ajustar `temperature` a `0.3`. Los cambios se comprobaron mediante las pruebas automatizadas.

- **Evaluación y documentación:** utilización del MSE como métrica principal, complementándolo con MAE, RMSE y R², y documentación de los resultados, incluyendo las métricas en las que Random Forest no mejora las previsiones originales de Open-Meteo.

Las sugerencias de las herramientas de IA no se han aceptado automáticamente, sino que se han revisado y adaptado a los objetivos del proyecto. Su funcionamiento se ha comprobado mediante la ejecución del código, las pruebas automatizadas y los resultados obtenidos.


### 6.3. Verificación y responsabilidad

El funcionamiento del sistema se ha comprobado mediante pruebas con pytest, ejecuciones del pipeline y evaluaciones del modelo sobre datos reservados.

Los resultados cuantitativos documentados proceden de ejecuciones del proyecto, no de valores generados por ChatGPT.

La selección final de componentes, la interpretación de los resultados y la responsabilidad sobre la entrega corresponden a los autores de AstroNight AI.