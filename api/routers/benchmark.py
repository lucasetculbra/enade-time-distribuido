from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extensions import cursor as PgCursor

from api.dependencies import get_db_cursor
from api.repositories import benchmark_repo
from api.schemas.benchmark import (
    BenchmarkComparativo,
    BenchmarkEtapa,
    BenchmarkExecucao,
    BenchmarkMetrica,
)
from api.settings import Settings, get_settings

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/execucoes", response_model=list[BenchmarkExecucao])
def execucoes(
    apenas_validas: bool = Query(True),
    cursor: PgCursor = Depends(get_db_cursor),
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    return benchmark_repo.listar_execucoes(
        cursor,
        apenas_validas=apenas_validas,
        ids_excluir=settings.benchmark_ids_excluir,
    )


@router.get("/execucoes/{execucao_id}", response_model=BenchmarkExecucao)
def execucao_por_id(
    execucao_id: int,
    apenas_validas: bool = Query(True),
    cursor: PgCursor = Depends(get_db_cursor),
    settings: Settings = Depends(get_settings),
) -> dict:
    row = benchmark_repo.get_execucao(
        cursor,
        execucao_id=execucao_id,
        apenas_validas=apenas_validas,
        ids_excluir=settings.benchmark_ids_excluir,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return row


@router.get("/etapas/{execucao_id}", response_model=list[BenchmarkEtapa])
def etapas(
    execucao_id: int,
    apenas_validas: bool = Query(True),
    cursor: PgCursor = Depends(get_db_cursor),
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    rows = benchmark_repo.listar_etapas(
        cursor,
        execucao_id=execucao_id,
        apenas_validas=apenas_validas,
        ids_excluir=settings.benchmark_ids_excluir,
    )
    if rows is None:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return rows


@router.get("/metricas", response_model=list[BenchmarkMetrica])
def metricas(
    apenas_validas: bool = Query(True),
    cursor: PgCursor = Depends(get_db_cursor),
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    return benchmark_repo.listar_metricas(
        cursor,
        apenas_validas=apenas_validas,
        ids_excluir=settings.benchmark_ids_excluir,
    )


@router.get("/comparativo", response_model=BenchmarkComparativo)
def comparativo(
    apenas_validas: bool = Query(True),
    cursor: PgCursor = Depends(get_db_cursor),
    settings: Settings = Depends(get_settings),
) -> dict:
    return benchmark_repo.comparativo(
        cursor,
        apenas_validas=apenas_validas,
        ids_excluir=settings.benchmark_ids_excluir,
    )
