
# Ejercicio E3 — Tests con pytest

En este ejercicio he realizado pruebas con `pytest` sobre el pipeline de ventas desarrollado en el Proyecto I, utilizando las clases `SalesValidator` y `CsvSalesRepository` de `ventas_app`.

El objetivo es practicar el uso de fixtures, la validación de errores, los tests parametrizados y los tests de integración.

## 1. Estructura

```text
dsia-26-27-martin-sara/
├── proyecto_1/
│   ├── ventas_app/
│   └── Datos/
│       └── ventas/
│           └── ventas.csv
│
└── 2_pruebas_y_despliegue/
    ├── test_e3_pytest.py
    ├── pytest.ini
    └── README.md
```

## 2. Tests realizados

He implementado las siguientes pruebas:

- **Fixture en memoria:** he creado un DataFrame con tres ventas para comprobar que el validador identifica una venta válida y dos inválidas.
- **Archivo inexistente:** utilizo `pytest.raises` para comprobar que se lanza `DataLoadError` cuando intento cargar un archivo que no existe.
- **Tests parametrizados:** compruebo el comportamiento del validador con precios `0`, `-1` y `1`, verificando que únicamente el último es válido.
- **Test de integración:** utilizo el archivo `ventas.csv` del curso para comprobar que contiene 140 registros válidos y 10 inválidos.

## 3. Instalación

Desde la carpeta `ejercicio_E3`, creo y activo el entorno virtual:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Instalo las dependencias necesarias:

```bash
python -m pip install pandas pytest
```

## 4. Ejecución de los tests

Como reutilizo las clases de `ventas_app`, que se encuentran dentro de `proyecto_1`, necesito indicar su ubicación mediante `PYTHONPATH`.

Desde la raíz del repositorio `dsia-26-27-martin-sara`, con el entorno virtual activado:

**Ejecutar todos los tests:**

```bash
PYTHONPATH=proyecto_1 python -m pytest 2_pruebas_y_despliegue/test_e3_pytest.py -v
```

**Ejecutar los tests excluyendo el de integración:**

```bash
PYTHONPATH=proyecto_1 python -m pytest 2_pruebas_y_despliegue/test_e3_pytest.py -v -m "not integration"
```

El marcador `integration` está registrado en `pytest.ini`.

## 5. Resultados esperados

Al ejecutar todos los tests, espero obtener seis casos superados:

- 1 test con la fixture.
- 1 test de archivo inexistente.
- 3 casos parametrizados.
- 1 test de integración con el CSV del curso.

El test de integración requiere que el archivo original `ventas.csv` esté disponible en `proyecto_1/Datos/ventas/`.