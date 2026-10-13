
from dataclasses import dataclass
import pandas as pd


class ValidationError(Exception):
    """Datos que no cumplen las reglas de negocio."""


@dataclass(frozen=True) #Clase para representar una venta válida, frozen true significa que una vez creado el objeto no puedes modificar sus atributos
class SalesRecord:
    region: str
    product: str
    units: float
    unit_price: float

    @property
    def amount(self) -> float: #Sirve para calcular el importe total de una venta
        return self.units * self.unit_price
''' 
Se usa @dataclass pporque sin el tendria que escribir
class SalesRecord:
    def __init__(self, region, product, units, unit_price):
        self.region = region
        self.product = product
        self.units = units
        self.unit_price = unit_price
Con @dataclass, Python genera automáticamente ese constructor.   

Sin @property, normalmente llamarías al método así: venta.amount()
Con @property, escribimos:venta.amoun
'''

class SalesValidator:
    """Valida los registros de ventas."""

    def split(
        self,
        frame: pd.DataFrame,
    ) -> tuple[list[SalesRecord], pd.DataFrame]:

        work = frame.copy()

        work["unidades"] = pd.to_numeric(
            work["unidades"],
            errors="coerce",#si no se puede convertir a numero se sustituye por NaN
        )

        work["precio_unitario"] = pd.to_numeric(
            work["precio_unitario"],
            errors="coerce",
        )

        valid_mask = (
            work["unidades"].notna()
            & (work["unidades"] > 0)
            & (work["precio_unitario"] > 0)
        )

        valid_records = [
            SalesRecord(
                region=str(row.region),
                product=str(row.producto),
                units=float(row.unidades),
                unit_price=float(row.precio_unitario),
            )
            for row in work.loc[valid_mask].itertuples(index=False)
        ]

        invalid_rows = work.loc[~valid_mask]

        return valid_records, invalid_rows