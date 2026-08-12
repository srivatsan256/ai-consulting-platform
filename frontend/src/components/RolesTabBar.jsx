import React from "react";
import { NavLink } from "react-router-dom";

export default function RolesTabBar() {
  const tabs = [
    { path: "/roles", label: "Roles" },
    { path: "/roles/assign", label: "Assign Roles" },
    { path: "/roles/permissions", label: "Permissions" },
    { path: "/roles/history", label: "Assignment History" },
  ];

  return (
    <div className="flex gap-2 border-b border-outline-variant/20 flex-wrap">
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          end
          className={({ isActive }) =>
            `roles-tab ${isActive ? "roles-tab-active" : "roles-tab-idle"}`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </div>
  );
}
