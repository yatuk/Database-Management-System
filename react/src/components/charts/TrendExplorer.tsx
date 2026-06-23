import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import LineChart from "./LineChart";
import { listDomain } from "../../api/domain";
import type { Domain } from "../../types";

interface Props {
  domain: Domain;
}

export default function TrendExplorer({ domain }: Props) {
  const [indicator, setIndicator] = useState("");
  const [viewMode, setViewMode] = useState<"global" | "country">("global");

  const { data, isLoading } = useQuery({
    queryKey: [domain, "trend", indicator],
    queryFn: () =>
      listDomain(domain, { page: 1, sort_by: "year", order: "asc" }),
    enabled: !!domain,
  });

  const indicators = useMemo(() => {
    if (!data?.data) return [];
    const names = new Set<string>();
    data.data.forEach((r) => names.add(r.indicator_name as string));
    return Array.from(names);
  }, [data]);

  const chartData = useMemo(() => {
    if (!data?.data) return { labels: [], datasets: [] };
    const filtered = indicator
      ? data.data.filter((r) => r.indicator_name === indicator)
      : data.data;

    const byYear: Record<number, { sum: number; count: number }> = {};
    filtered.forEach((r) => {
      const yr = r.year as number;
      if (!byYear[yr]) byYear[yr] = { sum: 0, count: 0 };
      byYear[yr].sum += Number(r.indicator_value || 0);
      byYear[yr].count++;
    });

    const years = Object.keys(byYear)
      .map(Number)
      .sort((a, b) => a - b);

    return {
      labels: years.map(String),
      datasets: [
        {
          label: viewMode === "global" ? "Global Average" : indicator || "Value",
          data: years.map((y) => {
            const s = byYear[y];
            return viewMode === "global"
              ? s.sum / s.count
              : s.sum;
          }),
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.1)",
          fill: true,
        },
      ],
    };
  }, [data, indicator, viewMode]);

  return (
    <div className="bg-white rounded-xl shadow p-6 mb-8">
      <h3 className="text-lg font-semibold mb-4">Trend Explorer</h3>
      <div className="flex gap-3 mb-4">
        <select
          value={indicator}
          onChange={(e) => setIndicator(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm"
        >
          <option value="">All indicators</option>
          {indicators.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
        <select
          value={viewMode}
          onChange={(e) => setViewMode(e.target.value as "global" | "country")}
          className="border rounded px-3 py-1.5 text-sm"
        >
          <option value="global">Global Average</option>
          <option value="country">Selected Indicator</option>
        </select>
      </div>
      {isLoading ? (
        <div className="text-center py-8 text-gray-400">Loading chart...</div>
      ) : (
        <LineChart
          labels={chartData.labels}
          datasets={chartData.datasets}
          title={`${viewMode === "global" ? "Global Average" : indicator} over Time`}
        />
      )}
    </div>
  );
}
