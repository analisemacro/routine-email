"""Envia o resumo HTML do Focus por e-mail via SMTP do Gmail.

Credenciais NUNCA ficam no código. São lidas de variáveis de ambiente:
- FOCUS_SMTP_USER          remetente (e-mail do Gmail)
- FOCUS_SMTP_APP_PASSWORD  senha de app do Gmail (não a senha normal)
- FOCUS_EMAIL_DEST         destinatários, separados por vírgula
- FOCUS_EMAIL_BCC          (opcional) cópias ocultas, separadas por vírgula
"""

import argparse
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from html.parser import HTMLParser
from pathlib import Path

# Servidor SMTP do Gmail por SSL.
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def html_mais_recente(pasta=None):
    """Retorna o focus_*.html mais recente em output/focus/.

    A ordem alfabética dos nomes focus_AAAA-MM-DD coincide com a cronológica.
    """
    if pasta is None:
        pasta = Path(__file__).resolve().parent.parent / "output" / "focus"
    pasta = Path(pasta)
    htmls = sorted(pasta.glob("focus_*.html"))
    if not htmls:
        raise SystemExit(f"Nenhum focus_*.html encontrado em {pasta}.")
    return htmls[-1]


def assunto_do_nome(html_path):
    """Deriva 'Resumo Focus — AAAA-MM-DD' a partir do nome do arquivo."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", Path(html_path).name)
    data = m.group(1) if m else "data desconhecida"
    return f"Resumo Focus — {data}"


class _ExtratorTexto(HTMLParser):
    """Extrai texto visível do HTML para o fallback em texto puro."""

    def __init__(self):
        super().__init__()
        self._partes = []
        self._ignorar = False

    def handle_starttag(self, tag, attrs):
        # Ignora conteúdo de <style>/<script>.
        if tag in ("style", "script"):
            self._ignorar = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._ignorar = False

    def handle_data(self, data):
        if not self._ignorar and data.strip():
            self._partes.append(data.strip())

    def texto(self):
        return "\n".join(self._partes)


def html_para_texto(html):
    """Converte o HTML em texto simples para o corpo alternativo."""
    parser = _ExtratorTexto()
    parser.feed(html)
    return parser.texto()


def montar_email(html, remetente, destinatarios, assunto, bcc=None):
    """Monta um EmailMessage multipart (texto + HTML).

    `destinatarios` e `bcc` são listas de endereços.
    """
    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = assunto

    # Corpo texto (fallback) + HTML como alternativa.
    msg.set_content(html_para_texto(html))
    msg.add_alternative(html, subtype="html")
    return msg


def _enderecos(valor):
    """Quebra uma string 'a@x, b@y' em lista de endereços, sem vazios."""
    if not valor:
        return []
    return [e.strip() for e in valor.split(",") if e.strip()]


def enviar(html_path=None, destinatarios=None, assunto=None):
    """Monta e envia o e-mail de fato, lendo credenciais do ambiente.

    Parâmetros opcionais sobrescrevem os padrões (HTML mais recente,
    destinatários do ambiente, assunto derivado do nome).
    """
    # Localiza o HTML.
    html_path = Path(html_path) if html_path else html_mais_recente()
    html = html_path.read_text(encoding="utf-8")

    # Credenciais — obrigatórias para envio real.
    remetente = os.environ.get("FOCUS_SMTP_USER")
    senha = os.environ.get("FOCUS_SMTP_APP_PASSWORD")
    if not remetente or not senha:
        raise SystemExit(
            "Defina FOCUS_SMTP_USER e FOCUS_SMTP_APP_PASSWORD no ambiente."
        )

    # Destinatários: argumento tem prioridade sobre a variável de ambiente.
    if destinatarios is None:
        destinatarios = _enderecos(os.environ.get("FOCUS_EMAIL_DEST"))
    if not destinatarios:
        raise SystemExit("Nenhum destinatário (use --dest ou FOCUS_EMAIL_DEST).")

    bcc = _enderecos(os.environ.get("FOCUS_EMAIL_BCC"))
    assunto = assunto or assunto_do_nome(html_path)

    msg = montar_email(html, remetente, destinatarios, assunto, bcc)

    # Envio por SSL com a senha de app.
    contexto = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=contexto) as smtp:
        smtp.login(remetente, senha)
        smtp.send_message(msg)

    print(f"E-mail enviado: '{assunto}' para {', '.join(destinatarios)}")


def main():
    parser = argparse.ArgumentParser(description="Envia o resumo HTML do Focus.")
    parser.add_argument("--html", help="Caminho do HTML. Padrão: mais recente.")
    parser.add_argument("--dest", help="Destinatários por vírgula (sobrescreve env).")
    parser.add_argument("--assunto", help="Assunto (sobrescreve o padrão).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Monta e mostra o e-mail SEM enviar e sem exigir credenciais.",
    )
    args = parser.parse_args()

    # Localiza o HTML (vale para dry-run e envio real).
    html_path = Path(args.html) if args.html else html_mais_recente()
    assunto = args.assunto or assunto_do_nome(html_path)

    if args.dry_run:
        # Não exige credenciais: só monta e exibe um resumo do que seria enviado.
        html = html_path.read_text(encoding="utf-8")
        # Remetente/dest apenas para visualização (placeholders se ausentes).
        remetente = os.environ.get("FOCUS_SMTP_USER", "(FOCUS_SMTP_USER não definido)")
        destinatarios = _enderecos(args.dest) or _enderecos(
            os.environ.get("FOCUS_EMAIL_DEST")
        ) or ["(FOCUS_EMAIL_DEST não definido)"]
        bcc = _enderecos(os.environ.get("FOCUS_EMAIL_BCC"))

        print("=== DRY-RUN (nada será enviado) ===")
        print(f"HTML:    {html_path}")
        print(f"From:    {remetente}")
        print(f"To:      {', '.join(destinatarios)}")
        if bcc:
            print(f"Bcc:     {', '.join(bcc)}")
        print(f"Subject: {assunto}")
        print("--- corpo texto (fallback) ---")
        print(html_para_texto(html))
        return

    # Envio real.
    enviar(
        html_path=html_path,
        destinatarios=_enderecos(args.dest) or None,
        assunto=args.assunto,
    )


if __name__ == "__main__":
    main()
