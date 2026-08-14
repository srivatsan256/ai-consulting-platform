import React from "react";
import { Link } from "react-router-dom";
import AuroraOverlay from "./AuroraOverlay";
import "../styles/components/OnboardingOne.css";
import {
  AUTH_BACKGROUND_STYLE,
  GLASS_INPUT,
  GLASS_INPUT_ERROR,
  GLASS_LABEL,
  GLASS_ICON,
  GLASS_BUTTON,
  GLASS_ERROR,
} from "../constants/auth";

export default function OnboardingOne({
  accountType,
  onToggleAccountType,
  values,
  onChange,
  roles,
  loading,
  error,
  fieldErrors,
  onSubmit,
  onShowLogin,
}) {
  const {
    firstName,
    lastName,
    email,
    companyName,
    role,
    password,
    confirmPassword,
    acceptedTerms,
  } = values;

  const isClient = accountType === "client";
  const fullName = [firstName, lastName].filter(Boolean).join(" ").trim();
  const displayName = fullName || "Your name";
  const initials =
    [firstName, lastName]
      .map((n) => (n || "").trim().charAt(0).toUpperCase())
      .filter(Boolean)
      .join("") || "RA";

  const workspaceName = (companyName || "").trim() || (isClient ? "Your company" : "Your team");
  const workspaceInitials =
    workspaceName
      .split(/\s+/)
      .slice(0, 2)
      .map((w) => w.charAt(0).toUpperCase())
      .join("") || "RA";

  const roleLabel = isClient
    ? "Workspace Admin"
    : roles.find((r) => r.key === role)?.label || "Consultant";

  const profileComplete = Boolean(firstName && lastName && email);
  const hasErrors = (field) => Boolean(fieldErrors[field]);
  const inputClass = (hasError) => (hasError ? GLASS_INPUT_ERROR : GLASS_INPUT);

  const toggleBtn = (active) =>
    `flex-1 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
      active
        ? "bg-gradient-to-r from-violet-600 to-fuchsia-500 text-white shadow-md shadow-fuchsia-500/30"
        : "text-white/70 hover:bg-white/10 hover:text-white"
    }`;

  return (
    <div className="onboarding-root">
      <div className="absolute inset-0 bg-cover bg-center" style={AUTH_BACKGROUND_STYLE} />
      <div className="absolute inset-0 bg-gradient-to-br from-black/80 via-black/65 to-black/80" />
      <AuroraOverlay />

      <div className="relative z-10 flex w-full min-h-screen flex-col lg:flex-row">
        {/* ── Left: profile setup ─────────────────────────────── */}
        <div className="w-full lg:w-[46%] xl:w-[44%] px-6 sm:px-10 lg:px-14 py-10 lg:py-16">
          <div className="max-w-lg mx-auto">
            {/* Brand */}
            <div className="flex items-center gap-3 mb-10">
              <span
                className="material-symbols-outlined text-primary-fixed text-[34px]"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                dataset
              </span>
              <div>
                <h1 className="font-display-lg text-2xl font-bold text-white">RequirementAI</h1>
                <p className="font-label-md text-[10px] uppercase tracking-widest text-white/70">
                  Consulting Delivery OS
                </p>
              </div>
            </div>

            {/* Step hint */}
            <div className="mb-6">
              <div className="flex items-center justify-between font-label-md text-[11px] uppercase tracking-wider text-white/60 mb-2">
                <span>Profile setup</span>
                <span>Step 1 of 3</span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full w-1/3 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500" />
              </div>
            </div>

            <h2 className="font-headline-lg text-3xl font-bold text-white">Set up your profile</h2>
            <p className="text-white/70 text-sm mt-2">
              Welcome, {fullName || "there"}. Here's how you'll appear in the workspace directory.
            </p>

            {/* Role Toggle */}
            <div className="mt-6 bg-white/10 rounded-xl p-1 flex gap-1 border border-white/15">
              <button
                type="button"
                onClick={() => onToggleAccountType("client")}
                className={toggleBtn(isClient)}
              >
                <span className="material-symbols-outlined text-[18px]">business</span>
                Client
              </button>
              <button
                type="button"
                onClick={() => onToggleAccountType("consultant")}
                className={toggleBtn(!isClient)}
              >
                <span className="material-symbols-outlined text-[18px]">admin_panel_settings</span>
                Consulting Team
              </button>
            </div>

            <form onSubmit={onSubmit} className="mt-6 space-y-5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={GLASS_LABEL}>First Name</label>
                  <div className="relative">
                    <span className={`material-symbols-outlined ${GLASS_ICON}`}>person</span>
                    <input
                      type="text"
                      value={firstName}
                      onChange={(e) => onChange("firstName", e.target.value)}
                      placeholder="John"
                      required
                      className={inputClass(hasErrors("first_name"))}
                    />
                  </div>
                  {fieldErrors.first_name && (
                    <p className="mt-1 text-xs text-red-300">{fieldErrors.first_name}</p>
                  )}
                </div>
                <div>
                  <label className={GLASS_LABEL}>Last Name</label>
                  <div className="relative">
                    <span className={`material-symbols-outlined ${GLASS_ICON}`}>person</span>
                    <input
                      type="text"
                      value={lastName}
                      onChange={(e) => onChange("lastName", e.target.value)}
                      placeholder="Smith"
                      required
                      className={inputClass(hasErrors("last_name"))}
                    />
                  </div>
                  {fieldErrors.last_name && (
                    <p className="mt-1 text-xs text-red-300">{fieldErrors.last_name}</p>
                  )}
                </div>
              </div>

              <div>
                <label className={GLASS_LABEL}>
                  {isClient ? "Company Email" : "Work Email"}
                </label>
                <div className="relative">
                  <span className={`material-symbols-outlined ${GLASS_ICON}`}>mail</span>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => onChange("email", e.target.value)}
                    placeholder={isClient ? "john@acmecorp.com" : "you@company.com"}
                    required
                    className={inputClass(hasErrors("email"))}
                  />
                </div>
                {fieldErrors.email && (
                  <p className="mt-1 text-xs text-red-300">{fieldErrors.email}</p>
                )}
              </div>

              {isClient ? (
                <div>
                  <label className={GLASS_LABEL}>Company Name</label>
                  <div className="relative">
                    <span className={`material-symbols-outlined ${GLASS_ICON}`}>business</span>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => onChange("companyName", e.target.value)}
                      placeholder="Acme Corp"
                      required
                      className={inputClass(hasErrors("company_name"))}
                    />
                  </div>
                  {fieldErrors.company_name && (
                    <p className="mt-1 text-xs text-red-300">{fieldErrors.company_name}</p>
                  )}
                </div>
              ) : (
                <div>
                  <label className={GLASS_LABEL}>Your Role</label>
                  <div className="relative">
                    <span className={`material-symbols-outlined ${GLASS_ICON}`}>badge</span>
                    <select
                      value={role}
                      onChange={(e) => onChange("role", e.target.value)}
                      required
                      className={`${inputClass(hasErrors("role"))} ${role ? "" : "text-white/40"}`}
                    >
                      <option value="" disabled>
                        Select your role
                      </option>
                      {roles.map((r) => (
                        <option key={r.key} value={r.key}>
                          {r.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  {fieldErrors.role && (
                    <p className="mt-1 text-xs text-red-300">{fieldErrors.role}</p>
                  )}
                </div>
              )}

              <div>
                <label className={GLASS_LABEL}>Password</label>
                <div className="relative">
                  <span className={`material-symbols-outlined ${GLASS_ICON}`}>lock</span>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => onChange("password", e.target.value)}
                    placeholder="At least 8 characters"
                    required
                    minLength={8}
                    className={inputClass(hasErrors("password"))}
                  />
                </div>
                {fieldErrors.password && (
                  <p className="mt-1 text-xs text-red-300">{fieldErrors.password}</p>
                )}
              </div>

              <div>
                <label className={GLASS_LABEL}>Confirm Password</label>
                <div className="relative">
                  <span className={`material-symbols-outlined ${GLASS_ICON}`}>lock</span>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => onChange("confirmPassword", e.target.value)}
                    placeholder="Re-enter your password"
                    required
                    className={inputClass(hasErrors("confirm_password"))}
                  />
                </div>
                {fieldErrors.confirm_password && (
                  <p className="mt-1 text-xs text-red-300">{fieldErrors.confirm_password}</p>
                )}
              </div>

              <label className="flex items-start gap-2 text-sm text-white/70 cursor-pointer">
                <input
                  type="checkbox"
                  checked={acceptedTerms}
                  onChange={(e) => onChange("acceptedTerms", e.target.checked)}
                  className="mt-0.5 rounded border-white/40 bg-white/10 text-fuchsia-400 focus:ring-fuchsia-400/40 focus:ring-2"
                />
                <span>
                  I agree to the{" "}
                  <Link to="/terms-of-service" className="text-fuchsia-300 font-medium hover:underline">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link to="/privacy-policy" className="text-fuchsia-300 font-medium hover:underline">
                    Privacy Policy
                  </Link>
                </span>
              </label>

              {error && (
                <div className={GLASS_ERROR}>
                  <span className="material-symbols-outlined text-[18px] text-red-300">error</span>
                  <span>{error}</span>
                </div>
              )}

              <button type="submit" disabled={loading} className={GLASS_BUTTON}>
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Creating account...
                  </>
                ) : (
                  <>
                    {isClient ? "Create Client Account" : "Create Consultant Account"}
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </form>

            <p className="text-center text-xs text-white/60 mt-6">
              Already have an account?{" "}
              <button type="button" onClick={onShowLogin} className="text-fuchsia-300 font-medium hover:underline">
                Sign in
              </button>
            </p>

            <p className="text-center text-xs text-white/50 mt-4">
              Enterprise SSO available · Contact IT for provisioning
            </p>
          </div>
        </div>

        {/* ── Right: live directory preview ───────────────────── */}
        <div className="hidden lg:flex lg:w-[54%] xl:w-[56%] items-center justify-center px-10 relative">
          <div className="w-full max-w-md">
            <div className="w-full rounded-3xl border border-white/15 bg-white/[0.07] backdrop-blur-2xl shadow-2xl shadow-black/40 overflow-hidden">
              {/* Window chrome */}
              <div className="flex items-center justify-between px-5 py-3 border-b border-white/10">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-400/80" />
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-400/80" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/80" />
                </div>
                <div className="flex items-center gap-2 text-white/60 text-[11px] font-label-md uppercase tracking-wider">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live
                </div>
              </div>

              <div className="p-6">
                {/* Workspace header */}
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center font-headline-lg font-bold text-white">
                    {workspaceInitials}
                  </div>
                  <div className="min-w-0">
                    <p className="font-headline-lg font-semibold text-white truncate">{workspaceName}</p>
                    <p className="text-white/50 text-xs">Workspace directory · 3 members</p>
                  </div>
                </div>

                {/* Decorative search */}
                <div className="mt-5 flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/40 text-sm">
                  <span className="material-symbols-outlined text-[16px]">search</span>
                  Search members
                </div>

                {/* Directory list */}
                <div className="mt-4 space-y-2.5">
                  {/* Current user (live) */}
                  <div className="flex items-center gap-3 p-3 rounded-xl border border-white/15 bg-white/[0.06]">
                    <div className="relative shrink-0">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center font-headline-lg font-bold text-white text-sm">
                        {initials}
                      </div>
                      <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#0a0e1c]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-white font-semibold text-sm truncate">{displayName}</p>
                        <span className="shrink-0 px-1.5 py-0.5 rounded bg-fuchsia-500/20 border border-fuchsia-400/30 text-fuchsia-200 text-[10px] font-bold uppercase tracking-wider">
                          You
                        </span>
                      </div>
                      <p className="text-white/60 text-xs truncate">{roleLabel}</p>
                      <p className="text-white/40 text-xs truncate">{email || "you@company.com"}</p>
                    </div>
                    <span className="shrink-0 inline-flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-400/15 border border-emerald-400/30 text-emerald-300 text-[10px] font-bold uppercase tracking-wider">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      {profileComplete ? "Active" : "Setting up"}
                    </span>
                  </div>

                  {/* Teammate slots */}
                  {[0, 1].map((i) => (
                    <div key={i} className="flex items-center gap-3 p-3 rounded-xl border border-dashed border-white/20">
                      <div className="w-10 h-10 rounded-lg border border-dashed border-white/30 flex items-center justify-center shrink-0">
                        <span className="material-symbols-outlined text-[18px] text-white/40">add</span>
                      </div>
                      <div className="flex-1">
                        <p className="text-white/60 text-sm font-medium">Invite teammate</p>
                        <p className="text-white/35 text-xs">Shows up here once they join</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer note */}
              <div className="px-6 py-4 border-t border-white/10 bg-white/[0.03]">
                <p className="text-white/50 text-xs flex items-center gap-2">
                  <span className="material-symbols-outlined text-[16px] text-fuchsia-300">visibility</span>
                  This is how teammates will see you in the directory.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
