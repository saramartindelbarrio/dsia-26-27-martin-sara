
import pandas as pd

class WHOMetrics:
    """Calcula métricas a partir de indicadores de la OMS."""

    # 1. La función calcula la variación porcentual para todos los países que tengan datos en ambos años (los años los eliges tu).
    def percentage_change(self, frame: pd.DataFrame, indicator: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Calcula la variación porcentual entre dos años."""
        # 1. Comprobar que existe el indicador
        if indicator not in frame.columns:
            raise ValueError(f"No existe el indicador: {indicator}")

        # 2. Seleccionar los datos del año inicial
        initial = frame.loc[frame["YEAR"] == start_year, ["COUNTRY_REGION", indicator]].copy()

        initial = initial.rename(columns={indicator: "initial_value"})

        # 3. Seleccionar los datos del año final
        final = frame.loc[frame["YEAR"] == end_year, ["COUNTRY_REGION", indicator]].copy()

        final = final.rename(columns={indicator: "final_value"})

        # 4. Unir los datos por país
        result = pd.merge(initial, final, on="COUNTRY_REGION", how="inner") #How inner solo conserva los paises qeu aparecen en ambos años

        # 5. Evitar divisiones entre cero
        result = result[
            result["initial_value"].notna()
            & result["final_value"].notna()
            & (result["initial_value"] != 0)
        ].copy()

        # 6. Calcular la variación porcentual
        result["percentage_change"] = (
            (result["final_value"] - result["initial_value"])
            / result["initial_value"]
        ) * 100

        return result       
    #2. La función calcula el cambio de un indicador entre dos años consecutivos, el pais es opcional 
    def yearly_change(self, frame: pd.DataFrame, indicator: str , country: str | None = None) -> pd.DataFrame:

        if indicator not in frame.columns:
            raise ValueError(f"No existe el indicador: {indicator}")
        # Filtrar por país si se ha indicado uno
        if country is not None:
            frame = frame[frame["COUNTRY_REGION"] == country]

        # Seleccionar las columnas necesarias
        result = frame[["COUNTRY_REGION", "YEAR", indicator]].copy()
        # Eliminar filas sin valor para el indicador
        result = result.dropna(subset=[indicator])

        # Ordenar por país y año
        result = result.sort_values(by=["COUNTRY_REGION", "YEAR"])

        # Obtener el valor del registro anterior de cada país
        result["previous_value"] = (result.groupby("COUNTRY_REGION")[indicator].shift(1))

        result["previous_year"] = (result.groupby("COUNTRY_REGION")["YEAR"].shift(1))

        # Calcular el cambio solo entre años consecutivos
        result["yearly_change"] = (
            result[indicator] - result["previous_value"]
        )

        result.loc[
            result["YEAR"] - result["previous_year"] != 1,
            "yearly_change"
        ] = float("nan")

        return result.drop(columns=["previous_value", "previous_year"])

    #3. La función ordena los países y regiones de mayor a menor según el valor de un indicar en un año determinado
    def country_ranking(self, frame: pd.DataFrame, indicator: str, year: int) -> pd.DataFrame:
        # 1. Comprobar que existe el indicador
        if indicator not in frame.columns:
            raise ValueError(f"No existe el indicador: {indicator}")

        # 2. Seleccionar las filas del año indicado
        result = frame.loc[frame["YEAR"] == year, ["COUNTRY_REGION", indicator]].copy()

        # 3. Eliminar las filas sin valor para ese indicador
        result = result.dropna(subset=[indicator])

        # 4. Ordenar de mayor a menor
        result = result.sort_values(
            by=indicator,
            ascending=False
        )

        # 5. Reiniciar el índice
        result = result.reset_index(drop=True)
        
        return result
        