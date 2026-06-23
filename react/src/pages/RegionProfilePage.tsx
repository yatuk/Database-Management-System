import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getRegionProfile } from "../api/countries";

const DOMAINS = ["health", "energy", "freshwater", "ghg", "sustainability"] as const;

export default function RegionProfilePage() {
  const { name } = useParams<{ name: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["region", name],
    queryFn: () => getRegionProfile(name!),
    enabled: !!name,
  });

  if (isLoading) return <div className="text-center py-12">Loading...</div>;
  if (!data) return <div className="text-center py-12 text-red-500">Region not found</div>;

  return (
    <div>
      <Link to="/countries" className="text-blue-600 hover:underline text-sm">&larr; Back to Countries</Link>
      <h1 className="text-3xl font-bold mt-2 mb-2">{data.region}</h1>
      <p className="text-gray-500 mb-6">{data.countries.length} countries</p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-8">
        {data.countries.map((c) => (
          <Link
            key={c.country_id}
            to={`/countries/${c.country_id}`}
            className="bg-white p-3 rounded-lg shadow text-sm hover:shadow-md"
          >
            {c.country_name}
          </Link>
        ))}
      </div>

      <div className="space-y-4">
        {DOMAINS.map((domain) => {
          const records = data.domains[domain] || [];
          return (
            <details key={domain} className="bg-white rounded-xl shadow">
              <summary className="px-6 py-4 font-semibold cursor-pointer hover:bg-gray-50 capitalize">
                {domain} ({records.length} aggregated records)
              </summary>
              <div className="px-6 pb-4 overflow-x-auto">
                {records.length === 0 ? (
                  <p className="text-gray-400 text-sm py-2">No data available</p>
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-gray-500">
                        <th className="py-2">Indicator</th>
                        <th className="py-2">Year</th>
                        <th className="py-2 text-right">Avg</th>
                        <th className="py-2 text-right">Min</th>
                        <th className="py-2 text-right">Max</th>
                        <th className="py-2 text-right">Countries</th>
                      </tr>
                    </thead>
                    <tbody>
                      {records.map((r, i) => (
                        <tr key={i} className="border-b">
                          <td className="py-1.5">{r.indicator}</td>
                          <td className="py-1.5">{r.year}</td>
                          <td className="py-1.5 text-right font-mono">{Number(r.avg_value).toLocaleString()}</td>
                          <td className="py-1.5 text-right font-mono">{Number(r.min_value).toLocaleString()}</td>
                          <td className="py-1.5 text-right font-mono">{Number(r.max_value).toLocaleString()}</td>
                          <td className="py-1.5 text-right">{r.country_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </details>
          );
        })}
      </div>
    </div>
  );
}
