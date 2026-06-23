import { createContext, useState, useEffect, type ReactNode } from "react";
import type { User } from "../types";
import { getMe, logout as apiLogout, fetchCsrfToken } from "../api/auth";

interface AuthContextType {
  user: User;
  csrfToken: string;
  login: (studentNumber: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextType>({
  user: { authenticated: false, role: "viewer" },
  csrfToken: "",
  login: async () => false,
  logout: async () => {},
  loading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>({
    authenticated: false,
    role: "viewer",
  });
  const [csrfToken, setCsrfToken] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const me = await getMe();
        setUser(me);
        const token = await fetchCsrfToken();
        setCsrfToken(token);
      } catch {
        setUser({ authenticated: false, role: "viewer" });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const loginFn = async (studentNumber: string, password: string) => {
    const token = await fetchCsrfToken();
    setCsrfToken(token);
    const { login } = await import("../api/auth");
    const result = await login(studentNumber, password, token);
    if (result.success) {
      const me = await getMe();
      setUser(me);
      return true;
    }
    return false;
  };

  const logoutFn = async () => {
    await apiLogout();
    setUser({ authenticated: false, role: "viewer" });
    setCsrfToken("");
  };

  return (
    <AuthContext.Provider
      value={{ user, csrfToken, login: loginFn, logout: logoutFn, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
}
