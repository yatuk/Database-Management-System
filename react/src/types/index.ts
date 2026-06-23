export interface User {
  authenticated: boolean;
  student_id?: number;
  student_number?: string;
  role: "admin" | "editor" | "viewer";
}

export interface Country {
  country_id: number;
  country_name: string;
  country_code: string;
  region: string;
  data_count: number;
}

export interface DomainRecord {
  [key: string]: unknown;
  country_name: string;
  country_code: string;
  region: string;
  indicator_name: string;
  year: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface DashboardStats {
  countries: number;
  health: DomainStats;
  energy: DomainStats;
  freshwater: DomainStats;
  ghg: DomainStats;
  sustainability: DomainStats;
}

export interface DomainStats {
  indicators: number;
  min_year: number | null;
  max_year: number | null;
  records: number;
}

export interface CountryProfile {
  country: Country;
  domains: Record<string, DomainRecord[]>;
}

export interface RegionProfile {
  region: string;
  countries: Country[];
  domains: Record<string, RegionDomainStats[]>;
}

export interface RegionDomainStats {
  indicator: string;
  year: number;
  avg_value: number;
  min_value: number;
  max_value: number;
  country_count: number;
}

export type Domain =
  | "energy"
  | "freshwater"
  | "ghg"
  | "health"
  | "sustainability";
