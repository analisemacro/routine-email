# Boletim Focus — automação semanal

Automação para baixar o boletim **Focus** do Banco Central (PDF) toda semana,
extrair o texto e, mais adiante, gerar um resumo executivo.

## Como funciona
1. **Baixar** — `src/baixar_focus.py` parte da última segunda anterior a hoje e
   recua um dia por tentativa até achar o PDF (lida com feriados).
2. **Extrair** — `src/extrair_texto.py` abre o PDF com pdfplumber e salva o
   texto em `.txt` (UTF-8).
3. **Resumir** — etapa futura: gerar um resumo executivo em `output/focus/`.

## Uso
```bash
pip install -r requirements.txt
python demo.py --abrir          # baixa, extrai e abre o texto
python src/baixar_focus.py      # só baixa para data/
python src/extrair_texto.py     # extrai o focus_*.pdf mais recente
```

## Testes
```bash
pytest -m "not network"   # testes puros (sem rede)
pytest                    # inclui o teste que baixa de verdade
```

## Estrutura
- `src/` — código
- `tests/` — testes
- `data/` — PDFs baixados e textos extraídos
- `output/focus/` — resumos (versionado)
- `.github/workflows/` — automação semanal

## Convenções
Arquivos nomeados `focus_AAAA-MM-DD` (data ISO). Veja `CLAUDE.md` para o
briefing completo e as regras do projeto.
