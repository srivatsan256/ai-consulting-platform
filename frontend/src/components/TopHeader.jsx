import React from "react";
import "./TopHeader.css";

export default function TopHeader({ title, subtitle, actions }) {
  return (
    <div className="topheader-root">
      <div>
        {subtitle && (
          <span className="topheader-subtitle">
            {subtitle}
          </span>
        )}
        <h2 className="topheader-title">
          {title}
        </h2>
      </div>
      {actions && <div className="topheader-actions">{actions}</div>}
    </div>
  );
}
