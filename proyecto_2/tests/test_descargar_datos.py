
import pytest
import requests

import descargar_datos


def test_reintento_error_429(monkeypatch):
    """HTTP 429 debe reintentarse y terminar correctamente."""

    llamadas = []

    class RespuestaSimulada:
        status_code = 200
        text = ""

        def raise_for_status(self):
            if len(llamadas) == 1:
                error = requests.exceptions.HTTPError(
                    "429 Too Many Requests"
                )
                error.response = requests.Response()
                error.response.status_code = 429
                raise error

        def json(self):
            return {
                "hourly": {
                    "time": ["2026-01-01T00:00"],
                    "cloud_cover": [25]
                }
            }

    def get_simulado(*args, **kwargs):
        llamadas.append(1)
        return RespuestaSimulada()

    monkeypatch.setattr(
        descargar_datos.requests,
        "get",
        get_simulado
    )

    # Evitar esperas reales durante el test
    monkeypatch.setattr(
        descargar_datos.time,
        "sleep",
        lambda segundos: None
    )

    resultado = descargar_datos.consultar_api(
        "https://api.example.com",
        {"hourly": "cloud_cover"}
    )

    assert len(llamadas) == 2
    assert resultado["hourly"]["cloud_cover"] == [25]


def test_no_reintento_error_400(monkeypatch):
    """HTTP 400 debe propagarse sin repetir la petición."""

    llamadas = []

    def get_simulado(*args, **kwargs):
        llamadas.append(1)

        respuesta = requests.Response()
        respuesta.status_code = 400
        respuesta.url = "https://api.example.com"

        return respuesta

    monkeypatch.setattr(
        descargar_datos.requests,
        "get",
        get_simulado
    )

    monkeypatch.setattr(
        descargar_datos.time,
        "sleep",
        lambda segundos: None
    )

    with pytest.raises(requests.exceptions.HTTPError):
        descargar_datos.consultar_api(
            "https://api.example.com",
            {"hourly": "cloud_cover"}
        )

    assert len(llamadas) == 1
