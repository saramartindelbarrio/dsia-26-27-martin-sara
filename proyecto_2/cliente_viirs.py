
from pathlib import Path
import math

import rasterio
from rasterio.warp import transform


RUTA_VIIRS = Path("data/viirs/espana_viirs.tif")


def consultar_viirs(latitud, longitud):
    """Consultar radiancia nocturna del mapa VIIRS local."""

    if not RUTA_VIIRS.exists():
        raise FileNotFoundError(
            f"No existe el mapa VIIRS: {RUTA_VIIRS}"
        )

    with rasterio.open(RUTA_VIIRS) as mapa:

        if mapa.crs is None:
            raise ValueError(
                "El mapa VIIRS no tiene sistema de coordenadas."
            )

        xs, ys = transform(
            "EPSG:4326",
            mapa.crs,
            [float(longitud)],
            [float(latitud)]
        )

        x, y = xs[0], ys[0]

        if not (
            mapa.bounds.left <= x < mapa.bounds.right
            and mapa.bounds.bottom < y <= mapa.bounds.top
        ):
            raise ValueError(
                "La ubicación está fuera del mapa VIIRS."
            )

        valor = next(
            mapa.sample([(x, y)], masked=True)
        )[0]

        if bool(getattr(valor, "mask", False)):
            raise ValueError(
                "No hay datos VIIRS válidos en esta ubicación."
            )

        radiancia = float(valor)

        if not math.isfinite(radiancia):
            raise ValueError(
                "La radiancia VIIRS no es válida."
            )

        return {
            "radiancia": radiancia,
            "unidad": "nW/cm²/sr",
            "fuente": "EOG VIIRS",
            "anio": 2025
        }
