import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import BarChart from "./BarChart";
import { listDomain } from "../../api/domain";
import type { Domain } from "../../types";

interface Props {
  domain: Domain;
}

const COLORS = [
  "#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6",
  "#06b6d4", "#f97316", "#6366f1", "#14b8a6", "#d946ef",
];

export default function SnapshotWidget({ domain }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: [domain, "snapshot"],
    queryFn: () =>
      listDomain(domain, { page: 1, sort_by: "value", order: "desc" }),
  });

  const { top10, byRegion } = useMemo(() => {
    if (!data?.data) return { top10: [], byRegion: [] };
    const sorted = [...data.data].sort(
      (a, b) => Number(b.indicator_value || 0) - Number(a.indicator_value || 0)
    );
    const top = sorted.slice(0, 10);

    const regionMap: Record<string, { sum: number; count: number }> = {};
    sorted.forEach((r) => {
      const reg = (r.region as string) || "Unknown";
      if (!regionMap[reg]) regionMap[reg] = { sum: 0, count: 0 };
      regionMap[reg].sum += Number(r.indicator_value || 0);
      regionMap[reg].count++;
    });

    const regions = Object.entries(regionMap)
      .map(([name, v]) => ({ name, avg: v.sum / v.count }))
      .sort((a, b) => b.avg - a.avg);

    return { top10: top, byRegion: regions };
  }, [data]);

  if (isLoading) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      {/* Top 10 */}
      <div className="bg-white rounded-xl shadow p-6">
        <h4 className="font-semibold mb-3">Top 10 Countries</h4>
        <div className="space-y-1">
          {top10.map((r, i) => (
            <div key={i} className="flex justify-between text-sm py-1 border-b">
              <span>
                <span className="text-gray-400 mr-2">{i + 1}.</span>
                {r.country_name as string}
              </span>
              <span className="font-mono">{Number(r.indicator_value).toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Region Breakdown */}
      <div className="bg-white rounded-xl shadow p-6">
        <h4 className="font-semibold mb-3">By Region</h4>
        <BarChart
          labels={byRegion.map((r) => r.name)}
          datasets={[
            {
              label: "Average",
              data: byRegion.map((r) => r.avg),
              backgroundColor: COLORS.slice(0, byRegion.length) as unknown as string,
            },
          ]}
          horizontal
        />
      </div>
    </div>
  );
}
