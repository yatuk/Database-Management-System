import client from "./client";
import type { Domain, PaginatedResponse, DomainRecord } from "../types";

export interface ListParams {
  page?: number;
  sort_by?: string;
  order?: string;
  country?: string;
  year?: number;
  year_min?: number;
  year_max?: number;
}

export async function listDomain(
  domain: Domain,
  params: ListParams = {}
): Promise<PaginatedResponse<DomainRecord>> {
  const { data } = await client.get(`/api/${domain}/list`, { params });
  return data;
}

export async function getDomain(
  domain: Domain,
  id: number
): Promise<DomainRecord> {
  const { data } = await client.get(`/api/${domain}/get/${id}`);
  if (!data.success) throw new Error(data.error);
  return data.record;
}

export async function addDomain(
  domain: Domain,
  record: Record<string, unknown>
): Promise<DomainRecord> {
  const { data } = await client.post(`/api/${domain}/add`, record);
  if (!data.success) throw new Error(data.error);
  return data.record;
}

export async function editDomain(
  domain: Domain,
  id: number,
  record: Record<string, unknown>
): Promise<DomainRecord> {
  const { data } = await client.post(`/api/${domain}/edit/${id}`, record);
  if (!data.success) throw new Error(data.error);
  return data.record;
}

export async function deleteDomain(
  domain: Domain,
  id: number
): Promise<void> {
  const { data } = await client.post(`/api/${domain}/delete/${id}`);
  if (!data.success) throw new Error(data.error);
}

export async function getCountries(domain: Domain) {
  const { data } = await client.get(`/api/${domain}/countries`);
  return data;
}

export async function getIndicators(domain: Domain) {
  const { data } = await client.get(`/api/${domain}/indicators`);
  return data;
}

export async function getYears(domain: Domain) {
  const { data } = await client.get(`/api/${domain}/years`);
  return data;
}
