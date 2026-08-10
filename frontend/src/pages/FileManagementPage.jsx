import React, { useState, useEffect, useCallback } from "react";
import {
  fileManagementService,
  projectService,
  userService,
  getApiError,
} from "../services/api";
import TopHeader from "../components/TopHeader";

const inputCls =
  "w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20";
const labelCls =
  "block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5";

const SCAN_STATUS = {
  pending: { label: "Pending", icon: "hourglass_top", color: "text-amber-500" },
  clean: { label: "Clean", icon: "verified", color: "text-emerald-500" },
  infected: { label: "Infected", icon: "error", color: "text-red-500" },
  error: { label: "Scan Error", icon: "warning", color: "text-orange-500" },
};

const PERMISSION_OPTIONS = [
  ["view", "View"],
  ["download", "Download"],
  ["delete", "Delete"],
  ["manage", "Manage"],
];

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename || "download";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

const formatDate = (v) => (v ? new Date(v).toLocaleString() : "N/A");

// ─────────────────────────────────────────────────────────────
// Upload Modal
// ─────────────────────────────────────────────────────────────
function UploadModal({ onClose, onUploaded }) {
  const [projects, setProjects] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    project: "",
    file_category: "",
    doc_type: "OTHER",
  });
  const [file, setFile] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.allSettled([
      projectService.list(),
      fileManagementService.categories(),
    ]).then(([pRes, cRes]) => {
      if (pRes.status === "fulfilled")
        setProjects(pRes.value.data.results || pRes.value.data || []);
      if (cRes.status === "fulfilled")
        setCategories(cRes.value.data.results || cRes.value.data || []);
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.project) return setError("Select a project.");
    if (!file) return setError("Choose a file to upload.");
    setSaving(true);
    setError(null);
    const formData = new FormData();
    formData.append("project", form.project);
    formData.append("file", file);
    formData.append("doc_type", form.doc_type || "OTHER");
    if (form.file_category) formData.append("file_category", form.file_category);
    try {
      await fileManagementService.upload(formData);
      onUploaded();
      onClose();
    } catch (err) {
      setError(getApiError(err, "Upload failed."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20">
          <h3 className="font-semibold text-on-surface">Upload File</h3>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className={labelCls}>Project</label>
            <select
              value={form.project}
              onChange={(e) => setForm({ ...form, project: e.target.value })}
              className={inputCls}
            >
              <option value="">Choose a project</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.project_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>File</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0] || null)}
              className="w-full text-sm text-on-surface-variant"
            />
            {file && (
              <p className="mt-1 text-xs text-on-surface-variant">
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Document Type</label>
              <input
                value={form.doc_type}
                onChange={(e) => setForm({ ...form, doc_type: e.target.value })}
                placeholder="e.g. REQUIREMENTS"
                className={inputCls}
              />
            </div>
            <div>
              <label className={labelCls}>Category</label>
              <select
                value={form.file_category}
                onChange={(e) =>
                  setForm({ ...form, file_category: e.target.value })
                }
                className={inputCls}
              >
                <option value="">No category</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {error && (
            <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {saving ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Permissions Modal
// ─────────────────────────────────────────────────────────────
function PermissionModal({ file, onClose, onChanged }) {
  const [permissions, setPermissions] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    target: "everyone",
    user: "",
    role_key: "",
    permission: "view",
    allow: true,
  });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.allSettled([
      fileManagementService.permissions({ file: file.id, page_size: 100 }),
      userService.list({ page_size: 100 }),
    ]).then(([pRes, uRes]) => {
      if (pRes.status === "fulfilled")
        setPermissions(pRes.value.data.results || pRes.value.data || []);
      if (uRes.status === "fulfilled")
        setUsers(uRes.value.data.results || uRes.value.data || []);
      setLoading(false);
    });
  }, [file.id]);

  const addPermission = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const payload = { file: file.id, permission: form.permission, allow: form.allow };
    if (form.target === "user") payload.user = Number(form.user);
    else if (form.target === "role") payload.role_key = form.role_key;
    try {
      await fileManagementService.createPermission(payload);
      const res = await fileManagementService.permissions({ file: file.id, page_size: 100 });
      setPermissions(res.data.results || res.data || []);
      setForm({ ...form, user: "", role_key: "" });
      onChanged();
    } catch (err) {
      setError(getApiError(err, "Failed to add permission."));
    } finally {
      setSaving(false);
    }
  };

  const removePermission = async (perm) => {
    if (!window.confirm("Remove this permission rule?")) return;
    try {
      await fileManagementService.deletePermission(perm.id);
      setPermissions(permissions.filter((p) => p.id !== perm.id));
      onChanged();
    } catch (err) {
      alert(getApiError(err, "Failed to remove permission."));
    }
  };

  const userName = (u) => {
    const name = [u.first_name, u.last_name].filter(Boolean).join(" ");
    return name || u.email || u.username;
  };

  const targetLabel = (p) => {
    if (p.user) return p.user_name || p.user_email;
    if (p.role_key) return `Role: ${p.role_key}`;
    return "Everyone";
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20">
          <div>
            <h3 className="font-semibold text-on-surface">File Permissions</h3>
            <p className="text-xs text-on-surface-variant truncate max-w-sm">
              {file.original_name}
            </p>
          </div>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="p-6">
          {loading ? (
            <p className="text-sm text-on-surface-variant">Loading permissions...</p>
          ) : permissions.length === 0 ? (
            <p className="text-sm text-on-surface-variant mb-4">
              No custom permission rules. Company members can view and download by default.
            </p>
          ) : (
            <div className="space-y-2 mb-4">
              {permissions.map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between gap-3 p-3 rounded-lg bg-surface-container-low border border-outline-variant/20"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={`material-symbols-outlined text-[18px] ${p.allow ? "text-emerald-500" : "text-red-500"}`}>
                      {p.allow ? "check_circle" : "cancel"}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-on-surface truncate">
                        {targetLabel(p)}
                      </p>
                      <p className="text-[11px] text-on-surface-variant">
                        {PERMISSION_OPTIONS.find(([v]) => v === p.permission)?.[1] || p.permission}
                        {p.allow ? " (allow)" : " (deny)"}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removePermission(p)}
                    className="text-on-surface-variant hover:text-red-500"
                    title="Remove rule"
                  >
                    <span className="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>
              ))}
            </div>
          )}

          <form onSubmit={addPermission} className="space-y-3 border-t border-outline-variant/20 pt-4">
            <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
              Add Rule
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Target</label>
                <select
                  value={form.target}
                  onChange={(e) => setForm({ ...form, target: e.target.value })}
                  className={inputCls}
                >
                  <option value="everyone">Everyone</option>
                  <option value="role">Role</option>
                  <option value="user">Specific User</option>
                </select>
              </div>
              <div>
                <label className={labelCls}>Permission</label>
                <select
                  value={form.permission}
                  onChange={(e) => setForm({ ...form, permission: e.target.value })}
                  className={inputCls}
                >
                  {PERMISSION_OPTIONS.map(([v, l]) => (
                    <option key={v} value={v}>
                      {l}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {form.target === "user" && (
              <div>
                <label className={labelCls}>User</label>
                <select
                  value={form.user}
                  onChange={(e) => setForm({ ...form, user: e.target.value })}
                  className={inputCls}
                >
                  <option value="">Choose a user</option>
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>
                      {userName(u)}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {form.target === "role" && (
              <div>
                <label className={labelCls}>Role Key</label>
                <input
                  value={form.role_key}
                  onChange={(e) => setForm({ ...form, role_key: e.target.value })}
                  placeholder="e.g. client_sme"
                  className={inputCls}
                />
              </div>
            )}

            <label className="flex items-center gap-2 text-sm text-on-surface-variant">
              <input
                type="checkbox"
                checked={form.allow}
                onChange={(e) => setForm({ ...form, allow: e.target.checked })}
                className="w-4 h-4 accent-primary"
              />
              Allow (uncheck to deny)
            </label>

            {error && (
              <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all disabled:opacity-50"
              >
                {saving ? "Adding..." : "Add Rule"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Category Form
// ─────────────────────────────────────────────────────────────
function CategoryForm({ initial, onClose, onSaved }) {
  const [form, setForm] = useState(
    initial || { name: "", color: "#2563eb", icon: "", description: "" }
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (form.id) await fileManagementService.updateCategory(form.id, form);
      else await fileManagementService.createCategory(form);
      onSaved();
      onClose();
    } catch (err) {
      setError(getApiError(err, "Failed to save category."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20">
          <h3 className="font-semibold text-on-surface">
            {form.id ? "Edit Category" : "New Category"}
          </h3>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className={labelCls}>Name</label>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g. Contracts"
              required
              className={inputCls}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Color</label>
              <input
                type="color"
                value={form.color}
                onChange={(e) => setForm({ ...form, color: e.target.value })}
                className="w-full h-11 rounded-xl border border-outline-variant/40 bg-surface-container-low"
              />
            </div>
            <div>
              <label className={labelCls}>Icon</label>
              <input
                value={form.icon}
                onChange={(e) => setForm({ ...form, icon: e.target.value })}
                placeholder="folder"
                className={inputCls}
              />
            </div>
          </div>
          <div>
            <label className={labelCls}>Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              className={inputCls}
            />
          </div>
          {error && (
            <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Storage Panel
// ─────────────────────────────────────────────────────────────
function StoragePanel({ quota, onChanged }) {
  const [limitInput, setLimitInput] = useState("");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const percent = Math.min(100, quota?.usage_percent || 0);

  const saveLimit = async (e) => {
    e.preventDefault();
    const gb = parseFloat(limitInput);
    if (!gb || gb <= 0) return setError("Enter a valid size in GB.");
    setSaving(true);
    setError(null);
    try {
      await fileManagementService.updateQuota(quota.id, {
        quota_limit_bytes: Math.round(gb * 1024 ** 3),
      });
      setEditing(false);
      onChanged();
    } catch (err) {
      setError(getApiError(err, "Failed to update quota."));
    } finally {
      setSaving(false);
    }
  };

  const toggleEnforced = async () => {
    try {
      await fileManagementService.updateQuota(quota.id, {
        enforced: !quota.enforced,
      });
      onChanged();
    } catch (err) {
      alert(getApiError(err, "Failed to update quota."));
    }
  };

  const barColor =
    percent >= 90 ? "bg-red-500" : percent >= 70 ? "bg-amber-500" : "bg-primary";

  return (
    <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="font-semibold text-on-surface text-sm">Storage Quota</h3>
          <p className="text-xs text-on-surface-variant mt-1">
            Track and limit how much storage the company uses across uploaded files.
          </p>
        </div>
        {!editing && (
          <button
            onClick={() => {
              setLimitInput((quota.quota_limit_bytes / 1024 ** 3).toFixed(1));
              setEditing(true);
            }}
            className="px-3 py-1.5 rounded-lg border border-outline-variant/40 text-on-surface-variant text-xs font-semibold hover:text-primary"
          >
            Edit Limit
          </button>
        )}
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-on-surface">
            {quota?.used_display} of {quota?.quota_limit_display} used
          </span>
          <span className="text-sm font-bold text-on-surface">{percent}%</span>
        </div>
        <div className="h-3 rounded-full bg-surface-container-low overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${barColor}`}
            style={{ width: `${percent}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-[11px] text-on-surface-variant">
          <span>{quota?.remaining_bytes > 0 ? `${quota?.used_display} used` : "Quota reached"}</span>
          <span>{(quota?.remaining_bytes / 1024 ** 3).toFixed(1)} GB remaining</span>
        </div>
      </div>

      {editing && (
        <form onSubmit={saveLimit} className="flex items-end gap-3 border-t border-outline-variant/20 pt-4">
          <div className="flex-1">
            <label className={labelCls}>Quota Limit (GB)</label>
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={limitInput}
              onChange={(e) => setLimitInput(e.target.value)}
              className={inputCls}
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            type="button"
            onClick={() => setEditing(false)}
            className="px-4 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-semibold"
          >
            Cancel
          </button>
        </form>
      )}

      <div className="mt-4 flex items-center justify-between p-4 rounded-lg bg-surface-container-low">
        <div>
          <p className="text-sm font-semibold text-on-surface">Enforce Quota</p>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Reject uploads that would exceed the limit.
          </p>
        </div>
        <button
          onClick={toggleEnforced}
          className={`w-12 h-6 rounded-full transition-colors relative ${quota?.enforced ? "bg-primary" : "bg-outline-variant/50"}`}
        >
          <span
            className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all ${quota?.enforced ? "left-[26px]" : "left-0.5"}`}
          />
        </button>
      </div>

      {error && (
        <p className="mt-3 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {error}
        </p>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────────────────────
export default function FileManagementPage() {
  const [tab, setTab] = useState("files");
  const [files, setFiles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [quota, setQuota] = useState(null);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [filterScan, setFilterScan] = useState("");

  const [showUpload, setShowUpload] = useState(false);
  const [showCategoryForm, setShowCategoryForm] = useState(null);
  const [permFile, setPermFile] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (filterCategory) params.file_category = filterCategory;
    if (filterScan) params.scan_status = filterScan;

    const [fRes, cRes, qRes] = await Promise.allSettled([
      fileManagementService.files(params),
      fileManagementService.categories(),
      fileManagementService.quota(),
    ]);
    if (fRes.status === "fulfilled")
      setFiles(fRes.value.data.results || fRes.value.data || []);
    if (cRes.status === "fulfilled")
      setCategories(cRes.value.data.results || cRes.value.data || []);
    if (qRes.status === "fulfilled") setQuota(qRes.value.data);
    setLoading(false);
  }, [search, filterCategory, filterScan]);

  useEffect(() => {
    const t = setTimeout(fetchAll, 250);
    return () => clearTimeout(t);
  }, [fetchAll]);

  const rescanFile = async (file) => {
    try {
      await fileManagementService.rescan(file.id);
      fetchAll();
    } catch (err) {
      alert(getApiError(err, "Scan failed."));
    }
  };

  const assignCategory = async (file, categoryId) => {
    try {
      await fileManagementService.updateFile(file.id, {
        category_id: categoryId || null,
      });
      fetchAll();
    } catch (err) {
      alert(getApiError(err, "Failed to update category."));
    }
  };

  const deleteFile = async (file) => {
    if (!window.confirm(`Delete "${file.original_name}"?`)) return;
    try {
      await fileManagementService.deleteFile(file.id);
      fetchAll();
    } catch (err) {
      alert(getApiError(err, "Failed to delete file."));
    }
  };

  const handleDownload = async (file) => {
    if (!file.can_download) {
      alert("You do not have permission to download this file.");
      return;
    }
    try {
      const res = await fileManagementService.download(file.id);
      downloadBlob(res.data, file.original_name);
    } catch (err) {
      alert(getApiError(err, "Download failed."));
    }
  };

  const scanBadge = (file) => {
    const scan = file.scan;
    const s = SCAN_STATUS[scan?.status] || SCAN_STATUS.pending;
    return (
      <span className={`inline-flex items-center gap-1 text-[11px] font-semibold ${s.color}`}>
        <span className="material-symbols-outlined text-[14px]">{s.icon}</span>
        {s.label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="File Management"
        subtitle="Files, categories, scans and storage"
        actions={
          tab === "files" ? (
            <button
              onClick={() => setShowUpload(true)}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <span className="material-symbols-outlined text-[18px]">upload_file</span>
              Upload File
            </button>
          ) : tab === "categories" ? (
            <button
              onClick={() => setShowCategoryForm({})}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Category
            </button>
          ) : null
        }
      />

      <div className="flex gap-2 border-b border-outline-variant/20 flex-wrap">
        {[
          ["files", "Files"],
          ["categories", "Categories"],
          ["storage", "Storage Quota"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors ${tab === key ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"}`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "files" && (
        <>
          {/* Filters */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-outline-variant text-[20px]">
                search
              </span>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search files..."
                className={`${inputCls} pl-10`}
              />
            </div>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className={inputCls}
            >
              <option value="">All categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            <select
              value={filterScan}
              onChange={(e) => setFilterScan(e.target.value)}
              className={inputCls}
            >
              <option value="">All scan statuses</option>
              {Object.entries(SCAN_STATUS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          {/* Files table */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
            {loading ? (
              <p className="p-6 text-sm text-on-surface-variant">Loading files...</p>
            ) : files.length === 0 ? (
              <div className="text-center py-12">
                <span className="material-symbols-outlined text-[48px] text-outline-variant">folder_open</span>
                <p className="text-on-surface-variant mt-3 text-sm">No files uploaded yet</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant border-b border-outline-variant/20 bg-surface-container-low">
                      <th className="px-4 py-3">File</th>
                      <th className="px-4 py-3">Project</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Size</th>
                      <th className="px-4 py-3">Scan</th>
                      <th className="px-4 py-3">Uploaded By</th>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {files.map((file) => (
                      <tr key={file.id} className="border-b border-outline-variant/10 hover:bg-surface-container-low/50">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3 min-w-[200px]">
                            <span className="material-symbols-outlined text-outline-variant">description</span>
                            <div className="min-w-0">
                              <p className="font-medium text-on-surface truncate">{file.original_name}</p>
                              <p className="text-[11px] text-on-surface-variant">{file.doc_type} · L{file.level}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-on-surface-variant">{file.project_name}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <select
                              value={file.file_category || ""}
                              onChange={(e) => assignCategory(file, e.target.value)}
                              className="px-2 py-1.5 rounded-lg border border-outline-variant/40 bg-surface-container-low text-xs focus:outline-none focus:border-primary max-w-[140px]"
                            >
                              <option value="">No category</option>
                              {categories.map((c) => (
                                <option key={c.id} value={c.id}>
                                  {c.name}
                                </option>
                              ))}
                            </select>
                            {file.category && (
                              <span
                                className="w-2.5 h-2.5 rounded-full inline-block"
                                style={{ backgroundColor: file.category.color }}
                              />
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-on-surface-variant">{file.size_display}</td>
                        <td className="px-4 py-3">{scanBadge(file)}</td>
                        <td className="px-4 py-3 text-on-surface-variant">{file.uploaded_by_name}</td>
                        <td className="px-4 py-3 text-on-surface-variant text-xs">{formatDate(file.uploaded_at)}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={() => handleDownload(file)}
                              title="Download"
                              className="p-2 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-primary"
                            >
                              <span className="material-symbols-outlined text-[18px]">download</span>
                            </button>
                            <button
                              onClick={() => rescanFile(file)}
                              title="Re-scan for viruses"
                              className="p-2 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-primary"
                            >
                              <span className="material-symbols-outlined text-[18px]">shield</span>
                            </button>
                            <button
                              onClick={() => setPermFile(file)}
                              title="Manage permissions"
                              className="p-2 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-primary"
                            >
                              <span className="material-symbols-outlined text-[18px]">lock</span>
                            </button>
                            <button
                              onClick={() => deleteFile(file)}
                              title="Delete"
                              className="p-2 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-red-500"
                            >
                              <span className="material-symbols-outlined text-[18px]">delete</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {tab === "categories" && (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
          {loading ? (
            <p className="text-sm text-on-surface-variant">Loading categories...</p>
          ) : categories.length === 0 ? (
            <div className="text-center py-10">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">label</span>
              <p className="text-on-surface-variant mt-3 text-sm">No categories yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((c) => (
                <div key={c.id} className="border border-outline-variant/20 rounded-xl p-4 flex flex-col">
                  <div className="flex items-start justify-between mb-3">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center"
                      style={{ backgroundColor: `${c.color}20`, color: c.color }}
                    >
                      <span className="material-symbols-outlined">{c.icon || "folder"}</span>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => setShowCategoryForm(c)}
                        className="p-1.5 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-primary"
                      >
                        <span className="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                      <button
                        onClick={async () => {
                          if (!window.confirm(`Delete category "${c.name}"?`)) return;
                          try {
                            await fileManagementService.deleteCategory(c.id);
                            fetchAll();
                          } catch (err) {
                            alert(getApiError(err, "Failed to delete category."));
                          }
                        }}
                        className="p-1.5 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-red-500"
                      >
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    </div>
                  </div>
                  <h4 className="font-semibold text-on-surface text-sm">{c.name}</h4>
                  <p className="text-xs text-on-surface-variant mt-1 flex-1">{c.description || "No description"}</p>
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-outline-variant/10 text-xs text-on-surface-variant">
                    <span className="material-symbols-outlined text-[14px]">description</span>
                    {c.file_count || 0} file{c.file_count === 1 ? "" : "s"}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "storage" && (
        <div className="max-w-3xl">
          {quota && <StoragePanel quota={quota} onChanged={fetchAll} />}
        </div>
      )}

      {showUpload && (
        <UploadModal onClose={() => setShowUpload(false)} onUploaded={fetchAll} />
      )}
      {showCategoryForm && (
        <CategoryForm
          initial={showCategoryForm.id ? showCategoryForm : null}
          onClose={() => setShowCategoryForm(null)}
          onSaved={fetchAll}
        />
      )}
      {permFile && (
        <PermissionModal
          file={permFile}
          onClose={() => setPermFile(null)}
          onChanged={fetchAll}
        />
      )}
    </div>
  );
}
