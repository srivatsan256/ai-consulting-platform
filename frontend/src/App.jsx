import React, { useState, useCallback } from "react";
import { useAuth } from "./context/AuthContext.jsx";
import SidebarNavigation from "./components/SidebarNavigation";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ProjectsPage from "./pages/ProjectsPage";
import ProjectDetailPage from "./pages/ProjectDetailPage.jsx";
import UploadPage from "./pages/UploadPage";
import VerificationPage from "./pages/VerificationPage";
import AIChatPage from "./pages/AIChatPage";
import ReportsPage from "./pages/ReportsPage";
import UseCaseLevel1 from "./pages/projectdetail/UseCaseLevel1";
import UseCaseEvaluationSheetLevel1 from "./pages/projectdetail/UseCaseEvaluationSheetLevel1";
import UseCaseShortlistingReportLevel1 from "./pages/projectdetail/UseCaseShortlistingReportLevel1";
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
  const { user, login, logout, isAdmin, isClient } = useAuth();
  const [activeView, setActiveView] = useState("dashboard");
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  const getRoleKey = useCallback((user) => {
    if (!user?.assigned_role) return null;
    return user.assigned_role
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_|_$/g, "");
  }, []);

  const handleLogin = useCallback(
    (email, password, role) => {
      const loggedInUser = login(email, password, role);
      const roleKey = getRoleKey(loggedInUser);
      const defaultView = roleToDashboard[roleKey] || "dashboard";
      setActiveView(defaultView);
    },
    [login, getRoleKey]
  );

  const handleLogout = useCallback(() => {
    logout();
    setActiveView("dashboard");
    setSelectedProjectId(null);
  }, [logout]);

  const openProject = useCallback(
    (projectId) => {
      setSelectedProjectId(projectId);
      setActiveView("project-detail");
    },
    []
  );

  const goBack = useCallback(() => {
    setSelectedProjectId(null);
    setActiveView("projects");
  }, []);

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

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
        return <ProjectsPage onSelectProject={openProject} onNewProject={() => setActiveView("projects")} />;
      case "project-detail":
        return (
          <ProjectDetailPage
            projectId={selectedProjectId}
            onBack={goBack}
            onNavigate={(view) => setActiveView(view)}
          />
        );
      case "upload":
        return <UploadPage projectId={selectedProjectId} onSelectProject={openProject} />;
      case "verification":
        return <VerificationPage projectId={selectedProjectId} onSelectProject={openProject} />;
      case "ai-chat":
        return <AIChatPage projectId={selectedProjectId} onSelectProject={openProject} />;
      case "reports":
        return <ReportsPage projectId={selectedProjectId} onSelectProject={openProject} />;
      case "use-case-level1":
        return (
          <UseCaseLevel1
            projectId={selectedProjectId}
            onBack={goBack}
            onNavigate={(view) => setActiveView(view)}
          />
        );
      case "use-case-evaluation-sheet-level1":
        return (
          <UseCaseEvaluationSheetLevel1
            projectId={selectedProjectId}
            onBack={goBack}
            onNavigate={(view) => setActiveView(view)}
          />
        );
      case "use-case-shortlisting-report-level1":
        return (
          <UseCaseShortlistingReportLevel1
            projectId={selectedProjectId}
            onBack={goBack}
            onNavigate={(view) => setActiveView(view)}
          />
        );
      default:
        return (
          <DashboardPage
            user={user}
            onNewProject={() => setActiveView("projects")}
            onOpenProject={openProject}
            onViewAllProjects={() => setActiveView("projects")}
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
