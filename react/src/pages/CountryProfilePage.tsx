import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getCountryProfile } from "../api/countries";

const DOMAINS = ["health", "energy", "freshwater", "ghg", "sustainability"] as const;

export default function CountryProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["country", id],
    queryFn: () => getCountryProfile(Number(id)),
    enabled: !!id,
  });

  if (isLoading) return <div className="text-center py-12">Loading...</div>;
  if (!data) return <div className="text-center py-12 text-red-500">Country not found</div>;

  const c = data.country;

  return (
    <div>
      <Link to="/countries" className="text-blue-600 hover:underline text-sm">&larr; Back to Countries</Link>
      <h1 className="text-3xl font-bold mt-2 mb-1">{c.country_name}</h1>
      <p className="text-gray-500 mb-6">
        {c.country_code} | {c.region || "No region"}
      </p>

      <div className="space-y-4">
        {DOMAINS.map((domain) => {
          const records = data.domains[domain] || [];
          return (
            <details key={domain} className="bg-white rounded-xl shadow">
              <summary className="px-6 py-4 font-semibold cursor-pointer hover:bg-gray-50 capitalize">
                {domain} ({records.length} records)
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
                        <th className="py-2 text-right">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {records.map((r, i) => (
                        <tr key={i} className="border-b">
                          <td className="py-1.5">{String(r.indicator)}</td>
                          <td className="py-1.5">{r.year}</td>
                          <td className="py-1.5 text-right font-mono">
                            {r.value != null ? Number(r.value).toLocaleString() : "-"}
                          </td>
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
