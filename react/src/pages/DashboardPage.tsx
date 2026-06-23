import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getDashboardStats } from "../api/countries";

const DOMAINS = [
  { key: "countries", label: "Countries", color: "bg-blue-500", link: "/countries" },
  { key: "health", label: "Health", color: "bg-red-500", link: "/domain/health" },
  { key: "ghg", label: "GHG Emissions", color: "bg-gray-600", link: "/domain/ghg" },
  { key: "energy", label: "Energy", color: "bg-yellow-500", link: "/domain/energy" },
  { key: "freshwater", label: "Freshwater", color: "bg-cyan-500", link: "/domain/freshwater" },
  { key: "sustainability", label: "Sustainability", color: "bg-green-500", link: "/domain/sustainability" },
];

function formatNumber(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toString();
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardStats,
  });

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">Loading dashboard...</div>;
  }

  if (!data) return null;

  const domainStats: Record<string, { indicators: number; records: number; min_year: number | null; max_year: number | null }> = {};
  for (const d of DOMAINS) {
    if (d.key === "countries") continue;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const ds = (data as any)[d.key];
    domainStats[d.key] = ds || { indicators: 0, records: 0, min_year: null, max_year: null };
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl shadow text-center">
          <div className="text-3xl font-bold text-blue-600">{data.countries}</div>
          <div className="text-sm text-gray-500">Countries</div>
        </div>
        {DOMAINS.filter((d) => d.key !== "countries").map((d) => (
          <Link key={d.key} to={d.link} className="bg-white p-4 rounded-xl shadow text-center hover:shadow-md transition-shadow">
            <div className="text-3xl font-bold">{formatNumber(domainStats[d.key]?.records ?? 0)}</div>
            <div className="text-sm text-gray-500">{d.label}</div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {DOMAINS.filter((d) => d.key !== "countries").map((d) => {
          const ds = domainStats[d.key];
          return (
            <Link key={d.key} to={d.link} className="bg-white p-5 rounded-xl shadow hover:shadow-md transition-shadow">
              <div className={`inline-block w-3 h-3 rounded-full ${d.color} mr-2`}></div>
              <span className="font-semibold">{d.label}</span>
              <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-gray-600">
                <div>Indicators: <strong>{ds.indicators}</strong></div>
                <div>Records: <strong>{formatNumber(ds.records)}</strong></div>
                <div>From: <strong>{ds.min_year ?? "-"}</strong></div>
                <div>To: <strong>{ds.max_year ?? "-"}</strong></div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
