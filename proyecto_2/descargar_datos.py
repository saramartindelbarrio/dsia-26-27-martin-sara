
#1. Descarga de datos para el modelo:
#1.1 Previous Runs que son las previsiones históricas de los 1-7 días anterioes que uso para entrenar el modelo
#1.2 ERA5 es la nubosidad histórica con la que comparo las previsiones (Y)

#2. Descarga de datos para previsiones en el momento
#2.1 Forecast API 


import argparse
import logging
import time
from pathlib import Path
from config import UBICACIONES, VARIABLES, VARIABLES_ERA5
from datetime import timedelta
import pandas as pd
import requests

#CONFIGURACIÓN 
URL_PREVIOUS = "https://previous-runs-api.open-meteo.com/v1/forecast"
URL_ERA5 = "https://archive-api.open-meteo.com/v1/archive"
URL_FORECAST = "https://api.open-meteo.com/v1/forecast"

CARPETA_DATOS = Path("data/raw")



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# FUNCIÓN COMÚN: CONSULTAR UNA API


def consultar_api(url, parametros):

    errores_reintentables = {429, 500, 502, 503, 504}
    max_intentos = 3

    for intento in range(1, max_intentos + 1):
        try:
            logger.info(
                "Consultando %s | Intento %s/%s",
                url,
                intento,
                max_intentos
            )

            respuesta = requests.get(
                url,
                params=parametros,
                timeout=(15, 180)
            )

            respuesta.raise_for_status()

            try:
                datos = respuesta.json()

            except requests.exceptions.JSONDecodeError:
                logger.warning(
                    "Open-Meteo devolvió un JSON no válido "
                    "(HTTP %s). Contenido inicial: %s",
                    respuesta.status_code,
                    respuesta.text[:200]
                )
                raise

            if datos.get("error"):
                raise ValueError(
                    datos.get("reason", "Error de Open-Meteo")
                )

            if "hourly" not in datos or "time" not in datos["hourly"]:
                raise ValueError(
                    "La API no devolvió datos horarios."
                )

            return datos

        except requests.exceptions.HTTPError as error:

            codigo = error.response.status_code

            # No reintentar errores HTTP permanentes.
            if codigo not in errores_reintentables:
                logger.error(
                    "Error HTTP no reintentable (%s): %s",
                    codigo,
                    error
                )
                raise

            logger.warning(
                "Error HTTP temporal (%s) | Intento %s/%s: %s",
                codigo,
                intento,
                max_intentos,
                error
            )

            if intento == max_intentos:
                logger.error(
                    "No se pudo completar la consulta "
                    "después de %s intentos.",
                    max_intentos
                )
                raise

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.JSONDecodeError
        ) as error:

            logger.warning(
                "Error de conexión o respuesta | "
                "Intento %s/%s: %s",
                intento,
                max_intentos,
                error
            )

            if intento == max_intentos:
                logger.error(
                    "No se pudo completar la consulta "
                    "después de %s intentos.",
                    max_intentos
                )
                raise

        # Esperar antes del siguiente intento.
        espera = 5 * intento

        logger.info(
            "Esperando %s segundos antes de reintentar.",
            espera
        )

        time.sleep(espera)


# FUNCIÓN COMÚN: GUARDAR EN CSV

def guardar_csv(datos, nombre_archivo):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(datos["hourly"])

    # Guardamos todas las fechas en UTC.
    df["time"] = pd.to_datetime(df["time"], utc=True)

    ruta = CARPETA_DATOS / nombre_archivo
    df.to_csv(ruta, index=False)

    logger.info("Guardado: %s", ruta)
    logger.info("Filas: %s | Columnas: %s", *df.shape)

    return df


def descargar_por_tramos(url, parametros, nombre_archivo):
    inicio = pd.Timestamp(parametros["start_date"])
    fin = pd.Timestamp(parametros["end_date"])

    carpeta_tramos = CARPETA_DATOS / "tramos"
    carpeta_tramos.mkdir(parents=True, exist_ok=True)

    bloques = []
    fecha_inicio = inicio

    while fecha_inicio <= fin:
        # Tramos de hasta
        fecha_fin = min(fecha_inicio + timedelta(days=29), fin)

        nombre_tramo = (
            f"{Path(nombre_archivo).stem}_"
            f"{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.csv"
        )
        ruta_tramo = carpeta_tramos / nombre_tramo

        if ruta_tramo.exists():
            bloque = pd.read_csv(ruta_tramo, parse_dates=["time"])

            horas_esperadas = pd.date_range(
                start=fecha_inicio,
                end=fecha_fin + timedelta(days=1) - timedelta(hours=1),
                freq="h",
                tz="UTC"
            )

            fechas = pd.DatetimeIndex(
                pd.to_datetime(bloque["time"], utc=True)
            )

            if (
                len(fechas) == len(horas_esperadas)
                and fechas.is_unique
                and fechas.sort_values().equals(horas_esperadas)
                and set(parametros["hourly"].split(",")).issubset(bloque.columns)
            ):
                logger.info("Reutilizando %s", ruta_tramo)
            else:
                logger.warning("Tramo incompleto: %s", ruta_tramo)
                ruta_tramo.unlink()
                bloque = None

        else:
            bloque = None

        if bloque is None:
            params_tramo = parametros.copy()
            params_tramo["start_date"] = fecha_inicio.strftime("%Y-%m-%d")
            params_tramo["end_date"] = fecha_fin.strftime("%Y-%m-%d")

            datos = consultar_api(url, params_tramo)


            bloque = pd.DataFrame(datos["hourly"])
            bloque["time"] = pd.to_datetime(bloque["time"], utc=True)

            horas_esperadas = (fecha_fin - fecha_inicio).days * 24 + 24

            if len(bloque) != horas_esperadas:
                raise ValueError(
                    f"Tramo incompleto: {ruta_tramo}. "
                    f"Esperadas {horas_esperadas} horas, "
                    f"recibidas {len(bloque)}."
                )

            bloque.to_csv(ruta_tramo, index=False)
            logger.info("Tramo guardado: %s", ruta_tramo)
            time.sleep(2)
        bloques.append(bloque)
        fecha_inicio = fecha_fin + timedelta(days=1)

    df_final = pd.concat(bloques, ignore_index=True)

    df_final = (
        df_final.drop_duplicates(subset=["time"])
        .sort_values("time")
        .reset_index(drop=True)
    )

    ruta_final = CARPETA_DATOS / nombre_archivo
    df_final.to_csv(ruta_final, index=False)

    logger.info("Archivo completo: %s", ruta_final)
    logger.info("Total de filas: %s", len(df_final))

    return df_final

# 1. PREVIOUS RUNS

def descargar_previous_runs(nombre, latitud, longitud, inicio, fin, modelo=None):
    # Seis variables para cada horizonte de 1 a 7 días.
    variables_previous = [
        f"{variable}_previous_day{dia}"
        for variable in VARIABLES
        for dia in range(1, 8)
    ]

    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "start_date": inicio,
        "end_date": fin,
        "hourly": ",".join(variables_previous),
        "timezone": "GMT",
    }

    if modelo:
        parametros["models"] = modelo
    return descargar_por_tramos(
    URL_PREVIOUS,
    parametros,
    f"{nombre}_previous_runs.csv"
    )

# 2. HISTORICAL WEATHER - ERA5
def descargar_era5(nombre, latitud, longitud, inicio, fin):
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "start_date": inicio,
        "end_date": fin,
        "hourly": ",".join(VARIABLES_ERA5),
        "models": "era5",
        "timezone": "GMT",
    }
    return descargar_por_tramos(
    URL_ERA5,
    parametros,
    f"{nombre}_era5.csv"
    )


# 3. FORECAST API - PRONÓSTICO ACTUAL

def descargar_forecast(nombre, latitud, longitud, modelo=None):
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "hourly": ",".join(VARIABLES),
        "forecast_days": 7,
        "timezone": "GMT",
    }

    if modelo:
        parametros["models"] = modelo

    datos = consultar_api(URL_FORECAST, parametros)

    return guardar_csv(datos, f"{nombre}_forecast.csv")

# EJECUCIÓN DEL SCRIPT

def main():
    parser = argparse.ArgumentParser(
        description="Descargar datos meteorológicos para AstroNight"
    )

    parser.add_argument(
        "modo",
        choices=["historicos", "forecast"],
        help="Qué datos quieres descargar",
    )

    parser.add_argument("--inicio", default="2024-01-26")
    parser.add_argument("--fin", default="2026-10-31")

    parser.add_argument(
        "--modelo",
        default=None,
        help="Modelo meteorológico, por ejemplo gfs_global",
    )

    args = parser.parse_args()

    for ubicacion in UBICACIONES:

        nombre = ubicacion["nombre"]
        latitud = ubicacion["latitud"]
        longitud = ubicacion["longitud"]

        logger.info("Descargando datos de %s", nombre)

        if args.modo == "historicos":

            descargar_previous_runs(
                nombre,
                latitud,
                longitud,
                args.inicio,
                args.fin,
                args.modelo
            )

            descargar_era5(
                nombre,
                latitud,
                longitud,
                args.inicio,
                args.fin
            )

        elif args.modo == "forecast":

            descargar_forecast(
                nombre,
                latitud,
                longitud,
                args.modelo
            )

    logger.info("Todas las descargas han finalizado")


if __name__ == "__main__":
    main()
