"""Baixa o boletim Focus do Banco Central (PDF).

Parte da última segunda-feira anterior a hoje e, se o PDF não existir nessa
data (feriado, atraso de publicação etc.), recua um dia por tentativa até
encontrar o arquivo disponível.
"""

from datetime import date, timedelta
from pathlib import Path

import requests

# URL-base do PDF do Focus. {} recebe a data no formato AAAAMMDD.
URL_FOCUS = "https://www.bcb.gov.br/content/focus/focus/R{}.pdf"

# User-Agent de navegador: o servidor do BCB tende a rejeitar clientes "crus".
CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Número máximo de dias a recuar antes de desistir.
MAX_TENTATIVAS = 7


def ultima_segunda(hoje):
    """Retorna a segunda-feira mais recente ESTRITAMENTE anterior a `hoje`.

    Se `hoje` já for uma segunda, retorna a segunda da semana anterior.
    """
    # weekday(): segunda=0, ..., domingo=6.
    # Recuamos pelo menos 1 dia para garantir "estritamente anterior".
    dias_desde_segunda = hoje.weekday()  # quantos dias desde a última segunda
    if dias_desde_segunda == 0:
        # Hoje é segunda: a "última segunda anterior" é 7 dias atrás.
        return hoje - timedelta(days=7)
    return hoje - timedelta(days=dias_desde_segunda)


def baixar(dest):
    """Baixa o Focus mais recente para a pasta `dest`.

    Parte da última segunda e recua um dia por tentativa (até MAX_TENTATIVAS),
    validando que o conteúdo começa com a assinatura %PDF. Salva como
    focus_AAAA-MM-DD.pdf.

    Retorna a tupla (data, caminho) do PDF baixado.
    Levanta RuntimeError se nenhuma tentativa encontrar um PDF válido.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Data inicial: a última segunda anterior a hoje.
    data_tentativa = ultima_segunda(date.today())

    for _ in range(MAX_TENTATIVAS):
        # Monta a URL com a data no formato AAAAMMDD.
        url = URL_FOCUS.format(data_tentativa.strftime("%Y%m%d"))
        try:
            resposta = requests.get(url, headers=CABECALHOS, timeout=30)
        except requests.RequestException:
            # Falha de rede nesta data: recua um dia e tenta de novo.
            data_tentativa -= timedelta(days=1)
            continue

        # Considera válido apenas se a resposta for 200 e os bytes forem PDF.
        if resposta.status_code == 200 and resposta.content[:4] == b"%PDF":
            # Nome do arquivo segue a convenção focus_AAAA-MM-DD.pdf.
            nome = f"focus_{data_tentativa.isoformat()}.pdf"
            caminho = dest / nome
            caminho.write_bytes(resposta.content)
            return data_tentativa, caminho

        # Não é PDF (provável feriado/ausência): recua um dia.
        data_tentativa -= timedelta(days=1)

    raise RuntimeError(
        f"Nenhum PDF do Focus encontrado nas últimas {MAX_TENTATIVAS} tentativas."
    )


def main():
    """Baixa o Focus mais recente para a pasta data/."""
    # data/ fica na raiz do projeto (um nível acima de src/).
    pasta_data = Path(__file__).resolve().parent.parent / "data"
    data, caminho = baixar(pasta_data)
    print(f"Focus de {data.isoformat()} salvo em {caminho}")


if __name__ == "__main__":
    main()
