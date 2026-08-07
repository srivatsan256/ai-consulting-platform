import React, { useState, useEffect } from "react";
import {
  roleService,
  permissionService,
  userService,
  getApiError,
} from "../services/api";
import TopHeader from "../components/TopHeader";

const inputCls = "w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20";
const labelCls = "block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5";

const FEATURE_COLUMNS = [
  ["can_view", "View"],
  ["can_create", "Create"],
  ["can_update", "Update"],
  ["can_delete", "Delete"],
  ["can_review", "Review"],
  ["can_approve", "Approve"],
  ["can_export", "Export"],
];

export default function RolesPage() {
  const [tab, setTab] = useState("roles");
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [roleForm, setRoleForm] = useState(null);
  const [roleError, setRoleError] = useState(null);
  const [roleSaving, setRoleSaving] = useState(false);

  const [assignForm, setAssignForm] = useState({ user: "", role: "" });
  const [assigning, setAssigning] = useState(false);
  const [assignError, setAssignError] = useState(null);
  const [assignSuccess, setAssignSuccess] = useState(null);

  const fetchAll = async () => {
    setLoading(true);
    const [rRes, pRes, aRes, uRes] = await Promise.allSettled([
      roleService.list(),
      permissionService.list(),
      roleService.assignments(),
      userService.list({ page_size: 100 }),
    ]);
    if (rRes.status === "fulfilled") setRoles(rRes.value.data.results || rRes.value.data || []);
    if (pRes.status === "fulfilled") setPermissions(pRes.value.data.results || pRes.value.data || []);
    if (aRes.status === "fulfilled") setAssignments(aRes.value.data || []);
    if (uRes.status === "fulfilled") setUsers(uRes.value.data.results || uRes.value.data || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const openRoleForm = (role) => {
    setRoleForm(role
      ? { id: role.id, role_key: role.role_key, display_name: role.display_name, description: role.description || "", is_active: role.is_active }
      : { id: null, role_key: "", display_name: "", description: "", is_active: true });
    setRoleError(null);
  };

  const saveRole = async (e) => {
    e.preventDefault();
    setRoleSaving(true);
    setRoleError(null);
    try {
      if (roleForm.id) await roleService.update(roleForm.id, roleForm);
      else await roleService.create(roleForm);
      setRoleForm(null);
      fetchAll();
    } catch (err) {
      setRoleError(getApiError(err, "Failed to save role."));
    } finally {
      setRoleSaving(false);
    }
  };

  const deleteRole = async (role) => {
    if (!window.confirm(`Delete role "${role.display_name}"?`)) return;
    try {
      await roleService.delete(role.id);
      fetchAll();
    } catch (err) {
      alert(getApiError(err, "Failed to delete role."));
    }
  };

  const handleAssign = async (e) => {
    e.preventDefault();
    setAssigning(true);
    setAssignError(null);
    setAssignSuccess(null);
    try {
      await roleService.assign({ user: Number(assignForm.user), role: Number(assignForm.role) });
      setAssignSuccess("Role assigned successfully.");
      setAssignForm({ user: "", role: "" });
      fetchAll();
    } catch (err) {
      setAssignError(getApiError(err, "Failed to assign role."));
    } finally {
      setAssigning(false);
    }
  };

  const permissionsByRole = {};
  permissions.forEach((p) => {
    if (!permissionsByRole[p.role]) permissionsByRole[p.role] = [];
    permissionsByRole[p.role].push(p);
  });

  const formatDate = (v) => (v ? new Date(v).toLocaleString() : "N/A");

  return (
    <div className="space-y-6">
      <TopHeader
        title="Roles & Permissions"
        subtitle="Manage RBAC roles, assignments and feature permissions"
        actions={
          tab === "roles" ? (
            <button
              onClick={() => openRoleForm(null)}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Role
            </button>
          ) : null
        }
      />

      <div className="flex gap-2 border-b border-outline-variant/20 flex-wrap">
        {[
          ["roles", "Roles"],
          ["assign", "Assign Roles"],
          ["permissions", "Permissions"],
          ["assignments", "Assignment History"],
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

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : tab === "roles" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {roles.length === 0 && (
            <div className="col-span-full bg-white rounded-xl soft-shadow border border-outline-variant/20 p-16 text-center">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">admin_panel_settings</span>
              <p className="text-on-surface-variant mt-3 text-sm">No roles found</p>
            </div>
          )}
          {roles.map((role) => (
            <div key={role.id} className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-on-surface text-sm">{role.display_name}</h3>
                  <p className="text-[11px] text-outline font-mono">{role.role_key}</p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => openRoleForm(role)} className="p-1.5 rounded-lg hover:bg-surface-container transition-colors" title="Edit">
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                  </button>
                  <button onClick={() => deleteRole(role)} className="p-1.5 rounded-lg hover:bg-red-50 transition-colors" title="Delete">
                    <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                  </button>
                </div>
              </div>
              {role.description && <p className="text-xs text-on-surface-variant">{role.description}</p>}
              <div className="mt-3 pt-3 border-t border-outline-variant/20 flex items-center justify-between">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${role.is_active ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-600"}`}>
                  {role.is_active ? "Active" : "Inactive"}
                </span>
                <span className="text-xs text-on-surface-variant">{(permissionsByRole[role.id] || []).length} permissions</span>
              </div>
            </div>
          ))}
        </div>
      ) : tab === "assign" ? (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6 max-w-lg">
          <h3 className="font-semibold text-on-surface text-sm mb-4">Assign Role to User</h3>
          <form onSubmit={handleAssign} className="space-y-4">
            {assignError && (
              <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                <span>{assignError}</span>
              </div>
            )}
            {assignSuccess && (
              <div className="px-4 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-sm text-emerald-800">
                {assignSuccess}
              </div>
            )}
            <div>
              <label className={labelCls()}>User *</label>
              <select required value={assignForm.user} onChange={(e) => setAssignForm({ ...assignForm, user: e.target.value })} className={inputCls()}>
                <option value="">Select user</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {[u.first_name, u.last_name].filter(Boolean).join(" ") || u.username} ({u.email})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelCls()}>Role *</label>
              <select required value={assignForm.role} onChange={(e) => setAssignForm({ ...assignForm, role: e.target.value })} className={inputCls()}>
                <option value="">Select role</option>
                {roles.filter((r) => r.is_active !== false).map((r) => (
                  <option key={r.id} value={r.id}>{r.display_name}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={assigning}
              className="w-full py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {assigning ? "Assigning..." : "Assign Role"}
            </button>
          </form>
        </div>
      ) : tab === "permissions" ? (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-outline-variant/20 text-on-surface-variant text-[11px] uppercase tracking-wider">
                  <th className="px-5 py-3 font-medium">Role</th>
                  <th className="px-5 py-3 font-medium">Feature</th>
                  {FEATURE_COLUMNS.map(([key, label]) => (
                    <th key={key} className="px-3 py-3 font-medium text-center">{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/10">
                {permissions.length === 0 && (
                  <tr>
                    <td colSpan={9} className="px-5 py-12 text-center text-on-surface-variant">No permissions configured.</td>
                  </tr>
                )}
                {permissions.map((p) => (
                  <tr key={p.id} className="hover:bg-surface-container-low/50 transition-colors">
                    <td className="px-5 py-3 font-medium text-on-surface">{p.role_name || "Role #" + p.role}</td>
                    <td className="px-5 py-3 text-on-surface-variant">{p.feature?.replace(/_/g, " ")}</td>
                    {FEATURE_COLUMNS.map(([key]) => (
                      <td key={key} className="px-3 py-3 text-center">
                        {p[key] ? (
                          <span className="material-symbols-outlined text-[18px] text-emerald-600">check_circle</span>
                        ) : (
                          <span className="material-symbols-outlined text-[18px] text-outline-variant">cancel</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-outline-variant/20 text-on-surface-variant text-[11px] uppercase tracking-wider">
                <th className="px-5 py-3 font-medium">User</th>
                <th className="px-5 py-3 font-medium">Role</th>
                <th className="px-5 py-3 font-medium">Previous Role</th>
                <th className="px-5 py-3 font-medium">Assigned By</th>
                <th className="px-5 py-3 font-medium">When</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {assignments.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-5 py-12 text-center text-on-surface-variant">No assignments yet.</td>
                </tr>
              )}
              {assignments.map((a) => (
                <tr key={a.id} className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-5 py-4">
                    <p className="font-medium text-on-surface">{a.user_email}</p>
                  </td>
                  <td className="px-5 py-4">
                    <span className="px-2 py-1 rounded bg-primary/10 text-primary text-[10px] font-bold">{a.role_name}</span>
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant">{a.previous_role_key || "-"}</td>
                  <td className="px-5 py-4 text-on-surface-variant">{a.assigned_by_email || "-"}</td>
                  <td className="px-5 py-4 text-on-surface-variant">{formatDate(a.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Role form modal */}
      {roleForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
          <div className="bg-white rounded-2xl w-full max-w-md soft-shadow">
            <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
              <h3 className="font-headline-lg text-lg font-bold text-on-surface">{roleForm.id ? "Edit Role" : "New Role"}</h3>
              <button onClick={() => setRoleForm(null)} className="p-2 rounded-lg hover:bg-surface-container transition-colors">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={saveRole} className="p-6 space-y-4">
              {roleError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                  <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                  <span>{roleError}</span>
                </div>
              )}
              <div>
                <label className={labelCls()}>Role Key *</label>
                <input
                  type="text"
                  required
                  disabled={!!roleForm.id}
                  value={roleForm.role_key}
                  onChange={(e) => setRoleForm({ ...roleForm, role_key: e.target.value })}
                  placeholder="e.g. data_analyst"
                  className={`${inputCls()} ${roleForm.id ? "opacity-50 cursor-not-allowed" : ""}`}
                />
              </div>
              <div>
                <label className={labelCls()}>Display Name *</label>
                <input
                  type="text"
                  required
                  value={roleForm.display_name}
                  onChange={(e) => setRoleForm({ ...roleForm, display_name: e.target.value })}
                  placeholder="e.g. Data Analyst"
                  className={inputCls()}
                />
              </div>
              <div>
                <label className={labelCls()}>Description</label>
                <textarea
                  rows={2}
                  value={roleForm.description}
                  onChange={(e) => setRoleForm({ ...roleForm, description: e.target.value })}
                  className={inputCls()}
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-on-surface">
                <input type="checkbox" checked={!!roleForm.is_active} onChange={(e) => setRoleForm({ ...roleForm, is_active: e.target.checked })} />
                Active role
              </label>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setRoleForm(null)} className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={roleSaving} className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50">
                  {roleSaving ? "Saving..." : "Save Role"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
