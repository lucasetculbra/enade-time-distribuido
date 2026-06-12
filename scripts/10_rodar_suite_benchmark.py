"""
Suite completa de benchmark — roda em sequência:
  1) Sequencial          (1 worker)
  2) Paralelo            (2 workers)
  3) Paralelo            (4 workers)

Opcionalmente (--include-cpu-count): adiciona uma 4ª rodada paralela com
N = os.cpu_count() workers — útil para máquinas mais robustas, mas pode
piorar o speedup em máquinas com pouca RAM ou disco lento.

No final, consulta v_benchmark_metricas com os IDs gerados nesta suite
e imprime tabela com tempo seq, tempo par, speedup, eficiência, throughput.

Importante (Windows + multiprocessing):
  - usa `if __name__ == "__main__":` + `freeze_support()`
  - delega para `rodar_sequencial` e `rodar_paralelo` (scripts 08 e 09)
  - apenas o processo principal conecta no PostgreSQL

Uso:
  python scripts/10_rodar_suite_benchmark.py
  python scripts/10_rodar_suite_benchmark.py --include-cpu-count
  python scripts/10_rodar_suite_benchmark.py --obs "rodada definitiva"
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from multiprocessing import freeze_support

# garante importação de `etl.*` e dos scripts irmãos
RAIZ = __import__("pathlib").Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

# import dos scripts 08 e 09 (não levantam multiprocessing no top-level)
import importlib.util


def _carregar(nome_modulo: str, caminho: str):
    spec = importlib.util.spec_from_file_location(nome_modulo, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


seq_mod = _carregar(
    "bench_seq", str(RAIZ / "scripts" / "08_benchmark_sequencial.py"))
par_mod = _carregar(
    "bench_par", str(RAIZ / "scripts" / "09_benchmark_paralelo.py"))

from etl.bench_db import conectar, consultar_metricas  # noqa: E402


def banner(titulo: str) -> None:
    print("\n" + "#" * 80)
    print(f"##  {titulo}")
    print("#" * 80)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--include-cpu-count", action="store_true",
                    help="Adiciona rodada paralela com N=os.cpu_count() "
                         "(default: NÃO incluir).")
    ap.add_argument("--obs", default="",
                    help="Observação livre aplicada a todas as execuções "
                         "(ex.: 'suite rodada 1, máquina X').")
    args = ap.parse_args()

    ts_suite = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"SUITE DE BENCHMARK — iniciada em {ts_suite}")
    obs_base = f"[suite {ts_suite}] {args.obs}".strip()

    ids: list[int] = []

    # 1) sequencial (servirá de baseline para a view)
    banner("RODADA 1/3 — SEQUENCIAL (1 worker)")
    ids.append(seq_mod.rodar_sequencial(observacoes=obs_base))

    # 2) paralelo 2 workers
    banner("RODADA 2/3 — PARALELO (2 workers)")
    ids.append(par_mod.rodar_paralelo(num_workers=2, observacoes=obs_base))

    # 3) paralelo 4 workers
    banner("RODADA 3/3 — PARALELO (4 workers)")
    ids.append(par_mod.rodar_paralelo(num_workers=4, observacoes=obs_base))

    # 4) opcional: cpu_count
    if args.include_cpu_count:
        n_cpu = os.cpu_count() or 4
        banner(f"RODADA EXTRA — PARALELO (cpu_count = {n_cpu} workers)")
        ids.append(par_mod.rodar_paralelo(
            num_workers=n_cpu, observacoes=obs_base))

    # ----- consulta a view com os IDs paralelos -----
    banner("MÉTRICAS DA SUITE (v_benchmark_metricas)")
    print("Speedup compara cada execução paralela contra a sequencial "
          "imediatamente anterior no tempo.\n")

    conn = conectar()
    try:
        metricas = consultar_metricas(conn, ids)
    finally:
        conn.close()

    if not metricas:
        print("  (nenhuma métrica retornada — a view só calcula para "
              "execuções paralelas com uma sequencial anterior)")
    else:
        print(f"{'workers':>8} {'t_seq(s)':>10} {'t_par(s)':>10} "
              f"{'speedup':>9} {'eficiência':>11} "
              f"{'thr_par(l/s)':>14} {'thr_seq(l/s)':>14}")
        for m in metricas:
            print(f"{m['num_workers']:>8} "
                  f"{float(m['tempo_sequencial']):>10.2f} "
                  f"{float(m['tempo_paralelo']):>10.2f} "
                  f"{float(m['speedup']):>9.3f} "
                  f"{float(m['eficiencia']):>11.3f} "
                  f"{float(m['throughput_paralelo']):>14,.0f} "
                  f"{float(m['throughput_sequencial']):>14,.0f}")

    print("\nIDs gerados nesta suite:", ids)
    print("\nPara inspecionar manualmente:")
    print("  psql -h localhost -U enade_user -d enade_db")
    print("  SELECT * FROM v_benchmark_metricas ORDER BY timestamp_inicio DESC;")
    return 0


if __name__ == "__main__":
    freeze_support()  # obrigatório no Windows
    sys.exit(main())
