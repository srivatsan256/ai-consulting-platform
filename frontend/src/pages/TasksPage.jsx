import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { taskService, projectService, userService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";
import TaskFormModal from "../components/TaskFormModal";

const STATUS_STYLES = {
  todo: "bg-gray-100 text-gray-700",
  in_progress: "bg-blue-100 text-blue-700",
  blocked: "bg-red-100 text-red-700",
  review: "bg-indigo-100 text-indigo-700",
  done: "bg-emerald-100 text-emerald-700",
};

const PRIORITY_STYLES = {
  low: "bg-gray-100 text-gray-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-amber-100 text-amber-700",
  critical: "bg-red-100 text-red-700",
};

function emptyForm(projectOptions, userOptions) {
  return {
    id: null,
    project: "",
    title: "",
    description: "",
    status: "todo",
    priority: "medium",
    assigned_to: "",
    estimated_hours: "",
    start_date: "",
    due_date: "",
    projectOptions,
    userOptions,
  };
}

export default function TasksPage() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("ALL");
  const [filterPriority, setFilterPriority] = useState("ALL");
  const [filterProject, setFilterProject] = useState("ALL");
  const [showCreate, setShowCreate] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [form, setForm] = useState(() => emptyForm([], []));

  const fetchTasks = useCallback(async () => {
    try {
      const params = {};
      if (filterStatus !== "ALL") params.status = filterStatus;
      if (filterPriority !== "ALL") params.priority = filterPriority;
      if (filterProject !== "ALL") params.project = filterProject;
      const res = await taskService.list(params);
      setTasks(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch tasks:", err);
    } finally {
      setLoading(false);
    }
  }, [filterStatus, filterPriority, filterProject]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [taskRes, projectRes, userRes] = await Promise.allSettled([
        taskService.list({
          status: filterStatus !== "ALL" ? filterStatus : undefined,
          priority: filterPriority !== "ALL" ? filterPriority : undefined,
          project: filterProject !== "ALL" ? filterProject : undefined,
        }),
        projectService.list(),
        userService.list({ page_size: 100 }),
      ]);
      if (taskRes.status === "fulfilled") {
        setTasks(taskRes.value.data.results || taskRes.value.data || []);
      }
      if (projectRes.status === "fulfilled") {
        setProjects(projectRes.value.data.results || projectRes.value.data || []);
      }
      if (userRes.status === "fulfilled") {
        setUsers(userRes.value.data.results || userRes.value.data || []);
      }
      setLoading(false);
    };
    load();
  }, [filterStatus, filterPriority, filterProject]);

  const openCreate = () => {
    setForm(emptyForm(projects, users));
    setEditingTask(null);
    setFormError(null);
    setShowCreate(true);
  };

  const openEdit = (task) => {
    setForm({
      ...emptyForm(projects, users),
      id: task.id,
      project: task.project,
      title: task.title,
      description: task.description,
      status: task.status,
      priority: task.priority,
      assigned_to: task.assigned_to || "",
      estimated_hours: task.estimated_hours,
      start_date: task.start_date || "",
      due_date: task.due_date || "",
    });
    setEditingTask(task);
    setFormError(null);
    setShowCreate(true);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setFormError(null);
    try {
      if (form.id) {
        await taskService.update(form.id, form);
      } else {
        await taskService.create(form);
      }
      setShowCreate(false);
      fetchTasks();
    } catch (err) {
      setFormError(getApiError(err, "Failed to save task."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (task) => {
    if (!window.confirm(`Delete task "${task.title}"?`)) return;
    try {
      await taskService.delete(task.id);
      fetchTasks();
    } catch (err) {
      alert(getApiError(err, "Failed to delete task."));
    }
  };

  const handleComplete = async (task) => {
    try {
      await taskService.complete(task.id);
      fetchTasks();
    } catch (err) {
      alert(getApiError(err, "Failed to complete task."));
    }
  };

  const filtered = tasks.filter((t) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      t.title?.toLowerCase().includes(q) ||
      t.description?.toLowerCase().includes(q) ||
      t.assigned_to_name?.toLowerCase().includes(q)
    );
  });

  const projectNameMap = Object.fromEntries(projects.map((p) => [p.id, p.project_name]));

  return (
    <div className="space-y-6">
      <TopHeader
        title="Tasks"
        subtitle="Manage project tasks"
        actions={
          <button
            onClick={openCreate}
            className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            New Task
          </button>
        }
      />

      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
          />
        </div>
        <select
          value={filterProject}
          onChange={(e) => setFilterProject(e.target.value)}
          className="px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary"
        >
          <option value="ALL">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.project_name}</option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary"
        >
          <option value="ALL">All Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="blocked">Blocked</option>
          <option value="review">Review</option>
          <option value="done">Done</option>
        </select>
        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary"
        >
          <option value="ALL">All Priority</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-16 text-center">
          <span className="material-symbols-outlined text-[48px] text-outline-variant">checklist</span>
          <p className="text-on-surface-variant mt-3 text-sm">No tasks found</p>
          <button
            onClick={openCreate}
            className="mt-4 px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium hover:opacity-90"
          >
            Create your first task
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-outline-variant/20 text-on-surface-variant text-[11px] uppercase tracking-wider">
                <th className="px-5 py-3 font-medium">Task</th>
                <th className="px-5 py-3 font-medium">Project</th>
                <th className="px-5 py-3 font-medium">Assignee</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Priority</th>
                <th className="px-5 py-3 font-medium">Due Date</th>
                <th className="px-5 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.map((task) => (
                <tr key={task.id} className="hover:bg-surface-container-low/50 transition-colors cursor-pointer" onClick={() => navigate(`/tasks/${task.id}`)}>
                  <td className="px-5 py-4">
                    <p className="font-semibold text-on-surface">{task.title}</p>
                    {task.subtasks?.length > 0 && (
                      <p className="text-xs text-on-surface-variant">{task.subtasks.length} subtask(s)</p>
                    )}
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant">{projectNameMap[task.project] || "-"}</td>
                  <td className="px-5 py-4 text-on-surface-variant">{task.assigned_to_name || "-"}</td>
                  <td className="px-5 py-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${STATUS_STYLES[task.status] || "bg-gray-100 text-gray-600"}`}>
                      {task.status?.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${PRIORITY_STYLES[task.priority] || "bg-gray-100 text-gray-600"}`}>
                      {task.priority}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant">{task.due_date || "-"}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center justify-end gap-1">
                      {task.status !== "done" && (
                        <button
                          title="Mark complete"
                          onClick={(e) => { e.stopPropagation(); handleComplete(task); }}
                          className="p-1.5 rounded-lg hover:bg-emerald-50 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[18px] text-emerald-600">check_circle</span>
                        </button>
                      )}
                      <button
                        title="Edit"
                        onClick={(e) => { e.stopPropagation(); openEdit(task); }}
                        className="p-1.5 rounded-lg hover:bg-surface-container transition-colors"
                      >
                        <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                      </button>
                      <button
                        title="Delete"
                        onClick={(e) => { e.stopPropagation(); handleDelete(task); }}
                        className="p-1.5 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <TaskFormModal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onSubmit={handleSubmit}
        submitting={submitting}
        form={form}
        setForm={setForm}
        formError={formError}
      />
    </div>
  );
}
