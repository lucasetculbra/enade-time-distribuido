# Design Log — ENADE-Time Distribuído

**Projeto 4 — ENADE-Time · Critério B**
Aluno responsável: **Lucas Eduardo Tavares Costa**

Registro cronológico das principais decisões de projeto, com a justificativa e as
consequências de cada uma. Serve de rastro para a defesa e para futuros mantenedores.

---

## D1 — Recorte do estudo (Computação, Norte/Nordeste, 6 ciclos)
**Decisão:** processar apenas `CO_GRUPO ∈ {40, 4004}` (Computação) em
`CO_REGIAO_CURSO ∈ {1, 2}`, edições 2005/2008/2011/2014/2017/2021.
**Por quê:** tornar o experimento tratável e reprodutível, mantendo
representatividade longitudinal (ciclos trienais da área).
**Consequência:** base final de 24.967 registros; demais pastas
`microdados_enade_*` permanecem no disco mas fora do recorte.

## D2 — Harmonização do código de curso (40 ↔ 4004)
**Decisão:** tratar 40 (2005/2008) e 4004 (2011+) como equivalentes via conjunto,
**sem** recodificar para um valor único (preserva o código original do ano).
**Por quê:** manter fidelidade ao dado bruto e permitir auditoria por ano.
**Consequência:** comparação longitudinal válida; o "mapa" da equivalência fica
documentado em `DICIONARIO_VARIAVEIS.md`, não embutido como recodificação cega.

## D3 — `CO_MODALIDADE` ausente em 2005/2008
**Decisão:** quando a coluna não existe no `arq1`, criá-la com NULL.
**Por quê:** os arquivos antigos não trazem a variável; imputar valor seria
inventar dado.
**Consequência:** modalidade fica nula nesses anos (coerente e auditável).

## D4 — Notas como média por curso (grão do `arq1`)
**Decisão:** a base consolidada está no grão de curso; cada nota é a média de
`NT_*` por `CO_CURSO` (do `arq3`).
**Por quê:** alinhar notas (nível aluno no `arq3`) ao cadastro de curso (`arq1`).
**Consequência:** linhas repetidas de um mesmo curso recebem a mesma média.

## D5 — PostgreSQL + Docker, sem ORM
**Decisão:** banco em container; API com SQL explícito (psycopg2), sem ORM.
**Por quê:** reprodutibilidade (container) e auditabilidade (SQL explícito) para
um projeto acadêmico de dados tabulares read-only.

## D6 — API read-only e CORS restrito
**Decisão:** expor apenas `GET`, sem mutações, CORS só para `localhost:5173/3000`.
**Por quê:** o dashboard nunca deve alterar dados; segurança por padrão.

## D7 — Métrica principal dos gráficos = Nota Geral (NT GER)
**Decisão:** gráficos principais usam `media_nt_ger`; tabelas mantêm FG/CE/GER.
**Por quê:** decisão pedagógica do projeto (Nota Geral como indicador-síntese).
**Consequência:** ranking de IES passou a ordenar por `media_nt_ger` no backend.

## D8 — Adição controlada de `MEDIA_NT_GER` e `MEDIA_NT_CE` (v1.0 → v1.1)
**Decisão:** acrescentar as duas notas ao consolidado por um utilitário dedicado
[`tools/adicionar_notas_ger_ce_consolidado.py`](../tools/adicionar_notas_ger_ce_consolidado.py),
com **backup automático**, **reconstrução a partir dos brutos** e **validação
linha-a-linha** contra a base anterior antes de gravar.
**Por quê:** evoluir o schema sem risco de corromper a base já validada.
**Consequência:** backup `*.backup_20260616_223051.csv` (v1.0, 11 colunas)
preservado; v1.1 com 13 colunas. Propagado ao schema/carga/validação (scripts
05/06/07), API e frontend.

## D9 — Incidente: `--reset` esvaziou o benchmark local
**Decisão/ocorrência:** ao recriar o schema com `scripts/05 --reset` (para
propagar as novas colunas), as tabelas `benchmark_execucao`/`benchmark_etapa`
foram dropadas; esses dados existiam **apenas** no banco (sem dump/CSV).
**Mitigação adotada:** **não** rerodar o benchmark nem fabricar dados; os números
oficiais permanecem em [`RESULTADOS_BENCHMARK.md`](RESULTADOS_BENCHMARK.md) e na
apresentação. As telas SPD do dashboard ficam temporariamente vazias.
**Pendência:** decidir, em etapa separada, entre restaurar de backup real ou
rerodar a suíte fora do OneDrive.

## D10 — Critério B: entregar Módulos 1 + 3
**Decisão:** priorizar ETL/Harmonização (Módulo 1, documentação) + Dashboard/
Exportação (Módulo 3, frontend), deixando o Módulo 2 (IC 95%, regressão/LOESS,
quebra estrutural) como complementar.
**Por quê:** Módulos 1 e 3 estão majoritariamente prontos e têm baixo risco;
Módulo 2 exige estatística inferencial pesada.
**Consequência:** criados 4 docs do Módulo 1 e a página `/enade/comparar` com
comparação de 2 grupos por NT GER, exportações (CSV/SVG/relatório) e alerta de
amostra reduzida.

---

## Convenções de ambiente
- Diretório oficial: `C:\Projetos\ENADE` (rodar **fora** do OneDrive).
- Comandos Node em `frontend/`; Python/Docker na raiz.
- Nada de alterar dados brutos, CSV consolidado, scripts 01–10, schema, benchmark
  ou carga sem decisão explícita.
