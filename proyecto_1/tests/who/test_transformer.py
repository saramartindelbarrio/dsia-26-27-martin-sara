
import pandas as pd
import pytest
from who_app.transformer import WHOTransformer, DataTransformationError


# Crear datos de prueba
def create_test_data():
    return pd.DataFrame({
        "Measure code": ["HFA_1", "HFA_1", "HFA_219","HFA_229", "HFA_520"],
        "SEX": [ "ALL", "ALL", "MALE","FEMALE", "ALL"],
        "PLACE_RESIDENCE": [None] * 5,
        "YES_NO": [None] * 5,
        "COUNTRY_REGION": ["ESP", "FRA", "ESP", "ESP", "ESP"],
        "YEAR": [2020, 2020, 2020, 2020, 2020],
        "VALUE": [100, 200, 50, 45, 80]})


def test_select_measures():
    """Comprueba que solo se seleccionan los indicadores indicados."""

    # ARRANGE
    frame = create_test_data()
    transformer = WHOTransformer()

    # ACT
    result = transformer.transform(
        frame,
        selected_measures=["HFA_1", "HFA_219", "HFA_229"]
    )

    # ASSERT
    assert "HFA_1_ALL" in result.columns
    assert "HFA_219_MALE" in result.columns
    assert "HFA_229_FEMALE" in result.columns
    assert "HFA_520_ALL" not in result.columns


def test_sex_columns():
    """Comprueba que no se crean columnas de sexos inexistentes."""
    frame = create_test_data()
    transformer = WHOTransformer()

    result = transformer.transform(
        frame,
        selected_measures=["HFA_1"]
    )

    assert "HFA_1_ALL" in result.columns
    assert "HFA_1_MALE" not in result.columns
    assert "HFA_1_FEMALE" not in result.columns


def test_invalid_measure():
    """Comprueba que se lanza un error si el indicador no existe."""

    frame = create_test_data()
    transformer = WHOTransformer()

    with pytest.raises(DataTransformationError):
        transformer.transform(
            frame,
            selected_measures=["HFA_9999"]
        )


def test_duplicate_records():
    """Comprueba que se detectan observaciones duplicadas."""

    frame = create_test_data()

    # Duplicamos la primera fila
    duplicate = frame.iloc[[0]].copy()

    frame = pd.concat(
        [frame, duplicate],
        ignore_index=True
    )

    transformer = WHOTransformer()

    with pytest.raises(DataTransformationError):
        transformer.transform(
            frame,
            selected_measures=["HFA_1"]
        )