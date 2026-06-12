import { BookOpen, Cpu, Database, FileText, GitBranch } from "lucide-react";

import { Card, CardHeader } from "@/components/ui/Card";
import { PageContainer } from "@/components/layout/PageContainer";

export default function Sobre() {
  return (
    <PageContainer
      title="Sobre o projeto"
      description="ENADE-Time Distribuído — Sistema Paralelo de Análise Longitudinal dos Microdados do ENADE. Projeto acadêmico de Sistemas Paralelos e Distribuídos."
    >
      <Card>
        <CardHeader
          title="Escopo"
          description="Recorte definido para tornar o experimento tratável"
        />
        <ul className="text-sm text-academia-700 list-disc pl-5 space-y-1">
          <li>
            <strong>Cursos:</strong> Ciência da Computação e Sistemas de
            Informação (CO_GRUPO ∈ {"{40, 4004}"}).
          </li>
          <li>
            <strong>Regiões:</strong> Norte e Nordeste (CO_REGIAO_CURSO ∈ {"{1, 2}"}).
          </li>
          <li>
            <strong>Edições do ENADE:</strong> 2005, 2008, 2011, 2014, 2017,
            2021 (ciclos trienais; 2021 é reaplicação pós-pandemia).
          </li>
          <li>
            <strong>Total processado:</strong> 24.967 registros consolidados em
            <em> fato_enade</em>.
          </li>
        </ul>
      </Card>

      <Card>
        <CardHeader
          title="Arquitetura"
          description="Camadas independentes, integradas via PostgreSQL"
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div className="flex items-start gap-2">
            <Database className="h-4 w-4 mt-0.5 text-academia-600" aria-hidden />
            <div>
              <div className="font-semibold">Banco de dados</div>
              <div className="text-academia-600">
                PostgreSQL 16 (Docker), schema dimensional (fato +
                dimensões), views agregadas.
              </div>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <Cpu className="h-4 w-4 mt-0.5 text-academia-600" aria-hidden />
            <div>
              <div className="font-semibold">ETL paralelo</div>
              <div className="text-academia-600">
                Python (pandas + multiprocessing). Pool de workers
                processando ano-a-ano.
              </div>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <FileText className="h-4 w-4 mt-0.5 text-academia-600" aria-hidden />
            <div>
              <div className="font-semibold">API read-only</div>
              <div className="text-academia-600">
                FastAPI + psycopg2, ThreadedConnectionPool, sem ORM, CORS
                restrito a localhost.
              </div>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <BookOpen className="h-4 w-4 mt-0.5 text-academia-600" aria-hidden />
            <div>
              <div className="font-semibold">Dashboard</div>
              <div className="text-academia-600">
                React + Vite + TanStack Query + Recharts. SPA pura,
                consumindo a API HTTP.
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader
          title="Metodologia do benchmark (Fase 2)"
          description="Métricas-padrão de paralelismo"
        />
        <p className="text-sm text-academia-700">
          O experimento mede tempo total, throughput (linhas/segundo) e CPU
          para diferentes números de workers, comparando contra o baseline
          sequencial. As métricas calculadas são:
        </p>
        <dl className="text-sm text-academia-700 mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <dt className="font-semibold">Speedup</dt>
            <dd className="text-academia-600">
              S(p) = T(1) / T(p) — quantas vezes mais rápido que o sequencial.
            </dd>
          </div>
          <div>
            <dt className="font-semibold">Eficiência</dt>
            <dd className="text-academia-600">
              E(p) = S(p) / p — fração do speedup ideal alcançada.
            </dd>
          </div>
          <div>
            <dt className="font-semibold">Throughput</dt>
            <dd className="text-academia-600">
              Linhas processadas por segundo de processamento.
            </dd>
          </div>
          <div>
            <dt className="font-semibold">Cobertura de I/O</dt>
            <dd className="text-academia-600">
              Execuções realizadas fora do OneDrive para evitar contenção de
              sincronização.
            </dd>
          </div>
        </dl>
      </Card>

      <Card>
        <CardHeader
          title="Fases do projeto"
          description="Estado atual e roadmap"
        />
        <ul className="text-sm text-academia-700 list-decimal pl-5 space-y-1">
          <li>
            <strong>Fase 1 (concluída):</strong> ETL inicial e schema PostgreSQL.
          </li>
          <li>
            <strong>Fase 2 (concluída):</strong> Benchmark sequencial vs. paralelo
            (2 e 4 workers).
          </li>
          <li>
            <strong>Fase 3 (concluída):</strong> API FastAPI read-only para
            consumo pelo dashboard.
          </li>
          <li>
            <strong>Fase 4 (atual):</strong> Dashboard React/Vite.
          </li>
          <li>
            <strong>Fase 5 (futura):</strong> Empacotamento Docker (Dockerfile
            da API e do frontend, serviços no docker-compose).
          </li>
        </ul>
        <div className="mt-3 flex items-center gap-2 text-xs text-academia-500">
          <GitBranch className="h-3.5 w-3.5" aria-hidden />
          Projeto acadêmico — sem fins comerciais.
        </div>
      </Card>
    </PageContainer>
  );
}
