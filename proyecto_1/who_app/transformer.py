import pandas as pd


class DataTransformationError(Exception):
    """Error al transformar los datos de la OMS."""


class WHOTransformer:
    """Selecciona indicadores y organiza los datos por país y año."""

    def transform(self, frame: pd.DataFrame, selected_measures: list[str]) -> pd.DataFrame:
        # 1. Seleccionar los indicadores que queremos
        selected = frame[frame["Measure code"].isin(selected_measures)].copy()

        if selected.empty:
            raise DataTransformationError("No se han encontrado los indicadores seleccionados.")

        # 2. Seleccionar el sexo
        selected = selected[selected["SEX"].isin(["ALL", "FEMALE", "MALE"])].copy()

        # 3. Comprobar observaciones duplicadas
        keys = ["COUNTRY_REGION", "YEAR", "Measure code", "SEX"]

        duplicados = selected[selected.duplicated(subset=keys, keep=False)]
        #Comprueba si existen dos filas con el mismo país, año, indicador y sexo al mismo tiempo.
        if not duplicados.empty:
            print("Se han encontrado observaciones duplicadas:")
            print(duplicados.head(20))
            raise DataTransformationError("Hay observaciones duplicadas para el mismo país, año, indicador y sexo.")
        
        # 4. Crear una columna con el indicador y el sexo
        selected["INDICATOR"] = (selected["Measure code"] + "_" + selected["SEX"])
        # 5. Convertir los indicadores en columnas
        transformed = selected.pivot(
            index=["COUNTRY_REGION", "YEAR"],
            columns="INDICATOR",
            values="VALUE"
        ).reset_index()
        transformed.columns.name = None
        
        # 6.Eliminar columnas de indicadores que sean completamente NaN
        transformed = transformed.dropna(axis=1, how="all")
        return transformed