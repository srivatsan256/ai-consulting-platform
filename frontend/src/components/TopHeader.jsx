import React from "react";

export default function TopHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-center justify-between mb-8">
      <div>
        {subtitle && (
          <span className="font-label-md text-primary uppercase tracking-tighter text-[11px]">
            {subtitle}
          </span>
        )}
        <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-1">
          {title}
        </h2>
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
}
