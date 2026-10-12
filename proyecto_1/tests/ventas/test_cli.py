
import sys
import pandas as pd
import pytest
from ventas_app.cli import main
from ventas_app.loader import DataLoadError


def create_test_csv(tmp_path):
    """Crea un CSV temporal con ventas válidas e inválidas."""

    frame = pd.DataFrame({
        "region": ["Norte", "Sur", "Norte", "Este"],
        "producto": ["A", "B", "C", "D"],
        "unidades": [2, 3, 4, -1],
        "precio_unitario": [10, 20, 5, 15]})

    input_file = tmp_path / "ventas.csv"
    frame.to_csv(input_file, index=False)

    return input_file


@pytest.mark.integration
def test_cli_creates_clean_csv(tmp_path, monkeypatch):
    """Comprueba que el CLI procesa y guarda las ventas válidas."""

    # ARRANGE
    input_file = create_test_csv(tmp_path)
    output_file = tmp_path / "ventas_limpias.csv"

    monkeypatch.setattr(sys, "argv", [
        "ventas_app.cli",
        "--input", str(input_file),
        "--output", str(output_file)])

    # ACT
    main()

    # ASSERT
    assert output_file.exists()

    result = pd.read_csv(output_file)

    assert len(result) == 3
    assert "importe" in result.columns
    assert list(result.columns) == [
        "region", "producto", "unidades",
        "precio_unitario", "importe"
    ]

    assert result["importe"].tolist() == [20, 60, 20]
    assert "Este" not in result["region"].values


def test_cli_region_totals(tmp_path, monkeypatch, capsys):
    """Comprueba que muestra los importes por región."""

    input_file = create_test_csv(tmp_path)
    output_file = tmp_path / "ventas_limpias.csv"

    monkeypatch.setattr(sys, "argv", [
        "ventas_app.cli",
        "--input", str(input_file),
        "--output", str(output_file)
    ])

    main()

    captured = capsys.readouterr()

    assert "Registros válidos: 3 | inválidos: 1" in captured.out
    assert "Importe por región:" in captured.out
    assert "Sur: 60.00" in captured.out
    assert "Norte: 40.00" in captured.out


def test_cli_missing_input_file(tmp_path, monkeypatch):
    """Comprueba que lanza un error si el CSV no existe."""

    input_file = tmp_path / "no_existe.csv"
    output_file = tmp_path / "ventas_limpias.csv"

    monkeypatch.setattr(sys, "argv", [
        "ventas_app.cli",
        "--input", str(input_file),
        "--output", str(output_file)])

    with pytest.raises(DataLoadError):
        main()

    assert not output_file.exists()


def test_cli_missing_arguments(monkeypatch):
    """Comprueba que los argumentos obligatorios son necesarios."""

    monkeypatch.setattr(sys, "argv", ["ventas_app.cli"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2