import React, { useState, useEffect } from "react";
import {
  roleService,
} from "../services/api";
import TopHeader from "../components/TopHeader";
import RolesTabBar from "../components/RolesTabBar";
import "../styles/pages/RolesPage.css";

export default function AssignmentHistoryPage() {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAssignments = async () => {
    setLoading(true);
    try {
      const res = await roleService.assignments();
      setAssignments(res.data || []);
    } catch (err) {
      console.error("Failed to load assignments:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignments();
  }, []);

  const formatDate = (v) => (v ? new Date(v).toLocaleString() : "N/A");

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
        <div className="roles-table-card soft-shadow">
          <table className="roles-table">
            <thead>
              <tr className="roles-thead-tr">
                <th className="roles-th">User</th>
                <th className="roles-th">Role</th>
                <th className="roles-th">Previous Role</th>
                <th className="roles-th">Assigned By</th>
                <th className="roles-th">When</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {assignments.length === 0 && (
                <tr>
                  <td colSpan={5} className="roles-empty-cell">No assignments yet.</td>
                </tr>
              )}
              {assignments.map((a) => (
                <tr key={a.id} className="roles-row">
                  <td className="roles-cell-lg">
                    <p className="font-medium text-on-surface">{a.user_email}</p>
                  </td>
                  <td className="roles-cell-lg">
                    <span className="roles-role-badge">{a.role_name}</span>
                  </td>
                  <td className="roles-cell-lg text-on-surface-variant">{a.previous_role_key || "-"}</td>
                  <td className="roles-cell-lg text-on-surface-variant">{a.assigned_by_email || "-"}</td>
                  <td className="roles-cell-lg text-on-surface-variant">{formatDate(a.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
