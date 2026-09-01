# Resultados do benchmark (Fase 2)

Resultados oficiais do experimento de processamento paralelo do ETL
dos microdados ENADE. Todas as execuções abaixo são as **válidas** —
realizadas com o projeto **fora do OneDrive** para evitar contenção de
I/O com a sincronização.

## Configuração do experimento

| Parâmetro | Valor |
|---|---|
| Pipeline | leitura dos TXT → filtro/parse pandas → upsert PostgreSQL |
| Linhas processadas por execução | 5.340.372 (somatório dos `arq3` dos 6 anos) |
| Anos por execução | 2005, 2008, 2011, 2014, 2017, 2021 |
| Banco | PostgreSQL 16 em Docker (`enade_postgres`) |
| Local de execução | `C:\Projetos\ENADE` (fora do OneDrive) |
| Modelo de paralelismo | `multiprocessing.Pool` (paralelismo por ano) |

## Execuções válidas

### Sequencial — execução #4 (baseline)

| Métrica | Valor |
|---|---|
| Modo | sequencial |
| Workers | 1 |
| Tempo total | **243,5496 s** |
| Linhas processadas | 5.340.372 |
| Throughput | **21.927,25 linhas/s** |

### Paralelo 2 workers — execução #5

| Métrica | Valor |
|---|---|
| Modo | paralelo |
| Workers | 2 |
| Tempo total | **198,5749 s** |
| Speedup | **1,2265 ×** |
| Eficiência | **61,32 %** |
| Throughput | **26.893,49 linhas/s** |

### Paralelo 4 workers — execução #6

| Métrica | Valor |
|---|---|
| Modo | paralelo |
| Workers | 4 |
| Tempo total | **218,9745 s** |
| Speedup | **1,1122 ×** |
| Eficiência | **27,81 %** |
| Throughput | **24.388,10 linhas/s** |

## Tabela comparativa

| Exec. | Modo | Workers | Tempo (s) | Speedup | Eficiência | Throughput (lps) |
|------:|------|--------:|----------:|--------:|-----------:|-----------------:|
| 4 | sequencial | 1 | 243,5496 | 1,0000 | 100,00 % | 21.927,25 |
| 5 | paralelo   | 2 | 198,5749 | **1,2265** | **61,32 %** | **26.893,49** |
| 6 | paralelo   | 4 | 218,9745 | 1,1122 | 27,81 % | 24.388,10 |

## Conclusão

> **Melhor configuração: 2 workers.**

- **2 workers** entregou o **menor tempo absoluto** e o **maior
  throughput** do experimento. A eficiência (61,32 %) indica que cada
  worker está bem utilizado, com sobreposição saudável entre I/O e
  CPU.
- **4 workers** ainda supera o sequencial (speedup 1,11 ×), mas
  **piora** em relação a 2 workers. A eficiência despenca para 27,81 %,
  evidenciando que cada worker adicional contribui cada vez menos.
- O comportamento é coerente com a **Lei de Amdahl**: a fração
  sequencial do pipeline (abertura de arquivos texto, parsing pandas
  linha a linha, `COPY FROM STDIN` no Postgres) limita o speedup
  máximo. Adicionar workers além do ponto ótimo aumenta o **overhead**
  sem proporcional ganho de throughput.

### Fatores que explicam o platô em 2 workers

1. **Gargalo de I/O de disco.** Mesmo em SSD, abrir/ler 6 arquivos TXT
   simultaneamente em 4 workers gera contenção da fila do controlador.
   Os workers passam mais tempo esperando bytes do que processando.
2. **Disputa do PostgreSQL.** O `COPY FROM STDIN` serializa no servidor
   por conexão. Múltiplos workers competem por escrita; o ganho
   "paralelo" some quando o gargalo é o banco.
3. **Overhead de `spawn` no Windows.** No Windows, `multiprocessing`
   usa o método `spawn` (em vez de `fork`), o que significa que cada
   worker carrega Python, importa módulos e reinicializa pandas do
   zero. Esse custo fixo penaliza configurações com mais workers
   processando jobs curtos.
4. **Lei de Amdahl.** Se ~30 % do pipeline for inerentemente
   sequencial, o speedup teórico máximo é
   `1 / (0,30 + 0,70/p)` — saturando rápido conforme `p` cresce. O
   speedup observado (1,23 ×) é compatível com uma fração paralela
   efetiva em torno de 65–70 %.

## Por que existem execuções #1, #2 e #3 e por que ficam ocultas

As execuções de id 1, 2 e 3 foram **testes de ambiente** realizados
**dentro do OneDrive**, antes da decisão de mover o projeto para
`C:\Projetos\ENADE`. O cliente do OneDrive estava sincronizando os
arquivos durante a leitura, criando contenção severa de I/O e
poluindo as métricas.

- Esses registros **não foram apagados** do banco (preservação do
  histórico).
- Na época, a API os filtrava por padrão via `BENCHMARK_IDS_EXCLUIR=[1,2,3]`
  em `api/settings.py`. **Esse default foi removido** — ver a nota abaixo.
- Para ocultar execuções específicas hoje, defina a variável de ambiente
  `BENCHMARK_IDS_EXCLUIR` (JSON) antes de subir a API, ex.:
  `$env:BENCHMARK_IDS_EXCLUIR='[1,2,3]'`.
- Para inspecionar as ocultas, use o query parameter
  `?apenas_validas=false` em qualquer endpoint `/api/benchmark/...`.

> ⚠️ **Por que o default virou lista vazia.** O `id` de
> `benchmark_execucao` é um `BIGSERIAL` e **reinicia em 1** a cada
> `05_criar_schema_postgres.py --reset`. Uma lista fixa `[1,2,3]` deixou de
> apontar para os testes do OneDrive e passou a esconder justamente as
> execuções válidas da rodada atual — zerando as três telas de Benchmark
> SPD. Exclusão por id é frágil por natureza; se precisar ocultar
> execuções, prefira a variável de ambiente por rodada.

> **Lição aprendida:** clientes de sincronização em nuvem (OneDrive,
> Dropbox, Google Drive) **invalidam medições de I/O**. Mover o projeto
> para um caminho local sem sincronização foi o que tornou o
> experimento reproduzível.

## Reprodução

```powershell
cd C:\Projetos\ENADE
.\.venv\Scripts\Activate.ps1
python scripts\10_rodar_suite_benchmark.py
```

Os novos `id`s serão maiores que 6 e aparecerão automaticamente na
API/dashboard (já não estão na lista de exclusão).

---

## Rodada adicional de repopulação do benchmark para demonstração

> Esta seção **não substitui** os resultados oficiais acima — eles continuam
> válidos. Ela apenas documenta uma **segunda execução real**, feita em outro
> momento e em outra condição de máquina, para repor os dados das telas
> **Benchmark SPD** depois que um `--reset` do schema esvaziou as tabelas
> `benchmark_execucao` / `benchmark_etapa`.

### Contexto
- A **rodada original documentada** (seção acima) apontava **2 workers** como
  melhor configuração (speedup 1,2265×).
- Após o reset do banco, as tabelas de benchmark ficaram vazias. Para a tela SPD
  voltar a ter dados, foi executada uma **nova rodada real**, novamente
  **fora do OneDrive**, com `python scripts\10_rodar_suite_benchmark.py`.
- Nenhum dado foi fabricado: os números abaixo são de uma execução genuína do
  pipeline (5.340.372 linhas por rodada, 6 anos).

### Resultados desta rodada adicional (data: 2026-06-21)

| ID | Modo | Workers | Tempo | Speedup | Eficiência | Throughput |
|----|------|--------:|------:|--------:|-----------:|-----------:|
| 1 | sequencial | 1 | 89,58 s | 1,000 | 100,0 % | 59.617 l/s |
| 2 | paralelo | 2 | 68,40 s | 1,3096 | 65,48 % | 78.076 l/s |
| **3** | **paralelo** | **4** | **43,17 s** | **2,0749** | **51,87 %** | **123.700 l/s** |

Máquina desta rodada: Intel 8 núcleos, 24 GB RAM.

### Interpretação
- **Nesta nova rodada, 4 workers apresentou o melhor tempo, speedup e
  throughput** — diferente da rodada original, onde 2 workers venceu.
- Isso **não invalida** nenhum dos dois resultados: **ambos são reais**, mas
  correspondem a **execuções diferentes**, em **condições de máquina diferentes**.
- Benchmarks de I/O e CPU **variam** conforme processador, disco (SSD/NVMe),
  quantidade de RAM, processos em segundo plano e estado térmico da máquina.
  Em uma máquina mais rápida e com I/O folgado, o paralelismo escala melhor e o
  ponto ótimo de workers tende a se deslocar para a direita (mais workers).

### O que está carregado no banco para a demonstração atual
- Para a **demonstração atual do dashboard**, os dados carregados no banco são os
  desta **rodada adicional** (IDs **1, 2, 3**).
- Esses IDs aparecem normalmente na API e no dashboard: o default de
  `BENCHMARK_IDS_EXCLUIR` é lista vazia. Nenhum passo extra é necessário —
  basta subir a API.
- Os **números oficiais** (Fase 2, seção no topo deste documento) permanecem como
  o resultado de referência do trabalho.

### Observação sobre a leitura das duas rodadas
A tela **Benchmark · Comparativo** gera a interpretação **a partir dos dados
carregados no banco**, e não de um texto fixo. Como a rodada atualmente
carregada é a adicional (onde 4 workers venceu), é isso que o dashboard
descreve — enquanto este documento preserva os números oficiais da Fase 2
(onde 2 workers venceu). Os dois são reais e correspondem a máquinas
diferentes.
