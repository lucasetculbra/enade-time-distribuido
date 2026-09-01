import { Award, Info } from "lucide-react";

import { BarSpeedup } from "@/components/charts/BarSpeedup";
import { BarTempoExecucao } from "@/components/charts/BarTempoExecucao";
import { BarThroughput } from "@/components/charts/BarThroughput";
import { LineEficiencia } from "@/components/charts/LineEficiencia";
import { QueryBoundary } from "@/components/feedback/QueryBoundary";
import { Card, CardHeader } from "@/components/ui/Card";
import { useComparativo } from "@/hooks/useBenchmark";
import { formatPercent, formatSeconds, formatSpeedup } from "@/lib/format";
import type { ComparativoItem } from "@/types/api";

/**
 * Métrica de Karp–Flatt: estima a fração sequencial `e` do programa a partir
 * do speedup medido S com p processadores — e = (1/S − 1/p) / (1 − 1/p).
 * Serve para separar "fração inerentemente serial" de "overhead de
 * paralelização" sem precisar instrumentar o código.
 */
function fracaoSerialKarpFlatt(speedup: number, p: number): number | null {
  if (p <= 1 || speedup <= 0) return null;
  const e = (1 / speedup - 1 / p) / (1 - 1 / p);
  return Number.isFinite(e) ? e : null;
}

/**
 * Interpretação gerada a partir dos dados realmente carregados no banco.
 * O ponto ótimo de workers varia por máquina/rodada, então nada aqui pode
 * ser fixo no código — senão o texto contradiz os gráficos ao lado.
 */
function Interpretacao({
  paralelos,
  melhor,
}: {
  paralelos: ComparativoItem[];
  melhor: ComparativoItem | null;
}) {
  if (melhor === null || paralelos.length === 0) {
    return (
      <p className="mt-1">
        Nenhuma execução paralela carregada — sem base para comparar contra o
        baseline sequencial.
      </p>
    );
  }

  const ordenados = [...paralelos].sort((a, b) => a.num_workers - b.num_workers);
  const maxWorkers = ordenados[ordenados.length - 1].num_workers;
  const escalouAteOFim = melhor.num_workers === maxWorkers;

  return (
    <>
      <p className="mt-1">
        A melhor configuração desta rodada foi{" "}
        <strong>{melhor.num_workers} workers</strong> (execução #
        {melhor.execucao_id}), com speedup de{" "}
        <strong>{formatSpeedup(melhor.speedup)}</strong> e eficiência de{" "}
        <strong>{formatPercent(melhor.eficiencia)}</strong>.
      </p>

      {escalouAteOFim ? (
        <p className="mt-2">
          O ganho ainda crescia no maior número de workers testado ({maxWorkers}
          ), ou seja, <strong>o ponto de saturação não foi atingido</strong>{" "}
          neste experimento — nesta máquina o pipeline ainda tinha folga de CPU
          e I/O. Testar mais workers provavelmente continuaria rendendo, até a
          fração sequencial (<strong>Lei de Amdahl</strong>) impor o teto.
        </p>
      ) : (
        <p className="mt-2">
          Aumentar para {maxWorkers} workers <strong>piorou</strong> o
          resultado: o overhead de criação de processos, a serialização entre
          eles e a contenção no disco/banco passaram a superar o ganho de CPU. É
          o platô previsto pela <strong>Lei de Amdahl</strong> — a fração
          inerentemente sequencial do pipeline (abertura dos TXT, parsing
          pandas, <code>COPY FROM STDIN</code> no Postgres) limita o speedup
          máximo.
        </p>
      )}

      <p className="mt-2">
        Eficiência abaixo de 100% indica que parte do tempo não é
        paralelizável. Estimativa da{" "}
        <strong>fração sequencial (métrica de Karp–Flatt)</strong> por
        configuração, calculada a partir dos tempos medidos:
      </p>
      <ul className="mt-1 list-disc pl-5 space-y-0.5">
        {ordenados.map((i) => {
          const serial =
            i.speedup !== null
              ? fracaoSerialKarpFlatt(i.speedup, i.num_workers)
              : null;
          return (
            <li key={i.execucao_id}>
              <strong>{i.num_workers} workers</strong> —{" "}
              {formatSeconds(i.tempo_total_seg)}, speedup{" "}
              {formatSpeedup(i.speedup)}, eficiência{" "}
              {formatPercent(i.eficiencia)}
              {serial !== null && (
                <> · fração sequencial estimada {formatPercent(serial)}</>
              )}
            </li>
          );
        })}
      </ul>
    </>
  );
}

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
                    Interpretação desta rodada
                  </h3>
                  <Interpretacao paralelos={paralelos} melhor={melhor} />
                </div>
              </div>
            </Card>
          </>
        );
      }}
    </QueryBoundary>
  );
}
