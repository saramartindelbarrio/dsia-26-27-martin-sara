
import pandas as pd
import pytest

import procesar_datos as procesador


def crear_datos_prueba(tmp_path):
    """Crear CSV meteorológicos pequeños para las pruebas."""
    fechas = [
        "2025-01-01T20:00:00Z",
        "2025-01-01T21:00:00Z",
    ]

    previous = {"time": fechas}

    valores = {
        "temperature_2m": 10.0,
        "wind_speed_10m": 5.0,
        "precipitation": 0.0,
        "relative_humidity_2m": 60.0,
        "dew_point_2m": 3.0,
        "cloud_cover": 40.0,
    }

    for dia in range(1, 8):
        for variable in procesador.VARIABLES:
            previous[f"{variable}_previous_day{dia}"] = [
                valores[variable],
                valores[variable],
            ]

    pd.DataFrame(previous).to_csv(
        tmp_path / "Madrid_previous_runs.csv",
        index=False,
    )

    pd.DataFrame({
        "time": fechas,
        "cloud_cover": [30.0, 70.0],
    }).to_csv(
        tmp_path / "Madrid_era5.csv",
        index=False,
    )


def test_procesar_ubicacion_genera_siete_horizontes(
    tmp_path, monkeypatch
):
    # Arrange: preparar datos sintéticos
    crear_datos_prueba(tmp_path)

    monkeypatch.setattr(
        procesador, "CARPETA_RAW", tmp_path
    )

    # Act: ejecutar el procesamiento real
    resultado = procesador.procesar_ubicacion("Madrid")

    # Assert: dos horas, siete horizontes cada una
    assert len(resultado) == 14
    assert set(resultado["lead_days"]) == set(range(1, 8))
    assert set(resultado["nombre"]) == {"Madrid"}

    assert "cloud_cover_forecast" in resultado.columns
    assert "cloud_cover_actual" in resultado.columns

    assert set(resultado["cloud_cover_forecast"]) == {40.0}
    assert set(resultado["cloud_cover_actual"]) == {30.0, 70.0}


def test_procesar_ubicacion_rechaza_fechas_duplicadas(
    tmp_path, monkeypatch
):
    # Arrange: crear los archivos de prueba
    crear_datos_prueba(tmp_path)

    ruta = tmp_path / "Madrid_previous_runs.csv"
    datos = pd.read_csv(ruta)

    # Duplicar una fecha intencionadamente
    datos.loc[1, "time"] = datos.loc[0, "time"]
    datos.to_csv(ruta, index=False)

    monkeypatch.setattr(
        procesador, "CARPETA_RAW", tmp_path
    )

    # Act + Assert: debe detectar el problema
    with pytest.raises(
        ValueError, match="Fechas duplicadas"
    ):
        procesador.procesar_ubicacion("Madrid")


def test_procesar_ubicacion_elimina_valores_ausentes(
    tmp_path, monkeypatch
):
    # Arrange: crear los CSV sintéticos
    crear_datos_prueba(tmp_path)

    ruta = tmp_path / "Madrid_previous_runs.csv"
    datos = pd.read_csv(ruta)

    # Introducir un dato ausente en el horizonte 1
    datos.loc[0, "temperature_2m_previous_day1"] = float("nan")
    datos.to_csv(ruta, index=False)

    monkeypatch.setattr(
        procesador, "CARPETA_RAW", tmp_path
    )

    # Act: procesar los datos
    resultado = procesador.procesar_ubicacion("Madrid")

    # Assert: de 14 filas posibles, se elimina una
    assert len(resultado) == 13

    assert not resultado[
        "temperature_2m"
    ].isna().any()

    # El horizonte 1 conserva solo la otra hora
    assert (resultado["lead_days"] == 1).sum() == 1
