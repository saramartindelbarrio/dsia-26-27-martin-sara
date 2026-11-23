
import argparse
import json
import logging
import re
import unicodedata
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import requests

from descargar_datos import descargar_forecast


# RUTAS
RUTA_MODELO = Path("models/random_forest.joblib")
RUTA_METADATA = Path("models/metadata.json")
CARPETA_SALIDA = Path("data/processed")

URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# 1. BUSCAR LAS COORDENADAS DE UNA UBICACIÓN
def buscar_ubicacion(nombre, pais=None, resultado=1):

    parametros = {
        "name": nombre,
        "count": 10,
        "language": "es",
        "format": "json"
    }

    if pais:
        parametros["countryCode"] = pais.upper()

    logger.info("Buscando ubicación: %s", nombre)

    respuesta = requests.get(
        URL_GEOCODING,
        params=parametros,
        timeout=(10, 30)
    )

    respuesta.raise_for_status()

    datos = respuesta.json()
    ubicaciones = datos.get("results", [])

    if not ubicaciones:
        raise ValueError(
            f"No se encontró la ubicación: {nombre}"
        )

    logger.info("Resultados encontrados:")

    for indice, ubicacion in enumerate(ubicaciones, start=1):
        logger.info(
            "%s. %s, %s, %s",
            indice,
            ubicacion["name"],
            ubicacion.get("admin1", ""),
            ubicacion.get("country", "")
        )

    if not 1 <= resultado <= len(ubicaciones):
        raise ValueError(
            f"El resultado debe estar entre 1 y {len(ubicaciones)}."
        )

    seleccionada = ubicaciones[resultado - 1]

    logger.info(
        "Ubicación seleccionada: %s, %s | Latitud: %s | Longitud: %s",
        seleccionada["name"],
        seleccionada.get("country", ""),
        seleccionada["latitude"],
        seleccionada["longitude"]
    )

    return seleccionada


# 2. CREAR NOMBRE SEGURO PARA EL ARCHIVO
def crear_slug(nombre):

    texto = unicodedata.normalize("NFKD", nombre)

    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)

    return texto.strip("_")


# 3. APLICAR EL RANDOM FOREST
def aplicar_modelo(datos, modelo, features):

    datos = datos.copy()

    # Por defecto, utilizar Open-Meteo
    datos["cloud_cover_predicted"] = (
    datos["cloud_cover_forecast"].astype(float).copy()
    )

    datos["metodo"] = "open_meteo"

    # Solo aplicar Random Forest a lead_days 1-7
    mascara = datos["lead_days"].between(1, 7)

    if mascara.any():

        X = datos.loc[mascara, features]

        datos.loc[
            mascara, "cloud_cover_predicted"
        ] = np.clip(
            modelo.predict(X),
            0,
            100
        )

        datos.loc[mascara, "metodo"] = "random_forest"

    return datos


# 4. GENERAR PREDICCIONES
def predecir_ubicacion(
    ubicacion="Madrid",
    pais=None,
    resultado=1
):

    # Cargar modelo entrenado
    logger.info("Cargando Random Forest")

    modelo = joblib.load(RUTA_MODELO)

    with open(RUTA_METADATA, "r", encoding="utf-8") as archivo:
        metadata = json.load(archivo)

    features = metadata["features"]

    # Obtener coordenadas con geocodificación
    lugar = buscar_ubicacion(
        nombre=ubicacion,
        pais=pais,
        resultado=resultado
    )
    zona_horaria = lugar["timezone"]

    logger.info("Zona horaria: %s", zona_horaria)

    nombre = lugar["name"]
    latitud = lugar["latitude"]
    longitud = lugar["longitude"]

    # Guardar archivos separados por localidad y país
    nombre_archivo = crear_slug(
        f"{nombre}_{lugar.get('country_code', '')}_{lugar['id']}"
    )

    logger.info("Descargando previsiones de %s", nombre)

    datos = descargar_forecast(
        nombre=nombre_archivo,
        latitud=latitud,
        longitud=longitud
    )

    # Preparar las fechas
    datos["time"] = pd.to_datetime(
        datos["time"],
        utc=True
    )

    ahora = pd.Timestamp.now(tz="UTC")

    # Quedarse únicamente con horas futuras
    datos = datos[
        datos["time"] > ahora
    ].copy()

    # Aproximar horizonte de predicción
    horas_adelanto = (
        (datos["time"] - ahora).dt.total_seconds() / 3600
    )

    datos["lead_days"] = np.floor(
        horas_adelanto / 24 + 0.5
    ).astype(int)

    datos = datos[
        datos["lead_days"].between(0, 7)
    ].copy()

    # Adaptar nombres al entrenamiento
    datos = datos.rename(
        columns={
            "cloud_cover": "cloud_cover_forecast"
        }
    )

    # Comprobar que existen todas las variables
    faltantes = [
        columna
        for columna in features
        if columna not in datos.columns
    ]

    if faltantes:
        raise ValueError(
            f"Faltan variables para predecir: {faltantes}"
        )

    datos = datos.dropna(subset=features)

    if datos.empty:
        raise ValueError(
            "No hay previsiones válidas para generar predicciones."
        )

    # Aplicar el modelo ya entrenado
    logger.info("Aplicando Random Forest")

    datos = aplicar_modelo(
        datos,
        modelo,
        features
    )

    # Preparar el resultado
    resultado_df = datos[
        [
            "time",
            "lead_days",
            "cloud_cover_forecast",
            "cloud_cover_predicted",
            "metodo"
        ]
    ].copy()
    resultado_df["zona_horaria"] = zona_horaria
    resultado_df["latitud"] = latitud
    resultado_df["longitud"] = longitud

    # Guardar cada ubicación en su propio CSV
    CARPETA_SALIDA.mkdir(
        parents=True,
        exist_ok=True
    )

    ruta_salida = (
        CARPETA_SALIDA /
        f"predicciones_{nombre_archivo}.csv"
    )

    resultado_df.to_csv(
        ruta_salida,
        index=False
    )

    logger.info("Predicciones guardadas en: %s", ruta_salida)
    logger.info("Filas generadas: %s", len(resultado_df))

    print("\n===== PREDICCIONES POR LEAD_DAYS =====")

    print(
        resultado_df.groupby("lead_days")
        .head(3)
        .to_string(index=False)
    )

    return resultado_df


# 5. CLI
def main():

    parser = argparse.ArgumentParser(
        description="Predecir nubosidad con AstroNight"
    )

    parser.add_argument(
        "--ubicacion",
        default="Madrid",
        help="Localidad para la que quieres predecir"
    )

    parser.add_argument(
        "--pais",
        default="ES",
        help="Código de país (por defecto España)"
    )

    parser.add_argument(
        "--resultado",
        type=int,
        default=1,
        help="Número de resultado de geocodificación (por defecto 1)"
    )

    args = parser.parse_args()

    predecir_ubicacion(
        ubicacion=args.ubicacion,
        pais=args.pais,
        resultado=args.resultado
    )


if __name__ == "__main__":
    main()
