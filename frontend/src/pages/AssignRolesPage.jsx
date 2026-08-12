import React, { useState, useEffect } from "react";
import {
  roleService,
  userService,
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

export default function AssignRolesPage() {
  const [roles, setRoles] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [assignForm, setAssignForm] = useState({ user: "", role: "" });
  const [assigning, setAssigning] = useState(false);
  const [assignError, setAssignError] = useState(null);
  const [assignSuccess, setAssignSuccess] = useState(null);

  const fetchAll = async () => {
    setLoading(true);
    const [rRes, uRes] = await Promise.allSettled([
      roleService.list(),
      userService.list({ page_size: 100 }),
    ]);
    if (rRes.status === "fulfilled") setRoles(rRes.value.data.results || rRes.value.data || []);
    if (uRes.status === "fulfilled") setUsers(uRes.value.data.results || uRes.value.data || []);
    setLoading(false);
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleAssign = async (e) => {
    e.preventDefault();
    setAssigning(true);
    setAssignError(null);
    setAssignSuccess(null);
    try {
      await roleService.assign({ user: Number(assignForm.user), role: Number(assignForm.role) });
      setAssignSuccess("Role assigned successfully.");
      setAssignForm({ user: "", role: "" });
    } catch (err) {
      setAssignError(getApiError(err, "Failed to assign role."));
    } finally {
      setAssigning(false);
    }
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="Roles & Permissions"
        subtitle="Manage RBAC roles, assignments and feature permissions"
      />

      <RolesTabBar />

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="roles-assign-card soft-shadow">
          <h3 className="roles-assign-title">Assign Role to User</h3>
          <form onSubmit={handleAssign} className="space-y-4">
            {assignError && (
              <div className="roles-error">
                <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
                <span>{assignError}</span>
              </div>
            )}
            {assignSuccess && (
              <div className="roles-success">
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
              className="roles-submit-btn-wide"
            >
              {assigning ? "Assigning..." : "Assign Role"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
