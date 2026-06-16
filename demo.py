"""Demonstração ponta a ponta: baixa o Focus e extrai o texto."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Adiciona src/ ao path para importar os módulos do projeto.
RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from baixar_focus import baixar  # noqa: E402
from extrair_texto import extrair  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Baixa o Focus e extrai o texto.")
    parser.add_argument(
        "--abrir", action="store_true", help="Abre o .txt extraído ao final."
    )
    args = parser.parse_args()

    pasta_data = RAIZ / "data"

    # Etapa 1: baixar o PDF.
    data, pdf_path = baixar(pasta_data)
    print(f"[1/2] PDF baixado: {pdf_path} (Focus de {data.isoformat()})")

    # Etapa 2: extrair o texto.
    txt_path = extrair(pdf_path)
    print(f"[2/2] Texto extraído: {txt_path}")

    if args.abrir:
        # Abre o .txt com o aplicativo padrão do sistema operacional.
        if sys.platform.startswith("win"):
            os.startfile(txt_path)  # noqa: S606 (Windows)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(txt_path)])
        else:
            subprocess.run(["xdg-open", str(txt_path)])


if __name__ == "__main__":
    main()
