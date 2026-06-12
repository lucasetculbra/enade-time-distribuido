# Guia de apresentação oral

Roteiro sugerido para apresentar o projeto **ENADE-Time Distribuído** em
**8 a 12 minutos**. As falas estão em linguagem simples e direta, para
serem usadas como referência (não como script literal). Adapte conforme
o público.

## Estrutura geral (≈ 10 min)

| Bloco | Tempo | Conteúdo |
|---|---:|---|
| 1 | 0:30 | Problema e objetivo |
| 2 | 1:00 | Base de dados ENADE |
| 3 | 1:00 | Pipeline de processamento |
| 4 | 0:45 | Banco PostgreSQL |
| 5 | 1:30 | Benchmark sequencial vs. paralelo |
| 6 | 1:30 | Resultados (speedup e eficiência) |
| 7 | 1:00 | API FastAPI |
| 8 | 1:30 | Dashboard React (demo ao vivo) |
| 9 | 0:45 | Conclusão técnica |

## Antes de começar

- Deixar abertos:
  - Docker Desktop com `enade_postgres` `(healthy)`.
  - Terminal com `uvicorn` rodando (`http://localhost:8000/docs` aberto).
  - Navegador com `http://localhost:5173` aberto na Visão Geral.
  - Aba extra com `/spd/comparativo` pré-carregada.
- Conferir o relógio do projetor.
- Ter [`RESULTADOS_BENCHMARK.md`](RESULTADOS_BENCHMARK.md) impresso ou
  em outra janela para citar os números exatos.

---

## 1. Problema e objetivo (0:30)

> *"O ENADE produz, a cada três anos, milhões de linhas de microdados.
> Processá-los é caro — ler, filtrar, validar e carregar tudo num banco
> leva minutos. Este projeto investiga: **dá pra ganhar tempo
> paralelizando esse trabalho?** Se sim, quanto, e qual o ponto ótimo
> de workers no nosso hardware?"*

Pontos a fixar:
- Objetivo **acadêmico**: aplicar SPD (Sistemas Paralelos e Distribuídos)
  a um cenário real.
- Não é só "rodar mais rápido": é **medir e explicar** o ganho.

## 2. Base de dados ENADE (1:00)

> *"Trabalhamos com os microdados oficiais do INEP, recorte de
> Computação no Norte e Nordeste, edições 2005, 2008, 2011, 2014, 2017
> e 2021 — os ciclos trienais do ENADE para essa área. Depois de
> filtrar e validar, ficamos com **24.967 registros** consolidados,
> com nota da prova de formação geral por aluno, IES e curso."*

Mostrar (opcional): pasta `microdados_enade_2021\` com os TXT brutos →
pasta `dados_processados\` com o CSV consolidado.

## 3. Pipeline de processamento (1:00)

> *"O pipeline tem três etapas: ler os TXT brutos (que vêm em
> encodings variados), filtrar pelo recorte (Computação + Norte/Nordeste)
> e carregar no PostgreSQL via COPY FROM STDIN. Todo o ETL está em
> scripts Python numerados de 01 a 10 — o ponto importante para o
> experimento é que o trabalho **pode ser dividido por ano**: cada ano
> é independente, então é candidato natural a paralelismo."*

Pontos a fixar:
- **Granularidade do paralelismo:** ano-a-ano (não linha-a-linha).
- **Por que ano-a-ano?** Cada arquivo está em uma pasta separada, e
  o banco aceita várias conexões simultâneas — ganho de paralelização
  sem reescrever o schema.

## 4. Banco PostgreSQL (0:45)

> *"O banco é um Postgres 16 rodando em Docker. Modelo dimensional:
> uma tabela fato (`fato_enade`) ligada a sete dimensões (região, UF,
> ano, curso, modalidade, categoria administrativa, organização
> acadêmica). Mais duas tabelas para guardar os experimentos —
> `benchmark_execucao` e `benchmark_etapa` — e uma view
> `v_benchmark_metricas` que calcula speedup e eficiência direto em
> SQL."*

Pontos a fixar:
- **Docker = reprodutibilidade**.
- **View** evita replicar a matemática de speedup no Python.

## 5. Benchmark sequencial vs. paralelo (1:30)

> *"O experimento compara três configurações: sequencial (1 worker),
> paralelo com 2 workers e paralelo com 4 workers — usando
> `multiprocessing.Pool` do Python, com cada worker processando um ano
> inteiro. Mesmo dataset, mesmo banco, mesma máquina."*

Definições rápidas (se a banca pedir):
- **Paralelismo de dados:** mesmo código rodando em pedaços
  diferentes do dado.
- **Worker:** processo independente do sistema operacional.
- **Speedup:** quantas vezes mais rápido que o sequencial.
  Fórmula: `S(p) = T(1) / T(p)`.
- **Eficiência:** quanto do speedup ideal foi alcançado.
  Fórmula: `E(p) = S(p) / p`.

> *"Importante: a primeira leva de execuções (#1, #2, #3) foi feita
> com o projeto dentro do OneDrive, e o sincronizador estava lendo os
> arquivos enquanto a gente lia. O resultado era ruído puro. Movemos o
> projeto para um caminho local e rodamos de novo — daí as execuções
> oficiais são as #4, #5 e #6."*

## 6. Resultados — speedup e eficiência (1:30)

> *"Vamos aos números:"* (abrir `/spd/comparativo`)

Citar os valores **olhando para o dashboard**:

- **Sequencial #4** — 243,55 s · 21.927 linhas/s.
- **Paralelo 2w #5** — 198,57 s · speedup **1,2265 ×** · eficiência **61,32 %**.
- **Paralelo 4w #6** — 218,97 s · speedup 1,1122 × · eficiência 27,81 %.

> *"O ponto-chave é este: **2 workers foi melhor que 4 workers**. Não
> só rodou mais rápido, como cada worker foi muito mais bem
> aproveitado — 61 % de eficiência contra 28 %."*

**Por que 4 workers escalou mal:**

1. **Lei de Amdahl.** Parte do pipeline é inerentemente sequencial —
   o `COPY FROM STDIN` no Postgres, a abertura dos arquivos, o parsing
   do pandas. Essa parte coloca um teto no speedup.
2. **Gargalo de I/O.** Quatro workers lendo simultaneamente do disco
   geram contenção. O disco vira o ponto lento; os workers ficam
   esperando.
3. **Spawn no Windows.** Em Windows, cada novo worker carrega Python e
   pandas do zero — um custo fixo que penaliza mais quando há jobs
   curtos.
4. **Disputa no banco.** Cada worker mantém conexão e escreve no
   mesmo Postgres; mais workers significam mais contenção interna no
   servidor.

> *"Conclusão prática: nesse hardware e nesse pipeline, o ponto ótimo
> é 2 workers. Aumentar para 4 traz ganho marginal sobre o sequencial,
> mas com eficiência muito baixa — não compensa."*

## 7. API FastAPI (1:00)

> *"Sobre o banco subimos uma API read-only em FastAPI. Endpoints
> separados em três grupos: dimensões (para popular filtros), análises
> ENADE (médias por ano, por região, por UF, por IES) e benchmark
> (execuções, métricas e o comparativo que vocês viram no dashboard).
> A API tem documentação automática em Swagger — `/docs`."*

Demonstração rápida: abrir `/docs`, expandir `/api/benchmark/comparativo`,
clicar "Try it out", "Execute" e mostrar o JSON.

Pontos a fixar:
- **Read-only** — não há `POST`/`PUT`. Garantia de que a UI nunca
  altera dado.
- **CORS controlado** — só `localhost:5173` e `localhost:3000` podem
  consumir.

## 8. Dashboard React — demo (1:30)

Roteiro de cliques:

1. **Visão geral** — KPIs de cobertura ENADE e do benchmark; card
   destacando "Melhor configuração: 2 workers".
2. **ENADE → por Ano** — gráfico de linha com 6 pontos; aplicar um
   filtro (ex.: região = Norte) e mostrar a URL mudar (deep-link).
3. **SPD → Comparativo** — 4 gráficos: tempo, speedup, eficiência,
   throughput. Ler em voz alta o card de destaque.
4. **SPD → Execuções** — marcar "Mostrar execuções inválidas" para
   evidenciar que ids 1–3 existem mas estão ocultos por padrão.
5. (Opcional) **`/spd/etapas/5`** — drill-down do paralelo 2w mostrando
   a divisão por worker_pid.

Falas curtas durante a demo:
- *"Cada gráfico vem direto do Postgres via API — não tem mock."*
- *"Os filtros ficam na URL, então a banca pode bookmarkar."*
- *"O badge no canto superior direito é o status da API — se ela cair,
  o dashboard avisa em 30 segundos."*

## 9. Conclusão técnica (0:45)

> *"Três conclusões para a defesa:"*

1. **Paralelismo não é grátis.** Speedup 1,23 × com 2 workers é
   modesto, mas é o **máximo coerente** com o pipeline e o hardware.
2. **A medição importa tanto quanto o código.** Sem o cuidado de
   mover o projeto para fora do OneDrive, os resultados seriam ruído.
   Métricas de I/O exigem ambiente controlado.
3. **Arquitetura em camadas isola o experimento.** O dashboard e a
   API funcionam mesmo sem rodar o benchmark de novo, porque os
   resultados ficam no banco. Quem vier depois pode reproduzir,
   adicionar mais workers ou novos anos, sem reescrever nada.

> *"Tudo está em `C:\Projetos\ENADE`, e o passo a passo de execução
> está no README. Obrigado."*

---

## Perguntas frequentes que a banca pode fazer

**"E se vocês tivessem mais núcleos físicos?"**
> O ponto ótimo provavelmente se desloca para a direita, mas a
> tendência se mantém: existe um teto imposto pelo I/O e pelo banco.
> Com SSD NVMe e um servidor Postgres dedicado em outro host, o ganho
> com 4–8 workers seria maior.

**"Por que não usaram Spark/Dask?"**
> O dataset é pequeno (24 mil linhas finais) — um framework distribuído
> teria overhead maior que o ganho. `multiprocessing` puro deixa claro
> o experimento sem esconder a Lei de Amdahl atrás de abstrações.

**"Como sabem que os números do speedup estão certos?"**
> A métrica é calculada por uma view SQL (`v_benchmark_metricas`)
> diretamente sobre os campos `tempo_total_seg` gravados pelos
> scripts. Mesmo cálculo, em SQL, fora do código Python — auditável.

**"O que aconteceria com 8 workers?"**
> Pela tendência observada (eficiência caindo de 61 % para 28 % entre
> 2 e 4 workers), a previsão é que 8 workers tenha speedup parecido
> com 4, ou levemente menor, com eficiência abaixo de 15 %. É um
> próximo experimento natural.
