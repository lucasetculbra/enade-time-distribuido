import { BarMediaUF } from "@/components/charts/BarMediaUF";
import { QueryBoundary } from "@/components/feedback/QueryBoundary";
import { Card, CardHeader } from "@/components/ui/Card";
import { useResumoUF } from "@/hooks/useAnalises";
import { useFiltrosUrl } from "@/hooks/useFiltrosUrl";
import { formatDecimal, formatInt } from "@/lib/format";

export default function EnadePorUF() {
  const { filtros } = useFiltrosUrl();
  const q = useResumoUF(filtros);

  return (
    <QueryBoundary query={q} isEmpty={(d) => d.length === 0}>
      {(rows) => (
        <>
          <Card>
            <CardHeader
              title="Média ENADE por UF"
              description="Ranking horizontal de médias da prova FG por unidade federativa (escala 0–100). Use o filtro de região para focar."
            />
            <BarMediaUF data={rows} />
          </Card>

          <Card>
            <CardHeader title="Detalhamento por UF" />
            <div className="overflow-auto">
              <table className="min-w-full text-sm">
                <thead className="text-academia-700">
                  <tr className="text-left">
                    <th className="px-2 py-2">UF</th>
                    <th className="px-2 py-2">Nome</th>
                    <th className="px-2 py-2 text-right">Região</th>
                    <th className="px-2 py-2 text-right">Registros</th>
                    <th className="px-2 py-2 text-right">Média</th>
                    <th className="px-2 py-2 text-right">Mínima</th>
                    <th className="px-2 py-2 text-right">Máxima</th>
                    <th className="px-2 py-2 text-right">Desvio</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((u) => (
                    <tr key={u.co_uf} className="border-t border-academia-100">
                      <td className="px-2 py-2 font-medium">{u.sigla}</td>
                      <td className="px-2 py-2">{u.nome}</td>
                      <td className="px-2 py-2 text-right">{u.co_regiao}</td>
                      <td className="px-2 py-2 text-right">{formatInt(u.total_registros)}</td>
                      <td className="px-2 py-2 text-right">{formatDecimal(u.media_geral, 2)}</td>
                      <td className="px-2 py-2 text-right">{formatDecimal(u.media_min, 2)}</td>
                      <td className="px-2 py-2 text-right">{formatDecimal(u.media_max, 2)}</td>
                      <td className="px-2 py-2 text-right">{formatDecimal(u.desvio_padrao, 2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </QueryBoundary>
  );
}
