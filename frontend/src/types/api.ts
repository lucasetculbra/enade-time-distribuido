export interface Regiao {
  co_regiao: number;
  nome: string;
}

export interface UF {
  co_uf: number;
  sigla: string;
  nome: string;
  co_regiao: number;
}

export interface Ano {
  co_ano: number;
  edicao: string | null;
}

export interface Grupo {
  co_grupo: number;
  nome: string;
}

export interface Modalidade {
  co_modalidade: number;
  nome: string;
}

export interface CategoriaAdm {
  co_categad: number;
  nome: string;
}

export interface OrganizacaoAcademica {
  co_orgacad: number;
  nome: string;
}

export interface FiltrosAnalise {
  nu_ano?: number;
  co_regiao?: number;
  co_uf?: number;
  co_ies?: number;
  co_grupo?: number;
  co_modalidade?: number;
  co_categad?: number;
  co_orgacad?: number;
}

export interface ResumoAnual {
  nu_ano: number;
  total_registros: number;
  media_geral: number | null;
  media_min: number | null;
  media_max: number | null;
  desvio_padrao: number | null;
}

export interface ResumoRegiao {
  co_regiao: number;
  nome: string;
  total_registros: number;
  media_geral: number | null;
  media_min: number | null;
  media_max: number | null;
  desvio_padrao: number | null;
}

export interface ResumoUF {
  co_uf: number;
  sigla: string;
  nome: string;
  co_regiao: number;
  total_registros: number;
  media_geral: number | null;
  media_min: number | null;
  media_max: number | null;
  desvio_padrao: number | null;
}

export interface ResumoIES {
  co_ies: number;
  co_categad: number;
  co_orgacad: number;
  co_uf_curso: number;
  total_registros: number;
  media_geral: number | null;
}

export interface Registro {
  id: number;
  nu_ano: number;
  co_curso: number;
  co_ies: number;
  co_categad: number;
  co_orgacad: number;
  co_grupo: number;
  co_modalidade: number | null;
  co_munic_curso: number | null;
  co_uf_curso: number;
  co_regiao_curso: number;
  media_nt_fg: number | null;
}

export interface PaginatedResponse<T> {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  items: T[];
}

export interface BenchmarkExecucao {
  id: number;
  timestamp_inicio: string;
  modo: "sequencial" | "paralelo";
  num_workers: number;
  tempo_total_seg: number;
  linhas_processadas: number;
  throughput_lps: number;
  cpu_count_maquina: number;
  cpu_modelo: string | null;
  memoria_pico_mb: number | null;
  observacoes: string | null;
}

export interface BenchmarkEtapa {
  id: number;
  execucao_id: number;
  ano: number;
  tempo_seg: number;
  linhas_arq3: number;
  worker_pid: number | null;
  timestamp_inicio: string;
  timestamp_fim: string;
}

export interface BenchmarkMetrica {
  execucao_id: number;
  timestamp_inicio: string;
  num_workers: number;
  tempo_sequencial: number | null;
  tempo_paralelo: number | null;
  speedup: number | null;
  eficiencia: number | null;
  throughput_sequencial: number | null;
  throughput_paralelo: number | null;
  cpu_count_maquina: number;
}

export interface ComparativoItem {
  execucao_id: number;
  modo: "sequencial" | "paralelo";
  num_workers: number;
  tempo_total_seg: number;
  throughput_lps: number;
  speedup: number | null;
  eficiencia: number | null;
}

export interface BenchmarkComparativo {
  baseline_sequencial_id: number | null;
  tempo_baseline_seg: number | null;
  throughput_baseline_lps: number | null;
  cpu_count_maquina: number | null;
  itens: ComparativoItem[];
}

export interface HealthStatus {
  status: string;
  database: string;
  version: string;
}
