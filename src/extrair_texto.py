"""Extrai o texto de um PDF do Focus e salva um .txt de mesmo nome."""

import argparse
from pathlib import Path

import pdfplumber


def extrair(pdf_path):
    """Abre o PDF com pdfplumber, junta o texto das páginas e salva um .txt.

    O .txt tem o mesmo nome do PDF (extensão trocada) e é gravado em UTF-8.
    Retorna o caminho do .txt gerado.
    """
    pdf_path = Path(pdf_path)

    partes = []  # texto de cada página
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # extract_text() pode devolver None em páginas sem texto.
            texto = pagina.extract_text() or ""
            partes.append(texto)

    # Junta as páginas com quebra de linha.
    texto_completo = "\n".join(partes)

    # .txt de mesmo nome, ao lado do PDF.
    txt_path = pdf_path.with_suffix(".txt")
    txt_path.write_text(texto_completo, encoding="utf-8")
    return txt_path


def main():
    """Extrai o texto de um PDF. Sem --pdf, usa o focus_*.pdf mais recente."""
    parser = argparse.ArgumentParser(description="Extrai texto de um PDF do Focus.")
    parser.add_argument("--pdf", help="Caminho do PDF. Padrão: mais recente em data/.")
    args = parser.parse_args()

    if args.pdf:
        pdf_path = Path(args.pdf)
    else:
        # Procura o focus_*.pdf mais recente em data/.
        pasta_data = Path(__file__).resolve().parent.parent / "data"
        pdfs = sorted(pasta_data.glob("focus_*.pdf"))
        if not pdfs:
            raise SystemExit("Nenhum focus_*.pdf encontrado em data/.")
        pdf_path = pdfs[-1]  # ordem alfabética = ordem de data (AAAA-MM-DD)

    txt_path = extrair(pdf_path)
    print(f"Texto extraído em {txt_path}")


if __name__ == "__main__":
    main()
