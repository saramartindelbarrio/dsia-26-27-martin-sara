# Diseño de ventas_app

Este proyecto está organizado en diferentes módulos para separar las responsabilidades del código y facilitar su mantenimiento.

## Principios SOLID aplicados

- **SRP (Principio de Responsabilidad Única) — `validator.py`:** La clase `SalesValidator` se encarga únicamente de validar los datos de ventas y separar los registros válidos de los inválidos. La carga de datos y el cálculo de métricas se realizan en otros módulos.

- **OCP (Principio Abierto/Cerrado) — `metrics.py`:** La clase `SalesMetrics` permite añadir nuevas métricas de ventas sin tener que modificar el código del validador ni del cargador de datos.

- **DIP (Principio de Inversión de Dependencias) — `loader.py` y `cli.py`:** Se utiliza el `Protocol` `SalesRepository` para definir cómo se deben cargar los datos. De esta forma, se pueden utilizar diferentes implementaciones, como CSV o JSON, sin cambiar la lógica principal de procesamiento.