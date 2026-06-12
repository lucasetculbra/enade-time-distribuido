"""
Helpers de banco e metadados de máquina para os scripts de benchmark.

Tudo aqui é executado apenas pelo **processo principal** — workers do
ProcessPoolExecutor não importam nada deste módulo, não abrem conexão e
não tocam em psutil.
"""

from __future__ import annotations

import os
import platform
import sys
from typing import Iterable

import psycopg2


# ---------------------------------------------------------------------------
# Configuração do PostgreSQL (mesmas env vars dos scripts 05/06/07)
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host":     os.environ.get("POSTGRES_HOST", "localhost"),
    "port":     int(os.environ.get("POSTGRES_PORT", "5432")),
    "dbname":   os.environ.get("POSTGRES_DB", "enade_db"),
    "user":     os.environ.get("POSTGRES_USER", "enade_user"),
    "password": os.environ.get("POSTGRES_PASSWORD", "enade_password"),
}


def conectar() -> psycopg2.extensions.connection:
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print(f"\nERRO ao conectar no PostgreSQL: {e}", file=sys.stderr)
        print("Sobe o container com:  docker compose up -d postgres",
              file=sys.stderr)
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# psutil opcional — falha amigável se não instalado
# ---------------------------------------------------------------------------

def carregar_psutil():
    """Retorna o módulo psutil ou aborta com mensagem amigável."""
    try:
        import psutil  # noqa: WPS433
        return psutil
    except ImportError:
        print("\nDependência ausente: psutil", file=sys.stderr)
        print("Instale com:  pip install psutil", file=sys.stderr)
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Metadados da máquina
# ---------------------------------------------------------------------------

def coletar_metadados_maquina() -> dict:
    """CPU, modelo, total de núcleos. psutil é obrigatório aqui."""
    psutil = carregar_psutil()
    cpu_count = os.cpu_count() or 1
    cpu_modelo = (platform.processor() or "").strip() or "desconhecido"
    memoria_total_mb = round(psutil.virtual_memory().total / (1024 * 1024), 2)
    return {
        "cpu_count": cpu_count,
        "cpu_modelo": cpu_modelo,
        "memoria_total_mb": memoria_total_mb,
    }


def memoria_atual_mb() -> float:
    psutil = carregar_psutil()
    return round(psutil.Process().memory_info().rss / (1024 * 1024), 2)


# ---------------------------------------------------------------------------
# Persistência no banco — apenas o main chama isto
# ---------------------------------------------------------------------------

SQL_INSERT_EXECUCAO = """
INSERT INTO benchmark_execucao
    (modo, num_workers, tempo_total_seg, linhas_processadas, throughput_lps,
     cpu_count_maquina, cpu_modelo, memoria_pico_mb, observacoes)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING id, timestamp_inicio;
"""

SQL_INSERT_ETAPA = """
INSERT INTO benchmark_etapa
    (execucao_id, ano, tempo_seg, linhas_arq3,
     worker_pid, timestamp_inicio, timestamp_fim)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""


def gravar_execucao(conn, *, modo: str, num_workers: int,
                    tempo_total_seg: float, linhas_processadas: int,
                    throughput_lps: float, cpu_count: int, cpu_modelo: str,
                    memoria_pico_mb: float, observacoes: str,
                    etapas: Iterable[dict]) -> tuple[int, str]:
    """
    Grava 1 execução + N etapas em uma única transação.
    Retorna (execucao_id, timestamp_inicio_iso).
    """
    with conn:
        with conn.cursor() as cur:
            cur.execute(SQL_INSERT_EXECUCAO, (
                modo, num_workers, tempo_total_seg, linhas_processadas,
                throughput_lps, cpu_count, cpu_modelo, memoria_pico_mb,
                observacoes,
            ))
            execucao_id, ts_inicio = cur.fetchone()

            for et in etapas:
                cur.execute(SQL_INSERT_ETAPA, (
                    execucao_id,
                    et["ano"],
                    et["tempo_seg"],
                    et["linhas_arq3"],
                    et["worker_pid"],
                    et["timestamp_inicio"],
                    et["timestamp_fim"],
                ))
    return execucao_id, str(ts_inicio)


def consultar_metricas(conn, execucao_ids: list[int]) -> list[dict]:
    """Lê v_benchmark_metricas filtrando pelos IDs informados."""
    if not execucao_ids:
        return []
    placeholders = ",".join(["%s"] * len(execucao_ids))
    sql = f"""
        SELECT execucao_id, num_workers,
               tempo_sequencial, tempo_paralelo,
               speedup, eficiencia,
               throughput_sequencial, throughput_paralelo,
               cpu_count_maquina
        FROM v_benchmark_metricas
        WHERE execucao_id IN ({placeholders})
        ORDER BY num_workers, execucao_id;
    """
    with conn.cursor() as cur:
        cur.execute(sql, execucao_ids)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
