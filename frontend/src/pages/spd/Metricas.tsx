import { useState } from "react";

import { MetricasTable } from "@/components/tables/MetricasTable";
import { QueryBoundary } from "@/components/feedback/QueryBoundary";
import { Card, CardHeader } from "@/components/ui/Card";
import { useMetricas } from "@/hooks/useBenchmark";

export default function SpdMetricas() {
  const [apenasValidas, setApenasValidas] = useState(true);
  const q = useMetricas(apenasValidas);

  return (
    <Card>
      <CardHeader
        title="Métricas detalhadas (view v_benchmark_metricas)"
        description="Dados crus de speedup, eficiência e throughput por execução paralela, comparados com o baseline sequencial."
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
        {(rows) => <MetricasTable data={rows} />}
      </QueryBoundary>
    </Card>
  );
}
