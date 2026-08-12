import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { taskService, projectService, userService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";
import TaskFormModal from "../components/TaskFormModal";
import "./TaskDetailPage.css";

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
        className="taskdetail-back-btn"
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
                className="taskdetail-btn-complete"
              >
                <span className="material-symbols-outlined text-[18px]">check_circle</span>
                Complete
              </button>
            )}
            <button
              onClick={() => setShowEdit(true)}
              className="taskdetail-btn-primary"
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
          <div className="taskdetail-card soft-shadow">
            <h3 className="taskdetail-card-title">Details</h3>
            <dl className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Status</dt>
                <dd>
                  <span className={`taskdetail-badge ${STATUS_STYLES[task.status] || "bg-gray-100 text-gray-600"}`}>
                    {task.status?.replace("_", " ")}
                  </span>
                </dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Priority</dt>
                <dd>
                  <span className={`taskdetail-badge ${PRIORITY_STYLES[task.priority] || "bg-gray-100 text-gray-600"}`}>
                    {task.priority}
                  </span>
                </dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Assignee</dt>
                <dd className="taskdetail-dd">{task.assigned_to_name || "Unassigned"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Project</dt>
                <dd className="taskdetail-dd">{projectName || "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Start Date</dt>
                <dd className="taskdetail-dd">{task.start_date || "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Due Date</dt>
                <dd className="taskdetail-dd">{task.due_date || "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Estimated</dt>
                <dd className="taskdetail-dd">{task.estimated_hours != null ? `${task.estimated_hours}h` : "-"}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="taskdetail-dt">Actual</dt>
                <dd className="taskdetail-dd">{task.actual_hours != null ? `${task.actual_hours}h` : "-"}</dd>
              </div>
              {task.completed_at && (
                <div className="flex items-center justify-between">
                  <dt className="taskdetail-dt">Completed</dt>
                  <dd className="taskdetail-dd">{formatDate(task.completed_at)}</dd>
                </div>
              )}
            </dl>
          </div>

          {task.subtasks?.length > 0 && (
            <div className="taskdetail-card soft-shadow">
              <h3 className="taskdetail-subtask-title">Subtasks</h3>
              <ul className="space-y-2">
                {task.subtasks.map((id) => (
                  <li key={id} className="taskdetail-subtask-item">
                    <span className="material-symbols-outlined text-[16px]">subdirectory_arrow_right</span>
                    Task #{id}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {task.description && (
            <div className="taskdetail-card soft-shadow">
              <h3 className="taskdetail-desc-title">Description</h3>
              <p className="text-sm text-on-surface-variant whitespace-pre-wrap">{task.description}</p>
            </div>
          )}
        </div>

        {/* Comments + Attachments */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="taskdetail-card soft-shadow">
            <h3 className="taskdetail-card-title">Comments ({comments.length})</h3>
            <form onSubmit={handleAddComment} className="mb-4">
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Add a comment..."
                rows={2}
                className="taskdetail-comment-input"
              />
              <div className="flex justify-end mt-2">
                <button
                  type="submit"
                  disabled={sendingComment || !commentText.trim()}
                  className="taskdetail-post-btn"
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
                    <div className="taskdetail-avatar">
                      <span className="material-symbols-outlined text-[18px] text-primary">person</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-2">
                        <p className="taskdetail-comment-author">{comment.author_name || "Unknown"}</p>
                        <p className="taskdetail-comment-time">{formatDate(comment.created_at)}</p>
                      </div>
                      <p className="text-sm text-on-surface-variant mt-0.5 whitespace-pre-wrap">{comment.content}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="taskdetail-card soft-shadow">
            <h3 className="taskdetail-card-title">Attachments ({attachments.length})</h3>
            <div className="flex items-center gap-3 mb-4">
              <label className="taskdetail-upload-label">
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
                  <div key={att.id} className="taskdetail-attach-row">
                    <span className="material-symbols-outlined text-[20px] text-primary">attach_file</span>
                    <a
                      href={att.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 min-w-0"
                    >
                      <p className="taskdetail-attach-name">{att.original_name}</p>
                      <p className="taskdetail-attach-meta">
                        {formatBytes(att.file_size)} · {att.uploaded_by_name || "Unknown"} · {formatDate(att.uploaded_at)}
                      </p>
                    </a>
                    <button
                      onClick={() => handleDeleteAttachment(att)}
                      className="taskdetail-delete-btn"
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
