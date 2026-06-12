"""
Benchmark PARALELO do ETL ENADE (processamento de dados por ano).

Cada worker processa 1 ano completo via `etl.processar_ano.processar_ano`.
Usa `concurrent.futures.ProcessPoolExecutor` (processos, não threads —
trabalho é CPU+I/O bound e o GIL atrapalha em threads).

No Windows o método padrão é SPAWN, por isso:
  - `processar_ano` está em módulo top-level (etl/processar_ano.py)
  - este script tem `if __name__ == "__main__":` + `freeze_support()`
  - apenas o processo principal conecta no PostgreSQL

Uso:
  python scripts/09_benchmark_paralelo.py                  # 4 workers
  python scripts/09_benchmark_paralelo.py --workers 2
  python scripts/09_benchmark_paralelo.py --workers 4 --obs "rodada A"

Requer: psycopg2-binary, psutil.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import freeze_support

# garante importação de `etl.*` quando rodado de qualquer CWD
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from etl.bench_db import (  # noqa: E402
    coletar_metadados_maquina, conectar, gravar_execucao, memoria_atual_mb,
)
from etl.processar_ano import processar_ano  # noqa: E402

ANOS = (2005, 2008, 2011, 2014, 2017, 2021)


def rodar_paralelo(num_workers: int, observacoes: str = "") -> int:
    """
    Executa o pipeline em paralelo com N workers e grava no banco.
    Retorna execucao_id. Reutilizável pela suite (script 10).
    """
    if num_workers < 1:
        raise ValueError("num_workers deve ser >= 1")

    meta = coletar_metadados_maquina()
    print("=" * 80)
    print(f"BENCHMARK PARALELO  (workers={num_workers})")
    print("=" * 80)
    print(f"CPU      : {meta['cpu_modelo']}  ({meta['cpu_count']} núcleos)")
    print(f"Memória  : {meta['memoria_total_mb']:.0f} MB total")
    print(f"Anos     : {list(ANOS)}")
    print()

    if num_workers > meta["cpu_count"]:
        print(f"AVISO: workers ({num_workers}) > núcleos lógicos "
              f"({meta['cpu_count']}) — oversubscription esperada.\n")

    mem_inicio = memoria_atual_mb()
    t0 = time.perf_counter()
    etapas: list[dict] = []
    mem_pico = mem_inicio

    # ProcessPoolExecutor: submete os 6 anos; workers retornam dict.
    # Como são 6 anos e os tempos por ano variam, ordem de conclusão != ordem
    # de submissão. Ordenamos por ano antes de gravar.
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futuros = {executor.submit(processar_ano, ano): ano for ano in ANOS}
        for fut in as_completed(futuros):
            ano = futuros[fut]
            try:
                et = fut.result()
            except Exception as exc:  # nunca quebra a suite
                et = {
                    "ano": ano, "worker_pid": -1,
                    "timestamp_inicio": "", "timestamp_fim": "",
                    "tempo_seg": 0.0, "linhas_arq1": 0, "linhas_arq3": 0,
                    "linhas_filtradas": 0, "cursos_unicos": 0,
                    "min_media": None, "max_media": None, "mean_media": None,
                    "count_cursos_com_media": 0,
                    "status": "erro", "observacoes": f"future: {exc}",
                }
            etapas.append(et)
            mem_pico = max(mem_pico, memoria_atual_mb())
            print(f"  [{et['ano']}] pid={et['worker_pid']:>6}  "
                  f"{et['tempo_seg']:>7.2f}s  "
                  f"linhas_arq3={et['linhas_arq3']:>7}  "
                  f"filtradas={et['linhas_filtradas']:>5}  "
                  f"status={et['status']}")

    etapas.sort(key=lambda e: e["ano"])

    tempo_total = round(time.perf_counter() - t0, 4)
    linhas_processadas = sum(e["linhas_arq1"] + e["linhas_arq3"] for e in etapas)
    throughput = round(linhas_processadas / tempo_total, 2) if tempo_total > 0 else 0.0

    soma_etapas = sum(e["tempo_seg"] for e in etapas)
    sobreposicao = soma_etapas / tempo_total if tempo_total > 0 else 0.0

    print()
    print(f"Tempo total wall-clock: {tempo_total:.2f}s")
    print(f"Soma tempos das etapas: {soma_etapas:.2f}s  "
          f"(sobreposição efetiva: {sobreposicao:.2f}x)")
    print(f"Linhas processadas    : {linhas_processadas:,}")
    print(f"Throughput            : {throughput:,.0f} linhas/s")
    print(f"Memória pico (RSS)    : {mem_pico:.1f} MB "
          f"(início: {mem_inicio:.1f} MB)")

    erros = [e for e in etapas if e["status"] != "ok"]
    if erros:
        print(f"\nATENÇÃO: {len(erros)} ano(s) com erro:")
        for e in erros:
            print(f"  [{e['ano']}] {e['observacoes']}")

    # ----- grava no banco (apenas no processo principal) -----
    print("\nGravando em benchmark_execucao + benchmark_etapa...")
    conn = conectar()
    try:
        execucao_id, ts = gravar_execucao(
            conn,
            modo="paralelo",
            num_workers=num_workers,
            tempo_total_seg=tempo_total,
            linhas_processadas=linhas_processadas,
            throughput_lps=throughput,
            cpu_count=meta["cpu_count"],
            cpu_modelo=meta["cpu_modelo"],
            memoria_pico_mb=mem_pico,
            observacoes=observacoes,
            etapas=etapas,
        )
    finally:
        conn.close()

    print(f"  execucao_id = {execucao_id}   timestamp = {ts}")
    return execucao_id


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=4,
                    help="Número de processos paralelos (default: 4).")
    ap.add_argument("--obs", default="", help="Observação livre (texto).")
    args = ap.parse_args()
    rodar_paralelo(num_workers=args.workers, observacoes=args.obs)
    return 0


if __name__ == "__main__":
    freeze_support()  # obrigatório no Windows quando empacotado (.exe)
    sys.exit(main())
