
from pathlib import Path
import pandas as pd


class DataLoadError(Exception):
    """Error al cargar los datos de la OMS."""


class WHOLoader:
    """Carga y une todos los archivos CSV de una carpeta."""

    def load(self, folder: Path) -> pd.DataFrame:

        # 1. Comprobar que la carpeta existe
        if not folder.is_dir():
            raise DataLoadError(f"No existe la carpeta: {folder}")

        # 2. Buscar todos los archivos CSV
        files = sorted(folder.glob("*.csv"))

        if not files:
            raise DataLoadError(f"No se han encontrado archivos CSV en: {folder}")

        # 3. Leer los archivos
        frames = []

        for file in files:
            frame = pd.read_csv(file, low_memory = False)
            frames.append(frame)

        # 4. Unir todos los DataFrames
        return pd.concat(frames, ignore_index=True)