import { createContext, useContext, useState, useCallback } from "react";
import { ROLES_DATA } from "../constants/roles";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const login = useCallback((email, password, toggleRole) => {
    // Look up the role in our ROLES_DATA dictionary
    const emailKey = Object.keys(ROLES_DATA).find(
      (key) => ROLES_DATA[key].email.toLowerCase() === (email || "").toLowerCase().trim()
    );

    let loggedInUser;
    if (emailKey) {
      loggedInUser = { ...ROLES_DATA[emailKey] };
    } else {
      // Fallback for custom typed emails
      const isClientRole = toggleRole === "client" || (email && (email.includes("client") || email.includes("acme")));
      loggedInUser = {
        id: "custom",
        name: email ? email.split("@")[0].replace(/[._]/g, " ") : "Custom User",
        email: email || (isClientRole ? "client_admin@acmecorp.com" : "pm@requirementai.com"),
        role: isClientRole ? "client" : "admin",
        assigned_role: isClientRole ? "Client Admin" : "Project Manager",
        company: isClientRole ? "Acme Corp" : "RequirementAI Consulting",
        department: isClientRole ? "Client Operations" : "Project Management Office",
        project_access: "Acme ERP Sync",
        dashboard_name: isClientRole ? "Client Dashboard" : "Project Dashboard",
        permissions: {
          upload: true,
          review: true,
          approve: false,
          manage_users: true,
          manage_projects: isClientRole ? false : true,
          platform_settings: false,
        },
        access_checklist: isClientRole
          ? ["View Projects", "Upload Company Documents", "Track Project Status"]
          : ["Create Project", "Manage Timeline", "View All Documents", "Review Documents"],
      };
    }

    setUser(loggedInUser);
    localStorage.setItem("user", JSON.stringify(loggedInUser));
    localStorage.setItem("token", "mock-token-" + loggedInUser.role);
    return loggedInUser;
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, isAdmin: user?.role === "admin", isClient: user?.role === "client" }}>
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
