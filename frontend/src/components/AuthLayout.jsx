import React from "react";

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-background flex">
      {/* Brand panel */}
      <div className="hidden lg:flex lg:w-[45%] bg-on-surface relative overflow-hidden items-center justify-center p-12">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-64 h-64 rounded-full bg-primary blur-3xl" />
          <div className="absolute bottom-20 right-10 w-80 h-80 rounded-full bg-primary-container blur-3xl" />
        </div>
        <div className="relative z-10 max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <span
              className="material-symbols-outlined text-primary-fixed text-[40px]"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              dataset
            </span>
            <div>
              <h1 className="font-display-lg text-[28px] font-bold text-surface-bright">RequirementAI</h1>
              <p className="text-outline-variant font-label-md text-[10px] uppercase tracking-widest">
                Consulting Delivery OS
              </p>
            </div>
          </div>
          <h2 className="font-headline-lg text-3xl font-bold text-surface-bright leading-tight">
            AI-powered consulting lifecycle management
          </h2>
          <p className="text-outline-variant mt-4 text-sm leading-relaxed">
            Gate every phase from onboarding through governance with expert AI verification and
            enterprise-grade deliverables.
          </p>
          <div className="mt-10 grid grid-cols-2 gap-4">
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
                className="flex items-center gap-2 px-4 py-3 rounded-xl bg-surface-container-highest/10 border border-outline-variant/20"
              >
                <span className="material-symbols-outlined text-primary-fixed text-[20px]">{item.icon}</span>
                <span className="text-surface-bright text-sm font-medium">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8">
            <h1 className="font-display-lg text-2xl font-bold text-on-surface">RequirementAI</h1>
            <p className="text-outline-variant text-xs uppercase tracking-widest mt-1">Consulting Delivery OS</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
