
import numpy as np
import pytest

from evaluacion_final import calcular_metricas


def test_metricas_prediccion_perfecta():
    """Una predicción perfecta debe tener error cero y R² igual a 1."""

    y_real = np.array([0, 25, 50, 75, 100])
    y_pred = np.array([0, 25, 50, 75, 100])

    resultado = calcular_metricas(y_real, y_pred)

    assert resultado["mse"] == pytest.approx(0)
    assert resultado["mae"] == pytest.approx(0)
    assert resultado["rmse"] == pytest.approx(0)
    assert resultado["r2"] == pytest.approx(1)


def test_metricas_con_error():
    """Comprobar métricas usando valores conocidos."""

    y_real = np.array([0, 50, 100])
    y_pred = np.array([10, 40, 90])

    resultado = calcular_metricas(y_real, y_pred)

    # Errores absolutos: 10, 10 y 10
    assert resultado["mae"] == pytest.approx(10)

    # Errores cuadrados: 100, 100 y 100
    assert resultado["mse"] == pytest.approx(100)

    assert resultado["rmse"] == pytest.approx(10)

    # R² = 1 - 300 / 5000 = 0.94
    assert resultado["r2"] == pytest.approx(0.94)
