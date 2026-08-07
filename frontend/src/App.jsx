import React, { useState, useCallback } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useParams,
} from "react-router-dom";
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
import TasksPage from "./pages/TasksPage";
import TaskDetailPage from "./pages/TaskDetailPage";
import UsersPage from "./pages/UsersPage";
import TeamsDepartmentsPage from "./pages/TeamsDepartmentsPage";
import RolesPage from "./pages/RolesPage";

import ClientDashboard from "./pages/ClientDashboard";
import ClientProjectsPage from "./pages/ClientProjectsPage";
import ClientChatPage from "./pages/ClientChatPage";
import ClientDownloads from "./pages/ClientDownloads";

// ─────────────────────────────────────────────────────────────
// Role helpers
// ─────────────────────────────────────────────────────────────
const roleToDashboard = {
  super_admin: "/dashboard",
  company_admin: "/dashboard",
  project_manager: "/dashboard",
  business_analyst: "/dashboard",
  solution_architect: "/dashboard",
  ai_ml_engineer: "/dashboard",
  backend_developer: "/dashboard",
  frontend_developer: "/dashboard",
  qa_test_engineer: "/dashboard",
  security_consultant: "/dashboard",
  devops_engineer: "/dashboard",
  document_reviewer: "/dashboard",
  client_admin: "/client-dashboard",
  client_sme: "/client-dashboard",
  client_reviewer: "/client-dashboard",
  business_sponsor: "/client-dashboard",
  viewer: "/client-dashboard",
};

const adminRoles = [
  "super_admin", "company_admin", "project_manager", "business_analyst",
  "solution_architect", "ai_ml_engineer", "backend_developer", "frontend_developer",
  "qa_test_engineer", "security_consultant", "devops_engineer", "document_reviewer",
];

const getRoleKey = (user) => {
  if (user?.role_key) return user.role_key;
  if (!user?.assigned_role) return null;
  return user.assigned_role
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "");
};

// ─────────────────────────────────────────────────────────────
// Auth screens (login / signup / password reset)
// ─────────────────────────────────────────────────────────────
function AuthScreens() {
  const [authView, setAuthView] = useState("login");
  const [forgotEmail, setForgotEmail] = useState("");
  const [resetCredentials, setResetCredentials] = useState({ uid: "", token: "" });
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleLogin = useCallback(
    async (email, password, role) => {
      const loggedInUser = await login(email, password, role);
      const roleKey = getRoleKey(loggedInUser);
      const path = roleToDashboard[roleKey] || (role === "admin" ? "/dashboard" : "/client-dashboard");
      navigate(path, { replace: true });
    },
    [login, navigate]
  );

  const handleRegister = useCallback(
    async (data) => {
      const newUser = await register(data);
      const roleKey = getRoleKey(newUser);
      const path =
        roleToDashboard[roleKey] ||
        (data.account_type === "client" ? "/client-dashboard" : "/dashboard");
      navigate(path, { replace: true });
    },
    [register, navigate]
  );

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
            setResetCredentials(credentials);
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

// ─────────────────────────────────────────────────────────────
// Protected layout (sidebar + content)
// ─────────────────────────────────────────────────────────────
const VIEW_ROUTE_MAP = {
  dashboard: "/dashboard",
  projects: "/projects",
  tasks: "/tasks",
  users: "/users",
  teams: "/teams",
  roles: "/roles",
  reports: "/projects",
  upload: "/projects",
  verification: "/projects",
  deliverables: "/projects",
  "ai-chat": "/projects",
  "client-dashboard": "/client-dashboard",
  "client-projects": "/client-projects",
  "client-chat": "/client-projects",
  "client-downloads": "/client-projects",
};

function AppLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const handleNavigate = (viewId) => {
    const path = VIEW_ROUTE_MAP[viewId];
    if (path) navigate(path);
  };

  return (
    <div className="min-h-screen bg-background flex">
      <SidebarNavigation user={user} onLogout={handleLogout} onNavigate={handleNavigate} />
      <div className="flex-1 ml-[240px] p-8">{children}</div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Route guards
// ─────────────────────────────────────────────────────────────
function RequireAuth({ children }) {
  const { user, authReady } = useAuth();
  if (!authReady) return null;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function RequireAdmin({ children }) {
  const { user, authReady } = useAuth();
  if (!authReady) return null;
  if (!user) return <Navigate to="/login" replace />;
  const roleKey = getRoleKey(user);
  if (!adminRoles.includes(roleKey)) {
    return <Navigate to="/client-dashboard" replace />;
  }
  return children;
}

function RoleHome() {
  const { user } = useAuth();
  const roleKey = getRoleKey(user);
  const path = roleToDashboard[roleKey] || "/dashboard";
  return <Navigate to={path} replace />;
}

// ─────────────────────────────────────────────────────────────
// Page wrappers that pull projectId from the URL
// ─────────────────────────────────────────────────────────────
function ProjectDetailWrapper() {
  const { projectId } = useParams();
  return <ProjectDetailPage projectId={projectId} />;
}

function UploadWrapper() {
  const { projectId } = useParams();
  return <UploadPage projectId={projectId} />;
}

function VerificationWrapper() {
  const { projectId } = useParams();
  return <VerificationPage projectId={projectId} />;
}

function AIChatWrapper() {
  const { projectId } = useParams();
  return <AIChatPage projectId={projectId} />;
}

function DeliverablesWrapper() {
  const { projectId } = useParams();
  return <DeliverablesPage projectId={projectId} />;
}

function ReportsWrapper() {
  const { projectId } = useParams();
  return <ReportsPage projectId={projectId} />;
}

function TaskDetailWrapper() {
  const { taskId } = useParams();
  return <TaskDetailPage taskId={taskId} />;
}

function ClientProjectsWrapper() {
  const { projectId } = useParams();
  return <ClientProjectsPage projectId={projectId} />;
}

function ClientChatWrapper() {
  const { projectId } = useParams();
  return <ClientChatPage projectId={projectId} />;
}

function ClientDownloadsWrapper() {
  const { projectId } = useParams();
  return <ClientDownloads projectId={projectId} />;
}

// ─────────────────────────────────────────────────────────────
// Main App
// ─────────────────────────────────────────────────────────────
export default function App() {
  const { user, authReady } = useAuth();

  if (!authReady) return null;

  return (
    <BrowserRouter>
      <Routes>
        {/* ── Public / Auth ─────────────────────────────────── */}
        <Route
          path="/login"
          element={user ? <RoleHome /> : <AuthScreens />}
        />
        <Route
          path="/signup"
          element={user ? <RoleHome /> : <AuthScreens />}
        />
        <Route path="/" element={<Navigate to={user ? "/" : "/login"} replace />} />

        {/* ── Admin routes ──────────────────────────────────── */}
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/projects"
          element={
            <RequireAdmin>
              <AppLayout>
                <ProjectsPage />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/projects/:projectId"
          element={
            <RequireAdmin>
              <AppLayout>
                <ProjectDetailWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/projects/:projectId/upload"
          element={
            <RequireAdmin>
              <AppLayout>
                <UploadWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/projects/:projectId/verification"
          element={
            <RequireAdmin>
              <AppLayout>
                <VerificationWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/projects/:projectId/ai-chat"
          element={
            <RequireAdmin>
              <AppLayout>
                <AIChatWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/projects/:projectId/deliverables"
          element={
            <RequireAdmin>
              <AppLayout>
                <DeliverablesWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/projects/:projectId/reports"
          element={
            <RequireAdmin>
              <AppLayout>
                <ReportsWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/tasks"
          element={
            <RequireAdmin>
              <AppLayout>
                <TasksPage />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/tasks/:taskId"
          element={
            <RequireAdmin>
              <AppLayout>
                <TaskDetailWrapper />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/users"
          element={
            <RequireAdmin>
              <AppLayout>
                <UsersPage />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/teams"
          element={
            <RequireAdmin>
              <AppLayout>
                <TeamsDepartmentsPage />
              </AppLayout>
            </RequireAdmin>
          }
        />
        <Route
          path="/roles"
          element={
            <RequireAdmin>
              <AppLayout>
                <RolesPage />
              </AppLayout>
            </RequireAdmin>
          }
        />

        {/* ── Client routes ─────────────────────────────────── */}
        <Route
          path="/client-dashboard"
          element={
            <RequireAuth>
              <AppLayout>
                <ClientDashboard />
              </AppLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/client-projects"
          element={
            <RequireAuth>
              <AppLayout>
                <ClientProjectsPage />
              </AppLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/client-projects/:projectId"
          element={
            <RequireAuth>
              <AppLayout>
                <ClientProjectsWrapper />
              </AppLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/client-projects/:projectId/chat"
          element={
            <RequireAuth>
              <AppLayout>
                <ClientChatWrapper />
              </AppLayout>
            </RequireAuth>
          }
        />
        <Route
          path="/client-projects/:projectId/downloads"
          element={
            <RequireAuth>
              <AppLayout>
                <ClientDownloadsWrapper />
              </AppLayout>
            </RequireAuth>
          }
        />

        {/* Fallback → role home */}
        <Route path="*" element={<RoleHome />} />
      </Routes>
    </BrowserRouter>
  );
}