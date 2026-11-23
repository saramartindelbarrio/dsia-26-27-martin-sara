
import logging
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from config import UBICACIONES_TEST
# CONFIGURACIÓN

RUTA_DATOS = Path("data/processed/datos_ml.csv")
CARPETA_MODELOS = Path("models")

# Reservamos 2026 para el test final
FIN_ENTRENAMIENTO = pd.Timestamp(
    "2026-01-01", tz="UTC"
)

FEATURES = [
    "temperature_2m",
    "wind_speed_10m",
    "precipitation",
    "relative_humidity_2m",
    "dew_point_2m",
    "cloud_cover_forecast",
    "lead_days",
]

TARGET = "cloud_cover_actual"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)



# CARGAR DATOS
def cargar_datos():
    datos = pd.read_csv(
        RUTA_DATOS,
        parse_dates=["time"]
    )

    datos = datos[
        ~datos["nombre"].isin(UBICACIONES_TEST)
    ].copy()

    columnas_necesarias = FEATURES + [TARGET, "time"]

    faltantes = [
        columna for columna in columnas_necesarias
        if columna not in datos.columns
    ]

    if faltantes:
        raise ValueError(
            f"Faltan columnas en el dataset: {faltantes}"
        )

    # No usar datos del test de 2026
    datos = datos[
        datos["time"] < FIN_ENTRENAMIENTO
    ].copy()

    # Eliminar filas incompletas
    datos = datos.dropna(
        subset=columnas_necesarias
    )

    if datos.empty:
        raise ValueError("No hay datos para entrenar")

    # Evitar entrenar con la descarga de prueba
    horas = datos["time"].nunique()

    if horas < 24 * 30:
        raise ValueError(
            "Hay menos de 30 días de datos horarios. "
            "Descarga primero el histórico completo."
        )

    logger.info("Filas para entrenamiento: %s", len(datos))
    logger.info(
        "Periodo: %s hasta %s",
        datos["time"].min(),
        datos["time"].max()
    )

    return datos


# ENTRENAR RANDOM FOREST

def entrenar_modelo(datos):
    X = datos[FEATURES]
    y = datos[TARGET]

    modelo = RandomForestRegressor(
        n_estimators=100,
        max_depth=8, #Probé con otros hiperparámetro y fueron los que menor mse medio dieron
        min_samples_leaf=20,
        random_state=42,
        n_jobs=-1
    )
    logger.info(
        "Entrenando Random Forest | "
        "n_estimators=%s | max_depth=%s | min_samples_leaf=%s",
        modelo.n_estimators,
        modelo.max_depth,
        modelo.min_samples_leaf
    )
        

    modelo.fit(X, y)

    predicciones_train = np.clip(
        modelo.predict(X), 0, 100
    )

    mse = mean_squared_error(y, predicciones_train)
    mae = mean_absolute_error(y, predicciones_train)
    rmse = np.sqrt(mse)

    logger.info("MSE entrenamiento: %.2f", mse)
    logger.info("MAE entrenamiento: %.2f", mae)
    logger.info("RMSE entrenamiento: %.2f", rmse)

    return modelo


# GUARDAR MODELO

def guardar_modelo(modelo, datos):
    CARPETA_MODELOS.mkdir(
        parents=True, exist_ok=True
    )

    ruta_modelo = CARPETA_MODELOS / "random_forest.joblib"

    joblib.dump(modelo, ruta_modelo)

    # Metadatos para recordar cómo se entrenó
    metadatos = {
        "algoritmo": "RandomForestRegressor",
        "max_depth": modelo.max_depth,
        "min_samples_leaf": modelo.min_samples_leaf,
        "n_estimators": modelo.n_estimators,
        "features": FEATURES,
        "target": TARGET,
        "fecha_inicio": str(datos["time"].min()),
        "fecha_fin": str(datos["time"].max()),
        "n_filas": len(datos),
        "ubicaciones": (
            sorted(datos["nombre"].unique().tolist())
            if "nombre" in datos.columns else []
        ),
    }

    ruta_metadata = CARPETA_MODELOS / "metadata.json"

    with open(ruta_metadata, "w", encoding="utf-8") as archivo:
        json.dump(
            metadatos, archivo,
            indent=4,
            ensure_ascii=False
        )

    logger.info("Modelo guardado: %s", ruta_modelo)
    logger.info("Metadatos guardados: %s", ruta_metadata)


# EJECUCIÓN

def main():
    datos = cargar_datos()

    modelo = entrenar_modelo(datos)

    guardar_modelo(modelo, datos)

    logger.info("Entrenamiento finalizado")


if __name__ == "__main__":
    main()
