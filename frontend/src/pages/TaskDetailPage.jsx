import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
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

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let value = Number(bytes);
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

function formatDate(value) {
  if (!value) return "N/A";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? "N/A" : d.toLocaleString();
}

export default function TaskDetailPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [projectName, setProjectName] = useState("");
  const [loading, setLoading] = useState(true);
  const [comments, setComments] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [sendingComment, setSendingComment] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [showEdit, setShowEdit] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [form, setForm] = useState(null);

  const loadTask = async () => {
    try {
      const res = await taskService.get(taskId);
      setTask(res.data);
      setForm({
        id: res.data.id,
        project: res.data.project,
        title: res.data.title,
        description: res.data.description,
        status: res.data.status,
        priority: res.data.priority,
        assigned_to: res.data.assigned_to || "",
        estimated_hours: res.data.estimated_hours,
        start_date: res.data.start_date || "",
        due_date: res.data.due_date || "",
        projectOptions: projects,
        userOptions: users,
      });
      return res.data;
    } catch (err) {
      alert(getApiError(err, "Failed to load task."));
      navigate("/tasks");
      return null;
    }
  };

  useEffect(() => {
    const load = async () => {
      const [projectRes, userRes] = await Promise.allSettled([
        projectService.list(),
        userService.list({ page_size: 100 }),
      ]);
      const ps = projectRes.status === "fulfilled" ? projectRes.value.data.results || projectRes.value.data || [] : [];
      const us = userRes.status === "fulfilled" ? userRes.value.data.results || userRes.value.data || [] : [];
      setProjects(ps);
      setUsers(us);
      const data = await loadTask();
      if (data) {
        const name = ps.find((p) => p.id === data.project);
        setProjectName(name?.project_name || "");
        const [commentRes, attachRes] = await Promise.allSettled([
          taskService.comments(taskId),
          taskService.attachments(taskId),
        ]);
        if (commentRes.status === "fulfilled") setComments(commentRes.value.data || []);
        if (attachRes.status === "fulfilled") setAttachments(attachRes.value.data || []);
      }
      setLoading(false);
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    setSendingComment(true);
    try {
      await taskService.addComment(taskId, commentText);
      setCommentText("");
      const res = await taskService.comments(taskId);
      setComments(res.data || []);
    } catch (err) {
      alert(getApiError(err, "Failed to add comment."));
    } finally {
      setSendingComment(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await taskService.addAttachment(taskId, formData);
      const res = await taskService.attachments(taskId);
      setAttachments(res.data || []);
    } catch (err) {
      setUploadError(getApiError(err, "Failed to upload attachment."));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDeleteAttachment = async (att) => {
    if (!window.confirm(`Delete attachment "${att.original_name}"?`)) return;
    try {
      await taskService.deleteAttachment(att.id);
      setAttachments(attachments.filter((a) => a.id !== att.id));
    } catch (err) {
      alert(getApiError(err, "Failed to delete attachment."));
    }
  };

  const handleComplete = async () => {
    try {
      await taskService.complete(taskId);
      await loadTask();
    } catch (err) {
      alert(getApiError(err, "Failed to complete task."));
    }
  };

  const handleSubmitEdit = async () => {
    setSubmitting(true);
    setFormError(null);
    try {
      await taskService.update(taskId, form);
      setShowEdit(false);
      const data = await loadTask();
      const name = projects.find((p) => p.id === data.project);
      setProjectName(name?.project_name || "");
    } catch (err) {
      setFormError(getApiError(err, "Failed to update task."));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!task) return null;

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate("/tasks")}
        className="flex items-center gap-1 text-sm text-on-surface-variant hover:text-primary transition-colors"
      >
        <span className="material-symbols-outlined text-[18px]">arrow_back</span>
        Back to tasks
      </button>

      <TopHeader
        title={task.title}
        subtitle={projectName ? `${projectName} · Created by ${task.created_by_name || "Unknown"}` : "Task detail"}
        actions={
          <div className="flex gap-2">
            {task.status !== "done" && (
              <button
                onClick={handleComplete}
                className="px-4 py-2.5 bg-emerald-600 text-white rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[18px]">check_circle</span>
                Complete
              </button>
            )}
            <button
              onClick={() => setShowEdit(true)}
              className="px-4 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">edit</span>
              Edit
            </button>
          </div>
        }
      />

      <div className="grid grid-cols-12 gap-6">
        {/* Details */}
        <div className="col-span-12 lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
            <h3 className="font-semibold text-on-surface text-sm mb-4">Details</h3>
            <dl className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Status</dt>
                <dd>
                  <span className={`px-2 py-1 rounded text-[10px] font-bold ${STATUS_STYLES[task.status] || "bg-gray-100 text-gray-600"}`}>
                    {task.status?.replace("_", " ")}
                  </span>
                </dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Priority</dt>
                <dd>
                  <span className={`px-2 py-1 rounded text-[10px] font-bold ${PRIORITY_STYLES[task.priority] || "bg-gray-100 text-gray-600"}`}>
                    {task.priority}
                  </span>
                </dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Assignee</dt>
                <dd className="text-on-surface font-medium">{task.assigned_to_name || "Unassigned"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Project</dt>
                <dd className="text-on-surface font-medium">{projectName || "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Start Date</dt>
                <dd className="text-on-surface font-medium">{task.start_date || "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Due Date</dt>
                <dd className="text-on-surface font-medium">{task.due_date || "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Estimated</dt>
                <dd className="text-on-surface font-medium">{task.estimated_hours != null ? `${task.estimated_hours}h` : "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-on-surface-variant">Actual</dt>
                <dd className="text-on-surface font-medium">{task.actual_hours != null ? `${task.actual_hours}h` : "-"}</dd>
              </div>
              {task.completed_at && (
                <div className="flex items-center justify-between">
                  <dt className="text-on-surface-variant">Completed</dt>
                  <dd className="text-on-surface font-medium">{formatDate(task.completed_at)}</dd>
                </div>
              )}
            </dl>
          </div>

          {task.subtasks?.length > 0 && (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
              <h3 className="font-semibold text-on-surface text-sm mb-3">Subtasks</h3>
              <ul className="space-y-2">
                {task.subtasks.map((id) => (
                  <li key={id} className="text-sm text-on-surface-variant flex items-center gap-2">
                    <span className="material-symbols-outlined text-[16px]">subdirectory_arrow_right</span>
                    Task #{id}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {task.description && (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
              <h3 className="font-semibold text-on-surface text-sm mb-2">Description</h3>
              <p className="text-sm text-on-surface-variant whitespace-pre-wrap">{task.description}</p>
            </div>
          )}
        </div>

        {/* Comments + Attachments */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
            <h3 className="font-semibold text-on-surface text-sm mb-4">Comments ({comments.length})</h3>
            <form onSubmit={handleAddComment} className="mb-4">
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Add a comment..."
                rows={2}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 resize-none"
              />
              <div className="flex justify-end mt-2">
                <button
                  type="submit"
                  disabled={sendingComment || !commentText.trim()}
                  className="px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-bold hover:opacity-90 disabled:opacity-50"
                >
                  {sendingComment ? "Posting..." : "Post Comment"}
                </button>
              </div>
            </form>
            <div className="space-y-4">
              {comments.length === 0 ? (
                <p className="text-sm text-on-surface-variant">No comments yet.</p>
              ) : (
                comments.map((comment) => (
                  <div key={comment.id} className="flex gap-3">
                    <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[18px] text-primary">person</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-2">
                        <p className="text-sm font-semibold text-on-surface">{comment.author_name || "Unknown"}</p>
                        <p className="text-[11px] text-outline">{formatDate(comment.created_at)}</p>
                      </div>
                      <p className="text-sm text-on-surface-variant mt-0.5 whitespace-pre-wrap">{comment.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
            <h3 className="font-semibold text-on-surface text-sm mb-4">Attachments ({attachments.length})</h3>
            <div className="flex items-center gap-3 mb-4">
              <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 rounded-xl border-2 border-dashed border-outline-variant/50 text-on-surface-variant text-sm font-medium hover:border-primary hover:text-primary transition-colors">
                <span className="material-symbols-outlined text-[18px]">upload_file</span>
                {uploading ? "Uploading..." : "Upload file"}
                <input type="file" onChange={handleUpload} className="hidden" disabled={uploading} />
              </label>
              {uploadError && <span className="text-sm text-red-500">{uploadError}</span>}
            </div>
            <div className="space-y-2">
              {attachments.length === 0 ? (
                <p className="text-sm text-on-surface-variant">No attachments yet.</p>
              ) : (
                attachments.map((att) => (
                  <div key={att.id} className="flex items-center gap-3 px-3 py-2 rounded-lg border border-outline-variant/20 hover:bg-surface-container-low transition-colors">
                    <span className="material-symbols-outlined text-[20px] text-primary">attach_file</span>
                    <a
                      href={att.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 min-w-0"
                    >
                      <p className="text-sm font-medium text-on-surface truncate">{att.original_name}</p>
                      <p className="text-[11px] text-outline">
                        {formatBytes(att.file_size)} · {att.uploaded_by_name || "Unknown"} · {formatDate(att.uploaded_at)}
                      </p>
                    </a>
                    <button
                      onClick={() => handleDeleteAttachment(att)}
                      className="p-1.5 rounded-lg hover:bg-red-50 transition-colors"
                      title="Delete attachment"
                    >
                      <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {form && (
        <TaskFormModal
          open={showEdit}
          onClose={() => setShowEdit(false)}
          onSubmit={handleSubmitEdit}
          submitting={submitting}
          form={form}
          setForm={setForm}
          formError={formError}
        />
      )}
    </div>
  );
}
