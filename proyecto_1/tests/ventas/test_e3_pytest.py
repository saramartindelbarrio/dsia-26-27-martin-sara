
from pathlib import Path

import pandas as pd
import pytest

from ventas_app.loader import CsvSalesRepository, DataLoadError
from ventas_app.validator import SalesValidator


# PARTE 1: Fixture en memoria

@pytest.fixture
def ventas_mini():
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })


def test_validacion_ventas_mini(ventas_mini):
    validas, invalidas = SalesValidator().split(ventas_mini)

    assert len(validas) == 1
    assert len(invalidas) == 2


# PARTE 2: Errores y casos límite

def test_archivo_inexistente(tmp_path):
    ruta = tmp_path / "no_existe.csv"

    with pytest.raises(DataLoadError):
        CsvSalesRepository(ruta).load()


@pytest.mark.parametrize(
    "precio, es_valido",
    [
        (0, False),
        (-1, False),
        (1, True),
    ]
)
def test_precios_limite(precio, es_valido):
    frame = pd.DataFrame({
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [2],
        "precio_unitario": [precio],
    })

    validas, invalidas = SalesValidator().split(frame)

    assert (len(validas) == 1) == es_valido
    assert (len(invalidas) == 0) == es_valido


# PARTE 3: Integración con el CSV del curso

@pytest.mark.integration
def test_csv_curso_tiene_140_validas_y_10_invalidas():
    ruta = (
        Path(__file__).resolve().parents[2]
        / "Datos"
        / "ventas"
        / "ventas.csv"
    )

    frame = CsvSalesRepository(ruta).load()
    validas, invalidas = SalesValidator().split(frame)

    assert len(validas) == 140
    assert len(invalidas) == 10