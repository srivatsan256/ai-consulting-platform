import React, { useState, useCallback } from "react";
import { useAuth } from "./context/AuthContext.jsx";
import SidebarNavigation from "./components/SidebarNavigation";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import ForgotPassword from "./pages/ForgotPassword";
import VerifyOTP from "./pages/VerifyOTP";
import ResetPassword from "./pages/ResetPassword";
import ResetSuccess from "./pages/ResetSuccess";
import DashboardPage from "./pages/DashboardPage";
import ProjectsPage from "./pages/ProjectsPage";
import ProjectDetailPage from "./pages/ProjectDetailPage";
import UploadPage from "./pages/UploadPage";
import VerificationPage from "./pages/VerificationPage";
import AIChatPage from "./pages/AIChatPage";
import DeliverablesPage from "./pages/DeliverablesPage";
import ReportsPage from "./pages/ReportsPage";
import ClientDashboard from "./pages/ClientDashboard";
import ClientProjectsPage from "./pages/ClientProjectsPage";
import ClientChatPage from "./pages/ClientChatPage";
import ClientDownloads from "./pages/ClientDownloads";
import { getPageTitle } from "./constants/navigation";

const roleToDashboard = {
  // Admin roles
  super_admin: "dashboard",
  company_admin: "dashboard",
  project_manager: "dashboard",
  business_analyst: "dashboard",
  solution_architect: "dashboard",
  ai_ml_engineer: "dashboard",
  backend_developer: "dashboard",
  frontend_developer: "dashboard",
  qa_test_engineer: "dashboard",
  security_consultant: "dashboard",
  devops_engineer: "dashboard",
  document_reviewer: "dashboard",
  // Client roles
  client_admin: "client-dashboard",
  client_sme: "client-dashboard",
  client_reviewer: "client-dashboard",
  business_sponsor: "client-dashboard",
  viewer: "client-dashboard",
};

const adminRoles = [
  "super_admin",
  "company_admin",
  "project_manager",
  "business_analyst",
  "solution_architect",
  "ai_ml_engineer",
  "backend_developer",
  "frontend_developer",
  "qa_test_engineer",
  "security_consultant",
  "devops_engineer",
  "document_reviewer",
];

export default function App() {
  const { user, authReady, login, register, logout, isAdmin, isClient } = useAuth();
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  // OTP-based password-reset flow
  const [authView, setAuthView] = useState("login");
  const [forgotEmail, setForgotEmail] = useState("");
  const [resetCredentials, setResetCredentials] = useState({ uid: "", token: "" });

  const getRoleKey = useCallback((user) => {
    if (user?.role_key) return user.role_key;
    if (!user?.assigned_role) return null;
    return user.assigned_role
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_|_$/g, "");
  }, []);

  const handleLogin = useCallback(
    async (email, password, role) => {
      const loggedInUser = await login(email, password, role);
      const roleKey = getRoleKey(loggedInUser);
      const defaultView = roleToDashboard[roleKey] || (role === "admin" ? "dashboard" : "client-dashboard");
      setActiveView(defaultView);
    },
    [login, getRoleKey]
  );

  const handleRegister = useCallback(
    async (data) => {
      const newUser = await register(data);
      const roleKey = getRoleKey(newUser);
      const defaultView =
        roleToDashboard[roleKey] ||
        (data.account_type === "client" ? "client-dashboard" : "dashboard");
      setActiveView(defaultView);
      setAuthView("login");
    },
    [register, getRoleKey]
  );

  const handleLogout = useCallback(() => {
    logout();
    setActiveView("dashboard");
    setSelectedProjectId(null);
  }, [logout]);

  const openProject = useCallback(
    (projectId) => {
      setSelectedProjectId(projectId);
      const roleKey = getRoleKey(user);
      if (roleKey && adminRoles.includes(roleKey)) {
        setActiveView("project-detail");
      } else {
        setActiveView("client-projects");
      }
    },
    [user, getRoleKey]
  );

  const goBack = useCallback(() => {
    setSelectedProjectId(null);
    const roleKey = getRoleKey(user);
    if (roleKey && adminRoles.includes(roleKey)) {
      setActiveView("projects");
    } else {
      setActiveView("client-projects");
    }
  }, [user, getRoleKey]);

  if (!authReady) {
    return null;
  }

  // ── Unauthenticated screens (login / signup / password-reset flow) ──
  if (!user) {
    switch (authView) {
      case "forgot-password":
        return (
          <ForgotPassword
            onBackToLogin={() => setAuthView("login")}
            onSent={(email) => {
              setForgotEmail(email);
              setAuthView("verify-otp");
            }}
          />
        );

      case "verify-otp":
        return (
          <VerifyOTP
            email={forgotEmail}
            onBackToLogin={() => setAuthView("login")}
            onBackToEmail={() => setAuthView("forgot-password")}
            onVerified={(credentials) => {
              setResetCredentials(credentials); // expects { uid, token }
              setAuthView("reset-password");
            }}
          />
        );

      case "reset-password":
        return (
          <ResetPassword
            uid={resetCredentials.uid}
            token={resetCredentials.token}
            onBackToLogin={() => setAuthView("login")}
            onSuccess={() => setAuthView("reset-success")}
          />
        );

      case "reset-success":
        return <ResetSuccess onBackToLogin={() => setAuthView("login")} />;

      case "signup":
        return (
          <SignupPage
            onRegister={handleRegister}
            onShowLogin={() => setAuthView("login")}
          />
        );

      case "login":
      default:
        return (
          <LoginPage
            onLogin={handleLogin}
            onShowSignup={() => setAuthView("signup")}
            onForgotPassword={() => setAuthView("forgot-password")}
          />
        );
    }
  }

  // ── Authenticated screens ──
  const renderPage = () => {
    switch (activeView) {
      case "dashboard":
        return (
          <DashboardPage
            user={user}
            onNewProject={() => setActiveView("projects")}
            onOpenProject={openProject}
            onViewAllProjects={() => setActiveView("projects")}
          />
        );
      case "projects":
        return (
          <ProjectsPage
            onSelectProject={openProject}
            onNewProject={() => setActiveView("projects")}
          />
        );
      case "project-detail":
        return (
          <ProjectDetailPage
            projectId={selectedProjectId}
            onBack={goBack}
          />
        );
      case "upload":
        return (
          <UploadPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      case "verification":
        return (
          <VerificationPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      case "ai-chat":
        return (
          <AIChatPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      case "deliverables":
        return (
          <DeliverablesPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      case "reports":
        return (
          <ReportsPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      case "client-dashboard":
        return (
          <ClientDashboard
            user={user}
            onSelectProject={openProject}
          />
        );
      case "client-projects":
        return (
          <ClientProjectsPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
            onBack={selectedProjectId ? goBack : null}
          />
        );
      case "client-chat":
        return (
          <ClientChatPage
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      case "client-downloads":
        return (
          <ClientDownloads
            projectId={selectedProjectId}
            onSelectProject={openProject}
          />
        );
      default:
        return isAdmin ? (
          <DashboardPage
            user={user}
            onNewProject={() => setActiveView("projects")}
            onOpenProject={openProject}
            onViewAllProjects={() => setActiveView("projects")}
          />
        ) : (
          <ClientDashboard
            user={user}
            onSelectProject={openProject}
          />
        );
    }
  };

  const pageTitle = getPageTitle(activeView);

  return (
    <div className="min-h-screen bg-background flex">
      <SidebarNavigation
        activeView={activeView}
        setActiveView={(view) => {
          setSelectedProjectId(null);
          setActiveView(view);
        }}
        role={user.role}
        user={user}
        onLogout={handleLogout}
      />

      <div className="flex-1 ml-[240px] p-8">
        {renderPage()}
      </div>
    </div>
  );
}
import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;