import React from "react";

const roleBasedNavItems = {
  super_admin: [
    { id: "dashboard", label: "Platform Dashboard", icon: "dashboard" },
    { id: "projects", label: "All Projects", icon: "folder_open" },
    { id: "tasks", label: "Tasks", icon: "checklist" },
    { id: "files", label: "File Management", icon: "folder_managed" },
    { id: "workflows", label: "Workflows", icon: "account_tree" },
    { id: "users", label: "Users", icon: "group" },
    { id: "teams", label: "Teams & Departments", icon: "account_tree" },
    { id: "roles", label: "Roles & Permissions", icon: "admin_panel_settings" },
  ],
  company_admin: [
    { id: "dashboard", label: "Company Dashboard", icon: "dashboard" },
    { id: "projects", label: "Projects", icon: "folder_open" },
    { id: "tasks", label: "Tasks", icon: "checklist" },
    { id: "files", label: "File Management", icon: "folder_managed" },
    { id: "workflows", label: "Workflows", icon: "account_tree" },
    { id: "users", label: "Users", icon: "group" },
    { id: "teams", label: "Teams & Departments", icon: "account_tree" },
    { id: "roles", label: "Roles & Permissions", icon: "admin_panel_settings" },
    { id: "reports", label: "Company Reports", icon: "assessment" },
  ],
  project_manager: [
    { id: "dashboard", label: "Project Dashboard", icon: "dashboard" },
    { id: "projects", label: "Projects", icon: "folder_open" },
    { id: "tasks", label: "Tasks", icon: "checklist" },
    { id: "upload", label: "Upload Documents", icon: "upload_file" },
    { id: "verification", label: "Verification", icon: "verified" },
    { id: "deliverables", label: "Deliverables", icon: "assignment_turned_in" },
    { id: "files", label: "File Management", icon: "folder_managed" },
    { id: "workflows", label: "Workflows", icon: "account_tree" },
  ],
  business_analyst: [
    { id: "dashboard", label: "Discovery Dashboard", icon: "dashboard" },
    { id: "upload", label: "Upload Documents", icon: "upload_file" },
    { id: "verification", label: "AI Validation", icon: "smart_toy" },
    { id: "reports", label: "Readiness Score", icon: "assessment" },
  ],
  solution_architect: [
    { id: "dashboard", label: "Architecture Dashboard", icon: "dashboard" },
    { id: "upload", label: "Upload Architecture", icon: "upload_file" },
    { id: "verification", label: "Review Documents", icon: "rate_review" },
    { id: "reports", label: "Technical Reports", icon: "assessment" },
  ],
  ai_ml_engineer: [
    { id: "dashboard", label: "AI Dashboard", icon: "dashboard" },
    { id: "upload", label: "Configure Models", icon: "upload_file" },
    { id: "verification", label: "Validation Results", icon: "verified" },
    { id: "reports", label: "AI Logs", icon: "assessment" },
  ],
  backend_developer: [
    { id: "dashboard", label: "Development Dashboard", icon: "dashboard" },
    { id: "upload", label: "API Documentation", icon: "upload_file" },
    { id: "projects", label: "Technical Docs", icon: "folder_open" },
  ],
  frontend_developer: [
    { id: "dashboard", label: "UI Dashboard", icon: "dashboard" },
    { id: "upload", label: "Design Files", icon: "upload_file" },
    { id: "projects", label: "UI Documents", icon: "folder_open" },
  ],
  qa_test_engineer: [
    { id: "dashboard", label: "QA Dashboard", icon: "dashboard" },
    { id: "upload", label: "Upload Test Cases", icon: "upload_file" },
    { id: "verification", label: "Verify Requirements", icon: "verified" },
    { id: "reports", label: "Test Reports", icon: "assessment" },
  ],
  security_consultant: [
    { id: "dashboard", label: "Security Dashboard", icon: "dashboard" },
    { id: "upload", label: "Security Reports", icon: "upload_file" },
    { id: "verification", label: "Compliance Review", icon: "verified" },
    { id: "reports", label: "Risk Assessment", icon: "assessment" },
  ],
  devops_engineer: [
    { id: "dashboard", label: "DevOps Dashboard", icon: "dashboard" },
    { id: "upload", label: "Deployment Docs", icon: "upload_file" },
    { id: "projects", label: "Infrastructure", icon: "folder_open" },
  ],
  document_reviewer: [
    { id: "dashboard", label: "Review Dashboard", icon: "dashboard" },
    { id: "verification", label: "Review Documents", icon: "rate_review" },
    { id: "reports", label: "Comments", icon: "comment" },
  ],
  client_admin: [
    { id: "client-dashboard", label: "Client Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "My Projects", icon: "folder_open" },
    { id: "upload", label: "Upload Documents", icon: "upload_file" },
    { id: "client-chat", label: "AI Assistant", icon: "smart_toy" },
    { id: "client-downloads", label: "Downloads", icon: "download" },
  ],
  client_sme: [
    { id: "client-dashboard", label: "Department Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "My Projects", icon: "folder_open" },
    { id: "upload", label: "Upload SOPs", icon: "upload_file" },
    { id: "client-chat", label: "AI Assistant", icon: "smart_toy" },
  ],
  client_reviewer: [
    { id: "client-dashboard", label: "Review Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "Projects", icon: "folder_open" },
    { id: "verification", label: "Review Documents", icon: "rate_review" },
    { id: "client-downloads", label: "Downloads", icon: "download" },
  ],
  business_sponsor: [
    { id: "client-dashboard", label: "Executive Dashboard", icon: "dashboard" },
    { id: "client-projects", label: "Projects", icon: "folder_open" },
    { id: "reports", label: "Milestone Status", icon: "assessment" },
    { id: "client-downloads", label: "Downloads", icon: "download" },
  ],
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
        .replace(/^_+|_+$/g, "")
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
    <aside className="w-64 flex flex-col bg-[#0b0f19] border-r border-[#1e293b]/40 text-slate-200">
      {/* Brand Header */}
      <div className="p-4 flex flex-col gap-1">
        <h1 className="text-white font-bold text-base">RequirementAI</h1>
        <p className="text-slate-400 text-xs">
          {user?.dashboard_name || (role === "admin" ? "Consultant Portal" : "Client Portal")}
        </p>
      </div>

      {/* Role Badge */}
      <div className="mx-4 mb-4 px-3 py-2 rounded-lg bg-[#1e293b]/40 border border-[#1e293b]/60">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-indigo-400 text-[18px]">
            {getRoleIcon()}
          </span>
          <div className="min-w-0">
            <p className="text-white text-xs font-bold truncate">{user?.name || "User"}</p>
            <p className="text-slate-400 text-[10px] truncate">{user?.assigned_role || user?.email}</p>
          </div>
        </div>
        {user?.company && (
          <div className="mt-2 pt-2 border-t border-[#1e293b]/60">
            <p className="text-slate-400 text-[10px] truncate">{user.company}</p>
          </div>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-2 space-y-1 overflow-y-auto">
        <p className="px-4 pt-2 pb-1 text-slate-500 font-label-md text-[10px] uppercase tracking-widest">
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
                  ? "bg-[#1e293b]/60 border-l-2 border-indigo-500 text-white font-bold"
                  : "text-slate-400 hover:text-white hover:bg-[#1e293b]/30 border-l-2 border-transparent"
              }`}
            >
              <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
              <span className="font-body-md text-[13px]">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-auto p-4">
        <div className="pt-3 border-t border-[#1e293b]/60">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-[#1e293b]/30"
          >
            <span className="material-symbols-outlined text-[20px]">logout</span>
            <span className="font-body-md text-[13px]">Sign Out</span>
          </button>
        </div>
      </div>
    </aside>
  );
}