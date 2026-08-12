import React, { useState, useEffect, useRef } from "react";
import { projectService, userService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";
import "./ProjectsPage.css";

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
    company_name: "",
    industry: "",
    project_name: "",
    objectives: [],       // array of strings
    team_members: [],     // array of user objects
    expected_timeline: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("ALL");

  // ===== Team Members (from DB) =====
  const [allUsers, setAllUsers] = useState([]);
  const [memberSearch, setMemberSearch] = useState("");
  const [showMemberDropdown, setShowMemberDropdown] = useState(false);
  const memberInputRef = useRef(null);

  // ===== Objectives (from Internet) =====
  const [objectiveSearch, setObjectiveSearch] = useState("");
  const [objectiveSuggestions, setObjectiveSuggestions] = useState([]);
  const [loadingObjectives, setLoadingObjectives] = useState(false);
  const [showObjectiveDropdown, setShowObjectiveDropdown] = useState(false);
  const objectiveInputRef = useRef(null);
  const objectiveDebounceRef = useRef(null);

  useEffect(() => {
    fetchProjects();
    fetchUsers();
  }, []);

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

  // Load team members from DB
  const fetchUsers = async () => {
    try {
      const res = await userService.list(); // adjust to your actual endpoint
      setAllUsers(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch users:", err);
      setAllUsers([]);
    }
  };

  // Load objective suggestions from Internet (backend uses web search / LLM)
  const fetchObjectiveSuggestions = async (query) => {
    if (!query || query.trim().length < 2) {
      setObjectiveSuggestions([]);
      return;
    }
    setLoadingObjectives(true);
    try {
      const params = new URLSearchParams({
        q: query.trim(),
        industry: form.industry || "",
        project: form.project_name || "",
        company: form.company_name || "",
      });
      // Backend endpoint that searches the internet / uses public data
      const res = await fetch(`/api/suggest-objectives?${params}`);
      const data = await res.json();
      setObjectiveSuggestions(data.suggestions || data.results || []);
    } catch (err) {
      console.error("Failed to fetch objective suggestions from internet:", err);
      setObjectiveSuggestions([]);
    } finally {
      setLoadingObjectives(false);
    }
  };

  const handleObjectiveSearchChange = (value) => {
    setObjectiveSearch(value);
    setShowObjectiveDropdown(true);
    if (objectiveDebounceRef.current) clearTimeout(objectiveDebounceRef.current);
    objectiveDebounceRef.current = setTimeout(() => {
      fetchObjectiveSuggestions(value);
    }, 350);
  };

  const addObjective = (text) => {
    const clean = (typeof text === "string" ? text : "").trim();
    if (!clean || form.objectives.includes(clean)) return;
    setForm((prev) => ({ ...prev, objectives: [...prev.objectives, clean] }));
    setObjectiveSearch("");
    setObjectiveSuggestions([]);
    setShowObjectiveDropdown(false);
    objectiveInputRef.current?.focus();
  };

  const removeObjective = (obj) => {
    setForm((prev) => ({
      ...prev,
      objectives: prev.objectives.filter((o) => o !== obj),
    }));
  };

  const handleObjectiveKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (objectiveSearch.trim()) addObjective(objectiveSearch);
    }
  };

  // Team member helpers
  const filteredUsers = allUsers.filter((u) => {
    const name = (u.name || u.full_name || u.email || "").toLowerCase();
    const matches = !memberSearch || name.includes(memberSearch.toLowerCase());
    const already = form.team_members.some((m) => m.id === u.id);
    return matches && !already;
  });

  const addTeamMember = (user) => {
    setForm((prev) => ({ ...prev, team_members: [...prev.team_members, user] }));
    setMemberSearch("");
    setShowMemberDropdown(false);
    memberInputRef.current?.focus();
  };

  const removeTeamMember = (userId) => {
    setForm((prev) => ({
      ...prev,
      team_members: prev.team_members.filter((m) => m.id !== userId),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      const payload = {
        ...form,
        team_members: form.team_members.map((u) => u.id), // send IDs
        objectives: form.objectives,                     // array of strings
      };
      if (editingProject) {
        await projectService.update(editingProject.id, payload);
      } else {
        await projectService.create(payload);
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
    // Team members from DB shape
    let members = [];
    if (Array.isArray(project.team_members)) {
      members = project.team_members.map((m) =>
        typeof m === "object"
          ? m
          : allUsers.find((u) => u.id === m) || { id: m, name: String(m) }
      );
    } else if (typeof project.team_members === "string" && project.team_members) {
      members = project.team_members.split(",").map((n) => ({
        id: n.trim(),
        name: n.trim(),
      }));
    }

    // Objectives (array or legacy string)
    let objectives = [];
    if (Array.isArray(project.objectives)) {
      objectives = project.objectives;
    } else if (typeof project.objectives === "string" && project.objectives) {
      objectives = project.objectives
        .split(/[;\n,]/)
        .map((s) => s.trim())
        .filter(Boolean);
    }

    setForm({
      company_name: project.company_name || "",
      industry: project.industry || "",
      project_name: project.project_name || "",
      objectives,
      team_members: members,
      expected_timeline: project.expected_timeline || "",
    });
    setEditingProject(project);
    setShowCreate(true);
    setFormError(null);
    setMemberSearch("");
    setObjectiveSearch("");
    setObjectiveSuggestions([]);
  };

  const resetForm = () => {
    setForm({
      company_name: "",
      industry: "",
      project_name: "",
      objectives: [],
      team_members: [],
      expected_timeline: "",
    });
    setMemberSearch("");
    setObjectiveSearch("");
    setObjectiveSuggestions([]);
  };

  const filtered = projects.filter((p) => {
    const matchesSearch =
      !search ||
      p.project_name?.toLowerCase().includes(search.toLowerCase()) ||
      p.company_name?.toLowerCase().includes(search.toLowerCase());
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
            onClick={() => {
              resetForm();
              setEditingProject(null);
              setShowCreate(true);
            }}
            className="projects-new-btn"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            New Project
          </button>
        }
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <span className="material-symbols-outlined projects-search-icon">
            search
          </span>
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="projects-search-input"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="projects-filter-select"
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
        <div className="projects-empty soft-shadow">
          <span className="material-symbols-outlined projects-empty-icon">folder_open</span>
          <p className="projects-empty-text">No projects found</p>
          <button
            onClick={() => {
              resetForm();
              setEditingProject(null);
              setShowCreate(true);
            }}
            className="projects-empty-btn"
          >
            Create your first project
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {filtered.map((project) => (
            <div
              key={project.id}
              className="projects-card group soft-shadow"
              onClick={() => onSelectProject(project.id)}
            >
              <div className="projects-card-header">
                <div className="projects-card-icon">
                  <span className="material-symbols-outlined text-primary">folder</span>
                </div>
                <div className="projects-card-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(project);
                    }}
                    className="projects-card-action"
                  >
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(project.id);
                    }}
                    className="projects-card-action-danger"
                  >
                    <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                  </button>
                </div>
              </div>
              <h3 className="projects-card-title">{project.project_name}</h3>
              <p className="projects-card-company">{project.company_name}</p>
              {project.industry && (
                <span className="projects-card-industry">
                  {project.industry}
                </span>
              )}
              <div className="projects-card-footer">
                <span
                  className={`projects-card-status ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"
                    }`}
                >
                  {project.status}
                </span>
                {project.readiness_score != null && (
                  <span className="projects-card-readiness">
                    {project.readiness_score}% ready
                  </span>
                )}
              </div>
              {project.readiness_score != null && (
                <div className="projects-card-progress">
                  <div
                    className="projects-card-progress-fill"
                    style={{ width: `${project.readiness_score}%` }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Modal */}
      {showCreate && (
        <div className="projects-modal-overlay">
          <div className="projects-modal-panel soft-shadow">
            <div className="projects-modal-header">
              <h3 className="projects-modal-title">
                {editingProject ? "Edit Project" : "New Project"}
              </h3>
              <button
                onClick={() => {
                  setShowCreate(false);
                  setEditingProject(null);
                  setFormError(null);
                }}
                className="projects-modal-close"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="projects-form">
              {formError && (
                <div className="projects-form-error">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{formError}</span>
                </div>
              )}

              {/* Company Name */}
              <div>
                <label className="projects-field-label">
                  Company Name *
                </label>
                <input
                  type="text"
                  required
                  value={form.company_name}
                  onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                  placeholder="e.g. Acme Corp"
                  className="projects-input"
                />
              </div>

              {/* Project Name */}
              <div>
                <label className="projects-field-label">
                  Project Name *
                </label>
                <input
                  type="text"
                  required
                  value={form.project_name}
                  onChange={(e) => setForm({ ...form, project_name: e.target.value })}
                  placeholder="e.g. Digital Transformation Initiative"
                  className="projects-input"
                />
              </div>

              {/* Industry */}
              <div>
                <label className="projects-field-label">
                  Industry
                </label>
                <select
                  value={form.industry}
                  onChange={(e) => setForm({ ...form, industry: e.target.value })}
                  className="projects-select"
                >
                  <option value="">Select industry</option>
                  {INDUSTRY_OPTIONS.map((ind) => (
                    <option key={ind} value={ind}>{ind}</option>
                  ))}
                </select>
              </div>

              {/* ========== OBJECTIVES (from Internet) ========== */}
              <div>
                <label className="projects-field-label">
                  Objectives
                </label>

                {/* Selected chips */}
                {form.objectives.length > 0 && (
                  <div className="projects-chips">
                    {form.objectives.map((obj) => (
                      <span
                        key={obj}
                        className="projects-chip"
                      >
                        {obj}
                        <button
                          type="button"
                          onClick={() => removeObjective(obj)}
                          className="projects-chip-remove"
                        >
                          <span className="material-symbols-outlined text-[14px]">close</span>
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {/* Search input – same style as Skill Set */}
                <div className="relative">
                  <input
                    ref={objectiveInputRef}
                    type="text"
                    value={objectiveSearch}
                    onChange={(e) => handleObjectiveSearchChange(e.target.value)}
                    onFocus={() => setShowObjectiveDropdown(true)}
                    onBlur={() => setTimeout(() => setShowObjectiveDropdown(false), 150)}
                    onKeyDown={handleObjectiveKeyDown}
                    placeholder="Search and add objectives"
                    className="projects-input"
                  />

                  {showObjectiveDropdown && (objectiveSearch || loadingObjectives) && (
                    <div className="projects-dropdown">
                      {loadingObjectives ? (
                        <div className="projects-dropdown-msg">
                          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                          Searching internet...
                        </div>
                      ) : objectiveSuggestions.length === 0 ? (
                        <div className="projects-dropdown-empty">
                          {objectiveSearch.length >= 2
                            ? "No suggestions found. Press Enter to add custom."
                            : "Type at least 2 characters"}
                        </div>
                      ) : (
                        objectiveSuggestions.map((sug) => (
                          <button
                            key={sug}
                            type="button"
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => addObjective(sug)}
                            className="projects-dropdown-option"
                          >
                            {sug}
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* ========== TEAM MEMBERS (from DB) ========== */}
              <div>
                <label className="projects-field-label">
                  Team Members
                </label>

                {/* Selected chips */}
                {form.team_members.length > 0 && (
                  <div className="projects-chips">
                    {form.team_members.map((member) => (
                      <span
                        key={member.id}
                        className="projects-chip"
                      >
                        {member.name || member.full_name || member.email}
                        <button
                          type="button"
                          onClick={() => removeTeamMember(member.id)}
                          className="projects-chip-remove"
                        >
                          <span className="material-symbols-outlined text-[14px]">close</span>
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {/* Search input – same style as Skill Set */}
                <div className="relative">
                  <input
                    ref={memberInputRef}
                    type="text"
                    value={memberSearch}
                    onChange={(e) => {
                      setMemberSearch(e.target.value);
                      setShowMemberDropdown(true);
                    }}
                    onFocus={() => setShowMemberDropdown(true)}
                    onBlur={() => setTimeout(() => setShowMemberDropdown(false), 150)}
                    placeholder="Search and add team members"
                    className="projects-input"
                  />

                  {showMemberDropdown && (
                    <div className="projects-dropdown">
                      {filteredUsers.length === 0 ? (
                        <div className="projects-dropdown-empty">
                          {memberSearch ? "No matching members found" : "No users available"}
                        </div>
                      ) : (
                        filteredUsers.slice(0, 8).map((user) => (
                          <button
                            key={user.id}
                            type="button"
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => addTeamMember(user)}
                            className="projects-dropdown-option-member"
                          >
                            <span className="material-symbols-outlined text-[18px] text-outline-variant">
                              person
                            </span>
                            <span>
                              {user.name || user.full_name || user.email}
                              {user.email && (user.name || user.full_name) && (
                                <span className="text-on-surface-variant text-xs ml-1">
                                  ({user.email})
                                </span>
                              )}
                            </span>
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Expected Timeline */}
              <div>
                <label className="projects-field-label">
                  Expected Timeline
                </label>
                <input
                  type="text"
                  value={form.expected_timeline}
                  onChange={(e) => setForm({ ...form, expected_timeline: e.target.value })}
                  placeholder="e.g. 12 weeks"
                  className="projects-input"
                />
              </div>

              <div className="projects-actions">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreate(false);
                    setEditingProject(null);
                    setFormError(null);
                  }}
                  className="projects-cancel-btn"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="projects-submit-btn"
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