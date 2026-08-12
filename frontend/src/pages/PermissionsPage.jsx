import React, { useState, useEffect } from "react";
import {
  permissionService,
} from "../services/api";
import TopHeader from "../components/TopHeader";
import RolesTabBar from "../components/RolesTabBar";
import "../styles/pages/RolesPage.css";

const FEATURE_COLUMNS = [
  ["can_view", "View"],
  ["can_create", "Create"],
  ["can_update", "Update"],
  ["can_delete", "Delete"],
  ["can_review", "Review"],
  ["can_approve", "Approve"],
  ["can_export", "Export"],
];

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPermissions = async () => {
    setLoading(true);
    try {
      const res = await permissionService.list();
      setPermissions(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to load permissions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPermissions();
  }, []);

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
          <div className="overflow-x-auto">
            <table className="roles-table">
              <thead>
                <tr className="roles-thead-tr">
                  <th className="roles-th">Role</th>
                  <th className="roles-th">Feature</th>
                  {FEATURE_COLUMNS.map(([key, label]) => (
                    <th key={key} className="roles-th-center">{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/10">
                {permissions.length === 0 && (
                  <tr>
                    <td colSpan={9} className="roles-empty-cell">No permissions configured.</td>
                  </tr>
                )}
                {permissions.map((p) => (
                  <tr key={p.id} className="roles-row">
                    <td className="roles-cell font-medium text-on-surface">{p.role_name || "Role #" + p.role}</td>
                    <td className="roles-cell text-on-surface-variant">{p.feature?.replace(/_/g, " ")}</td>
                    {FEATURE_COLUMNS.map(([key]) => (
                      <td key={key} className="roles-cell-center">
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
      )}
    </div>
  );
}
