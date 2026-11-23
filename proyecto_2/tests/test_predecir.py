import json

import joblib
import pandas as pd

from predecir import aplicar_modelo


def test_modelo_guardado_carga():
    modelo = joblib.load("models/random_forest.joblib")

    assert hasattr(modelo, "predict")


def test_inferencia_con_modelo_real():
    modelo = joblib.load("models/random_forest.joblib")

    with open("models/metadata.json", encoding="utf-8") as archivo:
        features = json.load(archivo)["features"]

    datos = pd.DataFrame([
        {
            "temperature_2m": 12.0,
            "wind_speed_10m": 10.0,
            "precipitation": 0.0,
            "relative_humidity_2m": 70.0,
            "dew_point_2m": 7.0,
            "cloud_cover_forecast": 65.0,
            "lead_days": 1,
        },
        {
            "temperature_2m": 11.0,
            "wind_speed_10m": 12.0,
            "precipitation": 0.0,
            "relative_humidity_2m": 75.0,
            "dew_point_2m": 7.0,
            "cloud_cover_forecast": 80.0,
            "lead_days": 3,
        },
        {
            "temperature_2m": 10.0,
            "wind_speed_10m": 8.0,
            "precipitation": 0.0,
            "relative_humidity_2m": 65.0,
            "dew_point_2m": 4.0,
            "cloud_cover_forecast": 40.0,
            "lead_days": 0,
        },
    ])

    resultado = aplicar_modelo(datos, modelo, features)

    assert len(resultado) == 3

    # El modelo produce nubosidad entre 0 y 100 %
    assert resultado["cloud_cover_predicted"].between(0, 100).all()

    # Los horizontes 1 y 3 utilizan Random Forest
    assert resultado.loc[0, "metodo"] == "random_forest"
    assert resultado.loc[1, "metodo"] == "random_forest"

    # El horizonte 0 mantiene la previsión original
    assert resultado.loc[2, "metodo"] == "open_meteo"
    assert resultado.loc[2, "cloud_cover_predicted"] == 40.0