import React, { useEffect, useMemo, useState } from 'react';
import { projectService } from '../services/api';

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

export default function DashboardPage({ user, onOpenProject, onNewProject, onViewAllProjects }) {
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
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <span className="font-label-md text-primary uppercase tracking-tighter text-[11px]">Overview</span>
          <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-1">
            {user?.dashboard_name || "Consultant Dashboard"}
          </h2>
          <p className="text-on-surface-variant text-sm mt-1">
            {user?.assigned_role
              ? `Welcome back, ${user.name?.split(" ")[0] || "User"}. Here's your ${user.dashboard_name || "dashboard"}.`
              : "Live portfolio overview from backend projects and verification status."}
          </p>
        </div>
        <button
          onClick={onNewProject}
          className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20 self-start md:self-auto"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Project
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
            <div className="flex items-start justify-between">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.color}`}>
                <span className="material-symbols-outlined text-[22px]">{stat.icon}</span>
              </div>
            </div>
            <p className="font-headline-lg text-2xl font-bold text-on-surface mt-4">{loading ? '...' : stat.value}</p>
            <p className="text-on-surface-variant text-sm mt-0.5">{stat.label}</p>
            <p className="text-[11px] text-outline mt-2">{stat.change}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8 bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
          <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
            <h3 className="font-headline-sm text-base font-semibold text-on-surface">Recent Projects</h3>
            <button onClick={onViewAllProjects} className="text-primary text-sm font-medium hover:underline">
              View all
            </button>
          </div>
          <div className="divide-y divide-outline-variant/10">
            {recentProjects.length > 0 ? recentProjects.map((project) => (
              <button
                key={project.id}
                onClick={() => onOpenProject(project.id)}
                className="w-full p-5 flex items-center gap-4 hover:bg-surface-container-low transition-colors text-left"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-primary">folder</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-on-surface text-sm">{project.project_name}</p>
                  <p className="text-xs text-on-surface-variant">{project.company_name} · Level {Math.max(1, project.current_level || 1)}</p>
                </div>
                <div className="hidden sm:block text-right shrink-0">
                  <span className={`text-xs font-label-md px-2 py-1 rounded ${getStatusTone(project.status)}`}>
                    {project.status}
                  </span>
                  <div className="w-24 h-1.5 bg-surface-container rounded-full mt-2 overflow-hidden">
                    <div className="h-full bg-primary rounded-full" style={{ width: `${Math.max(0, Math.min(100, Number(project.readiness_score) || 0))}%` }} />
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline-variant">chevron_right</span>
              </button>
            )) : (
              <div className="p-8 text-center text-sm text-on-surface-variant">No projects yet. Create one to start.</div>
            )}
          </div>
        </div>

        <div className="col-span-12 lg:col-span-4 bg-white p-6 rounded-xl soft-shadow border border-outline-variant/20">
          <h3 className="font-headline-sm text-base font-semibold text-on-surface mb-5">Recent Activity</h3>
          <ul className="space-y-4">
            {activity.length > 0 ? activity.map((item, i) => (
              <li key={i} className="flex gap-3">
                <span className={`material-symbols-outlined text-[20px] shrink-0 ${item.color}`} style={{ fontVariationSettings: "'FILL' 1" }}>
                  {item.icon}
                </span>
                <div>
                  <p className="text-sm text-on-surface leading-snug">{item.text}</p>
                  <p className="text-[11px] text-outline mt-0.5">{item.time}</p>
                </div>
              </li>
            )) : (
              <li className="text-sm text-on-surface-variant">No recent activity yet.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
