import React, { useState, useEffect } from "react";
import { projectService } from "../services/api";
import TopHeader from "../components/TopHeader";

const STATUS_COLORS = {
  DISCOVERY: "bg-blue-100 text-blue-700",
  VERIFICATION: "bg-amber-100 text-amber-700",
  PROCESSING: "bg-purple-100 text-purple-700",
  REVIEW: "bg-indigo-100 text-indigo-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
};

export default function ClientDashboard({ user, onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchProjects(); }, []);

  const fetchProjects = async () => {
    try {
      const res = await projectService.list();
      setProjects(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    } finally {
      setLoading(false);
    }
  };

  const completedCount = projects.filter((p) => p.status === "COMPLETED").length;
  const avgScore = projects.length
    ? Math.round(projects.reduce((sum, p) => sum + (p.readiness_score || 0), 0) / projects.length)
    : 0;
  const totalDocs = projects.reduce((sum, p) => sum + (p.documents?.length || 0), 0);

  return (
    <div className="space-y-6">
      <TopHeader
        title={user?.dashboard_name || "Client Dashboard"}
        subtitle={user?.assigned_role ? `${user.company || "Company"} • ${user.department || "Department"}` : "Project overview"}
      />

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-[22px]">folder_open</span>
            </div>
            <div>
              <p className="text-xl font-bold text-on-surface">{projects.length}</p>
              <p className="text-xs text-on-surface-variant">Total Projects</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-emerald-600 text-[22px]">check_circle</span>
            </div>
            <div>
              <p className="text-xl font-bold text-on-surface">{completedCount}</p>
              <p className="text-xs text-on-surface-variant">Completed</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-amber-600 text-[22px]">trending_up</span>
            </div>
            <div>
              <p className="text-xl font-bold text-on-surface">{avgScore}%</p>
              <p className="text-xs text-on-surface-variant">Avg. Readiness</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-blue-600 text-[22px]">description</span>
            </div>
            <div>
              <p className="text-xl font-bold text-on-surface">{totalDocs}</p>
              <p className="text-xs text-on-surface-variant">Documents</p>
            </div>
          </div>
        </div>
      </div>

      {/* Projects List */}
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
        <div className="p-6 border-b border-outline-variant/20">
          <h3 className="font-headline-sm text-base font-semibold text-on-surface">Your Projects</h3>
        </div>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-6 h-6 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <span className="material-symbols-outlined text-[48px] text-outline-variant">folder_open</span>
            <p className="text-on-surface-variant mt-3 text-sm">No projects assigned yet</p>
          </div>
        ) : (
          <div className="divide-y divide-outline-variant/10">
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => onSelectProject(project.id)}
                className="w-full p-5 flex items-center gap-4 hover:bg-surface-container-low transition-colors text-left"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-primary">folder</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-on-surface text-sm">{project.project_name}</p>
                  <p className="text-xs text-on-surface-variant">{project.company_name} · {project.industry || "General"}</p>
                </div>
                <div className="hidden sm:flex items-center gap-4 shrink-0">
                  {project.readiness_score != null && (
                    <div className="text-right">
                      <p className="text-xs text-on-surface-variant">Readiness</p>
                      <p className="text-sm font-bold text-on-surface">{project.readiness_score}%</p>
                    </div>
                  )}
                  <span className={`px-3 py-1.5 rounded-lg text-[10px] font-bold ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"}`}>
                    {project.status}
                  </span>
                </div>
                <span className="material-symbols-outlined text-outline-variant">chevron_right</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
