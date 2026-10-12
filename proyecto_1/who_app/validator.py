
import pandas as pd


class ValidationError(Exception):
    """Error al validar los datos de la OMS."""


class WHOValidator:
    """Comprueba la calidad de los datos de la OMS."""

    def split(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:

        # 1. Comprobar que existen las columnas necesarias
        required_columns = [
            "Measure code",
            "SEX",
            "PLACE_RESIDENCE",
            "YES_NO",
            "COUNTRY_REGION",
            "YEAR",
            "VALUE",
        ]

        missing_columns = [
            col for col in required_columns if col not in frame.columns
        ]

        if missing_columns:
            raise ValidationError(f"Faltan columnas obligatorias: {missing_columns}")

        # 2. Crear una copia para no modificar los datos originales
        work = frame.copy()

        # 3. Convertir año y valor a números
        work["YEAR"] = pd.to_numeric(work["YEAR"], errors="coerce")
        work["VALUE"] = pd.to_numeric(work["VALUE"], errors="coerce")
        
        # 4. Comprobar que los años sean válidos
        valid_year = ((work["YEAR"] > 0) & (work["YEAR"] % 1 == 0))

        # 5. Comprobar los datos obligatorios
        valid_mask = (
            work["Measure code"].notna()
            & work["COUNTRY_REGION"].notna()
            & work["YEAR"].notna()
            & work["VALUE"].notna()
            & work["SEX"].isin(["ALL", "FEMALE", "MALE"])
            & valid_year)            
        # 6. Separar registros válidos e inválidos
        valid_rows = work.loc[valid_mask].copy()
        invalid_rows = work.loc[~valid_mask].copy()

        return valid_rows, invalid_rows