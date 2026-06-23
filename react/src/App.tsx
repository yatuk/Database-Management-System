import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./contexts/AuthContext";
import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import CountriesPage from "./pages/CountriesPage";
import CountryProfilePage from "./pages/CountryProfilePage";
import RegionProfilePage from "./pages/RegionProfilePage";
import DomainListPage from "./pages/DomainListPage";
import AboutPage from "./pages/AboutPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<MainLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/countries" element={<CountriesPage />} />
              <Route path="/countries/:id" element={<CountryProfilePage />} />
              <Route path="/region/:name" element={<RegionProfilePage />} />
              <Route path="/domain/:domain" element={<DomainListPage />} />
              <Route path="/about" element={<AboutPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
