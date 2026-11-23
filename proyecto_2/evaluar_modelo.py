
import logging
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

from config import UBICACIONES_TEST

# CONFIGURACIÓN


RUTA_DATOS = Path("data/processed/datos_ml.csv")
CARPETA_RESULTADOS = Path("data/processed/comparacion_hiperparametros")

FIN_ENTRENAMIENTO = pd.Timestamp("2026-01-01", tz="UTC")

FEATURES = [
    "temperature_2m",
    "wind_speed_10m",
    "precipitation",
    "relative_humidity_2m",
    "dew_point_2m",
    "cloud_cover_forecast",
    "lead_days"
]

TARGET = "cloud_cover_actual"

VALORES_N_ESTIMATORS = [50, 100]
VALORES_MAX_DEPTH = [6, 8]
VALORES_MIN_SAMPLES_LEAF = [10, 20]

NUM_FOLDS = 4
GAP_HORAS = 168

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)



# 1. CARGAR DATOS


def cargar_datos():

    datos = pd.read_csv(
        RUTA_DATOS,
        parse_dates=["time"]
    )

    datos["time"] = pd.to_datetime(
        datos["time"],
        utc=True
    )

    # Reservar el test temporal de 2026 y
    # las ciudades del test geográfico.
    datos = datos[
        (datos["time"] < FIN_ENTRENAMIENTO)
        & (~datos["nombre"].isin(UBICACIONES_TEST))
    ].copy()

    columnas_necesarias = FEATURES + [TARGET, "time"]

    datos = datos.dropna(subset=columnas_necesarias)

    datos = datos.sort_values(
        ["time", "nombre", "lead_days"]
    ).reset_index(drop=True)

    if datos.empty:
        raise ValueError("No hay datos para validar.")

    logger.info(
        "Ubicaciones de entrenamiento: %s",
        datos["nombre"].unique().tolist()
    )

    logger.info("Número de filas: %s", len(datos))

    return datos



# 2. CALCULAR MÉTRICAS


def calcular_metricas(y_real, y_predicho):
    """Calcular métricas para una partición."""

    n = len(y_real)
    p = len(FEATURES)

    if n < 2:
        raise ValueError(
            "Se necesitan al menos 2 muestras."
        )

    mse = mean_squared_error(y_real, y_predicho)
    mae = mean_absolute_error(y_real, y_predicho)
    rmse = np.sqrt(mse)

    r2 = r2_score(y_real, y_predicho)

    return {
        "n_muestras": n,
        "mse": mse,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


# 3. EVALUAR UNA COMBINACIÓN


def evaluar_combinacion(datos, parametros):

    horas = (
        datos["time"]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    tscv = TimeSeriesSplit(
        n_splits=NUM_FOLDS,
        gap=GAP_HORAS
    )

    resultados = []

    for fold, (idx_train, idx_val) in enumerate(
        tscv.split(horas),
        start=1
    ):

        horas_train = horas.iloc[idx_train]
        horas_val = horas.iloc[idx_val]

        df_train = datos[
            datos["time"].isin(horas_train)
        ]

        df_val = datos[
            datos["time"].isin(horas_val)
        ]

        logger.info(
            "Fold %s | Entrenamiento: %s a %s",
            fold,
            horas_train.min(),
            horas_train.max()
        )

        logger.info(
            "Fold %s | Validación: %s a %s",
            fold,
            horas_val.min(),
            horas_val.max()
        )

        X_train = df_train[FEATURES]
        y_train = df_train[TARGET]

        X_val = df_val[FEATURES]
        y_val = df_val[TARGET]

        modelo = RandomForestRegressor(
            n_estimators=parametros["n_estimators"],
            max_depth=parametros["max_depth"],
            min_samples_leaf=parametros["min_samples_leaf"],
            random_state=42,
            n_jobs=-1
        )

        # Entrenar una sola vez por fold
        modelo.fit(X_train, y_train)

        pred_train = np.clip(
            modelo.predict(X_train), 0, 100
        )

        pred_val = np.clip(
            modelo.predict(X_val), 0, 100
        )

        # Comparar cada horizonte de 1 a 7 días
        for day in range(1, 8):

            mascara_train = (
                df_train["lead_days"] == day
            ).to_numpy()

            mascara_val = (
                df_val["lead_days"] == day
            ).to_numpy()

            if not mascara_train.any() or not mascara_val.any():
                raise ValueError(
                    f"No hay datos para el día {day} "
                    f"en el fold {fold}."
                )

            particiones = {
                "train": (
                    df_train.loc[
                        mascara_train, TARGET
                    ],
                    df_train.loc[
                        mascara_train, "cloud_cover_forecast"
                    ],
                    pred_train[mascara_train]
                ),
                "val": (
                    df_val.loc[
                        mascara_val, TARGET
                    ],
                    df_val.loc[
                        mascara_val, "cloud_cover_forecast"
                    ],
                    pred_val[mascara_val]
                )
            }

            for particion, valores in particiones.items():

                y_real, pred_baseline, pred_rf = valores

                metricas_baseline = calcular_metricas(
                    y_real,
                    pred_baseline
                )

                metricas_rf = calcular_metricas(
                    y_real,
                    pred_rf
                )

                fila = {
                    "fold": fold,
                    "lead_days": day,
                    "particion": particion,
                    **parametros
                }

                for nombre, valor in metricas_baseline.items():
                    fila[f"{nombre}_baseline"] = valor

                for nombre, valor in metricas_rf.items():
                    fila[f"{nombre}_rf"] = valor

                resultados.append(fila)

    return pd.DataFrame(resultados)


# 4. GUARDAR UN EXCEL POR COMBINACIÓN


def guardar_excel(resultado, parametros):

    nombre = (
        f"rf_n{parametros['n_estimators']}"
        f"_depth{parametros['max_depth']}"
        f"_leaf{parametros['min_samples_leaf']}.xlsx"
    )

    ruta = CARPETA_RESULTADOS / nombre

    # Resumir únicamente la validación,
    # sin mezclar métricas de entrenamiento.
    validacion = resultado[
        resultado["particion"] == "val"
    ].copy()

    columnas_metricas = [
        "mse_baseline",
        "mse_rf",
        "mae_baseline",
        "mae_rf",
        "rmse_baseline",
        "rmse_rf",
        "r2_baseline",
        "r2_rf",
    ]

    resumen_dia = (
        validacion
        .groupby("lead_days")[columnas_metricas]
        .mean()
        .reset_index()
    )

    resumen_fold = (
        validacion
        .groupby("fold")[columnas_metricas]
        .mean()
        .reset_index()
    )

    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:

        resultado.to_excel(
            writer,
            sheet_name="Detalle",
            index=False
        )

        resumen_dia.to_excel(
            writer,
            sheet_name="Resumen_por_dia",
            index=False
        )

        resumen_fold.to_excel(
            writer,
            sheet_name="Resumen_por_fold",
            index=False
        )

        pd.DataFrame([parametros]).to_excel(
            writer,
            sheet_name="Hiperparametros",
            index=False
        )

        # Mejorar legibilidad en Excel
        for hoja in writer.book.worksheets:
            hoja.freeze_panes = "A2"
            hoja.auto_filter.ref = hoja.dimensions

            for columna in hoja.columns:
                letra = columna[0].column_letter
                longitud = max(
                    len(str(celda.value))
                    if celda.value is not None else 0
                    for celda in columna
                )

                hoja.column_dimensions[letra].width = min(
                    longitud + 2,
                    28
                )

                for celda in columna[1:]:
                    if isinstance(celda.value, float):
                        celda.number_format = "0.0000"

    logger.info("Excel guardado: %s", ruta)

    return validacion



# 5. PROBAR TODAS LAS COMBINACIONES
def main():

    CARPETA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    datos = cargar_datos()

    combinaciones = list(product(
        VALORES_N_ESTIMATORS,
        VALORES_MAX_DEPTH,
        VALORES_MIN_SAMPLES_LEAF
    ))

    logger.info(
        "Combinaciones que se evaluarán: %s",
        len(combinaciones)
    )

    resumen_general = []

    for indice, (n, depth, leaf) in enumerate(
        combinaciones,
        start=1
    ):

        parametros = {
            "n_estimators": n,
            "max_depth": depth,
            "min_samples_leaf": leaf
        }

        logger.info(
            "Combinación %s/%s: %s",
            indice,
            len(combinaciones),
            parametros
        )

        resultado = evaluar_combinacion(
            datos,
            parametros
        )

        validacion = guardar_excel(
            resultado,
            parametros
        )

        # Resumir los resultados de validación
        fila_resumen = parametros.copy()

        for metrica in [
            "mse",
            "mae",
            "rmse",
            "r2",
        ]:
            for modelo in ["baseline", "rf"]:
                columna = f"{metrica}_{modelo}"
                fila_resumen[columna] = (
                    validacion[columna].mean()
                )

        fila_resumen["mejora_mse"] = (
            fila_resumen["mse_baseline"]
            - fila_resumen["mse_rf"]
        )

        resumen_general.append(fila_resumen)

    resumen_df = pd.DataFrame(resumen_general)

    # La mejor combinación tendrá menor MSE
    resumen_df = resumen_df.sort_values(
        "mse_rf",
        ascending=True
    ).reset_index(drop=True)

    ruta_resumen = (
        CARPETA_RESULTADOS
        / "resumen_hiperparametros.xlsx"
    )

    with pd.ExcelWriter(
        ruta_resumen,
        engine="openpyxl"
    ) as writer:

        resumen_df.to_excel(
            writer,
            sheet_name="Comparacion",
            index=False
        )

        hoja = writer.book["Comparacion"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        for columna in hoja.columns:
            letra = columna[0].column_letter
            longitud = max(
                len(str(celda.value))
                if celda.value is not None else 0
                for celda in columna
            )
            hoja.column_dimensions[letra].width = min(
                longitud + 2, 28
            )

            for celda in columna[1:]:
                if isinstance(celda.value, float):
                    celda.number_format = "0.0000"

    logger.info("Resumen guardado: %s", ruta_resumen)

    print("\n===== COMPARACIÓN DE HIPERPARÁMETROS =====")

    print(
        resumen_df[
            [
                "n_estimators",
                "max_depth",
                "min_samples_leaf",
                "mse_baseline",
                "mse_rf",
                "mae_rf",
                "r2_rf",
            ]
        ].round(4).to_string(index=False)
    )

    print("\n===== MEJOR COMBINACIÓN SEGÚN MSE =====")

    mejor = resumen_df.iloc[0]

    print(
        f"n_estimators: {int(mejor['n_estimators'])}"
    )
    print(
        f"max_depth: {int(mejor['max_depth'])}"
    )
    print(
        f"min_samples_leaf: "
        f"{int(mejor['min_samples_leaf'])}"
    )
    print(f"MSE validación: {mejor['mse_rf']:.4f}")
    print(f"MAE validación: {mejor['mae_rf']:.4f}")
    print(f"R² validación: {mejor['r2_rf']:.4f}")


if __name__ == "__main__":
    main()
