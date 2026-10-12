
import pandas as pd
import pytest

from ventas_app.validator import SalesValidator, SalesRecord


def create_test_data():
    """Crea un DataFrame con ventas válidas e inválidas."""

    return pd.DataFrame({
        "region": ["Norte", "Sur", "Este", "Oeste"],
        "producto": ["A", "B", "C", "D"],
        "unidades": [2, 3, -1, 0],
        "precio_unitario": [10, 20, 15, 30]
    })


def test_split_valid_invalid():
    """Comprueba que separa correctamente ventas válidas e inválidas."""

    # ARRANGE
    frame = create_test_data()
    validator = SalesValidator()

    # ACT
    valid_records, invalid_rows = validator.split(frame)

    # ASSERT
    assert len(valid_records) == 2
    assert len(invalid_rows) == 2


def test_sales_record():
    """Comprueba que las ventas válidas se convierten en SalesRecord."""

    frame = create_test_data()
    validator = SalesValidator()

    valid_records, invalid_rows = validator.split(frame)

    assert isinstance(valid_records[0], SalesRecord)
    assert valid_records[0].region == "Norte"
    assert valid_records[0].product == "A"
    assert valid_records[0].units == 2
    assert valid_records[0].unit_price == 10


def test_amount():
    """Comprueba que el importe se calcula correctamente."""

    record = SalesRecord(
        region="Norte",
        product="A",
        units=2,
        unit_price=10
    )

    assert record.amount == 20


@pytest.mark.parametrize(
    "units, price",
    [
        (0, 10),
        (-2, 10),
        ("abc", 10),
        (2, 0),
        (2, -5),
        (2, "abc"),
        (None, 10)
    ]
)
def test_invalid_sales(units, price):
    """Comprueba que se rechazan unidades y precios incorrectos."""

    frame = pd.DataFrame({
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [units],
        "precio_unitario": [price]
    })

    validator = SalesValidator()

    valid_records, invalid_rows = validator.split(frame)

    assert len(valid_records) == 0
    assert len(invalid_rows) == 1