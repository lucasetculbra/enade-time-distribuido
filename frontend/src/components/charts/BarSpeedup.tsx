import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS } from "@/lib/constants";
import { formatSpeedup } from "@/lib/format";
import type { ComparativoItem } from "@/types/api";

export function BarSpeedup({ data }: { data: ComparativoItem[] }) {
  const paralelos = data.filter(
    (d) => d.modo === "paralelo" && d.speedup !== null,
  );
  const chart = paralelos.map((d) => ({
    label: `${d.num_workers} workers (#${d.execucao_id})`,
    speedup: d.speedup ?? 0,
    workers: d.num_workers,
  }));

  const maxIdeal = Math.max(...chart.map((c) => c.workers), 1);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chart} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="label" stroke="#475569" fontSize={12} />
        <YAxis
          stroke="#475569"
          fontSize={12}
          domain={[0, Math.max(maxIdeal + 0.5, 2)]}
        />
        <Tooltip
          formatter={(v: number) => formatSpeedup(v)}
          contentStyle={{ borderRadius: 8 }}
        />
        <ReferenceLine
          y={1}
          stroke={CHART_COLORS.alert}
          strokeDasharray="4 4"
          label={{ value: "sem ganho (1×)", position: "right", fontSize: 10, fill: CHART_COLORS.alert }}
        />
        <Bar dataKey="speedup" name="Speedup">
          {chart.map((d, i) => (
            <Cell key={i} fill={CHART_COLORS.paralelo} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
