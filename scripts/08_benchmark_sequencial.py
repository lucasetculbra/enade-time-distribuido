"""
Benchmark SEQUENCIAL do ETL ENADE.

Processa os 6 anos um após o outro no processo principal (sem
multiprocessing). Mede tempo total, throughput, memória de pico.
Grava 1 linha em benchmark_execucao e 6 em benchmark_etapa.

Uso:
  python scripts/08_benchmark_sequencial.py
  python scripts/08_benchmark_sequencial.py --obs "rodada 1, máquina A"

Requer: psycopg2-binary, psutil.
"""

from __future__ import annotations

import argparse
import sys
import time

# garante importação de `etl.*` quando rodado de qualquer CWD
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from etl.bench_db import (  # noqa: E402
    coletar_metadados_maquina, conectar, consultar_metricas,
    gravar_execucao, memoria_atual_mb,
)
from etl.processar_ano import processar_ano  # noqa: E402

ANOS = (2005, 2008, 2011, 2014, 2017, 2021)


def rodar_sequencial(observacoes: str = "") -> int:
    """
    Executa o pipeline sequencial e grava no banco. Retorna execucao_id.
    Função reutilizável pela suite (script 10).
    """
    meta = coletar_metadados_maquina()
    print("=" * 80)
    print("BENCHMARK SEQUENCIAL")
    print("=" * 80)
    print(f"CPU      : {meta['cpu_modelo']}  ({meta['cpu_count']} núcleos)")
    print(f"Memória  : {meta['memoria_total_mb']:.0f} MB total")
    print(f"Anos     : {list(ANOS)}")
    print()

    mem_inicio = memoria_atual_mb()
    t0 = time.perf_counter()
    etapas: list[dict] = []
    mem_pico = mem_inicio

    for ano in ANOS:
        print(f"  [{ano}] iniciando...", end="", flush=True)
        et = processar_ano(ano)
        etapas.append(et)
        mem_pico = max(mem_pico, memoria_atual_mb())
        print(f" {et['tempo_seg']:>7.2f}s  "
              f"linhas_arq1={et['linhas_arq1']:>7}  "
              f"linhas_arq3={et['linhas_arq3']:>7}  "
              f"filtradas={et['linhas_filtradas']:>5}  "
              f"status={et['status']}")

    tempo_total = round(time.perf_counter() - t0, 4)
    linhas_processadas = sum(e["linhas_arq1"] + e["linhas_arq3"] for e in etapas)
    throughput = round(linhas_processadas / tempo_total, 2) if tempo_total > 0 else 0.0

    print()
    print(f"Tempo total           : {tempo_total:.2f}s")
    print(f"Linhas processadas    : {linhas_processadas:,}  "
          f"(arq1+arq3 dos 6 anos)")
    print(f"Throughput            : {throughput:,.0f} linhas/s")
    print(f"Memória pico (RSS)    : {mem_pico:.1f} MB "
          f"(início: {mem_inicio:.1f} MB)")

    erros = [e for e in etapas if e["status"] != "ok"]
    if erros:
        print(f"\nATENÇÃO: {len(erros)} ano(s) com erro:")
        for e in erros:
            print(f"  [{e['ano']}] {e['observacoes']}")

    # ----- grava no banco -----
    print("\nGravando em benchmark_execucao + benchmark_etapa...")
    conn = conectar()
    try:
        execucao_id, ts = gravar_execucao(
            conn,
            modo="sequencial",
            num_workers=1,
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
    ap.add_argument("--obs", default="", help="Observação livre (texto).")
    args = ap.parse_args()
    rodar_sequencial(observacoes=args.obs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
