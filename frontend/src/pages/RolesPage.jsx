import React, { useState, useEffect } from "react";
import {
  roleService,
  permissionService,
  getApiError,
} from "../services/api";
import TopHeader from "../components/TopHeader";
import RolesTabBar from "../components/RolesTabBar";
import "../styles/pages/RolesPage.css";

function labelCls() {
  return "roles-label";
}

function inputCls() {
  return "roles-input";
}

export default function RolesPage() {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const [roleForm, setRoleForm] = useState(null);
  const [roleError, setRoleError] = useState(null);
  const [roleSaving, setRoleSaving] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    const [rRes, pRes] = await Promise.allSettled([
      roleService.list(),
      permissionService.list(),
    ]);
    if (rRes.status === "fulfilled") setRoles(rRes.value.data.results || rRes.value.data || []);
    if (pRes.status === "fulfilled") setPermissions(pRes.value.data.results || pRes.value.data || []);
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

  const permissionsByRole = {};
  permissions.forEach((p) => {
    if (!permissionsByRole[p.role]) permissionsByRole[p.role] = [];
    permissionsByRole[p.role].push(p);
  });

  return (
    <div className="space-y-6">
      <TopHeader
        title="Roles & Permissions"
        subtitle="Manage RBAC roles, assignments and feature permissions"
        actions={
          <button
            onClick={() => openRoleForm(null)}
            className="roles-primary-btn"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            New Role
          </button>
        }
      />

      <RolesTabBar />

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {roles.length === 0 && (
            <div className="roles-empty-card">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">admin_panel_settings</span>
              <p className="text-on-surface-variant mt-3 text-sm">No roles found</p>
            </div>
          )}
          {roles.map((role) => (
            <div key={role.id} className="roles-card soft-shadow">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="roles-h3">{role.display_name}</h3>
                  <p className="text-[11px] text-outline font-mono">{role.role_key}</p>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => openRoleForm(role)} className="roles-icon-btn" title="Edit">
                    <span className="material-symbols-outlined text-[18px] text-outline-variant">edit</span>
                  </button>
                  <button onClick={() => deleteRole(role)} className="roles-icon-btn-red" title="Delete">
                    <span className="material-symbols-outlined text-[18px] text-red-500">delete</span>
                  </button>
                </div>
              </div>
              {role.description && <p className="text-xs text-on-surface-variant">{role.description}</p>}
              <div className="roles-card-footer">
                <span className={`roles-mini-badge ${role.is_active ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-600"}`}>
                  {role.is_active ? "Active" : "Inactive"}
                </span>
                <span className="text-xs text-on-surface-variant">{(permissionsByRole[role.id] || []).length} permissions</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Role form modal */}
      {roleForm && (
        <div className="roles-overlay">
          <div className="roles-modal-panel soft-shadow">
            <div className="roles-modal-header">
              <h3 className="roles-modal-title">{roleForm.id ? "Edit Role" : "New Role"}</h3>
              <button onClick={() => setRoleForm(null)} className="roles-close-btn">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={saveRole} className="roles-modal-body">
              {roleError && (
                <div className="roles-error">
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
                <button type="button" onClick={() => setRoleForm(null)} className="roles-cancel-btn">
                  Cancel
                </button>
                <button type="submit" disabled={roleSaving} className="roles-submit-btn">
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
