
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()


class AIClientError(RuntimeError):
    pass

def crear_prompt(
    ubicacion,
    fecha,
    nubosidad_forecast,
    nubosidad_predicted,
    metodo,
    recomendacion=None
):
    """Preparar la explicación para NVIDIA."""

    if metodo == "open_meteo":
        informacion = (
            f"Nubosidad prevista por Open-Meteo: "
            f"{nubosidad_forecast:.1f} %. "
            "AstroNight utiliza directamente esta previsión."
        )

    elif metodo == "random_forest":
        informacion = (
            f"Nubosidad original de Open-Meteo: "
            f"{nubosidad_forecast:.1f} %. "
            f"Nubosidad estimada por el Random Forest "
            f"de AstroNight: {nubosidad_predicted:.1f} %."
        )

    else:
        raise ValueError(
            f"Método desconocido: {metodo}"
        )

    return (
        "Eres AstroNight, un asistente de observación astronómica. "
        "Explica en español, brevemente y con lenguaje sencillo, "
        "qué significan las siguientes predicciones de nubosidad "
        "para observar estrellas. "
        "Distingue entre Open-Meteo y Random Forest cuando corresponda. "
        "No afirmes que Random Forest es siempre más preciso. "
        "No inventes datos sobre la Luna, lluvia, viento "
        "ni contaminación lumínica. "
        "No garantices las condiciones del cielo.\n\n"
        f"Ubicación: {ubicacion}\n"
        f"Fecha y hora local: {fecha}\n"
        f"{informacion}\n"
        f"Evaluación astronómica calculada: {recomendacion or 'No disponible'}\n"
        "Si hay evaluación astronómica, apóyate solo en esos datos. "
        "No inventes un Bortle si es desconocido."
    )


def explicar_nubosidad(
    ubicacion: str,
    fecha: str,
    nubosidad_forecast: float,
    nubosidad_predicted: float,
    metodo: str,
    mock: bool = True,
    recomendacion=None
) -> str:
    """Generar explicación local o mediante NVIDIA."""

    nubosidad_forecast = float(nubosidad_forecast)
    nubosidad_predicted = float(nubosidad_predicted)

    for valor in (nubosidad_forecast, nubosidad_predicted):
        if not 0 <= valor <= 100:
            raise ValueError(
                "La nubosidad debe estar entre 0 y 100."
            )

    if metodo not in ("open_meteo", "random_forest"):
        raise ValueError(
            f"Método desconocido: {metodo}"
        )

    # MODO MOCK: no utiliza Internet
    if mock:

        if metodo == "open_meteo":
            texto = (
                f"En {ubicacion}, para {fecha}, Open-Meteo "
                f"prevé un {nubosidad_forecast:.1f} % de nubosidad. "
                "Esta es la predicción final de AstroNight."
            )

        else:
            texto = (
                f"En {ubicacion}, para {fecha}, Open-Meteo "
                f"prevé un {nubosidad_forecast:.1f} % de nubosidad, "
                f"mientras que AstroNight estima un "
                f"{nubosidad_predicted:.1f} % mediante Random Forest."
            )

        if nubosidad_predicted < 30:
            valoracion = "Se espera relativamente poca nubosidad."

        elif nubosidad_predicted < 70:
            valoracion = (
                "Puede haber nubes que dificulten la observación."
            )

        else:
            valoracion = (
                "La nubosidad podría dificultar mucho la observación."
            )

        explicacion = f"{texto} {valoracion}"

        if recomendacion is not None:
            explicacion += f"\n\n{recomendacion}"

        return explicacion
    
    # MODO REAL: NVIDIA
    token = os.getenv("NVIDIA_API_KEY")

    modelo = os.getenv(
        "NVIDIA_MODEL",
        "nvidia/nemotron-3.5-super-vl-120b-a12b"
    )

    if not token:
        raise ValueError(
            "Falta NVIDIA_API_KEY en el archivo .env."
        )

    cliente = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=token,
        timeout=60
    )
    try:
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "user",
                    "content": crear_prompt(
                        ubicacion,
                        fecha,
                        nubosidad_forecast,
                        nubosidad_predicted,
                        metodo,
                        recomendacion=recomendacion
                    )
                }
            ],
            temperature=0.3,
            top_p=0.95,
            max_tokens=300,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False
                }
            },
            stream=False
        )

    except OpenAIError as error:
        raise AIClientError(
            f"No se pudo obtener una respuesta de NVIDIA: {error}"
        ) from error

    texto = respuesta.choices[0].message.content

    if not texto or not texto.strip():
        raise ValueError(
            "NVIDIA devolvió una respuesta vacía."
        )

    return texto.strip()


