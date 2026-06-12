import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { CHART_COLORS } from "@/lib/constants";
import { formatPercent } from "@/lib/format";
import type { ComparativoItem } from "@/types/api";

export function LineEficiencia({ data }: { data: ComparativoItem[] }) {
  const chart = data
    .filter((d) => d.modo === "paralelo" && d.eficiencia !== null)
    .sort((a, b) => a.num_workers - b.num_workers)
    .map((d) => ({
      workers: d.num_workers,
      eficiencia: d.eficiencia ?? 0,
    }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chart} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey="workers"
          stroke="#475569"
          fontSize={12}
          label={{
            value: "Número de workers",
            position: "insideBottom",
            offset: -2,
            fontSize: 11,
            fill: "#64748b",
          }}
        />
        <YAxis
          stroke="#475569"
          fontSize={12}
          domain={[0, 1.1]}
          tickFormatter={(v) => formatPercent(v)}
        />
        <Tooltip
          formatter={(v: number) => formatPercent(v)}
          contentStyle={{ borderRadius: 8 }}
        />
        <ReferenceLine
          y={1}
          stroke={CHART_COLORS.ideal}
          strokeDasharray="4 4"
          label={{
            value: "ideal (100%)",
            position: "right",
            fontSize: 10,
            fill: CHART_COLORS.ideal,
          }}
        />
        <Line
          type="monotone"
          dataKey="eficiencia"
          name="Eficiência"
          stroke={CHART_COLORS.paralelo}
          strokeWidth={2.5}
          dot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
