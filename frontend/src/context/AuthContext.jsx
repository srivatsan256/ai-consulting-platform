import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { ROLES_DATA } from "../constants/roles";
import { authService, TOKEN_KEY, companyService, subscriptionService } from "../services/api";
import "../styles/context/AuthContext.css";

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
  const [tenant, setTenant] = useState(null);
  const [plan, setPlan] = useState(null);
  const [authReady, setAuthReady] = useState(false);

  const loadTenant = useCallback(async () => {
    try {
      const [contextRes, featuresRes, usageRes, quotasRes] = await Promise.all([
        companyService.context(),
        subscriptionService.features(),
        subscriptionService.usage(),
        subscriptionService.quotas(),
      ]);
      setTenant({
        company: contextRes.data?.data?.company || null,
        settings: contextRes.data?.data?.settings || null,
        onboarding: contextRes.data?.data?.onboarding || null,
      });
      setPlan({
        features: featuresRes.data || {},
        usage: usageRes.data?.period || [],
        quotas: quotasRes.data?.quotas || [],
        plan: quotasRes.data?.plan || null,
      });
    } catch {
      setTenant(null);
      setPlan(null);
    }
  }, []);

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
        await loadTenant();
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
  }, [loadTenant]);

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
    await loadTenant();
    return built;
  }, [loadTenant]);

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
    await loadTenant();
    return built;
  }, [loadTenant]);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    setTenant(null);
    setPlan(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        tenant,
        plan,
        authReady,
        login,
        register,
        logout,
        loadTenant,
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
