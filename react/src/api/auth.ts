import client from "./client";
import type { User } from "../types";

export async function getMe(): Promise<User> {
  const { data } = await client.get("/api/auth/me");
  return data;
}

export async function login(
  student_number: string,
  password: string,
  csrfToken: string
): Promise<{ success: boolean; error?: string }> {
  const formData = new URLSearchParams();
  formData.append("student_number", student_number);
  formData.append("password", password);
  formData.append("csrf_token", csrfToken);

  const { data } = await client.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function logout(): Promise<void> {
  await client.get("/auth/logout");
}

export async function fetchCsrfToken(): Promise<string> {
  // Hit /api/auth/me to get a session cookie with CSRF token
  await fetch("/api/auth/me", { credentials: "include" });
  return "";
}
