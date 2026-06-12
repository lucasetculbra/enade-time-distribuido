# Evidências de testes — checklist de entrega

Documento para anexar as capturas de tela (prints) que comprovam o
funcionamento de cada camada do projeto. Os espaços abaixo estão
**vazios propositadamente** — adicione cada imagem antes da entrega
final.

## Convenções

- Salvar as imagens em `docs\evidencias\` (pode criar a pasta no
  momento da entrega).
- Nomear sequencialmente: `01_docker_ps.png`, `02_validar_banco.png`,
  etc.
- Capturar a janela inteira com a barra de título visível para
  comprovar o contexto (terminal/navegador, hora, host).
- Preferir prints com **resolução nativa** (não capturar com zoom).

---

## 1. Infraestrutura

### 1.1 Docker / PostgreSQL healthy

**Comando:**
```powershell
docker compose ps
```

**Esperado:** linha do container `enade_postgres` com `STATUS = Up X minutes (healthy)` e porta `5432->5432`.

> _Adicionar print aqui — `docs/evidencias/01_docker_ps.png`._

---

### 1.2 Validação do banco — 24.967 linhas em `fato_enade`

**Comando:**
```powershell
.\.venv\Scripts\Activate.ps1
python scripts\07_validar_banco.py
```

**Esperado:** saída do script mostrando contagem `24967` em `fato_enade`, presença das dimensões e tabelas de benchmark.

> _Adicionar print aqui — `docs/evidencias/02_validar_banco.png`._

---

## 2. Fase 2 — benchmark

### 2.1 Benchmark sequencial (execução #4)

**Comando:**
```powershell
python scripts\08_benchmark_sequencial.py
```

**Esperado:** tempo total ≈ 243 s, throughput ≈ 21.927 linhas/s.

> _Adicionar print aqui — `docs/evidencias/03_bench_sequencial.png`._

---

### 2.2 Benchmark paralelo — 2 workers (execução #5)

**Comando:**
```powershell
python scripts\09_benchmark_paralelo.py --workers 2
```

**Esperado:** tempo total ≈ 198 s, speedup ≈ 1,23 ×, eficiência ≈ 61 %.

> _Adicionar print aqui — `docs/evidencias/04_bench_2w.png`._

---

### 2.3 Benchmark paralelo — 4 workers (execução #6)

**Comando:**
```powershell
python scripts\09_benchmark_paralelo.py --workers 4
```

**Esperado:** tempo total ≈ 219 s, speedup ≈ 1,11 ×, eficiência ≈ 28 %.

> _Adicionar print aqui — `docs/evidencias/05_bench_4w.png`._

---

## 3. Fase 3 — API FastAPI

### 3.1 Swagger UI

**URL:** http://localhost:8000/docs

**Esperado:** página Swagger com 4 grupos de endpoints (`health`, `dimensoes`, `analises`, `benchmark`) e ~15 rotas listadas.

> _Adicionar print aqui — `docs/evidencias/06_swagger.png`._

---

### 3.2 `/api/health`

**URL:** http://localhost:8000/api/health

**Esperado:** resposta JSON `{ "status": "ok", "database": "ok", "version": "0.1.0" }`.

> _Adicionar print aqui — `docs/evidencias/07_health.png`._

---

### 3.3 `/api/benchmark/comparativo`

**URL:** http://localhost:8000/api/benchmark/comparativo

**Esperado:** JSON com baseline #4 e itens das execuções #4, #5, #6 com speedup/eficiência calculados.

> _Adicionar print aqui — `docs/evidencias/08_comparativo.png`._

---

## 4. Fase 4 — frontend

### 4.1 Visão geral

**URL:** http://localhost:5173

**Esperado:** badge "API online" no header, KPIs preenchidos com valores reais (24.967, 6 anos, 2 regiões, 16 UFs, 243,55 s, 1,2265 ×, 61,32 %, 26.893 linhas/s), card destacando "Melhor configuração: 2 workers".

> _Adicionar print aqui — `docs/evidencias/09_home.png`._

---

### 4.2 ENADE — por ano

**URL:** http://localhost:5173/enade/anual

**Esperado:** gráfico de linha com 6 pontos (2005, 2008, 2011, 2014, 2017, 2021) e cards de KPI calculados.

> _Adicionar print aqui — `docs/evidencias/10_enade_anual.png`._

---

### 4.3 SPD — comparativo (a tela-vitrine)

**URL:** http://localhost:5173/spd/comparativo

**Esperado:**
- Card verde de destaque com "Melhor configuração: 2 workers (#5)".
- 4 gráficos: tempo, speedup, eficiência, throughput.
- Texto explicativo "Por que 2 workers superou 4 workers".

> _Adicionar print aqui — `docs/evidencias/11_spd_comparativo.png`._

---

### 4.4 Drill-down de etapas

**URL:** http://localhost:5173/spd/etapas/5

**Esperado:** gráfico de barras com tempo por ano e tabela detalhada das 6 etapas com `worker_pid` e timestamps.

> _Adicionar print aqui — `docs/evidencias/12_etapas.png`._

---

## 5. Build do frontend

### 5.1 `npm run build` passando

**Comando:**
```powershell
cd C:\Projetos\ENADE\frontend
npm run build
```

**Esperado:** `vite v5.x building for production...`, lista de chunks em `dist/`, mensagem `built in X.XXs`. Pode haver aviso "chunks larger than 500 kB" — é informativo, não é erro.

> _Adicionar print aqui — `docs/evidencias/13_build.png`._

---

### 5.2 `npm run preview` rodando em :3000

**Comando:**
```powershell
npm run preview -- --host 0.0.0.0 --port 3000
```

**Esperado:** Vite servindo `dist/` em http://localhost:3000 e dashboard funcional com API conectada (CORS já configurado para essa porta).

> _Adicionar print aqui — `docs/evidencias/14_preview.png`._

---

## Resumo da bateria

| # | Item | Status |
|--:|------|:------:|
| 1.1 | Docker healthy | ⬜ |
| 1.2 | Banco com 24.967 linhas | ⬜ |
| 2.1 | Bench sequencial #4 | ⬜ |
| 2.2 | Bench paralelo 2w #5 | ⬜ |
| 2.3 | Bench paralelo 4w #6 | ⬜ |
| 3.1 | Swagger UI | ⬜ |
| 3.2 | `/api/health` | ⬜ |
| 3.3 | `/api/benchmark/comparativo` | ⬜ |
| 4.1 | Frontend — Visão geral | ⬜ |
| 4.2 | Frontend — ENADE anual | ⬜ |
| 4.3 | Frontend — SPD comparativo | ⬜ |
| 4.4 | Frontend — etapas | ⬜ |
| 5.1 | `npm run build` | ⬜ |
| 5.2 | `npm run preview` em :3000 | ⬜ |

Marcar com `✅` cada item conforme o print correspondente for anexado.
