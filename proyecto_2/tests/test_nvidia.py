
from types import SimpleNamespace

import pandas as pd
import pytest
import cliente_nvidia as nv
from explicar_predicciones import (
    ejecutar,
    seleccionar_prediccion,
    formatear_fecha_hora
)

def test_prompt_con_dos_nubosidades():
    prompt = nv.crear_prompt(
        "Madrid",
        "2026-11-15",
        65,
        40,
        "random_forest"
    )

    assert "65.0 %" in prompt
    assert "40.0 %" in prompt
    assert "Random Forest" in prompt


def test_mock_random_forest():
    texto = nv.explicar_nubosidad(
        "Madrid",
        "2026-11-15",
        65,
        40,
        "random_forest",
        mock=True
    )

    assert "65.0 %" in texto
    assert "40.0 %" in texto
    assert "Random Forest" in texto


def test_mock_open_meteo():
    texto = nv.explicar_nubosidad(
        "Madrid",
        "2026-11-15",
        20,
        20,
        "open_meteo",
        mock=True
    )

    assert "Open-Meteo" in texto
    assert "Random Forest" not in texto


def test_nubosidad_invalida():
    with pytest.raises(ValueError):
        nv.explicar_nubosidad(
            "Madrid",
            "2026-11-15",
            120,
            40,
            "random_forest",
            mock=True
        )


def test_cliente_nvidia_simulado(monkeypatch):
    # No utiliza Internet ni una API key real
    monkeypatch.setenv("NVIDIA_API_KEY", "clave_ficticia")
    monkeypatch.setenv(
        "NVIDIA_MODEL",
        "nvidia/nemotron-3.5-super-vl-120b-a12b"
    )

    class CompletionsFalso:
        def create(self, **kwargs):
            assert kwargs["model"] == (
                "nvidia/nemotron-3.5-super-vl-120b-a12b"
            )

            assert kwargs["stream"] is False

            assert "65.0 %" in kwargs["messages"][0]["content"]
            assert "40.0 %" in kwargs["messages"][0]["content"]

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="Explicación simulada de NVIDIA."
                        )
                    )
                ]
            )

    class ClienteFalso:
        def __init__(self, **kwargs):
            assert kwargs["base_url"] == (
                "https://integrate.api.nvidia.com/v1"
            )

            self.chat = SimpleNamespace(
                completions=CompletionsFalso()
            )

    monkeypatch.setattr(nv, "OpenAI", ClienteFalso)

    resultado = nv.explicar_nubosidad(
        "Madrid",
        "2026-11-15",
        65,
        40,
        "random_forest",
        mock=False
    )

    assert resultado == "Explicación simulada de NVIDIA."



def test_integracion_csv_mock(tmp_path):
    # Crear CSV temporal sin modificar los datos del proyecto
    ruta = tmp_path / "predicciones.csv"

    datos = pd.DataFrame([
        {
            "time": "2026-11-15T12:00:00Z",
            "lead_days": 3,
            "cloud_cover_forecast": 65.0,
            "cloud_cover_predicted": 40.0,
            "metodo": "random_forest",
            "zona_horaria": "Europe/Madrid"
        }
    ])

    datos.to_csv(ruta, index=False)

    resultado = ejecutar(
        ruta_csv=ruta,
        ubicacion="Madrid",
        lead_days=3,
        mock=True
    )

    assert "65.0 %" in resultado
    assert "40.0 %" in resultado
    assert "13:00" in resultado
    assert "hora peninsular" in resultado


def test_fecha_hora_peninsula():

    datos = pd.DataFrame([
        {
            "time": "2026-11-15T22:00:00Z",
            "lead_days": 3,
            "cloud_cover_forecast": 76.0,
            "cloud_cover_predicted": 70.06,
            "metodo": "random_forest",
            "zona_horaria": "Europe/Madrid"
        }
    ])

    fila = seleccionar_prediccion(
        datos,
        fecha="2026-11-15",
        hora=23,
        zona_horaria="Europe/Madrid"
    )

    assert fila["cloud_cover_forecast"] == 76.0

    fecha_texto = formatear_fecha_hora(
        fila["time"],
        "Europe/Madrid"
    )

    assert "15/11/2026" in fecha_texto
    assert "23:00" in fecha_texto
    assert "hora peninsular" in fecha_texto


def test_fecha_hora_canarias():

    datos = pd.DataFrame([
        {
            "time": "2026-11-15T23:00:00Z",
            "lead_days": 3,
            "cloud_cover_forecast": 50.0,
            "cloud_cover_predicted": 45.0,
            "metodo": "random_forest",
            "zona_horaria": "Atlantic/Canary"
        }
    ])

    fila = seleccionar_prediccion(
        datos,
        fecha="2026-11-15",
        hora=23,
        zona_horaria="Atlantic/Canary"
    )

    assert fila["cloud_cover_forecast"] == 50.0

    fecha_texto = formatear_fecha_hora(
        fila["time"],
        "Atlantic/Canary"
    )

    assert "15/11/2026" in fecha_texto
    assert "23:00" in fecha_texto
    assert "hora de Canarias" in fecha_texto



def test_nvidia_sin_api_key(monkeypatch):
    # Eliminar la clave solo durante este test
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)

    with pytest.raises(ValueError, match="NVIDIA_API_KEY"):
        nv.explicar_nubosidad(
            "Madrid",
            "15/11/2026",
            65,
            40,
            "random_forest",
            mock=False
        )


def test_nvidia_respuesta_vacia(monkeypatch):
    monkeypatch.setenv(
        "NVIDIA_API_KEY",
        "clave_ficticia"
    )

    class CompletionsFalso:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="")
                    )
                ]
            )

    class ClienteFalso:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(
                completions=CompletionsFalso()
            )

    monkeypatch.setattr(nv, "OpenAI", ClienteFalso)

    with pytest.raises(ValueError, match="respuesta vacía"):
        nv.explicar_nubosidad(
            "Madrid",
            "15/11/2026",
            65,
            40,
            "random_forest",
            mock=False
        )


def test_nvidia_metodo_desconocido():
    with pytest.raises(ValueError, match="Método desconocido"):
        nv.explicar_nubosidad(
            "Madrid",
            "15/11/2026",
            65,
            40,
            "metodo_inventado",
            mock=True
        )
