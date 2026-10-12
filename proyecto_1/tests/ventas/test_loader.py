
from pathlib import Path

import pandas as pd
import pytest

from ventas_app.loader import (
    CsvSalesRepository,
    JsonSalesRepository,
    DataLoadError
)


def test_load_csv(tmp_path: Path):
    """Comprueba que se cargan correctamente los datos de un CSV."""

    # ARRANGE: creamos un CSV de prueba
    frame = pd.DataFrame({
        "region": ["Norte", "Sur"],
        "producto": ["A", "B"],
        "unidades": [2, 3],
        "precio_unitario": [10, 20]
    })

    csv_path = tmp_path / "ventas.csv"
    frame.to_csv(csv_path, index=False)

    # ACT: cargamos el archivo
    repository = CsvSalesRepository(csv_path)
    result = repository.load()

    # ASSERT: comprobamos el resultado
    pd.testing.assert_frame_equal(result, frame)


def test_load_json(tmp_path: Path):
    """Comprueba que se cargan correctamente los datos de un JSON."""

    frame = pd.DataFrame({
        "region": ["Norte", "Sur"],
        "producto": ["A", "B"],
        "unidades": [2, 3],
        "precio_unitario": [10, 20]
    })

    json_path = tmp_path / "ventas.json"
    frame.to_json(json_path, orient="records")

    repository = JsonSalesRepository(json_path)
    result = repository.load()

    pd.testing.assert_frame_equal(result, frame)


@pytest.mark.parametrize(
    "repository_class, filename",
    [
        (CsvSalesRepository, "no_existe.csv"),
        (JsonSalesRepository, "no_existe.json")
    ]
)
def test_file_not_found(tmp_path: Path, repository_class, filename):
    """Comprueba que se lanza DataLoadError si el archivo no existe."""

    file_path = tmp_path / filename
    repository = repository_class(file_path)

    with pytest.raises(DataLoadError):
        repository.load()