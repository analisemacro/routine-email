# Boletim Focus — automação semanal

## Objetivo
Toda segunda-feira, baixar o boletim Focus do Banco Central (PDF), extrair o
texto e preparar um **resumo executivo**. O fluxo é: baixar → extrair texto →
gerar resumo → entregar.

## Fonte dos dados
- Página oficial: https://www.bcb.gov.br/publicacoes/focus
- PDF (padrão de URL): `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - `{AAAAMMDD}` é a data do boletim (ano, mês, dia, sem separadores). Ex.: o
    boletim de 2026-06-15 fica em `.../R20260615.pdf`.

## Convenções
- Nomes de arquivo: `focus_AAAA-MM-DD` (data ISO, com hífens).
  - PDF baixado: `focus_AAAA-MM-DD.pdf`
  - Texto extraído: `focus_AAAA-MM-DD.txt`
  - Resumo: `focus_AAAA-MM-DD.md`
- Pastas:
  - `src/` — código.
  - `tests/` — testes.
  - `data/` — guarda os **PDFs baixados** e os **textos extraídos**.
  - `output/focus/` — guarda os **resumos**.
  - `.github/workflows/` — automação (agendamento semanal).

## Regras
- **Nunca inventar número.** Toda mediana (ou qualquer valor) citada no resumo
  deve estar presente no texto extraído do PDF. Se não está no texto, não entra
  no resumo.
- **Feriado na segunda.** O Focus normalmente sai na segunda. Quando a segunda é
  feriado (ou o PDF ainda não existe), o download **retrocede um dia por vez**
  até encontrar o PDF disponível.
