import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import {
  listDomain,
  addDomain,
  editDomain,
  deleteDomain,
  getIndicators,
  getYears,
  type ListParams,
} from "../api/domain";
import { useAuth } from "../hooks/useAuth";
import type { Domain, DomainRecord } from "../types";

const DOMAIN_META: Record<Domain, { label: string; icon: string }> = {
  energy: { label: "Energy", icon: "⚡" },
  freshwater: { label: "Freshwater", icon: "💧" },
  ghg: { label: "GHG Emissions", icon: "💨" },
  health: { label: "Health", icon: "❤" },
  sustainability: { label: "Sustainability", icon: "🌿" },
};

export default function DomainListPage() {
  const { domain } = useParams<{ domain: Domain }>();
  const d = domain as Domain;
  const meta = DOMAIN_META[d] || { label: d, icon: "" };
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("year");
  const [order, setOrder] = useState("desc");
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<Record<string, string>>({});

  const params: ListParams = { page, sort_by: sortBy, order };
  if (search) params.country = search;

  const { data, isLoading } = useQuery({
    queryKey: [d, "list", params],
    queryFn: () => listDomain(d, params),
  });

  const { data: indicators } = useQuery({
    queryKey: [d, "indicators"],
    queryFn: () => getIndicators(d),
    enabled: showModal || editingId !== null,
  });

  const { data: years } = useQuery({
    queryKey: [d, "years"],
    queryFn: () => getYears(d),
  });

  const addMut = useMutation({
    mutationFn: (record: Record<string, unknown>) => addDomain(d, record),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [d, "list"] });
      setShowModal(false);
      setForm({});
    },
  });

  const editMut = useMutation({
    mutationFn: ({ id, record }: { id: number; record: Record<string, unknown> }) =>
      editDomain(d, id, record),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [d, "list"] });
      setEditingId(null);
      setForm({});
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteDomain(d, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [d, "list"] }),
  });

  const canEdit = user.role === "admin" || user.role === "editor";
  const canDelete = user.role === "admin";

  const handleSubmit = () => {
    const record: Record<string, unknown> = { ...form };
    if (editingId) {
      editMut.mutate({ id: editingId, record });
    } else {
      addMut.mutate(record);
    }
  };

  const openEdit = async (record: DomainRecord) => {
    const mod = await import("../api/domain");
    try {
      const full = await mod.getDomain(d, record[getPk(d)] as number);
      setForm(full as unknown as Record<string, string>);
      setEditingId(record[getPk(d)] as number);
    } catch {
      setEditingId(record[getPk(d)] as number);
    }
  };

  const indicatorField = getIndicatorFk(d);
  const pkField = getPk(d);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">
          {meta.icon} {meta.label}
        </h1>
        {canEdit && (
          <button
            onClick={() => { setShowModal(true); setEditingId(null); setForm({}); }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            + Add Record
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <input
          type="text"
          placeholder="Search country..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="border rounded-lg px-3 py-2 text-sm"
        />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="year">Year</option>
          <option value="country">Country</option>
          <option value="value">Value</option>
          <option value="indicator">Indicator</option>
          <option value="region">Region</option>
        </select>
        <select
          value={order}
          onChange={(e) => setOrder(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
        <select
          value={(form as Record<string, string>).year_filter || ""}
          onChange={(e) => {
            const y = e.target.value;
            setForm((prev) => ({ ...prev, year_filter: y }));
            if (y) {
              setPage(1);
              // re-fetch via updating params
            }
          }}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="">All years</option>
          {(years || []).map((y: number) => (
            <option key={y} value={String(y)}>{y}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3">Country</th>
                  <th className="text-left px-4 py-3">Indicator</th>
                  <th className="text-left px-4 py-3">Year</th>
                  <th className="text-right px-4 py-3">Value</th>
                  {(canEdit || canDelete) && (
                    <th className="text-center px-4 py-3 w-24">Actions</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {(data?.data || []).map((row: DomainRecord, i: number) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">
                      <Link to={`/countries/${row.country_id}`} className="text-blue-600 hover:underline">
                        {row.country_name}
                      </Link>
                      <div className="text-xs text-gray-400">{row.region}</div>
                    </td>
                    <td className="px-4 py-2">{row.indicator_name as string}</td>
                    <td className="px-4 py-2">{row.year as number}</td>
                    <td className="px-4 py-2 text-right font-mono">
                      {row.indicator_value != null ? Number(row.indicator_value).toLocaleString() : "-"}
                    </td>
                    {(canEdit || canDelete) && (
                      <td className="px-4 py-2 text-center">
                        <div className="flex gap-1 justify-center">
                          {canEdit && (
                            <button
                              onClick={() => openEdit(row)}
                              className="px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
                            >
                              Edit
                            </button>
                          )}
                          {canDelete && (
                            <button
                              onClick={() => {
                                if (confirm("Delete this record?")) {
                                  deleteMut.mutate(row[pkField] as number);
                                }
                              }}
                              className="px-2 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100"
                            >
                              Del
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data && data.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page <= 1}
                className="px-3 py-1 rounded border disabled:opacity-30"
              >
                Prev
              </button>
              <span className="px-3 py-1 text-sm text-gray-500">
                Page {data.page} of {data.total_pages} ({data.total} records)
              </span>
              <button
                onClick={() => setPage(Math.min(data.total_pages, page + 1))}
                disabled={page >= data.total_pages}
                className="px-3 py-1 rounded border disabled:opacity-30"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Modal */}
      {(showModal || editingId !== null) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg mx-4 max-h-[80vh] overflow-auto">
            <h3 className="text-lg font-bold mb-4">
              {editingId ? "Edit" : "Add"} {meta.label} Record
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Country</label>
                <input
                  type="text"
                  placeholder="Country name"
                  value={(form as Record<string, string>).country_name || ""}
                  onChange={(e) => setForm({ ...form, country_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Indicator</label>
                <select
                  value={(form as Record<string, string>)[indicatorField] || ""}
                  onChange={(e) => setForm({ ...form, [indicatorField]: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Select...</option>
                  {(indicators || []).map(
                    (ind: Record<string, unknown>) => (
                      <option key={ind[indicatorField] as number} value={String(ind[indicatorField])}>
                        {ind.indicator_name as string}
                      </option>
                    )
                  )}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Year</label>
                  <input
                    type="number"
                    value={(form as Record<string, string>)["year"] || ""}
                    onChange={(e) => setForm({ ...form, year: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Value</label>
                  <input
                    type="number"
                    step="any"
                    value={(form as Record<string, string>)["indicator_value"] || ""}
                    onChange={(e) => setForm({ ...form, indicator_value: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Source Notes</label>
                <input
                  type="text"
                  value={(form as Record<string, string>)[getSourceField(d)] || ""}
                  onChange={(e) => setForm({ ...form, [getSourceField(d)]: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => { setShowModal(false); setEditingId(null); }}
                className="px-4 py-2 border rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {editingId ? "Update" : "Create"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getIndicatorFk(domain: Domain): string {
  const map: Record<Domain, string> = {
    energy: "energy_indicator_id",
    freshwater: "freshwater_indicator_id",
    ghg: "ghg_indicator_id",
    health: "health_indicator_id",
    sustainability: "sus_indicator_id",
  };
  return map[domain];
}

function getPk(domain: Domain): string {
  const map: Record<Domain, string> = {
    energy: "data_id",
    freshwater: "data_id",
    ghg: "row_id",
    health: "row_id",
    sustainability: "data_id",
  };
  return map[domain];
}

function getSourceField(domain: Domain): string {
  const map: Record<Domain, string> = {
    energy: "data_source",
    freshwater: "source_notes",
    ghg: "source_notes",
    health: "source_notes",
    sustainability: "source_note",
  };
  return map[domain];
}
