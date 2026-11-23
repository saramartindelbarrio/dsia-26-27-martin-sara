"""Recomendador astronómico basado en reglas (no altera el Random Forest)."""
import math
import pandas as pd


def calcular_oscuridad(latitud, longitud, fecha_utc):
    """Clasifica la altura solar. Requiere astral instalado."""
    from astral import Observer
    from astral.sun import elevation

    fecha = pd.Timestamp(fecha_utc)
    if fecha.tzinfo is None:
        raise ValueError("La fecha de observación debe incluir zona horaria.")
    altura = float(elevation(Observer(latitude=float(latitud), longitude=float(longitud)), fecha.to_pydatetime()))
    if altura <= -18:
        estado = "noche astronómica"
    elif altura < 0:
        estado = "crepúsculo"
    else:
        estado = "día"
    return estado, round(altura, 2)


def recomendar_observacion(
    nubosidad,
    latitud,
    longitud,
    fecha_utc,
    datos_viirs=None
):
    """Combinar nubosidad, oscuridad y radiancia VIIRS."""

    import math

    nubosidad = float(nubosidad)

    if not math.isfinite(nubosidad) or not 0 <= nubosidad <= 100:
        raise ValueError(
            "La nubosidad debe estar entre 0 y 100."
        )

    estado, altura_sol = calcular_oscuridad(
        latitud,
        longitud,
        fecha_utc
    )

    # Reglas basadas en nubosidad y altura solar
    if estado != "noche astronómica":
        conclusion = (
            "No es noche astronómica: espera a que "
            "termine el crepúsculo."
        )

    elif nubosidad >= 70:
        conclusion = (
            "Poco favorable: nubosidad elevada."
        )

    elif nubosidad <= 30:
        conclusion = (
            "Nubosidad favorable para observar, "
            "pendiente de valorar otros factores."
        )

    else:
        conclusion = (
            "Condiciones intermedias por nubosidad."
        )

    # Información de contaminación lumínica
    if datos_viirs is None:
        texto_viirs = (
            "Radiancia VIIRS no disponible."
        )
    else:
        radiancia = float(datos_viirs["radiancia"])

        if not math.isfinite(radiancia):
            raise ValueError("Radiancia VIIRS no válida.")

        texto_viirs = (
            f"Radiancia nocturna VIIRS: "
            f"{radiancia:.2f} nW/cm²/sr. "
            f"Fuente: {datos_viirs['fuente']}, "
            f"año {datos_viirs['anio']}. "
            "Es iluminación detectada desde satélite, "
            "no una clase Bortle ni una medida directa "
            "del brillo del cielo."
        )

    texto = (
        f"Oscuridad: {estado} "
        f"(altura solar {altura_sol:.2f}°). "
        f"Nubosidad estimada: {nubosidad:.1f} %. "
        f"{texto_viirs} "
        f"Recomendación: {conclusion}"
    )

    return {
        "estado": estado,
        "altura_sol": altura_sol,
        "nubosidad": nubosidad,
        "datos_viirs": datos_viirs,
        "conclusion": conclusion,
        "texto": texto
    }
