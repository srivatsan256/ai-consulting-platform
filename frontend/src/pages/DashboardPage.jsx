import React, { useEffect, useMemo, useState } from 'react';
import { projectService } from '../services/api';
import "../styles/pages/DashboardPage.css";

function formatDate(value) {
  if (!value) return 'N/A';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'N/A' : date.toLocaleDateString();
}

function getStatusTone(status) {
  if (status === 'COMPLETED') return 'bg-emerald-50 text-emerald-700';
  if (status === 'PROCESSING') return 'bg-purple-50 text-purple-700';
  if (status === 'VERIFICATION') return 'bg-amber-50 text-amber-700';
  if (status === 'REVIEW') return 'bg-indigo-50 text-indigo-700';
  return 'bg-blue-50 text-blue-700';
}


export default function DashboardPage({ user, onOpenProject, onNewProject, onViewAllProjects, onOpenPainAreas }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchProjects = async () => {
      try {
        const res = await projectService.list();
        if (!mounted) return;
        setProjects(res.data.results || res.data || []);
      } catch (err) {
        console.error('Failed to fetch projects:', err);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchProjects();
    return () => {
      mounted = false;
    };
  }, []);

  const stats = useMemo(() => {
    const total = projects.length;
    const completed = projects.filter((p) => p.status === 'COMPLETED').length;
    const verification = projects.filter((p) => p.status === 'VERIFICATION').length;
    const avgReadiness = total
      ? Math.round(projects.reduce((sum, p) => sum + (Number(p.readiness_score) || 0), 0) / total)
      : 0;

    return [
      { label: 'Active Projects', value: String(total), change: `${completed} completed`, icon: 'folder_open', color: 'bg-primary/10 text-primary' },
      { label: 'Avg. Readiness', value: `${avgReadiness}%`, change: `${verification} in verification`, icon: 'trending_up', color: 'bg-emerald-50 text-emerald-600' },
      { label: 'Completed', value: String(completed), change: `${total ? Math.round((completed / total) * 100) : 0}% of portfolio`, icon: 'check_circle', color: 'bg-blue-50 text-blue-600' },
      { label: 'Pending Review', value: String(verification), change: 'Needs verification', icon: 'verified_user', color: 'bg-amber-50 text-amber-600' },
    ];
  }, [projects]);

  const recentProjects = useMemo(
    () => [...projects].sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)).slice(0, 4),
    [projects],
  );

  const activity = useMemo(() => {
    const sorted = [...projects].sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at));
    return sorted.slice(0, 4).map((project, index) => ({
      icon: index === 0 ? 'check_circle' : index === 1 ? 'smart_toy' : 'folder_open',
      text: `${project.project_name} is ${project.status?.toLowerCase() || 'in progress'} at level ${Math.max(1, project.current_level || 1)}`,
      time: formatDate(project.updated_at || project.created_at),
      color: index === 0 ? 'text-emerald-500' : index === 1 ? 'text-primary' : 'text-blue-500',
    }));
  }, [projects]);

  return (
    <div className="space-y-8">
      <div className="dash-header">
        <div>
          <span className="dash-eyebrow">Overview</span>
          <h2 className="dash-title">
            {user?.dashboard_name || "Consultant Dashboard"}
          </h2>
          <p className="dash-subtitle">
            {user?.assigned_role
              ? `Welcome back, ${user.name?.split(" ")[0] || "User"}. Here's your ${user.dashboard_name || "dashboard"}.`
              : "Live portfolio overview from backend projects and verification status."}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenPainAreas}
            className="dash-pain-areas-btn"
            title="Open AI Intervention Pain Areas Tracker"
          >
            <span className="material-symbols-outlined text-[18px]">healing</span>
            Pain Areas Tracker
          </button>
          <button
            onClick={onNewProject}
            className="dash-new-btn"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            New Project
          </button>
        </div>
      </div>

      <div className="dash-stats-grid">
        {stats.map((stat) => (
          <div key={stat.label} className="dash-stat-card soft-shadow">
            <div className="flex items-start justify-between">
              <div className={`dash-stat-icon ${stat.color}`}>
                <span className="material-symbols-outlined">{stat.icon}</span>
              </div>
            </div>
            <p className="dash-stat-value">{loading ? '...' : stat.value}</p>
            <p className="dash-stat-label">{stat.label}</p>
            <p className="dash-stat-change">{stat.change}</p>
          </div>
        ))}
      </div>

      <div className="dash-grid">
        <div className="dash-projects-card soft-shadow">
          <div className="dash-card-header">
            <h3 className="dash-section-title">Recent Projects</h3>
            <button onClick={onViewAllProjects} className="dash-view-all">
              View all
            </button>
          </div>
          <div className="dash-project-list">
            {recentProjects.length > 0 ? recentProjects.map((project) => (
              <button
                key={project.id}
                onClick={() => onOpenProject(project.id)}
                className="dash-project-row"
              >
                <div className="dash-project-icon">
                  <span className="material-symbols-outlined text-primary">folder</span>
                </div>
                <div className="dash-project-info">
                  <p className="dash-project-name">{project.project_name}</p>
                  <p className="dash-project-meta">{project.company_name} · Level {Math.max(1, project.current_level || 1)}</p>
                </div>
                <div className="dash-project-side">
                  <span className={`dash-status-badge ${getStatusTone(project.status)}`}>
                    {project.status}
                  </span>
                  <div className="dash-progress-track">
                    <div className="dash-progress-fill" style={{ width: `${Math.max(0, Math.min(100, Number(project.readiness_score) || 0))}%` }} />
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline-variant">chevron_right</span>
              </button>
            )) : (
              <div className="dash-projects-empty">No projects yet. Create one to start.</div>
            )}
          </div>
        </div>

        <div className="dash-activity-card soft-shadow">
          <h3 className="dash-activity-title">Recent Activity</h3>
          <ul className="space-y-4">
            {activity.length > 0 ? activity.map((item, i) => (
              <li key={i} className="flex gap-3">
                <span className={`material-symbols-outlined dash-activity-icon ${item.color}`} style={{ fontVariationSettings: "'FILL' 1" }}>
                  {item.icon}
                </span>
                <div>
                  <p className="dash-activity-text">{item.text}</p>
                  <p className="dash-activity-time">{item.time}</p>
                </div>
              </li>
            )) : (
              <li className="dash-activity-empty">No recent activity yet.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
