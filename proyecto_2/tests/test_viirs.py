
import math

import pytest

import cliente_viirs
import recomendador



# PRUEBAS DEL MAPA VIIRS


def test_viirs_madrid():
    """Comprobar que podemos consultar el GeoTIFF real."""

    resultado = cliente_viirs.consultar_viirs(
        40.4165,
        -3.70256
    )

    assert isinstance(resultado["radiancia"], float)
    assert math.isfinite(resultado["radiancia"])
    assert resultado["radiancia"] >= 0

    assert resultado["unidad"] == "nW/cm²/sr"
    assert resultado["fuente"] == "EOG VIIRS"
    assert resultado["anio"] == 2025


def test_viirs_pueblo():
    """Comprobar que también funciona con pueblos."""

    # Coordenadas de La Hiruela (Madrid), aproximadas.
    resultado = cliente_viirs.consultar_viirs(
        41.077,
        -3.455
    )

    assert isinstance(resultado["radiancia"], float)
    assert math.isfinite(resultado["radiancia"])


def test_viirs_fuera_del_mapa():
    """Una ubicación fuera de España debe fallar."""

    with pytest.raises(ValueError, match="fuera"):
        cliente_viirs.consultar_viirs(0, 0)


def test_viirs_archivo_inexistente(monkeypatch, tmp_path):
    """Comprobar el error si falta el mapa."""

    ruta_inexistente = tmp_path / "no_existe.tif"

    monkeypatch.setattr(
        cliente_viirs,
        "RUTA_VIIRS",
        ruta_inexistente
    )

    with pytest.raises(FileNotFoundError):
        cliente_viirs.consultar_viirs(
            40.4165,
            -3.70256
        )



# PRUEBAS DEL RECOMENDADOR


def simular_noche(monkeypatch):
    """Simular noche astronómica sin depender de la fecha."""

    monkeypatch.setattr(
        recomendador,
        "calcular_oscuridad",
        lambda *args: ("noche astronómica", -25.0)
    )


def test_recomendacion_con_viirs(monkeypatch):
    """Debe incluir los datos de radiancia y su fuente."""

    simular_noche(monkeypatch)

    datos_viirs = {
        "radiancia": 12.5,
        "unidad": "nW/cm²/sr",
        "fuente": "EOG VIIRS",
        "anio": 2025
    }

    resultado = recomendador.recomendar_observacion(
        nubosidad=25,
        latitud=40,
        longitud=-3,
        fecha_utc="2026-11-15T22:00:00Z",
        datos_viirs=datos_viirs
    )

    assert resultado["datos_viirs"] == datos_viirs
    assert "12.50" in resultado["texto"]
    assert "EOG VIIRS" in resultado["texto"]
    assert "2025" in resultado["texto"]
    assert "favorable" in resultado["conclusion"]


def test_recomendacion_sin_viirs(monkeypatch):
    """Debe funcionar aunque no haya datos VIIRS."""

    simular_noche(monkeypatch)

    resultado = recomendador.recomendar_observacion(
        nubosidad=25,
        latitud=40,
        longitud=-3,
        fecha_utc="2026-11-15T22:00:00Z"
    )

    assert resultado["datos_viirs"] is None
    assert "VIIRS no disponible" in resultado["texto"]


def test_recomendacion_nubosidad_alta(monkeypatch):
    """No debe recomendar observación con muchas nubes."""

    simular_noche(monkeypatch)

    resultado = recomendador.recomendar_observacion(
        nubosidad=90,
        latitud=40,
        longitud=-3,
        fecha_utc="2026-11-15T22:00:00Z"
    )

    assert "Poco favorable" in resultado["conclusion"]


def test_recomendacion_fuera_noche_astronomica(monkeypatch):
    """Debe advertir si todavía no es noche astronómica."""

    monkeypatch.setattr(
        recomendador,
        "calcular_oscuridad",
        lambda *args: ("día", 20.0)
    )

    resultado = recomendador.recomendar_observacion(
        nubosidad=10,
        latitud=40,
        longitud=-3,
        fecha_utc="2026-11-15T12:00:00Z"
    )

    assert "No es noche astronómica" in resultado["conclusion"]


def test_recomendacion_nubosidad_invalida():
    """La nubosidad debe estar entre 0 y 100."""

    with pytest.raises(ValueError):
        recomendador.recomendar_observacion(
            nubosidad=120,
            latitud=40,
            longitud=-3,
            fecha_utc="2026-11-15T22:00:00Z"
        )
