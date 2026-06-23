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

  try {
    await client.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      maxRedirects: 0,
    });
    return { success: true };
  } catch (err: unknown) {
    if (err && typeof err === "object" && "response" in err) {
      const axiosErr = err as { response?: { status: number } };
      if (axiosErr.response?.status === 302) return { success: true };
    }
    return { success: false, error: "Login failed" };
  }
}

export async function logout(): Promise<void> {
  await client.get("/auth/logout");
}

// Fetch a fresh CSRF token by hitting a GET endpoint
export async function fetchCsrfToken(): Promise<string> {
  await client.get("/api/auth/me");
  // The session cookie carries the CSRF info;
  // we need to GET a page that sets it. Try auth login page.
  try {
    const resp = await fetch("/auth/login", { credentials: "include" });
    const html = await resp.text();
    const match = html.match(/name="csrf_token" value="([^"]+)"/);
    if (match) return match[1];
  } catch {
    // fallback
  }
  return "";
}
