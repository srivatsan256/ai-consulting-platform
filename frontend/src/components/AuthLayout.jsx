import React from "react";
import AuroraOverlay from "./AuroraOverlay";
import { AUTH_BACKGROUND_STYLE, GLASS_CARD } from "../constants/auth";
import "../styles/components/AuthLayout.css";

export default function AuthLayout({ children }) {
  return (
    <div className="authlayout-root">
      {/* Full-page Background Image */}
      <div className="authlayout-bg" style={AUTH_BACKGROUND_STYLE} />
      {/* Dark overlay for readability */}
      <div className="authlayout-overlay" />
      {/* Animated aurora glow */}
      <AuroraOverlay />

      {/* Content */}
      <div className="authlayout-content">
        {/* Left Brand Content */}
        <div className="authlayout-brand">
          <div className="authlayout-brand-inner">
            <div className="authlayout-brand-head">
              <span
                className="material-symbols-outlined authlayout-brand-icon"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                dataset
              </span>
              <div>
                <h1 className="authlayout-brand-title">
                  RequirementAI
                </h1>
                <p className="authlayout-brand-sub">
                  Consulting Delivery OS
                </p>
              </div>
            </div>

            <h2 className="authlayout-brand-h2">
              AI-powered consulting lifecycle management
            </h2>
            <p className="authlayout-brand-p">
              Gate every phase from onboarding through governance with expert AI verification and
              enterprise-grade deliverables.
            </p>

            <div className="authlayout-feature-grid">
              {[
                { icon: "person_add", label: "Client Onboarding" },
                { icon: "query_stats", label: "Smart Discovery" },
                { icon: "verified_user", label: "Gated Verification" },
                { icon: "auto_awesome", label: "AI Readiness Score" },
                { icon: "smart_toy", label: "AI Consultant" },
                { icon: "assignment_turned_in", label: "Document Generation" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="authlayout-feature-item"
                >
                  <span className="material-symbols-outlined authlayout-feature-icon">
                    {item.icon}
                  </span>
                  <span className="authlayout-feature-label">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Form panel */}
        <div className="authlayout-form-wrap">
          <div className="authlayout-form-inner">
            {/* Mobile logo */}
            <div className="authlayout-mobile-logo">
              <h1 className="authlayout-mobile-title">
                RequirementAI
              </h1>
              <p className="authlayout-mobile-sub">
                Consulting Delivery OS
              </p>
            </div>
            <div className={GLASS_CARD}>{children}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
