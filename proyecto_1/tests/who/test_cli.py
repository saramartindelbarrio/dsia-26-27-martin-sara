
import sys

import pandas as pd
import pytest

from who_app.cli import main


def create_test_csv(tmp_path):
    """Crea un CSV pequeño con datos de prueba de la OMS."""

    frame = pd.DataFrame({
        "Measure code": ["HFA_1", "HFA_1", "HFA_1", "HFA_1"],
        "SEX": ["ALL", "ALL", "ALL", "ALL"],
        "PLACE_RESIDENCE": [None, None, None, None],
        "YES_NO": [None, None, None, None],
        "COUNTRY_REGION": ["ESP", "ESP", "FRA", "FRA"],
        "YEAR": [2020, 2021, 2020, 2021],
        "VALUE": [100, 110, 200, 220]
    })

    input_folder = tmp_path / "who"
    input_folder.mkdir()

    frame.to_csv(input_folder / "datos.csv", index=False)

    return input_folder


@pytest.mark.integration
def test_cli_creates_dataset(tmp_path, monkeypatch):
    """Comprueba que el CLI ejecuta todo el pipeline y guarda el CSV."""

    # ARRANGE
    input_folder = create_test_csv(tmp_path)
    output_file = tmp_path / "processed" / "who_dataset.csv"

    monkeypatch.setattr(sys, "argv", [
        "who_app.cli",
        "--input", str(input_folder),
        "--output", str(output_file),
        "--measures", "HFA_1"
    ])

    # ACT
    main()

    # ASSERT
    assert output_file.exists()

    result = pd.read_csv(output_file)

    assert len(result) == 4
    assert "HFA_1_ALL" in result.columns

    esp_2020 = result[
        (result["COUNTRY_REGION"] == "ESP")
        & (result["YEAR"] == 2020)
    ]

    assert esp_2020.iloc[0]["HFA_1_ALL"] == 100


def test_cli_percentage_change(tmp_path, monkeypatch, capsys):
    """Comprueba que el CLI calcula la variación porcentual."""

    input_folder = create_test_csv(tmp_path)
    output_file = tmp_path / "resultado.csv"

    monkeypatch.setattr(sys, "argv", [
        "who_app.cli",
        "--input", str(input_folder),
        "--output", str(output_file),
        "--measures", "HFA_1",
        "--metric", "percentage_change",
        "--indicator", "HFA_1_ALL",
        "--start-year", "2020",
        "--end-year", "2021"
    ])

    main()

    captured = capsys.readouterr()

    assert "Resultado de la métrica:" in captured.out
    assert "percentage_change" in captured.out


def test_cli_yearly_change(tmp_path, monkeypatch, capsys):
    """Comprueba que el CLI calcula el cambio anual de España."""

    input_folder = create_test_csv(tmp_path)
    output_file = tmp_path / "resultado.csv"

    monkeypatch.setattr(sys, "argv", [
        "who_app.cli",
        "--input", str(input_folder),
        "--output", str(output_file),
        "--measures", "HFA_1",
        "--metric", "yearly_change",
        "--indicator", "HFA_1_ALL",
        "--country", "ESP"
    ])

    main()

    captured = capsys.readouterr()

    assert "Resultado de la métrica:" in captured.out
    assert "ESP" in captured.out
    assert "FRA" not in captured.out


def test_cli_missing_indicator(tmp_path, monkeypatch):
    """Comprueba que una métrica requiere indicar un indicador."""

    input_folder = create_test_csv(tmp_path)
    output_file = tmp_path / "resultado.csv"

    monkeypatch.setattr(sys, "argv", [
        "who_app.cli",
        "--input", str(input_folder),
        "--output", str(output_file),
        "--measures", "HFA_1",
        "--metric", "percentage_change",
        "--start-year", "2020",
        "--end-year", "2021"
    ])

    with pytest.raises(ValueError, match="--indicator"):
        main()