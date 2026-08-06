import React, { useState, useEffect } from "react";
import { projectService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";

const STATUS_COLORS = {
  DISCOVERY: "bg-blue-100 text-blue-700",
  VERIFICATION: "bg-amber-100 text-amber-700",
  PROCESSING: "bg-purple-100 text-purple-700",
  REVIEW: "bg-indigo-100 text-indigo-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
};

const INDUSTRY_OPTIONS = [
  "Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
  "Education", "Energy", "Telecommunications", "Government", "Other",
];

export default function ProjectsPage({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [form, setForm] = useState({
    company_name: "", industry: "", project_name: "", objectives: "",
    team_members: "", expected_timeline: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("ALL");

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      if (editingProject) {
        await projectService.update(editingProject.id, form);
      } else {
        await projectService.create(form);
      }
      setShowCreate(false);
      setEditingProject(null);
      resetForm();
      fetchProjects();
    } catch (err) {
      setFormError(getApiError(err, "Failed to save project."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this project?")) return;
    try {
      await projectService.delete(id);
      fetchProjects();
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
  };

  const handleEdit = (project) => {
    setForm({
      company_name: project.company_name || "",
      industry: project.industry || "",
      project_name: project.project_name || "",
      objectives: project.objectives || "",
      team_members: project.team_members || "",
      expected_timeline: project.expected_timeline || "",
    });
    setEditingProject(project);
    setShowCreate(true);
    setFormError(null);
  };

  const resetForm = () => {
    setForm({ company_name: "", industry: "", project_name: "", objectives: "", team_members: "", expected_timeline: "" });
  };

  const filtered = projects.filter((p) => {
    const matchesSearch = !search || p.project_name?.toLowerCase().includes(search.toLowerCase()) || p.company_name?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = filterStatus === "ALL" || p.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <TopHeader
        title="Projects"
        subtitle="Manage consulting engagements"
        actions={
          <button
            onClick={() => { resetForm(); setEditingProject(null); setShowCreate(true); }}
            className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            New Project
          </button>
        }
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary"
        >
          <option value="ALL">All Status</option>
          <option value="DISCOVERY">Discovery</option>
          <option value="VERIFICATION">Verification</option>
          <option value="PROCESSING">Processing</option>
          <option value="REVIEW">Review</option>
          <option value="COMPLETED">Completed</option>
        </select>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-16 text-center">
          <span className="material-symbols-outlined text-[48px] text-outline-variant">folder_open</span>
          <p className="text-on-surface-variant mt-3 text-sm">No projects found</p>
          <button
            onClick={() => { resetForm(); setEditingProject(null); setShowCreate(true); }}
            className="mt-4 px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium hover:opacity-90"
          >
            Create your first project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5 hover:shadow-md transition-shadow cursor-pointer group"
              onClick={() => onSelectProject(project.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary">folder</span>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleEdit(project); }}
                    className="p-1.5 rounded-lg hover:bg-surface-container transition-colors"
                  >
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(project.id); }}
                    className="p-1.5 rounded-lg hover:bg-red-50 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                  </button>
                </div>
              </div>
              <h3 className="font-semibold text-on-surface text-sm">{project.project_name}</h3>
              <p className="text-xs text-on-surface-variant mt-0.5">{project.company_name}</p>
              {project.industry && (
                <span className="inline-block mt-2 px-2 py-0.5 bg-surface-container rounded text-[10px] text-on-surface-variant font-medium">
                  {project.industry}
                </span>
              )}
              <div className="mt-4 flex items-center justify-between">
                <span className={`px-2 py-1 rounded text-[10px] font-bold ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"}`}>
                  {project.status}
                </span>
                {project.readiness_score != null && (
                  <span className="text-xs text-on-surface-variant">
                    {project.readiness_score}% ready
                  </span>
                )}
              </div>
              {project.readiness_score != null && (
                <div className="w-full h-1.5 bg-surface-container rounded-full mt-2 overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${project.readiness_score}%` }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto soft-shadow">
            <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
              <h3 className="font-headline-lg text-lg font-bold text-on-surface">
                {editingProject ? "Edit Project" : "New Project"}
              </h3>
              <button
                onClick={() => { setShowCreate(false); setEditingProject(null); setFormError(null); }}
                className="p-2 rounded-lg hover:bg-surface-container transition-colors"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{formError}</span>
                </div>
              )}
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Company Name *
                </label>
                <input
                  type="text"
                  required
                  value={form.company_name}
                  onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                  placeholder="e.g. Acme Corp"
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Project Name *
                </label>
                <input
                  type="text"
                  required
                  value={form.project_name}
                  onChange={(e) => setForm({ ...form, project_name: e.target.value })}
                  placeholder="e.g. Digital Transformation Initiative"
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Industry
                </label>
                <select
                  value={form.industry}
                  onChange={(e) => setForm({ ...form, industry: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                >
                  <option value="">Select industry</option>
                  {INDUSTRY_OPTIONS.map((ind) => (
                    <option key={ind} value={ind}>{ind}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Objectives
                </label>
                <textarea
                  value={form.objectives}
                  onChange={(e) => setForm({ ...form, objectives: e.target.value })}
                  placeholder="Describe the project objectives..."
                  rows={3}
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 resize-none"
                />
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Team Members
                </label>
                <input
                  type="text"
                  value={form.team_members}
                  onChange={(e) => setForm({ ...form, team_members: e.target.value })}
                  placeholder="Comma-separated names"
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                  Expected Timeline
                </label>
                <input
                  type="text"
                  value={form.expected_timeline}
                  onChange={(e) => setForm({ ...form, expected_timeline: e.target.value })}
                  placeholder="e.g. 12 weeks"
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => { setShowCreate(false); setEditingProject(null); setFormError(null); }}
                  className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50"
                >
                  {submitting ? "Saving..." : editingProject ? "Update Project" : "Create Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
