# Routine — Resumo semanal do Focus

Você está executando a Routine de resumo semanal do boletim **Focus** do Banco
Central. O download e a extração do PDF **já foram feitos** por um GitHub Action
(workflow `focus-download.yml`), que deixou os arquivos em `data/`.

Sua tarefa: ler o `.txt` mais recente de `data/`, gerar um **resumo executivo em
HTML** com a logo da **Análise Macro** e **publicá-lo** (commit + push para
`main`), o que dispara o envio do e-mail.

## Regra inviolável
**Nunca invente número.** Toda mediana (ou qualquer valor) citada no resumo deve
estar presente, literalmente, no texto extraído. Se não está no `.txt`, não
entra no resumo.

## Passos

1. **Localizar o `.txt`.** Encontre o `data/focus_*.txt` mais recente (a ordem
   alfabética dos nomes `focus_AAAA-MM-DD` coincide com a ordem cronológica).

2. **Checar frescor.** Confirme pela data no nome do arquivo que o boletim é da
   semana corrente. Se for de uma semana anterior (Action pode ter falhado),
   **pare sem commitar o HTML** e relate em vez de seguir — não gere um resumo
   de dado velho (assim nada é enviado).

3. **Sanity check.** Localize no texto os valores-âncora — projeções de
   **IPCA**, **Selic** e **PIB** (medianas do Top 5 / do mercado, para o ano
   corrente e o seguinte). Confirme que cada número que você pretende citar
   aparece de fato no `.txt`. Se algum não for encontrado, não o cite. Se os
   valores-âncora não fecharem (números que claramente não batem com o texto),
   **pare sem commitar o HTML** — sem commit, nada é enviado.

4. **Escrever o resumo executivo + 3 revisões.** Redija um resumo executivo
   curto e objetivo (foco em IPCA, Selic, PIB e câmbio, com as variações em
   relação à semana anterior quando o texto trouxer). Em seguida, **revise 3
   vezes**, cada passada com um objetivo: (a) conferir que todo número bate com
   o `.txt`; (b) cortar excesso e jargão, deixar claro e direto; (c) checar
   coesão e tom (profissional, sem maneirismos de IA).

5. **Montar o HTML.** Gere o arquivo `output/focus/focus_AAAA-MM-DD.html`
   (mesma data do `.txt`), com a **logo da Análise Macro** no topo e o resumo
   formatado de forma limpa para e-mail.

6. **Publicar o HTML.** Faça `git add output/focus/focus_AAAA-MM-DD.html`,
   `git commit` e `git push` para a branch `main`. **É esse push que dispara o
   Action de envio** (`focus-enviar.yml`), que roda `src/enviar_email.py` e
   manda o e-mail. Ou seja: você não envia o e-mail diretamente — você publica o
   HTML e o Action cuida do envio.

   O **remetente**, a **senha de app** e o(s) **destinatário(s)** ficam nos
   **Secrets do repositório** (`FOCUS_SMTP_USER`, `FOCUS_SMTP_APP_PASSWORD`,
   `FOCUS_EMAIL_DEST`, `FOCUS_EMAIL_BCC`), **nunca** no HTML, no commit ou em
   qualquer arquivo versionado.

## Lembrete final
Se em qualquer passo um número não puder ser confirmado no `.txt`, omita-o e
sinalize a ausência — **nunca preencha com estimativa própria**.
