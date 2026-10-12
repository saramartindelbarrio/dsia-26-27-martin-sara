# Proyecto I — Programación Avanzada en Python

Este proyecto consiste en el desarrollo de dos aplicaciones en Python para la carga, validación, transformación y análisis de datos.

Se divide en dos partes:

- **Parte A — Ventas:** procesamiento de datos de ventas, identificación de registros inválidos y cálculo del importe total por región.
- **Parte B — OMS:** procesamiento de indicadores de salud de la Organización Mundial de la Salud (OMS) en ingles WHO, transformación del dataset y cálculo de métricas por país y año.

## 1. Estructura del proyecto

```text
dsia-26-27-martin-sara/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
└── proyecto_1/
    ├── ventas_app/
    │   ├── __init__.py
    │   ├── loader.py
    │   ├── validator.py
    │   ├── metrics.py
    │   ├── cli.py
    │   └── DESIGN.md
    │
    ├── who_app/
    │   ├── loader.py
    │   ├── validator.py
    │   ├── transformer.py
    │   ├── metrics.py
    │   └── cli.py
    │
    ├── tests/
    │   ├── __init__.py
    │   ├── ventas/
    │   │   ├── __init__.py
    │   │   ├── test_loader.py
    │   │   ├── test_validator.py
    │   │   ├── test_metrics.py
    │   │   └── test_cli.py
    │   │
    │   └── who/
    │       ├── __init__.py
    │       ├── test_loader.py
    │       ├── test_validator.py
    │       ├── test_transformer.py
    │       ├── test_metrics.py
    │       └── test_cli.py
    │
    ├── Datos/
    │   ├── ventas/
    │   │   └── ventas.csv
    │   ├── who/
    │   │   └── archivos originales CSV
    │   └── who_processed/
    │       └── who_dataset.csv
    │
    ├── pytest.ini
    ├── requirements.txt
    └── README.md
```


## 2. Instalación

El proyecto utiliza Python 3.12.

Desde la carpeta `proyecto_1`, crear un entorno virtual:

```bash
python -m venv .venv
```

Activar el entorno virtual en Git Bash (Windows):

```bash
source .venv/Scripts/activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt  
#El archivo requirements.txt incluye también dependencias de Jupyter Notebook, ya que he utilizado notebooks durante el desarrollo para realizar pruebas y comprobar el funcionamiento del código.
```

## 3. Parte A — Procesamiento de ventas

La aplicación `ventas_app` permite:

- Cargar datos desde archivos CSV o JSON mediante repositorios.
- Validar que las unidades y los precios unitarios sean positivos.
- Separar los registros válidos de los inválidos.
- Calcular el importe de cada venta.
- Obtener el importe total por región, ordenado de mayor a menor.
- Exportar los registros válidos a un nuevo CSV.

Para ejecutar el programa desde `proyecto_1`:

```bash
python -m ventas_app.cli --input Datos/ventas/ventas.csv --output Datos/ventas/ventas_limpias.csv
```

El archivo de salida contiene las columnas `region`, `producto`, `unidades`, `precio_unitario` e `importe`.

La explicación de los principios SOLID aplicados se encuentra en `ventas_app/DESIGN.md`.

## 4. Parte B — Indicadores de salud de la OMS

La aplicación `who_app` permite:

- Cargar y unir varios CSV originales de la OMS.
- Validar las observaciones y separar los registros válidos e inválidos.
- Seleccionar indicadores mediante su código (`Measure code`).
- Crear un dataset con una fila por país o región y año.
- Añadir la categoría de sexo (ALL, FEMALE o MALE) al nombre de cada indicador para conservar esta información en el dataset transformado.
- Calcular métricas sobre el dataset transformado.

Selección de indicadores:

Los archivos originales de la OMS contienen un gran número de indicadores de salud, identificados mediante la columna Measure code.

Dado que todavía estoy estudiando qué variables utilizaré en la segunda parte del proyecto, he desarrollado una demostración que me permite seleccionar los indicadores que quiero analizar.

Para ello, debo indicar los códigos de los indicadores mediante el argumento --measures al ejecutar el programa. De esta forma, puedo seleccionar tantos indicadores como quiera sin necesidad de modificar el código.

Por ejemplo, para seleccionar cinco indicadores (HFA_1, HFA_219, HFA_520, HFA_426 y HFA_427), ejecutaría desde la carpeta proyecto_1:
```bash
python -m who_app.cli --input Datos/who --output Datos/who_processed/who_dataset.csv --measures HFA_1 HFA_219 HFA_520 HFA_426 HFA_427
```

En este comando:

--input: indica la carpeta donde se encuentran los CSV originales de la OMS.

--output: indica dónde se guardará el dataset transformado.

--measures: permite especificar los indicadores que quiero incluir, separados por espacios.

El programa selecciona únicamente los indicadores que he indicado y genera un dataset con una fila por país o región y año, y una columna por cada indicador.


Los módulos principales son:

- `loader.py`: carga y unión de archivos CSV.
- `validator.py`: validación de observaciones.
- `transformer.py`: selección de indicadores y transformación del dataset.
- `metrics.py`: cálculo de métricas.
- `cli.py`: ejecución del proceso desde la terminal.

### Preparar el dataset

Los CSV originales deben colocarse en `Datos/who/`.

Ejemplo de ejecución:

```bash
python -m who_app.cli --input Datos/who --output Datos/who_processed/who_dataset.csv --measures HFA_1 HFA_219 HFA_520
```

El dataset resultante contiene `COUNTRY_REGION`, `YEAR` y las columnas correspondientes a los indicadores seleccionados, por ejemplo `HFA_1_ALL` o `HFA_219_MALE`.

### Calcular métricas

**Variación porcentual entre dos años**

```bash
python -m who_app.cli --input Datos/who --output Datos/who_processed/who_dataset.csv --measures HFA_1 --metric percentage_change --indicator HFA_1_ALL --start-year 2000 --end-year 2020
```

**Cambio anual de un indicador para España**

```bash
python -m who_app.cli --input Datos/who --output Datos/who_processed/who_dataset.csv --measures HFA_1 --metric yearly_change --indicator HFA_1_ALL --country ESP
```

**Ranking de países y regiones para un año determinado**

```bash
python -m who_app.cli --input Datos/who --output Datos/who_processed/who_dataset.csv --measures HFA_1 --metric country_ranking --indicator HFA_1_ALL --year 2020
```

Actualmente, cada ejecución vuelve a cargar, validar y transformar los archivos originales antes de calcular la métrica.

### Consideraciones sobre los datos

Las observaciones se consideran válidas para este análisis cuando contienen un indicador, un país o región, un año positivo y entero, un valor numérico y una categoría de sexo admitida (`ALL`, `FEMALE` o `MALE`).

Además he decidido añadir ALL, FEMALE o MALE al nombre de cada variable, según el sexo al que corresponda, ya que cada indicador está asociado a una única categoría.
Como en el dataset transformado elimino la columna SEX, de esta forma puedo seguir identificando qué variables corresponden a hombres, mujeres o población total, lo que me facilitará su selección en las siguientes partes del proyecto.


En la transformación se excluyen las observaciones con valores en `PLACE_RESIDENCE` o `YES_NO`, para evitar mezclar distintos desgloses en una misma columna.




## 5. Tests y cobertura

El proyecto utiliza `pytest` para realizar tests unitarios y de integración.

Para ejecutar todos los tests:

```bash
python -m pytest tests/ -v
```

Para calcular la cobertura de ambos módulos:

```bash
python -m pytest tests/ --cov=ventas_app --cov=who_app --cov-report=term-missing
```

Para exigir una cobertura mínima del 60 %:

```bash
python -m pytest tests/ --cov=ventas_app --cov=who_app --cov-report=term-missing --cov-fail-under=60
```

Los tests de integración comprueban el funcionamiento conjunto de los módulos de carga, validación, transformación y ejecución desde el CLI.

## 6. Integración continua

El repositorio incluye un workflow de GitHub Actions que ejecuta automáticamente los tests y comprueba la cobertura mínima del 60 %.

El workflow se encuentra en `.github/workflows/tests.yml`, en la raíz del repositorio Git.

## 7. Origen y licencia de los datos de la OMS

Los indicadores de salud utilizados proceden de la Organización Mundial de la Salud (OMS), concretamente de su base de datos europea **Health for All (HFA)**.


- **Fuente:** Organización Mundial de la Salud (OMS), base de datos European Health for All (HFA-DB).
- **Base de datos:** Health for All (HFA-DB).
- **Página oficial:** https://gateway.euro.who.int/en/datasets/european-health-for-all-database/?utm_source=chatgpt.com 
- **Formato utilizado:** archivos CSV.
- **Fecha de descarga:** 11/10/2026.
- **Licencia o condiciones de reutilización:** Creative Commons Attribution 4.0 International (CC BY 4.0), según las condiciones generales de la OMS, salvo que el dataset indique otras condiciones específicas. Condiciones de uso: https://data.who.int/about/data/terms-and-conditions 
- **Uso de los datos:** He utilizado estos datos con fines académicos y los he procesado y transformado para realizar el análisis del proyecto.

Los archivos originales se conservan localmente y no se incluyen necesariamente en el repositorio debido a su tamaño. 