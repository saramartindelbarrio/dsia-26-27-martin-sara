import argparse #Sirve para recibir argumentos desde la terminal.
from pathlib import Path

import pandas as pd

from ventas_app.loader import CsvSalesRepository, SalesRepository
from ventas_app.metrics import SalesMetrics
from ventas_app.validator import SalesValidator

#coordina los tres archivos anteriores y guarda los resultados.

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Procesa y valida datos de ventas."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Ruta del fichero CSV de entrada.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Ruta donde guardar las ventas limpias.",
    )

    return parser.parse_args()

#La función principal del programa, Es la que va a ejecutar todo el proceso.
def main() -> None:
    args = parse_args() #Llamamos a la función que hemos explicado antes

    input_path = Path(args.input)
    output_path = Path(args.output)

    repository: SalesRepository = CsvSalesRepository(input_path)
    validator = SalesValidator()
    metrics = SalesMetrics()

    frame = repository.load()

    records, invalid_rows = validator.split(frame)

    print(
        f"Registros válidos: {len(records)} | "
        f"inválidos: {len(invalid_rows)}"
    )

    print("Importe por región:")

    for region, total in metrics.total_by_region(records).items():
        print(f"  {region}: {total:.2f}")

    clean_data = pd.DataFrame(
        [
            {
                "region": record.region,
                "producto": record.product,
                "unidades": record.units,
                "precio_unitario": record.unit_price,
                "importe": record.amount,
            }
            for record in records
        ]
    )

    clean_data.to_csv(output_path, index=False)

    print(f"Datos limpios guardados en: {output_path}")


if __name__ == "__main__":
    main()