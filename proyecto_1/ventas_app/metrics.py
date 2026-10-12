from ventas_app.validator import SalesRecord


class SalesMetrics:
    """Calcula métricas sobre registros de ventas válidos."""

    def total_by_region(
        self,
        records: list[SalesRecord],
    ) -> dict[str, float]:

        totals: dict[str, float] = {}

        for record in records:
            totals[record.region] = (
                totals.get(record.region, 0.0) #pone cero si todavia no existia en el diccionarioa
                + record.amount
            )

        return dict(
            sorted(
                totals.items(), #obtenemos los pares de clave y valor
                key=lambda item: item[1], #queremos ordenar por el importe y no por el nombre de la region
                reverse=True, #de mayor a menor
            )
        )