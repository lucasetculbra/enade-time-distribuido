import { Award, Info } from "lucide-react";

import { BarSpeedup } from "@/components/charts/BarSpeedup";
import { BarTempoExecucao } from "@/components/charts/BarTempoExecucao";
import { BarThroughput } from "@/components/charts/BarThroughput";
import { LineEficiencia } from "@/components/charts/LineEficiencia";
import { QueryBoundary } from "@/components/feedback/QueryBoundary";
import { Card, CardHeader } from "@/components/ui/Card";
import { useComparativo } from "@/hooks/useBenchmark";
import { formatPercent, formatSeconds, formatSpeedup } from "@/lib/format";

export default function SpdComparativo() {
  const q = useComparativo(true);

  return (
    <QueryBoundary query={q} isEmpty={(d) => d.itens.length === 0}>
      {(data) => {
        const paralelos = data.itens.filter((i) => i.modo === "paralelo");
        const melhor = paralelos.reduce<typeof paralelos[number] | null>(
          (best, cur) =>
            cur.speedup !== null &&
            (best === null || (cur.speedup ?? 0) > (best.speedup ?? 0))
              ? cur
              : best,
          null,
        );

        return (
          <>
            {melhor && (
              <Card className="border-emerald-200 bg-emerald-50">
                <div className="flex items-start gap-3">
                  <Award className="h-6 w-6 text-emerald-600 shrink-0" aria-hidden />
                  <div>
                    <h3 className="text-base font-semibold text-emerald-900">
                      Melhor configuração: {melhor.num_workers} workers (#{melhor.execucao_id})
                    </h3>
                    <p className="text-sm text-emerald-800 mt-1 max-w-3xl">
                      Speedup de <strong>{formatSpeedup(melhor.speedup)}</strong> em
                      relação ao baseline sequencial ({formatSeconds(data.tempo_baseline_seg)}),
                      com eficiência de <strong>{formatPercent(melhor.eficiencia)}</strong>.
                    </p>
                  </div>
                </div>
              </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader
                  title="Tempo total de execução"
                  description="Sequencial vs. paralelo (menor é melhor)."
                />
                <BarTempoExecucao data={data.itens} />
              </Card>

              <Card>
                <CardHeader
                  title="Speedup"
                  description="S(p) = T(1) / T(p). Linha vermelha marca o limiar sem ganho (1×)."
                />
                <BarSpeedup data={data.itens} />
              </Card>

              <Card>
                <CardHeader
                  title="Eficiência"
                  description="E(p) = S(p) / p. Linha verde marca o ideal (100%)."
                />
                <LineEficiencia data={data.itens} />
              </Card>

              <Card>
                <CardHeader
                  title="Throughput"
                  description="Linhas processadas por segundo (maior é melhor)."
                />
                <BarThroughput data={data.itens} />
              </Card>
            </div>

            <Card>
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-academia-600 shrink-0 mt-0.5" aria-hidden />
                <div className="text-sm text-academia-800">
                  <h3 className="font-semibold text-academia-900">
                    Por que 2 workers superou 4 workers?
                  </h3>
                  <p className="mt-1">
                    O ganho marginal de paralelismo é limitado pela{" "}
                    <strong>Lei de Amdahl</strong>: parte do pipeline (leitura
                    de arquivos texto, parsing CSV, escrita no Postgres) é
                    inerentemente sequencial e/ou limitada por I/O.
                  </p>
                  <p className="mt-2">
                    Com 4 workers, o overhead de criação de processos,
                    serialização entre eles e contenção no disco/banco supera
                    o ganho de CPU. O resultado é uma eficiência baixa
                    (~28%) — cada worker fica ocioso boa parte do tempo. Com 2
                    workers, há melhor sobreposição entre I/O e processamento,
                    resultando em eficiência ~61% e o melhor tempo absoluto
                    observado no experimento.
                  </p>
                </div>
              </div>
            </Card>
          </>
        );
      }}
    </QueryBoundary>
  );
}
