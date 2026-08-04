import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { ROLES_DATA } from "../constants/roles";
import { authService, TOKEN_KEY } from "../services/api";

const AuthContext = createContext(null);

const CLIENT_ROLE_KEYS = [
  "client_admin",
  "client_sme",
  "client_reviewer",
  "business_sponsor",
  "viewer",
];

function buildUser(me) {
  const roleKey = me.role?.key || "viewer";
  const defaults = ROLES_DATA[roleKey] || ROLES_DATA.viewer;
  const isClient = CLIENT_ROLE_KEYS.includes(roleKey);
  return {
    id: me.id ?? roleKey,
    role_key: roleKey,
    name: me.full_name || (me.email ? me.email.split("@")[0].replace(/[._]/g, " ") : "User"),
    email: me.email,
    role: isClient ? "client" : "admin",
    assigned_role: me.role?.name || defaults.assigned_role,
    company: me.company?.name || defaults.company,
    department: defaults.department,
    project_access: defaults.project_access,
    dashboard_name: defaults.dashboard_name,
    permissions: defaults.permissions,
    access_checklist: defaults.access_checklist,
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function restore() {
      if (!localStorage.getItem(TOKEN_KEY)) {
        localStorage.removeItem("user");
        setUser(null);
        setAuthReady(true);
        return;
      }
      try {
        const res = await authService.me();
        if (cancelled) return;
        const built = buildUser(res.data.data);
        setUser(built);
        localStorage.setItem("user", JSON.stringify(built));
      } catch {
        authService.logout();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setAuthReady(true);
      }
    }
    restore();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email, password, _toggleRole) => {
    const res = await authService.login(email, password);
    const { access, refresh, user: userData, company, role } = res.data;
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem("refresh_token", refresh);
    const built = buildUser({
      id: userData?.id,
      email: userData?.email,
      full_name: userData?.full_name,
      company,
      role,
    });
    setUser(built);
    localStorage.setItem("user", JSON.stringify(built));
    return built;
  }, []);

  const register = useCallback(async (data) => {
    const res = await authService.register(data);
    const { access, refresh, user: userData, company, role } = res.data;
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem("refresh_token", refresh);
    const built = buildUser({
      id: userData?.id,
      email: userData?.email,
      full_name: userData?.full_name,
      company,
      role,
    });
    setUser(built);
    localStorage.setItem("user", JSON.stringify(built));
    return built;
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        authReady,
        login,
        register,
        logout,
        isAdmin: user?.role === "admin",
        isClient: user?.role === "client",
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export default AuthContext;
