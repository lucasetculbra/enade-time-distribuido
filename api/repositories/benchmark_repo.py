from psycopg2.extensions import cursor as PgCursor


def _filtro_validas(
    apenas_validas: bool,
    ids_excluir: list[int],
    coluna: str = "id",
) -> tuple[str, dict]:
    """Filtro seguro para excluir ids inválidos.

    Usa `coluna <> ALL(%(ids_excluir)s)` em vez de NOT IN, que é a forma
    nativa de psycopg2 para passar listas como array Postgres com
    placeholders parametrizados.
    """
    if apenas_validas and ids_excluir:
        return (f"AND {coluna} <> ALL(%(ids_excluir)s)", {"ids_excluir": ids_excluir})
    return ("", {})


def listar_execucoes(
    cursor: PgCursor,
    apenas_validas: bool,
    ids_excluir: list[int],
) -> list[dict]:
    where, params = _filtro_validas(apenas_validas, ids_excluir, coluna="id")
    cursor.execute(
        f"""
        SELECT
            id, timestamp_inicio, modo, num_workers,
            tempo_total_seg::float AS tempo_total_seg,
            linhas_processadas, throughput_lps::float AS throughput_lps,
            cpu_count_maquina, cpu_modelo,
            memoria_pico_mb::float AS memoria_pico_mb,
            observacoes
        FROM benchmark_execucao
        WHERE 1=1 {where}
        ORDER BY id
        """,
        params,
    )
    return list(cursor.fetchall())


def get_execucao(
    cursor: PgCursor,
    execucao_id: int,
    apenas_validas: bool,
    ids_excluir: list[int],
) -> dict | None:
    if apenas_validas and execucao_id in ids_excluir:
        return None
    cursor.execute(
        """
        SELECT
            id, timestamp_inicio, modo, num_workers,
            tempo_total_seg::float AS tempo_total_seg,
            linhas_processadas, throughput_lps::float AS throughput_lps,
            cpu_count_maquina, cpu_modelo,
            memoria_pico_mb::float AS memoria_pico_mb,
            observacoes
        FROM benchmark_execucao
        WHERE id = %(id)s
        """,
        {"id": execucao_id},
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def listar_etapas(
    cursor: PgCursor,
    execucao_id: int,
    apenas_validas: bool,
    ids_excluir: list[int],
) -> list[dict] | None:
    if apenas_validas and execucao_id in ids_excluir:
        return None
    cursor.execute(
        "SELECT 1 FROM benchmark_execucao WHERE id = %(id)s",
        {"id": execucao_id},
    )
    if cursor.fetchone() is None:
        return None

    cursor.execute(
        """
        SELECT
            id, execucao_id, ano,
            tempo_seg::float AS tempo_seg,
            linhas_arq3, worker_pid,
            timestamp_inicio, timestamp_fim
        FROM benchmark_etapa
        WHERE execucao_id = %(execucao_id)s
        ORDER BY ano
        """,
        {"execucao_id": execucao_id},
    )
    return list(cursor.fetchall())


def listar_metricas(
    cursor: PgCursor,
    apenas_validas: bool,
    ids_excluir: list[int],
) -> list[dict]:
    where, params = _filtro_validas(apenas_validas, ids_excluir, coluna="execucao_id")
    cursor.execute(
        f"""
        SELECT
            execucao_id, timestamp_inicio, num_workers,
            tempo_sequencial::float AS tempo_sequencial,
            tempo_paralelo::float AS tempo_paralelo,
            speedup::float AS speedup,
            eficiencia::float AS eficiencia,
            throughput_sequencial::float AS throughput_sequencial,
            throughput_paralelo::float AS throughput_paralelo,
            cpu_count_maquina
        FROM v_benchmark_metricas
        WHERE 1=1 {where}
        ORDER BY execucao_id
        """,
        params,
    )
    return list(cursor.fetchall())


def comparativo(
    cursor: PgCursor,
    apenas_validas: bool,
    ids_excluir: list[int],
) -> dict:
    """Retorna baseline sequencial mais recente + execuções paralelas com speedup/eficiência."""
    where, params = _filtro_validas(apenas_validas, ids_excluir, coluna="id")

    cursor.execute(
        f"""
        SELECT id, tempo_total_seg::float AS tempo_total_seg,
               throughput_lps::float AS throughput_lps,
               cpu_count_maquina
        FROM benchmark_execucao
        WHERE modo = 'sequencial' {where}
        ORDER BY timestamp_inicio DESC
        LIMIT 1
        """,
        params,
    )
    baseline = cursor.fetchone()

    cursor.execute(
        f"""
        SELECT
            id, modo, num_workers,
            tempo_total_seg::float AS tempo_total_seg,
            throughput_lps::float AS throughput_lps,
            cpu_count_maquina
        FROM benchmark_execucao
        WHERE 1=1 {where}
        ORDER BY modo, num_workers, id
        """,
        params,
    )
    execucoes = list(cursor.fetchall())

    itens: list[dict] = []
    t_base = float(baseline["tempo_total_seg"]) if baseline else None

    for ex in execucoes:
        speedup = None
        eficiencia = None
        if t_base and float(ex["tempo_total_seg"]) > 0:
            speedup = t_base / float(ex["tempo_total_seg"])
            n_workers = max(int(ex["num_workers"]), 1)
            eficiencia = speedup / n_workers
        itens.append(
            {
                "execucao_id": int(ex["id"]),
                "modo": ex["modo"],
                "num_workers": int(ex["num_workers"]),
                "tempo_total_seg": float(ex["tempo_total_seg"]),
                "throughput_lps": float(ex["throughput_lps"]),
                "speedup": speedup,
                "eficiencia": eficiencia,
            }
        )

    return {
        "baseline_sequencial_id": int(baseline["id"]) if baseline else None,
        "tempo_baseline_seg": t_base,
        "throughput_baseline_lps": float(baseline["throughput_lps"]) if baseline else None,
        "cpu_count_maquina": int(baseline["cpu_count_maquina"]) if baseline else None,
        "itens": itens,
    }
