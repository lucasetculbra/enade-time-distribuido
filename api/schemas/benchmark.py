from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BenchmarkExecucao(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp_inicio: datetime
    modo: str
    num_workers: int
    tempo_total_seg: float
    linhas_processadas: int
    throughput_lps: float
    cpu_count_maquina: int
    cpu_modelo: str | None = None
    memoria_pico_mb: float | None = None
    observacoes: str | None = None


class BenchmarkEtapa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    execucao_id: int
    ano: int
    tempo_seg: float
    linhas_arq3: int
    worker_pid: int | None = None
    timestamp_inicio: datetime
    timestamp_fim: datetime


class BenchmarkMetrica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execucao_id: int
    timestamp_inicio: datetime
    num_workers: int
    tempo_sequencial: float | None = None
    tempo_paralelo: float | None = None
    speedup: float | None = None
    eficiencia: float | None = None
    throughput_sequencial: float | None = None
    throughput_paralelo: float | None = None
    cpu_count_maquina: int


class ComparativoItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execucao_id: int
    modo: str
    num_workers: int
    tempo_total_seg: float
    throughput_lps: float
    speedup: float | None = None
    eficiencia: float | None = None


class BenchmarkComparativo(BaseModel):
    baseline_sequencial_id: int | None = None
    tempo_baseline_seg: float | None = None
    throughput_baseline_lps: float | None = None
    cpu_count_maquina: int | None = None
    itens: list[ComparativoItem]
