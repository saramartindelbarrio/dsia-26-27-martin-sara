
from pathlib import Path
import pandas as pd
import pytest
from who_app.loader import WHOLoader, DataLoadError


def test_load_csv_correctly(tmp_path: Path):
    """Comprueba que se cargan y unen varios CSV."""

        # ARRANGE: preparar los datos de prueba
    df1 = pd.DataFrame({
        "Measure code": ["HFA_1"],
        "SEX": ["ALL"],
        "PLACE_RESIDENCE": [None],
        "YES_NO": [None],
        "COUNTRY_REGION": ["ESP"],
        "YEAR": [2020],
        "VALUE": [100]
    })

    df2 = pd.DataFrame({
        "Measure code": ["HFA_1"],
        "SEX": ["ALL"],
        "PLACE_RESIDENCE": [None],
        "YES_NO": [None],
        "COUNTRY_REGION": ["FRA"],
        "YEAR": [2020],
        "VALUE": [200]
    })

    df1.to_csv(tmp_path / "parte1.csv", index=False)
    df2.to_csv(tmp_path / "parte2.csv", index=False)

    # ACT: ejecutar el método que queremos probar
    loader = WHOLoader()
    result = loader.load(tmp_path)

    # ASSERT: comprobar el resultado
    assert len(result) == 2
    assert set(result["COUNTRY_REGION"]) == {"ESP", "FRA"}
    assert result.shape == (2, 7)


def test_load_folder_not_found(tmp_path: Path):
    """Comprueba que se lanza un error si la carpeta no existe."""

    nonexistent_folder = tmp_path / "no_existe"

    loader = WHOLoader()

    with pytest.raises(DataLoadError):
        loader.load(nonexistent_folder)


def test_load_empty_folder(tmp_path: Path):
    """Comprueba que se lanza un error si no hay archivos CSV."""

    loader = WHOLoader()

    with pytest.raises(DataLoadError):
        loader.load(tmp_path)