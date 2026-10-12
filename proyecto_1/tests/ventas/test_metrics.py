
import pytest

from ventas_app.metrics import SalesMetrics
from ventas_app.validator import SalesRecord


def create_test_data():
    """Crea una lista de ventas para las pruebas."""

    return [SalesRecord(region="Norte", product="A", units=2, unit_price=10),
        SalesRecord(region="Sur", product="B", units=3, unit_price=20),
        SalesRecord(region="Norte", product="C", units=4, unit_price=5)]


def test_total_by_region():
    """Comprueba el importe total calculado para cada región."""

    records = create_test_data()
    metrics = SalesMetrics()

    result = metrics.total_by_region(records)

    assert result["Norte"] == pytest.approx(40)
    assert result["Sur"] == pytest.approx(60)


def test_sum_same_region():
    """Comprueba que se suman las ventas de una misma región."""

    records = create_test_data()
    metrics = SalesMetrics()

    result = metrics.total_by_region(records)

    # Norte tiene dos ventas: 2*10 + 4*5 = 40
    assert result["Norte"] == 40
    assert len(result) == 2


def test_order_by_amount():
    """Comprueba que las regiones están ordenadas de mayor a menor."""
    records = create_test_data()
    metrics = SalesMetrics()
    result = metrics.total_by_region(records)

    assert list(result.keys()) == ["Sur", "Norte"]


def test_empty_records():
    """Comprueba el resultado cuando no existen ventas."""
    metrics = SalesMetrics()
    result = metrics.total_by_region([])

    assert result == {}