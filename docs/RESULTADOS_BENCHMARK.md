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
- A API os **filtra por padrão** via `BENCHMARK_IDS_EXCLUIR=[1,2,3]` em
  `api/settings.py`.
- Para inspecioná-los manualmente (depuração), use o query parameter
  `?apenas_validas=false` em qualquer endpoint `/api/benchmark/...`.

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
