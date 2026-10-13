from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar datos de origen."""


class SalesRepository(Protocol): #Define que método debe existir
    """Abstracción para repositorios de ventas."""

    def load(self) -> pd.DataFrame:
        ...


class CsvSalesRepository: #implementa el método para leer un csv
    """Repositorio que carga ventas desde un CSV."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")

        return pd.read_csv(self._path)

class JsonSalesRepository: #implementa el método para leer un json
    """Repositorio que carga ventas desde un JSON."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")

        return pd.read_json(self._path)