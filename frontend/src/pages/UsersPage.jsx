import React, { useState, useEffect } from "react";
import { userService, membershipService, roleService, departmentService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";
import "../styles/pages/UsersPage.css";

function formatDate(value) {
  if (!value) return "N/A";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? "N/A" : d.toLocaleDateString();
}

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [memberships, setMemberships] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [roles, setRoles] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterActive, setFilterActive] = useState("ALL");

  const [showInvite, setShowInvite] = useState(false);
  const [inviteForm, setInviteForm] = useState({ email: "", role: "", department: "" });
  const [inviteError, setInviteError] = useState(null);
  const [inviting, setInviting] = useState(false);

  const [showImport, setShowImport] = useState(false);
  const [importMode, setImportMode] = useState("json");
  const [importJson, setImportJson] = useState("");
  const [importFile, setImportFile] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState(null);

  const [showEdit, setShowEdit] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [editUser, setEditUser] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editError, setEditError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    const params = { page_size: 100 };
    if (filterActive !== "ALL") params.is_active = filterActive === "ACTIVE";
    const [userRes, memRes, invRes, roleRes, deptRes] = await Promise.allSettled([
      userService.list(params),
      membershipService.list({ page_size: 100 }),
      userService.invitations(),
      roleService.list(),
      departmentService.list(),
    ]);
    if (userRes.status === "fulfilled") {
      setUsers(userRes.value.data.results || userRes.value.data || []);
    }
    if (memRes.status === "fulfilled") {
      setMemberships(memRes.value.data.results || memRes.value.data || []);
    }
    if (invRes.status === "fulfilled") {
      setInvitations(invRes.value.data.results || invRes.value.data || []);
    }
    if (roleRes.status === "fulfilled") {
      setRoles(roleRes.value.data.results || roleRes.value.data || []);
    }
    if (deptRes.status === "fulfilled") {
      setDepartments(deptRes.value.data.results || deptRes.value.data || []);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [filterActive]);

  const roleByUser = {};
  memberships.forEach((m) => {
    if (!roleByUser[m.user] && m.role_name) roleByUser[m.user] = m.role_name;
  });

  const filtered = users.filter((u) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      u.email?.toLowerCase().includes(q) ||
      u.first_name?.toLowerCase().includes(q) ||
      u.last_name?.toLowerCase().includes(q) ||
      u.username?.toLowerCase().includes(q)
    );
  });

  const handleInvite = async (e) => {
    e.preventDefault();
    setInviting(true);
    setInviteError(null);
    try {
      await userService.invite({
        email: inviteForm.email,
        role: Number(inviteForm.role),
        department: inviteForm.department ? Number(inviteForm.department) : null,
      });
      setShowInvite(false);
      setInviteForm({ email: "", role: "", department: "" });
      fetchData();
    } catch (err) {
      setInviteError(getApiError(err, "Failed to send invitation."));
    } finally {
      setInviting(false);
    }
  };

  const handleImport = async () => {
    setImporting(true);
    setImportError(null);
    setImportResult(null);
    try {
      if (importMode === "json") {
        let rows;
        try {
          rows = JSON.parse(importJson);
        } catch {
          throw new Error("Invalid JSON payload.");
        }
        if (!Array.isArray(rows)) throw new Error("Expected a JSON array of users.");
        const res = await userService.bulkImportJson(rows);
        setImportResult(res.data);
      } else {
        if (!importFile) throw new Error("Choose a CSV file to upload.");
        const formData = new FormData();
        formData.append("file", importFile);
        const res = await userService.bulkImport(formData);
        setImportResult(res.data);
      }
      fetchData();
    } catch (err) {
      setImportError(typeof err === "string" ? err : getApiError(err, "Import failed."));
    } finally {
      setImporting(false);
    }
  };

  const handleExport = async () => {
    try {
      const res = await userService.exportCsv();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "users-export.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(getApiError(err, "Export failed."));
    }
  };

  const openEdit = (user) => {
    setEditUser(user);
    setEditForm({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      phone: user.phone || "",
      designation: user.designation || "",
    });
    setEditError(null);
    setShowEdit(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    setEditing(true);
    setEditError(null);
    try {
      await userService.update(editUser.id, editForm);
      setShowEdit(false);
      fetchData();
    } catch (err) {
      setEditError(getApiError(err, "Failed to update user."));
    } finally {
      setEditing(false);
    }
  };

  const handleToggleActive = async (user) => {
    const action = user.is_active ? "deactivate" : "activate";
    if (!window.confirm(`${action === "activate" ? "Activate" : "Deactivate"} ${user.email}?`)) return;
    try {
      if (action === "activate") await userService.activate(user.id);
      else await userService.deactivate(user.id);
      fetchData();
    } catch (err) {
      alert(getApiError(err, `Failed to ${action} user.`));
    }
  };

  const handleDelete = async (user) => {
    if (!window.confirm(`Delete user ${user.email}? This cannot be undone.`)) return;
    try {
      await userService.delete(user.id);
      fetchData();
    } catch (err) {
      alert(getApiError(err, "Failed to delete user."));
    }
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="User Management"
        subtitle="Invite, manage and import company users"
        actions={
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={handleExport}
              className="users-secondary-btn"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
              Export CSV
            </button>
            <button
              onClick={() => { setImportResult(null); setImportError(null); setImportJson(""); setImportFile(null); setShowImport(true); }}
              className="users-secondary-btn"
            >
              <span className="material-symbols-outlined text-[18px]">upload_file</span>
              Bulk Import
            </button>
            <button
              onClick={() => { setInviteError(null); setInviteForm({ email: "", role: "", department: "" }); setShowInvite(true); }}
              className="users-primary-btn"
            >
              <span className="material-symbols-outlined text-[18px]">person_add</span>
              Invite User
            </button>
          </div>
        }
      />

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="users-search-input"
          />
        </div>
        <select
          value={filterActive}
          onChange={(e) => setFilterActive(e.target.value)}
          className="users-select"
        >
          <option value="ALL">All Users</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="users-card soft-shadow">
          <table className="w-full text-sm">
            <thead>
              <tr className="users-th-row">
                <th className="users-th">User</th>
                <th className="users-th">Role</th>
                <th className="users-th">Designation</th>
                <th className="users-th">Verified</th>
                <th className="users-th">Status</th>
                <th className="users-th">Joined</th>
                <th className="users-th text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-on-surface-variant">No users found.</td>
                </tr>
              )}
              {filtered.map((user) => (
                <tr key={user.id} className="users-tr">
                  <td className="users-td">
                    <p className="font-semibold text-on-surface">
                      {[user.first_name, user.last_name].filter(Boolean).join(" ") || user.username}
                    </p>
                    <p className="text-xs text-on-surface-variant">{user.email}</p>
                  </td>
                  <td className="users-td">
                    <span className="users-role-badge">
                      {roleByUser[user.id] || "No membership"}
                    </span>
                  </td>
                  <td className="users-td-muted">{user.designation || "-"}</td>
                  <td className="users-td">
                    {user.is_email_verified ? (
                      <span className="text-emerald-600 text-xs font-bold">Verified</span>
                    ) : (
                      <span className="text-amber-600 text-xs font-bold">Unverified</span>
                    )}
                  </td>
                  <td className="users-td">
                    <span className={`users-mini-badge ${user.is_active ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="users-td-muted">{formatDate(user.created_at)}</td>
                  <td className="users-td">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        title={user.is_active ? "Deactivate" : "Activate"}
                        onClick={() => handleToggleActive(user)}
                        className="users-icon-btn"
                      >
                        <span className={`material-symbols-outlined text-[18px] ${user.is_active ? "text-red-500" : "text-emerald-600"}`}>
                          {user.is_active ? "block" : "check_circle"}
                        </span>
                      </button>
                      <button
                        title="Edit"
                        onClick={() => openEdit(user)}
                        className="users-icon-btn"
                      >
                        <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                      </button>
                      <button
                        title="Delete"
                        onClick={() => handleDelete(user)}
                        className="users-icon-btn-red"
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

      {/* Pending invitations */}
      {invitations.length > 0 && (
        <div className="users-invite-card soft-shadow">
          <h3 className="users-h3-mb3">Pending Invitations</h3>
          <div className="space-y-2">
            {invitations.map((inv) => (
              <div key={inv.id} className="users-inv-row">
                <span className="material-symbols-outlined text-[20px] text-primary">mail</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-on-surface truncate">{inv.email}</p>
                  <p className="text-[11px] text-outline">
                    {inv.role_name || "No role"} · Expires {formatDate(inv.expires_at)}
                  </p>
                </div>
                <span className={`users-mini-badge ${inv.status === "pending" ? "bg-amber-100 text-amber-700" : inv.status === "accepted" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                  {inv.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Invite modal */}
      {showInvite && (
        <div className="users-overlay">
          <div className="users-modal-panel soft-shadow">
            <div className="users-modal-header">
              <h3 className="users-modal-title">Invite User</h3>
              <button onClick={() => setShowInvite(false)} className="users-close-btn">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={handleInvite} className="users-modal-body">
              {inviteError && (
                <div className="users-error">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{inviteError}</span>
                </div>
              )}
              <div>
                <label className="users-label">Email *</label>
                <input
                  type="email"
                  required
                  value={inviteForm.email}
                  onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                  placeholder="user@company.com"
                  className="users-input"
                />
              </div>
              <div>
                <label className="users-label">Role *</label>
                <select
                  required
                  value={inviteForm.role}
                  onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                  className="users-select-input"
                >
                  <option value="">Select role</option>
                  {roles.filter((r) => r.is_active !== false).map((r) => (
                    <option key={r.id} value={r.id}>{r.display_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="users-label">Department</label>
                <select
                  value={inviteForm.department}
                  onChange={(e) => setInviteForm({ ...inviteForm, department: e.target.value })}
                  className="users-select-input"
                >
                  <option value="">No department</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowInvite(false)} className="users-cancel-btn">
                  Cancel
                </button>
                <button type="submit" disabled={inviting} className="users-submit-btn">
                  {inviting ? "Sending..." : "Send Invite"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk import modal */}
      {showImport && (
        <div className="users-overlay">
          <div className="users-modal-panel-xl soft-shadow">
            <div className="users-modal-header">
              <h3 className="users-modal-title">Bulk Import Users</h3>
              <button onClick={() => setShowImport(false)} className="users-close-btn">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div className="users-modal-body">
              <div className="flex gap-2">
                <button
                  onClick={() => setImportMode("json")}
                  className={`users-mode-btn ${importMode === "json" ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant"}`}
                >
                  JSON
                </button>
                <button
                  onClick={() => setImportMode("csv")}
                  className={`users-mode-btn ${importMode === "csv" ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant"}`}
                >
                  CSV File
                </button>
              </div>
              {importMode === "json" ? (
                <div>
                  <label className="users-label">
                    Users array (email, first_name, last_name, role, is_active)
                  </label>
                  <textarea
                    rows={6}
                    value={importJson}
                    onChange={(e) => setImportJson(e.target.value)}
                    placeholder={`[\n  { "email": "a@company.com", "first_name": "Alice", "role": "document_reviewer" },\n  { "email": "b@company.com", "first_name": "Bob", "is_active": false }\n]`}
                    className="users-textarea"
                  />
                </div>
              ) : (
                <div>
                  <label className="users-label">
                    CSV file (email, username, first_name, last_name, role, is_active)
                  </label>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                    className="users-file-input"
                  />
                </div>
              )}
              {importError && (
                <div className="users-error">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{importError}</span>
                </div>
              )}
              {importResult && (
                <div className="users-success">
                  <p className="font-bold mb-1">{importResult.detail}</p>
                  {importResult.created?.length > 0 && <p>Created: {importResult.created.length}</p>}
                  {importResult.skipped?.length > 0 && <p>Skipped: {importResult.skipped.length}</p>}
                  {importResult.errors?.length > 0 && (
                    <p className="text-red-600 mt-1">Errors: {importResult.errors.length}</p>
                  )}
                </div>
              )}
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowImport(false)} className="users-cancel-btn">
                  Close
                </button>
                <button onClick={handleImport} disabled={importing} className="users-submit-btn">
                  {importing ? "Importing..." : "Import Users"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit user modal */}
      {showEdit && (
        <div className="users-overlay">
          <div className="users-modal-panel-md soft-shadow">
            <div className="users-modal-header">
              <h3 className="users-modal-title">Edit User</h3>
              <button onClick={() => setShowEdit(false)} className="users-close-btn">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={handleSaveEdit} className="users-modal-body">
              {editError && (
                <div className="users-error">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{editError}</span>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="users-label">First Name</label>
                  <input
                    type="text"
                    value={editForm.first_name || ""}
                    onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                    className="users-select-input"
                  />
                </div>
                <div>
                  <label className="users-label">Last Name</label>
                  <input
                    type="text"
                    value={editForm.last_name || ""}
                    onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                    className="users-select-input"
                  />
                </div>
              </div>
              <div>
                <label className="users-label">Phone</label>
                <input
                  type="text"
                  value={editForm.phone || ""}
                  onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                  className="users-select-input"
                />
              </div>
              <div>
                <label className="users-label">Designation</label>
                <input
                  type="text"
                  value={editForm.designation || ""}
                  onChange={(e) => setEditForm({ ...editForm, designation: e.target.value })}
                  className="users-select-input"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowEdit(false)} className="users-cancel-btn">
                  Cancel
                </button>
                <button type="submit" disabled={editing} className="users-submit-btn">
                  {editing ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
