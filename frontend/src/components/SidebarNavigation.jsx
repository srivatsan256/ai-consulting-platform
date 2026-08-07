import React from "react";

const roleBasedNavItems = {
  // Super Admin
  super_admin: [
    { id: "dashboard", label: "Platform Dashboard", icon: "dashboard" },
    { id: "projects", label: "All Projects", icon: "folder_open" },
    { id: "tasks", label: "Tasks", icon: "checklist" },
    { id: "users", label: "Users", icon: "group" },
    { id: "teams", label: "Teams & Departments", icon: "account_tree" },
    { id: "roles", label: "Roles & Permissions", icon: "admin_panel_settings" },
  ],
  // Company Admin
  company_admin: [
    { id: "dashboard", label: "Company Dashboard", icon: "dashboard" },
    { id: "projects", label: "Projects", icon: "folder_open" },
    { id: "tasks", label: "Tasks", icon: "checklist" },
    { id: "users", label: "Users", icon: "group" },
    { id: "teams", label: "Teams & Departments", icon: "account_tree" },
    { id: "roles", label: "Roles & Permissions", icon: "admin_panel_settings" },
    { id: "reports", label: "Company Reports", icon: "assessment" },
  ],
  // Project Manager
  project_manager: [
    { id: "dashboard", label: "Project Dashboard", icon: "dashboard" },
    { id: "projects", label: "Projects", icon: "folder_open" },
    { id: "tasks", label: "Tasks", icon: "checklist" },
    { id: "upload", label: "Upload Documents", icon: "upload_file" },
    { id: "verification", label: "Verification", icon: "verified" },
    { id: "deliverables", label: "Deliverables", icon: "assignment_turned_in" },
  ],
  // Business Analyst
  business_analyst: [
    { id: "dashboard", label: "Discovery Dashboard", icon: "dashboard" },
    { id: "upload", label: "Upload Documents", icon: "upload_file" },
    { id: "verification", label: "AI Validation", icon: "smart_toy" },
    { id: "reports", label: "Readiness Score", icon: "assessment" },
  ],
  // Solution Architect
  solution_architect: [
    { id: "dashboard", label: "Architecture Dashboard", icon: "dashboard" },
    { id: "upload", label: "Upload Architecture", icon: "upload_file" },
    { id: "verification", label: "Review Documents", icon: "rate_review" },
    { id: "reports", label: "Technical Reports", icon: "assessment" },
  ],
  // AI/ML Engineer
  ai_ml_engineer: [
    { id: "dashboard", label: "AI Dashboard", icon: "dashboard" },
    { id: "upload", label: "Configure Models", icon: "upload_file" },
    { id: "verification", label: "Validation Results", icon: "verified" },
    { id: "reports", label: "AI Logs", icon: "assessment" },
  ],
  // Backend Developer
  backend_developer: [
    { id: "dashboard", label: "Development Dashboard", icon: "dashboard" },
    { id: "upload", label: "API Documentation", icon: "upload_file" },
    { id: "projects", label: "Technical Docs", icon: "folder_open" },
  ],
  // Frontend Developer
  frontend_developer: [
    { id: "dashboard", label: "UI Dashboard", icon: "dashboard" },
    { id: "upload", label: "Design Files", icon: "upload_file" },
    { id: "projects", label: "UI Documents", icon: "folder_open" },
  ],
  // QA/Test Engineer
  qa_test_engineer: [
    { id: "dashboard", label: "QA Dashboard", icon: "dashboard" },
    { id: "upload", label: "Upload Test Cases", icon: "upload_file" },
    { id: "verification", label: "Verify Requirements", icon: "verified" },
    { id: "reports", label: "Test Reports", icon: "assessment" },
  ],
  // Security Consultant
  security_consultant: [
    { id: "dashboard", label: "Security Dashboard", icon: "dashboard" },
    { id: "upload", label: "Security Reports", icon: "upload_file" },
    { id: "verification", label: "Compliance Review", icon: "verified" },
    { id: "reports", label: "Risk Assessment", icon: "assessment" },
  ],
  // DevOps Engineer
  devops_engineer: [
    { id: "dashboard", label: "DevOps Dashboard", icon: "dashboard" },
    { id: "upload", label: "Deployment Docs", icon: "upload_file" },
    { id: "projects", label: "Infrastructure", icon: "folder_open" },
  ],
  // Document Reviewer
  document_reviewer: [
    { id: "dashboard", label: "Review Dashboard", icon: "dashboard" },
    { id: "verification", label: "Review Documents", icon: "rate_review" },
    { id: "reports", label: "Comments", icon: "comment" },
  ],
  // Client Admin
  client_admin: [
    { id: "client-dashboard", label: "Client Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "My Projects", icon: "folder_open" },
    { id: "upload", label: "Upload Documents", icon: "upload_file" },
    { id: "client-chat", label: "AI Assistant", icon: "smart_toy" },
    { id: "client-downloads", label: "Downloads", icon: "download" },
  ],
  // Client SME
  client_sme: [
    { id: "client-dashboard", label: "Department Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "My Projects", icon: "folder_open" },
    { id: "upload", label: "Upload SOPs", icon: "upload_file" },
    { id: "client-chat", label: "AI Assistant", icon: "smart_toy" },
  ],
  // Client Reviewer
  client_reviewer: [
    { id: "client-dashboard", label: "Review Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "Projects", icon: "folder_open" },
    { id: "verification", label: "Review Documents", icon: "rate_review" },
    { id: "client-downloads", label: "Downloads", icon: "download" },
  ],
  // Business Sponsor
  business_sponsor: [
    { id: "client-dashboard", label: "Executive Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "Projects", icon: "folder_open" },
    { id: "reports", label: "Milestone Status", icon: "assessment" },
    { id: "client-downloads", label: "Downloads", icon: "download" },
  ],
  // Viewer
  viewer: [
    { id: "client-dashboard", label: "Read-Only Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "View Projects", icon: "folder_open" },
    { id: "client-downloads", label: "View Reports", icon: "download" },
  ],
};

const defaultAdminNav = [
  { id: "dashboard", label: "Dashboard", icon: "dashboard" },
  { id: "projects", label: "Projects", icon: "folder_open" },
];

const defaultClientNav = [
  { id: "client-dashboard", label: "Dashboard", icon: "dashboard" },
  { id: "client-projects", label: "My Projects", icon: "folder_open" },
  { id: "client-chat", label: "AI Assistant", icon: "smart_toy" },
  { id: "client-downloads", label: "Downloads", icon: "download" },
];

export default function SidebarNavigation({ activeView, setActiveView, role, user, onLogout, onNavigate }) {
  const assignedRole = user?.assigned_role;
  const roleKey = user?.role_key || (assignedRole
    ? assignedRole
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "_")
        .replace(/_+/g, "_")
        .replace(/^_|_$/g, "")
    : null);

  let navItems = role === "admin" ? defaultAdminNav : defaultClientNav;
  if (roleKey && roleBasedNavItems[roleKey]) {
    navItems = roleBasedNavItems[roleKey];
  }

  const getRoleIcon = () => {
    if (!assignedRole) return role === "admin" ? "admin_panel_settings" : "business";

    const iconMap = {
      "Super Admin": "admin_panel_settings",
      "Company Admin": "corporate_fare",
      "Project Manager": "project",
      "Business Analyst": "analytics",
      "Solution Architect": "architecture",
      "AI/ML Engineer": "psychology",
      "Backend Developer": "code",
      "Frontend Developer": "web",
      "QA / Test Engineer": "bug_report",
      "Security Consultant": "shield",
      "DevOps Engineer": "cloud",
      "Document Reviewer": "rate_review",
      "Client Admin": "business",
      "Client Department Owner (SME)": "account_tree",
      "Client Reviewer": "fact_check",
      "Business Sponsor": "workspace_premium",
      "Viewer": "visibility",
    };

    return iconMap[assignedRole] || (role === "admin" ? "admin_panel_settings" : "business");
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-[240px] bg-on-surface flex flex-col border-r border-outline-variant/30 z-50 select-none">
      {/* Brand Header */}
      <div className="p-6">
        <h1 className="font-display-lg text-[24px] font-bold text-surface-bright tracking-tight">
          RequirementAI
        </h1>
        <p className="text-outline-variant font-label-md text-[10px] mt-1 uppercase tracking-widest">
          {user?.dashboard_name || (role === "admin" ? "Consultant Portal" : "Client Portal")}
        </p>
      </div>

      {/* Role Badge */}
      <div className="mx-4 mb-4 px-3 py-2 rounded-lg bg-surface-container-highest/10 border border-outline-variant/20">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary-fixed text-[18px]">
            {getRoleIcon()}
          </span>
          <div className="min-w-0">
            <p className="text-surface-bright text-xs font-bold truncate">{user?.name || "User"}</p>
            <p className="text-outline-variant text-[10px] truncate">{user?.assigned_role || user?.email}</p>
          </div>
        </div>
        {user?.company && (
          <div className="mt-2 pt-2 border-t border-outline-variant/20">
            <p className="text-outline-variant text-[10px] truncate">{user.company}</p>
          </div>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-2 space-y-1">
        <p className="px-4 pt-2 pb-1 text-outline-variant font-label-md text-[10px] uppercase tracking-widest">
          Navigation
        </p>
        {navItems.map((item) => {
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                if (onNavigate) onNavigate(item.id);
                else if (setActiveView) setActiveView(item.id);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 transition-colors duration-200 ${
                isActive
                  ? "bg-surface-container-highest/10 border-l-2 border-primary text-surface-bright font-bold"
                  : "text-outline-variant hover:text-surface-bright hover:bg-surface-container-highest/5 border-l-2 border-transparent"
              }`}
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="font-body-md text-[13px]">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Access Checklist */}
      {user?.access_checklist && user.access_checklist.length > 0 && (
        <div className="mx-4 mb-4 p-3 rounded-lg bg-surface-container-highest/5 border border-outline-variant/20">
          <p className="text-outline-variant font-label-md text-[10px] uppercase tracking-widest mb-2">
            Your Access
          </p>
          <div className="space-y-1">
            {user.access_checklist.slice(0, 4).map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="material-symbols-outlined text-emerald-400 text-[12px]">check_circle</span>
                <span className="text-outline-variant text-[10px]">{item}</span>
              </div>
            ))}
            {user.access_checklist.length > 4 && (
              <p className="text-primary text-[10px] pl-5">
                +{user.access_checklist.length - 4} more
              </p>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-auto p-4 space-y-2">
        {user?.permissions?.upload && (
          <button
            onClick={() => setActiveView("upload")}
            className="w-full py-3 px-4 bg-primary text-on-primary rounded-xl font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-primary/20"
          >
            <span className="material-symbols-outlined text-[18px]">upload_file</span>
            Upload Document
          </button>
        )}
        <div className="pt-3 border-t border-outline-variant/20">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-outline-variant hover:text-surface-bright transition-colors rounded-lg hover:bg-surface-container-highest/5"
          >
            <span className="material-symbols-outlined text-[20px]">logout</span>
            <span className="font-body-md text-[13px]">Sign Out</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
