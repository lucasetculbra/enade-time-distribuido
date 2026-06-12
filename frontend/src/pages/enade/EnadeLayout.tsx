import { NavLink, Outlet } from "react-router-dom";

import { PageContainer } from "@/components/layout/PageContainer";
import { FiltrosAnaliseBar } from "@/components/filters/FiltrosAnalise";
import { cn } from "@/lib/cn";

const TABS = [
  { to: "/enade/anual", label: "Por Ano" },
  { to: "/enade/regional", label: "Por Região" },
  { to: "/enade/uf", label: "Por UF" },
  { to: "/enade/ies", label: "Ranking IES" },
  { to: "/enade/registros", label: "Registros" },
];

function tabClass({ isActive }: { isActive: boolean }) {
  return cn(
    "px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
    isActive
      ? "border-academia-700 text-academia-900"
      : "border-transparent text-academia-600 hover:text-academia-900",
  );
}

export default function EnadeLayout() {
  return (
    <PageContainer
      title="Análises ENADE"
      description="Indicadores agregados dos microdados ENADE para cursos de Computação no Norte e Nordeste (2005–2021). Use os filtros abaixo para refinar a análise."
    >
      <FiltrosAnaliseBar />
      <nav className="flex gap-1 border-b border-academia-200">
        {TABS.map((t) => (
          <NavLink key={t.to} to={t.to} className={tabClass}>
            {t.label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </PageContainer>
  );
}
