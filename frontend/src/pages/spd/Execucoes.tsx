import { useState } from "react";

import { ExecucoesTable } from "@/components/tables/ExecucoesTable";
import { QueryBoundary } from "@/components/feedback/QueryBoundary";
import { Card, CardHeader } from "@/components/ui/Card";
import { useExecucoes } from "@/hooks/useBenchmark";

export default function SpdExecucoes() {
  const [apenasValidas, setApenasValidas] = useState(true);
  const q = useExecucoes(apenasValidas);

  return (
    <Card>
      <CardHeader
        title="Execuções de benchmark"
        description="Cada linha representa uma execução completa do pipeline ETL (sequencial ou paralela). Execuções marcadas como inválidas na configuração da API (BENCHMARK_IDS_EXCLUIR) ficam ocultas por padrão."
        action={
          <label className="flex items-center gap-2 text-xs text-academia-700">
            <input
              type="checkbox"
              checked={!apenasValidas}
              onChange={(e) => setApenasValidas(!e.target.checked)}
            />
            Mostrar execuções ocultas
          </label>
        }
      />
      <QueryBoundary query={q} isEmpty={(d) => d.length === 0}>
        {(rows) => <ExecucoesTable data={rows} />}
      </QueryBoundary>
    </Card>
  );
}
