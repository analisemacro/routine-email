"""Testes da lógica de datas e do download do Focus."""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Adiciona src/ ao path para importar o módulo sob teste.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from baixar_focus import baixar, ultima_segunda  # noqa: E402


def test_ultima_segunda_quinta():
    # Quinta 2026-06-18 -> segunda da mesma semana, 2026-06-15.
    assert ultima_segunda(date(2026, 6, 18)) == date(2026, 6, 15)


def test_ultima_segunda_terca():
    # Terça 2026-06-16 -> segunda da mesma semana, 2026-06-15.
    assert ultima_segunda(date(2026, 6, 16)) == date(2026, 6, 15)


def test_ultima_segunda_hoje_e_segunda_recua_uma_semana():
    # Segunda 2026-06-15 -> segunda anterior, 2026-06-08 (estritamente anterior).
    assert ultima_segunda(date(2026, 6, 15)) == date(2026, 6, 8)


def test_ultima_segunda_domingo():
    # Domingo 2026-06-21 -> segunda da semana que termina, 2026-06-15.
    assert ultima_segunda(date(2026, 6, 21)) == date(2026, 6, 15)


def test_ultima_segunda_varredura_60_dias():
    # Para qualquer dia, o resultado deve ser uma segunda e estritamente anterior.
    base = date(2026, 1, 1)
    for i in range(60):
        hoje = base + timedelta(days=i)
        resultado = ultima_segunda(hoje)
        assert resultado.weekday() == 0  # é segunda-feira
        assert resultado < hoje  # estritamente anterior


@pytest.mark.network
def test_baixar_de_verdade(tmp_path):
    # Baixa o Focus real e valida o arquivo salvo.
    data, caminho = baixar(tmp_path)
    assert caminho.exists()
    assert caminho.name == f"focus_{data.isoformat()}.pdf"
    assert caminho.read_bytes()[:4] == b"%PDF"
