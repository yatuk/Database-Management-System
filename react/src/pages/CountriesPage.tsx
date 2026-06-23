import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getCountriesList } from "../api/countries";
import type { Country } from "../types";

export default function CountriesPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["countries", search],
    queryFn: () => getCountriesList(search || undefined),
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Countries</h1>

      <input
        type="text"
        placeholder="Search countries..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md border rounded-lg px-4 py-2 mb-6 focus:ring-2 focus:ring-blue-500 outline-none"
      />

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data?.countries || []).map((c: Country) => (
            <Link
              key={c.country_id}
              to={`/countries/${c.country_id}`}
              className="bg-white p-4 rounded-xl shadow hover:shadow-md transition-shadow"
            >
              <div className="font-semibold">{c.country_name}</div>
              <div className="text-sm text-gray-500">
                {c.country_code} | {c.region || "No region"}
              </div>
              <div className="mt-2">
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    c.data_count > 0
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {c.data_count > 0 ? `${c.data_count} records` : "No data"}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
