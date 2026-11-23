
import argparse
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from cliente_nvidia import explicar_nubosidad
from cliente_viirs import consultar_viirs
from recomendador import recomendar_observacion

CARPETA_PREVISIONES = Path("data/processed")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def formatear_fecha_hora(fecha_utc, zona_horaria):

    fecha_local = pd.Timestamp(fecha_utc).tz_convert(
        zona_horaria
    )

    dias = [
        "lunes",
        "martes",
        "miércoles",
        "jueves",
        "viernes",
        "sábado",
        "domingo"
    ]

    dia_semana = dias[fecha_local.weekday()]

    if zona_horaria == "Europe/Madrid":
        nombre_zona = "hora peninsular"

    elif zona_horaria == "Atlantic/Canary":
        nombre_zona = "hora de Canarias"

    else:
        nombre_zona = zona_horaria

    return (
        f"{dia_semana} "
        f"{fecha_local:%d/%m/%Y} "
        f"a las {fecha_local:%H:%M} "
        f"({nombre_zona})"
    )



def buscar_csv_predicciones(ubicacion, pais="ES"):

    # Normalizar el nombre igual que en predecir.py
    from predecir import crear_slug

    nombre = crear_slug(ubicacion)
    pais = pais.lower()

    # Archivos creados por predecir.py:
    # predicciones_madrid_es_3117735.csv
    patron = f"predicciones_{nombre}_{pais}_*.csv"

    archivos = list(CARPETA_PREVISIONES.glob(patron))

    if not archivos:
        raise FileNotFoundError(
            f"No hay predicciones guardadas para {ubicacion}. "
            f"Ejecuta primero predecir.py --ubicacion '{ubicacion}'."
        )

    # Elegir el CSV modificado más recientemente
    ruta = max(archivos, key=lambda archivo: archivo.stat().st_mtime)

    logger.info("CSV seleccionado: %s", ruta)

    return ruta




def seleccionar_prediccion(
    datos,
    lead_days=3,
    fecha=None,
    hora=None,
    zona_horaria="Europe/Madrid"
):
    """Seleccionar una predicción por fecha/hora o lead_days."""

    columnas = [
        "time",
        "cloud_cover_forecast",
        "cloud_cover_predicted",
        "lead_days",
        "metodo"
    ]

    faltantes = set(columnas) - set(datos.columns)

    if faltantes:
        raise ValueError(
            f"Faltan columnas en el CSV: {sorted(faltantes)}"
        )

    datos = datos.copy()
    datos["time"] = pd.to_datetime(datos["time"], utc=True)

    # OPCIÓN 1: fecha y hora elegidas por el usuario
    if fecha is not None and hora is not None:

        try:
            fecha_hora = datetime.strptime(
                f"{fecha} {hora:02d}",
                "%Y-%m-%d %H"
            )
        except ValueError:
            raise ValueError(
                "La fecha debe tener formato AAAA-MM-DD "
                "y la hora debe estar entre 0 y 23."
            )

        # Convertir la hora local a UTC
        fecha_hora_local = pd.Timestamp(fecha_hora).tz_localize(
            zona_horaria,
            ambiguous="raise",
            nonexistent="raise"
        )

        fecha_hora_utc = fecha_hora_local.tz_convert("UTC")

        seleccion = datos[
            datos["time"] == fecha_hora_utc
        ]

        if seleccion.empty:
            raise ValueError(
                f"No hay predicción disponible para "
                f"{fecha} a las {hora:02d}:00 "
                f"({zona_horaria})."
            )

        return seleccion.iloc[0]

    # OPCIÓN 2: comportamiento anterior por lead_days
    datos_dia = datos[
        datos["lead_days"] == lead_days
    ].sort_values("time")

    if datos_dia.empty:
        raise ValueError(
            f"No hay predicciones para lead_days={lead_days}"
        )

    return datos_dia.iloc[0]



def ejecutar(
    ruta_csv=None,
    ubicacion="Madrid",
    lead_days=3,
    mock=True,
    fecha=None,
    hora=None,
):
    """Leer predicciones y generar una explicación."""
    if ruta_csv is None:
        ruta_csv = buscar_csv_predicciones(ubicacion)

    logger.info("Leyendo predicciones: %s", ruta_csv)

    datos = pd.read_csv(ruta_csv)

    if "zona_horaria" not in datos.columns:
        raise ValueError(
            "El CSV no contiene zona_horaria. "
            "Vuelve a ejecutar predecir.py para actualizarlo."
        )

    zona_horaria = datos["zona_horaria"].iloc[0]

    logger.info("Zona horaria detectada: %s", zona_horaria)

    fila = seleccionar_prediccion(
        datos,
        lead_days=lead_days,
        fecha=fecha,
        hora=hora,
        zona_horaria=zona_horaria
    )

    fecha = formatear_fecha_hora(
        fila["time"],
        zona_horaria
    )
    nubosidad_forecast = float(
        fila["cloud_cover_forecast"]
    )
    nubosidad_predicted = float(
        fila["cloud_cover_predicted"]
    )
    metodo = str(fila["metodo"])
    logger.info("Ubicación: %s", ubicacion)
    logger.info("Fecha: %s", fecha)
    logger.info("Lead days: %s", int(fila["lead_days"]))

    logger.info(
        "Nubosidad Open-Meteo: %.2f %%",
        nubosidad_forecast
    )

    logger.info(
        "Nubosidad final AstroNight: %.2f %%",
        nubosidad_predicted
    )

    logger.info("Método: %s", metodo)

    recomendacion = None

    if {"latitud", "longitud"}.issubset(datos.columns):

        latitud = float(fila["latitud"])
        longitud = float(fila["longitud"])

        # Leer la radiancia del mapa VIIRS local
        datos_viirs = None

        try:
            datos_viirs = consultar_viirs(
                latitud,
                longitud
            )

            logger.info(
                "Radiancia VIIRS: %.2f %s",
                datos_viirs["radiancia"],
                datos_viirs["unidad"]
            )

        except (FileNotFoundError, ValueError, OSError) as error:
            logger.warning(
                "No se pudo consultar VIIRS: %s",
                error
            )

        # Combinar radiancia, nubosidad y oscuridad
        resultado_ast = recomendar_observacion(
            nubosidad=nubosidad_predicted,
            latitud=latitud,
            longitud=longitud,
            fecha_utc=fila["time"],
            datos_viirs=datos_viirs
        )

        recomendacion = resultado_ast["texto"]

        logger.info(
            "Recomendación astronómica: %s",
            recomendacion
        )

    else:
        logger.warning(
            "El CSV no contiene coordenadas. "
            "Vuelve a ejecutar predecir.py."
        )

    logger.info(
        "Modo NVIDIA: %s",
        "mock" if mock else "real"
    )

    explicacion = explicar_nubosidad(
        ubicacion=ubicacion,
        fecha=fecha,
        nubosidad_forecast=nubosidad_forecast,
        nubosidad_predicted=nubosidad_predicted,
        metodo=metodo,
        mock=mock,
        recomendacion=recomendacion
    )

    logger.info("Explicación generada correctamente")

    if recomendacion is not None:
        print("\n===== RECOMENDACIÓN ASTRONÓMICA =====")
        print(recomendacion)

    print("\n===== EXPLICACIÓN ASTRONIGHT =====")
    print(explicacion)

    return explicacion


def main():
    parser = argparse.ArgumentParser(
        description="Explicar las predicciones de AstroNight"
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Ruta al CSV de predicciones"
    )

    parser.add_argument(
        "--ubicacion",
        default="Madrid",
        help="Nombre de la ubicación"
    )

    parser.add_argument(
    "--pais",
    default="ES",
    help="Código de país (por defecto ES)"
    )

    parser.add_argument(
        "--lead-days",
        type=int,
        choices=range(0, 8),
        default=3,
        metavar="{0,...,7}",
        help="Horizonte de predicción que se quiere explicar"
    )
    parser.add_argument(
    "--fecha",
    default=None,
    help="Fecha de observación (AAAA-MM-DD)"
)

    parser.add_argument(
        "--hora",
        type=int,
        choices=range(24),
        default=None,
        metavar="{0,...,23}",
        help="Hora local de observación (0-23)"
    )





    modo = parser.add_mutually_exclusive_group()

    modo.add_argument(
        "--mock",
        action="store_true",
        help="Generar explicación local sin consultar la API"
    )

    modo.add_argument(
        "--real",
        action="store_true",
        help="Consultar realmente NVIDIA"
    )
    args = parser.parse_args()

    # Usar la ruta indicada o buscarla automáticamente
    ruta_csv = args.csv
    if (args.fecha is None) != (args.hora is None):
        parser.error(
        "Debes indicar --fecha y --hora juntos."
    )

    if ruta_csv is None:
        ruta_csv = buscar_csv_predicciones(
            ubicacion=args.ubicacion,
            pais=args.pais
        )

    ejecutar(
        ruta_csv=ruta_csv,
        ubicacion=args.ubicacion,
        lead_days=args.lead_days,
        mock=not args.real,
        fecha=args.fecha,
        hora=args.hora,
    )


if __name__ == "__main__":
    main()
