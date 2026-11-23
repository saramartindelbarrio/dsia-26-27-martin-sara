#Test de integracion sin llamar a la API por si esta muy saturada
import pytest

from datetime import timedelta
import pandas as pd
import predecir


@pytest.mark.integracion
def test_integracion_predicciones(monkeypatch, tmp_path):

    # 1. Simular los datos de Forecast API
    # Usamos horas futuras respecto al momento del test
    ahora = pd.Timestamp.now(tz="UTC").floor("h")

    datos_simulados = pd.DataFrame({
        "time": [
            ahora + timedelta(hours=3),
            ahora + timedelta(hours=30),
            ahora + timedelta(hours=72),
        ],
        "temperature_2m": [12.0, 11.0, 10.0],
        "wind_speed_10m": [10.0, 12.0, 8.0],
        "precipitation": [0.0, 0.0, 0.0],
        "relative_humidity_2m": [70.0, 75.0, 65.0],
        "dew_point_2m": [7.0, 7.0, 4.0],
        "cloud_cover": [90.0, 65.0, 40.0],
    })
    # 2. Simular la búsqueda de Madrid
    def buscar_ubicacion_simulada(nombre, pais=None, resultado=1):
        assert nombre == "Madrid"

        return {
            "id": 3117735,
            "name": "Madrid",
            "country_code": "ES",
            "latitude": 40.4165,
            "longitude": -3.70256,
            "timezone": "Europe/Madrid"
        }

    monkeypatch.setattr(
        predecir,
        "buscar_ubicacion",
        buscar_ubicacion_simulada
    )

    # 3. Simular la descarga de Open-Meteo
    def forecast_simulado(nombre, latitud, longitud, modelo=None):

        assert nombre == "madrid_es_3117735"
        assert latitud == 40.4165
        assert longitud == -3.70256

        return datos_simulados.copy()

    monkeypatch.setattr(
        predecir,
        "descargar_forecast",
        forecast_simulado
    )

    # 4. Guardar las predicciones en una carpeta temporal
    monkeypatch.setattr(
        predecir,
        "CARPETA_SALIDA",
        tmp_path
    )

    # 5. Ejecutar el flujo completo
    resultado = predecir.predecir_ubicacion(
        ubicacion="Madrid",
        pais="ES"
    )

    # 6. Comprobar el resultado
    assert len(resultado) == 3

    assert "cloud_cover_forecast" in resultado.columns
    assert "cloud_cover_predicted" in resultado.columns
    assert "metodo" in resultado.columns
    assert "zona_horaria" in resultado.columns

    assert (
        resultado["zona_horaria"] == "Europe/Madrid"
    ).all()

    assert resultado["cloud_cover_predicted"].between(
        0, 100
    ).all()

    # 7. Comprobar que se ha generado el CSV
    ruta_esperada = (
        tmp_path / "predicciones_madrid_es_3117735.csv"
    )

    assert ruta_esperada.exists()

    datos_guardados = pd.read_csv(ruta_esperada)

    assert len(datos_guardados) == 3