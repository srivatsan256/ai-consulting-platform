import React, { useState, useEffect } from "react";
import { userService, membershipService, roleService, departmentService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";

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
              className="px-4 py-2.5 bg-white border border-outline-variant/40 text-on-surface rounded-xl font-bold text-sm hover:bg-surface-container transition-colors flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
              Export CSV
            </button>
            <button
              onClick={() => { setImportResult(null); setImportError(null); setImportJson(""); setImportFile(null); setShowImport(true); }}
              className="px-4 py-2.5 bg-white border border-outline-variant/40 text-on-surface rounded-xl font-bold text-sm hover:bg-surface-container transition-colors flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">upload_file</span>
              Bulk Import
            </button>
            <button
              onClick={() => { setInviteError(null); setInviteForm({ email: "", role: "", department: "" }); setShowInvite(true); }}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
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
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
          />
        </div>
        <select
          value={filterActive}
          onChange={(e) => setFilterActive(e.target.value)}
          className="px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-white text-on-surface text-sm focus:outline-none focus:border-primary"
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
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-outline-variant/20 text-on-surface-variant text-[11px] uppercase tracking-wider">
                <th className="px-5 py-3 font-medium">User</th>
                <th className="px-5 py-3 font-medium">Role</th>
                <th className="px-5 py-3 font-medium">Designation</th>
                <th className="px-5 py-3 font-medium">Verified</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Joined</th>
                <th className="px-5 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-on-surface-variant">No users found.</td>
                </tr>
              )}
              {filtered.map((user) => (
                <tr key={user.id} className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-5 py-4">
                    <p className="font-semibold text-on-surface">
                      {[user.first_name, user.last_name].filter(Boolean).join(" ") || user.username}
                    </p>
                    <p className="text-xs text-on-surface-variant">{user.email}</p>
                  </td>
                  <td className="px-5 py-4">
                    <span className="px-2 py-1 rounded bg-primary/10 text-primary text-[10px] font-bold">
                      {roleByUser[user.id] || "No membership"}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant">{user.designation || "-"}</td>
                  <td className="px-5 py-4">
                    {user.is_email_verified ? (
                      <span className="text-emerald-600 text-xs font-bold">Verified</span>
                    ) : (
                      <span className="text-amber-600 text-xs font-bold">Unverified</span>
                    )}
                  </td>
                  <td className="px-5 py-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${user.is_active ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant">{formatDate(user.created_at)}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        title={user.is_active ? "Deactivate" : "Activate"}
                        onClick={() => handleToggleActive(user)}
                        className="p-1.5 rounded-lg hover:bg-surface-container transition-colors"
                      >
                        <span className={`material-symbols-outlined text-[18px] ${user.is_active ? "text-red-500" : "text-emerald-600"}`}>
                          {user.is_active ? "block" : "check_circle"}
                        </span>
                      </button>
                      <button
                        title="Edit"
                        onClick={() => openEdit(user)}
                        className="p-1.5 rounded-lg hover:bg-surface-container transition-colors"
                      >
                        <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                      </button>
                      <button
                        title="Delete"
                        onClick={() => handleDelete(user)}
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

      {/* Pending invitations */}
      {invitations.length > 0 && (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
          <h3 className="font-semibold text-on-surface text-sm mb-3">Pending Invitations</h3>
          <div className="space-y-2">
            {invitations.map((inv) => (
              <div key={inv.id} className="flex items-center gap-3 px-3 py-2 rounded-lg border border-outline-variant/20">
                <span className="material-symbols-outlined text-[20px] text-primary">mail</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-on-surface truncate">{inv.email}</p>
                  <p className="text-[11px] text-outline">
                    {inv.role_name || "No role"} · Expires {formatDate(inv.expires_at)}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-[10px] font-bold ${inv.status === "pending" ? "bg-amber-100 text-amber-700" : inv.status === "accepted" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                  {inv.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Invite modal */}
      {showInvite && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto soft-shadow">
            <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
              <h3 className="font-headline-lg text-lg font-bold text-on-surface">Invite User</h3>
              <button onClick={() => setShowInvite(false)} className="p-2 rounded-lg hover:bg-surface-container transition-colors">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={handleInvite} className="p-6 space-y-4">
              {inviteError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{inviteError}</span>
                </div>
              )}
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">Email *</label>
                <input
                  type="email"
                  required
                  value={inviteForm.email}
                  onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                  placeholder="user@company.com"
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">Role *</label>
                <select
                  required
                  value={inviteForm.role}
                  onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                >
                  <option value="">Select role</option>
                  {roles.filter((r) => r.is_active !== false).map((r) => (
                    <option key={r.id} value={r.id}>{r.display_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">Department</label>
                <select
                  value={inviteForm.department}
                  onChange={(e) => setInviteForm({ ...inviteForm, department: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                >
                  <option value="">No department</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowInvite(false)} className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={inviting} className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50">
                  {inviting ? "Sending..." : "Send Invite"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk import modal */}
      {showImport && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto soft-shadow">
            <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
              <h3 className="font-headline-lg text-lg font-bold text-on-surface">Bulk Import Users</h3>
              <button onClick={() => setShowImport(false)} className="p-2 rounded-lg hover:bg-surface-container transition-colors">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setImportMode("json")}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${importMode === "json" ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant"}`}
                >
                  JSON
                </button>
                <button
                  onClick={() => setImportMode("csv")}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${importMode === "csv" ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant"}`}
                >
                  CSV File
                </button>
              </div>
              {importMode === "json" ? (
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                    Users array (email, first_name, last_name, role, is_active)
                  </label>
                  <textarea
                    rows={6}
                    value={importJson}
                    onChange={(e) => setImportJson(e.target.value)}
                    placeholder={`[\n  { "email": "a@company.com", "first_name": "Alice", "role": "document_reviewer" },\n  { "email": "b@company.com", "first_name": "Bob", "is_active": false }\n]`}
                    className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm font-mono focus:outline-none focus:border-primary"
                  />
                </div>
              ) : (
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                    CSV file (email, username, first_name, last_name, role, is_active)
                  </label>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                    className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm"
                  />
                </div>
              )}
              {importError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{importError}</span>
                </div>
              )}
              {importResult && (
                <div className="px-4 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-sm text-emerald-800">
                  <p className="font-bold mb-1">{importResult.detail}</p>
                  {importResult.created?.length > 0 && <p>Created: {importResult.created.length}</p>}
                  {importResult.skipped?.length > 0 && <p>Skipped: {importResult.skipped.length}</p>}
                  {importResult.errors?.length > 0 && (
                    <p className="text-red-600 mt-1">Errors: {importResult.errors.length}</p>
                  )}
                </div>
              )}
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowImport(false)} className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors">
                  Close
                </button>
                <button onClick={handleImport} disabled={importing} className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50">
                  {importing ? "Importing..." : "Import Users"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit user modal */}
      {showEdit && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl w-full max-w-md soft-shadow">
            <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
              <h3 className="font-headline-lg text-lg font-bold text-on-surface">Edit User</h3>
              <button onClick={() => setShowEdit(false)} className="p-2 rounded-lg hover:bg-surface-container transition-colors">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={handleSaveEdit} className="p-6 space-y-4">
              {editError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{editError}</span>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">First Name</label>
                  <input
                    type="text"
                    value={editForm.first_name || ""}
                    onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">Last Name</label>
                  <input
                    type="text"
                    value={editForm.last_name || ""}
                    onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                    className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                  />
                </div>
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">Phone</label>
                <input
                  type="text"
                  value={editForm.phone || ""}
                  onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">Designation</label>
                <input
                  type="text"
                  value={editForm.designation || ""}
                  onChange={(e) => setEditForm({ ...editForm, designation: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowEdit(false)} className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={editing} className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50">
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
