import logging
from pathlib import Path
from config import UBICACIONES, VARIABLES
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

CARPETA_RAW = Path("data/raw")
CARPETA_PROCESSED = Path("data/processed")


def procesar_ubicacion(nombre):
    ruta_previous = CARPETA_RAW / f"{nombre}_previous_runs.csv"
    ruta_era5 = CARPETA_RAW / f"{nombre}_era5.csv"

    previous = pd.read_csv(ruta_previous, parse_dates=["time"])
    previous.columns = (previous.columns.str.replace(r"\s*\(.*?\)", "", regex=True).str.strip())
    previous["time"] = pd.to_datetime(previous["time"], utc=True)

    
    era5 = pd.read_csv(ruta_era5, parse_dates=["time"])
    era5.columns = (era5.columns.str.replace(r"\s*\(.*?\)", "", regex=True).str.strip())
    era5["time"] = pd.to_datetime(era5["time"], utc=True)

    # Comprobar que no hay horas repetidas
    if previous["time"].duplicated().any():
        raise ValueError("Fechas duplicadas en Previous Runs")

    if era5["time"].duplicated().any():
        raise ValueError("Fechas duplicadas en ERA5")

    # Renombrar la nubosidad de referencia
    era5 = era5.rename(
        columns={"cloud_cover": "cloud_cover_actual"}
    )

    # Unir los dos conjuntos por fecha UTC
    datos = previous.merge(
        era5[["time", "cloud_cover_actual"]],
        on="time",
        how="inner",
        validate="one_to_one",
    )

    logger.info(
        "%s: %s horas coincidentes",
        nombre,
        len(datos),
    )

    # Pasar de formato ancho a formato largo:
    # una fila por hora y día de antelación
    bloques = []

    for dia in range(1, 8):
        columnas = {
            f"{variable}_previous_day{dia}": variable
            for variable in VARIABLES
        }

        bloque = datos[
            ["time", "cloud_cover_actual", *columnas.keys()]
        ].rename(columns=columnas).copy()

        bloque = bloque.rename(
            columns={"cloud_cover": "cloud_cover_forecast"}
        )

        bloque["lead_days"] = dia
        bloque["nombre"] = nombre

        bloques.append(bloque)

    datos_ml = pd.concat(bloques, ignore_index=True)

    # Quitar filas sin alguna variable necesaria
    filas_antes = len(datos_ml)
    datos_ml = datos_ml.dropna(
        subset=[
            "cloud_cover_actual",
            "cloud_cover_forecast",
            "temperature_2m",
            "wind_speed_10m",
            "precipitation",
            "relative_humidity_2m",
            "dew_point_2m",
        ]
    )

    logger.info(
        "%s: eliminadas %s filas incompletas",
        nombre,
        filas_antes - len(datos_ml),
    )

    return datos_ml


def main():
    bloques = []

    for ubicacion in UBICACIONES:
        ubicacion_nombre = ubicacion["nombre"]
        logger.info("Procesando %s", ubicacion_nombre)
        bloques.append(procesar_ubicacion(ubicacion_nombre))

    datos_ml = pd.concat(bloques, ignore_index=True)
    # Asegurar que todas las ubicaciones utilizan UTC
    datos_ml["time"] = pd.to_datetime(
        datos_ml["time"],
        utc=True
    )
    # Ordenar cronológicamente
    datos_ml = datos_ml.sort_values(
        ["time", "nombre", "lead_days"]
    ).reset_index(drop=True)

    CARPETA_PROCESSED.mkdir(parents=True, exist_ok=True)

    ruta = CARPETA_PROCESSED / "datos_ml.csv"
    datos_ml.to_csv(ruta, index=False)

    logger.info("Datos preparados: %s", ruta)
    logger.info("Filas: %s | Columnas: %s", *datos_ml.shape)


if __name__ == "__main__":
    main()