import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const DOMAINS = [
  { key: "health", label: "Health", icon: "❤" },
  { key: "ghg", label: "GHG Emissions", icon: "💨" },
  { key: "energy", label: "Energy", icon: "⚡" },
  { key: "freshwater", label: "Freshwater", icon: "💧" },
  { key: "sustainability", label: "Sustainability", icon: "🌿" },
];

export default function MainLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-slate-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-6">
              <Link to="/" className="font-bold text-lg">
                WDI Database
              </Link>
              <div className="hidden md:flex gap-1">
                <Link to="/countries" className="px-3 py-1 rounded hover:bg-slate-700 text-sm">
                  Countries
                </Link>
                <Link to="/dashboard" className="px-3 py-1 rounded hover:bg-slate-700 text-sm">
                  Dashboard
                </Link>
                {DOMAINS.map((d) => (
                  <Link
                    key={d.key}
                    to={`/domain/${d.key}`}
                    className="px-3 py-1 rounded hover:bg-slate-700 text-sm"
                  >
                    {d.icon} {d.label}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              {user.authenticated ? (
                <>
                  <span className="text-slate-300">
                    {user.student_number}
                    <span className="ml-2 px-2 py-0.5 rounded text-xs bg-blue-600">
                      {user.role}
                    </span>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1 rounded bg-red-600 hover:bg-red-700"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <Link to="/login" className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-700">
                  Login
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>

      <footer className="border-t bg-white mt-12 py-6 text-center text-sm text-gray-500">
        BLG-317E Database Systems - WDI Project
      </footer>
    </div>
  );
}
