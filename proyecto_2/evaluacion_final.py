
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

from config import UBICACIONES_TEST


RUTA_DATOS = Path("data/processed/datos_ml.csv")
RUTA_MODELO = Path("models/random_forest.joblib")
RUTA_METADATA = Path("models/metadata.json")

CARPETA_RESULTADOS = Path("data/processed/evaluacion_final")
FECHA_CORTE = pd.Timestamp("2026-01-01", tz="UTC")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def calcular_metricas(y_real, y_pred):
    return {
        "n_muestras": len(y_real),
        "mse": mean_squared_error(y_real, y_pred),
        "mae": mean_absolute_error(y_real, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_real, y_pred)),
        "r2": r2_score(y_real, y_pred)
    }


def evaluar_conjunto(datos, escenario, modelo, features):
    resultados = []

    for horizonte in ["global", *range(1, 8)]:

        if horizonte == "global":
            subconjunto = datos
        else:
            subconjunto = datos[
                datos["lead_days"] == horizonte
            ]

        if len(subconjunto) < 2:
            logger.warning(
                "%s | Horizonte %s: sin muestras suficientes",
                escenario,
                horizonte
            )
            continue

        y_real = subconjunto["cloud_cover_actual"]

        pred_open_meteo = subconjunto[
            "cloud_cover_forecast"
        ].to_numpy()

        pred_rf = np.clip(
            modelo.predict(subconjunto[features]),
            0,
            100
        )

        for nombre_modelo, predicciones in [
            ("open_meteo", pred_open_meteo),
            ("random_forest", pred_rf)
        ]:
            metricas = calcular_metricas(
                y_real,
                predicciones
            )

            resultados.append({
                "escenario": escenario,
                "lead_days": horizonte,
                "modelo": nombre_modelo,
                **metricas
            })

    return resultados


def main():
    CARPETA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    logger.info("Cargando modelo definitivo")

    modelo = joblib.load(RUTA_MODELO)

    with RUTA_METADATA.open(encoding="utf-8") as archivo:
        metadata = json.load(archivo)

    features = metadata["features"]

    datos = pd.read_csv(RUTA_DATOS)
    datos["time"] = pd.to_datetime(
        datos["time"],
        utc=True
    )

    columnas = features + [
        "time",
        "nombre",
        "cloud_cover_actual"
    ]

    faltantes = set(columnas) - set(datos.columns)

    if faltantes:
        raise ValueError(
            f"Faltan columnas: {sorted(faltantes)}"
        )

    # No eliminar silenciosamente observaciones del test.
    if datos[columnas].isna().any().any():
        raise ValueError(
            "Hay valores ausentes en los datos de evaluación."
        )

    # 1. Generalización temporal
    test_temporal = datos[
        (datos["time"] >= FECHA_CORTE)
        & (~datos["nombre"].isin(UBICACIONES_TEST))
    ].copy()

    # 2. Generalización geográfica
    test_geografico = datos[
        (datos["time"] < FECHA_CORTE)
        & (datos["nombre"].isin(UBICACIONES_TEST))
    ].copy()

    # 3. Generalización temporal y geográfica
    test_combinado = datos[
        (datos["time"] >= FECHA_CORTE)
        & (datos["nombre"].isin(UBICACIONES_TEST))
    ].copy()

    escenarios = {
        "temporal": test_temporal,
        "geografico": test_geografico,
        "combinado": test_combinado
    }

    resultados = []

    for nombre, conjunto in escenarios.items():

        logger.info(
            "Escenario %s: %s filas",
            nombre,
            len(conjunto)
        )

        if conjunto.empty:
            raise ValueError(
                f"El escenario {nombre} no contiene datos."
            )

        resultados.extend(
            evaluar_conjunto(
                conjunto,
                nombre,
                modelo,
                features
            )
        )

    resultado_df = pd.DataFrame(resultados)

    ruta = CARPETA_RESULTADOS / "resultados_finales.xlsx"

    with pd.ExcelWriter(
        ruta,
        engine="openpyxl"
    ) as writer:

        resultado_df.to_excel(
            writer,
            sheet_name="Resultados",
            index=False
        )

        globales = resultado_df[
            resultado_df["lead_days"] == "global"
        ]

        globales.to_excel(
            writer,
            sheet_name="Resumen_global",
            index=False
        )

        for escenario in escenarios:
            resultado_df[
                resultado_df["escenario"] == escenario
            ].to_excel(
                writer,
                sheet_name=escenario.capitalize(),
                index=False
            )

    logger.info("Resultados guardados en %s", ruta)

    print("\n===== EVALUACIÓN FINAL =====")
    print(
        globales[
            [
                "escenario",
                "modelo",
                "n_muestras",
                "mse",
                "mae",
                "rmse",
                "r2"
            ]
        ].round(4).to_string(index=False)
    )


if __name__ == "__main__":
    main()
