
import pandas as pd
import pytest
from who_app.validator import WHOValidator, ValidationError


# Creamos una función para generar datos de prueba
def create_test_data(year=2020, sex="ALL"):
    return pd.DataFrame({
        "Measure code": ["HFA_1"],
        "SEX": [sex],
        "PLACE_RESIDENCE": [None],
        "YES_NO": [None],
        "COUNTRY_REGION": ["ESP"],
        "YEAR": [year],
        "VALUE": [100]
    })


def test_valid_record():
    """Comprueba que una observación correcta es válida."""
    # ARRANGE
    frame = create_test_data()
    validator = WHOValidator()
    # ACT
    valid_rows, invalid_rows = validator.split(frame)
    # ASSERT
    assert len(valid_rows) == 1
    assert len(invalid_rows) == 0


@pytest.mark.parametrize("year",[None, -1, 0, 2020.5])#En lugar de escribir cuatro funciones distintas, pytest ejecutará el mismo test cuatro veces
def test_invalid_year(year):
    """Comprueba que los años incorrectos se consideran inválidos."""
    frame = create_test_data(year=year)
    validator = WHOValidator()
    valid_rows, invalid_rows = validator.split(frame)

    assert len(valid_rows) == 0
    assert len(invalid_rows) == 1


@pytest.mark.parametrize("sex",[None, "UNKNOWN", "OTRO"]) 
def test_invalid_sex(sex):
    """Comprueba que se rechazan categorías de sexo no permitidas."""
    frame = create_test_data(sex=sex)
    validator = WHOValidator()
    valid_rows, invalid_rows = validator.split(frame)

    assert len(valid_rows) == 0
    assert len(invalid_rows) == 1


def test_missing_column():
    """Comprueba que se lanza un error si falta una columna obligatoria."""
    frame = create_test_data()
    # Eliminamos una columna
    frame = frame.drop(columns=["VALUE"])
    validator = WHOValidator()
    with pytest.raises(ValidationError):
        validator.split(frame)