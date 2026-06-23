import client from "./client";
import type { Country, DashboardStats, CountryProfile, RegionProfile } from "../types";

export async function getCountriesList(q?: string) {
  const { data } = await client.get("/api/countries", { params: { q } });
  return data;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await client.get("/api/dashboard");
  return data;
}

export async function getCountryProfile(id: number): Promise<CountryProfile> {
  const { data } = await client.get(`/api/countries/${id}`);
  return data;
}

export async function getRegionProfile(name: string): Promise<RegionProfile> {
  const { data } = await client.get(`/api/countries/region/${encodeURIComponent(name)}`);
  return data;
}

export async function autocompleteCountries(q: string): Promise<Country[]> {
  const { data } = await client.get("/api/countries/autocomplete", { params: { q } });
  return data;
}
