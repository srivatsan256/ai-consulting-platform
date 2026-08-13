import React, { useEffect, useMemo, useState } from 'react';
import { projectService } from '../services/api';
import { useAuth } from '../context/AuthContext';
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

function featureLabel(code) {
  const labels = {
    custom_rag: 'Custom RAG',
    advanced_reports: 'Advanced Reports',
    custom_integrations: 'Custom Integrations',
  };
  return labels[code] || code.replace(/_/g, ' ');
}

function QuotaBar({ label, used, limit }) {
  const pct = limit > 0 ? Math.min(100, Math.round(((used || 0) / limit) * 100)) : 0;
  const nearLimit = pct >= 90;
  return (
    <div>
      <div className="dash-quota-row">
        <p className="dash-quota-label">{label}</p>
        <p className="dash-quota-value">
          {used ?? 0} / {limit}
        </p>
      </div>
      <div className="dash-quota-track">
        <div
          className={`dash-quota-fill ${nearLimit ? "bg-red-500" : "bg-primary"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function DashboardPage({ user, onOpenProject, onNewProject, onViewAllProjects, onOpenPainAreas }) {
  const { plan } = useAuth();
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

      {/* Plan & Usage */}
      <div className="dash-card soft-shadow">
        <div className="dash-card-header gap-4">
          <div>
            <span className="dash-eyebrow">Subscription</span>
            <h3 className="dash-card-title">
              Plan & Usage
            </h3>
          </div>
          {plan?.plan && (
            <span className="dash-plan-badge">
              {plan.plan}
            </span>
          )}
        </div>
        {plan ? (
          <div className="dash-plan-body">
            <div className="space-y-4">
              <QuotaBar
                label="Active Projects"
                used={projects.length}
                limit={(plan.quotas || []).find((q) => q.resource === "projects")?.limit}
              />
              <QuotaBar
                label="AI Requests / Month"
                used={(plan.usage || []).find((u) => u.feature === "ai_requests_per_month")?.quantity}
                limit={(plan.quotas || []).find((q) => q.resource === "ai_requests_per_month")?.limit}
              />
              <QuotaBar
                label="Team Members"
                used={(plan.quotas || []).find((q) => q.resource === "users")?.usage}
                limit={(plan.quotas || []).find((q) => q.resource === "users")?.limit}
              />
            </div>
            <div>
              <p className="dash-features-label">
                Enabled Features
              </p>
              {Object.keys(plan.features || {}).length > 0 ? (
                <div className="dash-feature-chips">
                  {Object.entries(plan.features)
                    .filter(([, enabled]) => enabled)
                    .map(([code]) => (
                      <span
                        key={code}
                        className="dash-feature-chip"
                      >
                        <span className="material-symbols-outlined text-[14px]">check_circle</span>
                        {featureLabel(code)}
                      </span>
                    ))}
                </div>
              ) : (
                <p className="dash-no-features">
                  No features enabled yet. Check your subscription plan.
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="dash-no-plan">
            <span className="material-symbols-outlined text-[20px] text-outline-variant">info</span>
            <div>
              <p className="dash-no-plan-title">No active plan found.</p>
              <p className="dash-no-plan-sub">
                Quotas and AI features are gated by your company's subscription plan.
              </p>
            </div>
          </div>
        )}
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
