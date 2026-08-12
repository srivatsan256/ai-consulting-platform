import React, { useState, useEffect } from "react";
import { projectService } from "../services/api";
import TopHeader from "../components/TopHeader";
import "./ClientDashboard.css";

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
      <div className="clientdash-stats-grid">
        <div className="clientdash-stat-card soft-shadow">
          <div className="clientdash-stat-row">
            <div className="clientdash-stat-icon-box">
              <span className="material-symbols-outlined clientdash-stat-icon">folder_open</span>
            </div>
            <div>
              <p className="clientdash-stat-value">{projects.length}</p>
              <p className="clientdash-stat-label">Total Projects</p>
            </div>
          </div>
        </div>
        <div className="clientdash-stat-card soft-shadow">
          <div className="clientdash-stat-row">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-emerald-600 text-[22px]">check_circle</span>
            </div>
            <div>
              <p className="clientdash-stat-value">{completedCount}</p>
              <p className="clientdash-stat-label">Completed</p>
            </div>
          </div>
        </div>
        <div className="clientdash-stat-card soft-shadow">
          <div className="clientdash-stat-row">
            <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-amber-600 text-[22px]">trending_up</span>
            </div>
            <div>
              <p className="clientdash-stat-value">{avgScore}%</p>
              <p className="clientdash-stat-label">Avg. Readiness</p>
            </div>
          </div>
        </div>
        <div className="clientdash-stat-card soft-shadow">
          <div className="clientdash-stat-row">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <span className="material-symbols-outlined text-blue-600 text-[22px]">description</span>
            </div>
            <div>
              <p className="clientdash-stat-value">{totalDocs}</p>
              <p className="clientdash-stat-label">Documents</p>
            </div>
          </div>
        </div>
      </div>

      {/* Projects List */}
      <div className="clientdash-list-card soft-shadow">
        <div className="clientdash-list-head">
          <h3 className="clientdash-list-title">Your Projects</h3>
        </div>
        {loading ? (
          <div className="clientdash-spinner-wrap">
            <div className="clientdash-spinner" />
          </div>
        ) : projects.length === 0 ? (
          <div className="clientdash-empty">
            <span className="material-symbols-outlined clientdash-empty-icon">folder_open</span>
            <p className="clientdash-empty-text">No projects assigned yet</p>
          </div>
        ) : (
          <div className="clientdash-list">
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => onSelectProject(project.id)}
                className="clientdash-row"
              >
                <div className="clientdash-row-icon-box">
                  <span className="material-symbols-outlined clientdash-row-icon">folder</span>
                </div>
                <div className="clientdash-row-info">
                  <p className="clientdash-row-title">{project.project_name}</p>
                  <p className="clientdash-row-sub">{project.company_name} · {project.industry || "General"}</p>
                </div>
                <div className="clientdash-row-right">
                  {project.readiness_score != null && (
                    <div className="text-right">
                      <p className="clientdash-row-meta">Readiness</p>
                      <p className="clientdash-row-value">{project.readiness_score}%</p>
                    </div>
                  )}
                  <span className={`clientdash-status-badge ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"}`}>
                    {project.status}
                  </span>
                </div>
                <span className="material-symbols-outlined clientdash-chevron">chevron_right</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
