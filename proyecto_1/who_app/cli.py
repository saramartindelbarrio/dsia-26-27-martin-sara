
import argparse
from pathlib import Path

from who_app.loader import WHOLoader
from who_app.validator import WHOValidator
from who_app.transformer import WHOTransformer
from who_app.metrics import WHOMetrics


def parse_args() -> argparse.Namespace:
    """Define y obtiene los argumentos de la terminal."""

    parser = argparse.ArgumentParser(description="Procesa indicadores de salud de la OMS.")

    parser.add_argument(
        "--input",
        required=True,
        help="Carpeta con los archivos CSV originales."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Ruta del CSV donde guardar el dataset transformado."
    )

    parser.add_argument(
        "--measures",
        nargs="+",
        required=True,
        help="Códigos de los indicadores que queremos seleccionar."
    )

    parser.add_argument(
        "--metric",
        choices=["percentage_change", "yearly_change", "country_ranking"],
        help="Métrica que queremos calcular (opcional)."
    )

    parser.add_argument(
        "--indicator",
        help="Indicador concreto para calcular la métrica, por ejemplo HFA_1_ALL."
    )

    parser.add_argument(
        "--country",
        help="Código del país para calcular una métrica."
    )

    parser.add_argument(
        "--start-year",
        type=int,
        help="Año inicial para la variación porcentual."
    )

    parser.add_argument(
        "--end-year",
        type=int,
        help="Año final para la variación porcentual."
    )

    parser.add_argument(
        "--year",
        type=int,
        help="Año para el ranking de países."
    )

    return parser.parse_args()

#La función que coordina todos los módulos.
def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # 1. Cargar los CSV
    loader = WHOLoader()
    frame = loader.load(input_path)

    # 2. Validar los datos
    validator = WHOValidator()
    valid_rows, invalid_rows = validator.split(frame)

    print(f"Registros válidos: {len(valid_rows)}")
    print(f"Registros inválidos: {len(invalid_rows)}")

    # 3. Seleccionar indicadores y transformar
    transformer = WHOTransformer()
    transformed = transformer.transform(
        valid_rows,
        selected_measures=args.measures
    )

    # 4. Guardar el dataset transformado
    output_path.parent.mkdir(parents=True, exist_ok=True)
    transformed.to_csv(output_path, index=False)

    print(f"Dataset guardado en: {output_path}")

    # 5. Calcular la métrica si el usuario la ha solicitado
    if args.metric:
        metrics = WHOMetrics()

        if not args.indicator:
            raise ValueError("Debes indicar --indicator para calcular una métrica.")

        if args.metric == "percentage_change":
            if args.start_year is None or args.end_year is None:
                raise ValueError("Debes indicar --start-year y --end-year.")

            result = metrics.percentage_change(
                transformed,
                indicator=args.indicator,
                start_year=args.start_year,
                end_year=args.end_year
            )

        elif args.metric == "yearly_change":
            result = metrics.yearly_change(
                transformed,
                indicator=args.indicator,
                country=args.country
            )

        else:
            if args.year is None:
                raise ValueError("Debes indicar --year para country_ranking.")

            result = metrics.country_ranking(
                transformed,
                indicator=args.indicator,
                year=args.year
            )

        print("\nResultado de la métrica:")
        print(result.head(20).to_string(index=False))


if __name__ == "__main__":
    main()