import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS } from "@/lib/constants";
import { formatThroughput } from "@/lib/format";
import type { ComparativoItem } from "@/types/api";

export function BarThroughput({ data }: { data: ComparativoItem[] }) {
  const chart = data.map((d) => ({
    label:
      d.modo === "sequencial"
        ? `Sequencial #${d.execucao_id}`
        : `Paralelo ${d.num_workers}w #${d.execucao_id}`,
    throughput_lps: d.throughput_lps,
    modo: d.modo,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chart} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="label" stroke="#475569" fontSize={12} />
        <YAxis stroke="#475569" fontSize={12} />
        <Tooltip
          formatter={(v: number) => formatThroughput(v)}
          contentStyle={{ borderRadius: 8 }}
        />
        <Bar dataKey="throughput_lps" name="Throughput">
          {chart.map((d, i) => (
            <Cell
              key={i}
              fill={d.modo === "sequencial" ? CHART_COLORS.seq : CHART_COLORS.paralelo}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
