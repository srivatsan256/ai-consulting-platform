import React, { useState } from "react";
import Stepper, { Step } from "../components/bits/Stepper";
import AuroraOverlay from "../components/AuroraOverlay";
import {
  AUTH_BACKGROUND_STYLE,
  GLASS_CARD,
  GLASS_INPUT,
  GLASS_LABEL,
  GLASS_ICON,
  GLASS_ERROR,
} from "../constants/auth";
import "./LoginPage.css";

export default function LoginPage({ onLogin, onShowSignup, onForgotPassword }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("admin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      await onLogin(email, password, role);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Invalid email or password.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = async () => {
    const ssoEmail =
      role === "client" ? "client_admin@acmecorp.com" : "companyadmin@requirementai.com";
    setEmail(ssoEmail);
    setPassword("password123");
    setError(null);
    setLoading(true);
    try {
      await onLogin(ssoEmail, "password123", role);
    } catch (err) {
      setError(err?.response?.data?.detail || "SSO login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const isLastStep = currentStep === 2;

  const nextButtonProps = isLastStep
    ? {
        onClick: handleSubmit,
        disabled: loading,
        className:
          "flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-fuchsia-500/40 transition-all hover:opacity-90 active:opacity-80 disabled:opacity-60 disabled:cursor-not-allowed",
        children: loading ? (
          <>
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Signing in...
          </>
        ) : (
          "Sign In"
        ),
      }
    : {
        className:
          "flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 via-fuchsia-500 to-violet-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-fuchsia-500/40 transition-all hover:opacity-90 active:opacity-80",
        children: "Continue",
      };

  return (
    <div className="lp-page">
      {/* Full-page Background Image */}
      <div className="lp-bg" style={AUTH_BACKGROUND_STYLE} />
      {/* Dark overlay for readability */}
      <div className="lp-overlay" />
      {/* Animated aurora glow */}
      <AuroraOverlay />

      {/* Content */}
      <div className="lp-content">
        {/* Left Brand Content */}
        <div className="lp-brand">
          <div className="lp-brand-inner">
            <div className="lp-brand-head">
              <span
                className="material-symbols-outlined lp-brand-icon"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                dataset
              </span>
              <div>
                <h1 className="lp-brand-title">RequirementAI</h1>
                <p className="lp-brand-sub">Consulting Delivery OS</p>
              </div>
            </div>

            <h2 className="lp-brand-h2">
              AI-powered consulting lifecycle management
            </h2>
            <p className="lp-brand-p">
              Gate every phase from onboarding through governance with expert AI verification and
              enterprise-grade deliverables.
            </p>

            <div className="lp-feature-grid">
              {[
                { icon: "person_add", label: "Client Onboarding" },
                { icon: "query_stats", label: "Smart Discovery" },
                { icon: "verified_user", label: "Gated Verification" },
                { icon: "auto_awesome", label: "AI Readiness Score" },
                { icon: "smart_toy", label: "AI Consultant" },
                { icon: "assignment_turned_in", label: "Document Generation" },
              ].map((item) => (
                <div key={item.label} className="lp-feature-item">
                  <span className="material-symbols-outlined lp-feature-icon">
                    {item.icon}
                  </span>
                  <span className="lp-feature-label">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Login form - Right side */}
        <div className="lp-form-wrap">
          <div className="lp-form-inner">
            {/* Mobile logo */}
            <div className="lp-mobile-logo">
              <h1 className="lp-mobile-title">RequirementAI</h1>
              <p className="lp-mobile-sub">Consulting Delivery OS</p>
            </div>

            <Stepper
              initialStep={1}
              onStepChange={setCurrentStep}
              nextButtonText="Continue"
              nextButtonProps={nextButtonProps}
              stepContainerClassName={`${GLASS_CARD} overflow-hidden`}
            >
              <Step>
                {/* Step 1: Account type */}
                <h2 className="lp-step-h2">Welcome back</h2>
                <p className="lp-step-p">
                  Choose your account type to get started.
                </p>

                {/* Role Toggle */}
                <div className="lp-toggle">
                  <button
                    type="button"
                    onClick={() => setRole("admin")}
                    className={`lp-toggle-btn ${
                      role === "admin"
                        ? "lp-toggle-btn-active"
                        : "lp-toggle-btn-inactive"
                    }`}
                  >
                    <span className="material-symbols-outlined lp-toggle-icon">
                      admin_panel_settings
                    </span>
                    Consulting Team
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole("client")}
                    className={`lp-toggle-btn ${
                      role === "client"
                        ? "lp-toggle-btn-active"
                        : "lp-toggle-btn-inactive"
                    }`}
                  >
                    <span className="material-symbols-outlined lp-toggle-icon">business</span>
                    Client
                  </button>
                </div>

                {/* Divider */}
                <div className="lp-divider">
                  <div className="lp-divider-line" />
                  <span className="lp-divider-text">or continue with</span>
                  <div className="lp-divider-line" />
                </div>

                {/* SSO Buttons */}
                <div className="lp-sso">
                  <button
                    type="button"
                    onClick={handleSSOLogin}
                    disabled={loading}
                    className="lp-sso-ms"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 23 23" fill="none">
                      <rect x="1" y="1" width="10" height="10" fill="#F25022" />
                      <rect x="12" y="1" width="10" height="10" fill="#7FBA00" />
                      <rect x="1" y="12" width="10" height="10" fill="#00A4EF" />
                      <rect x="12" y="12" width="10" height="10" fill="#FFB900" />
                    </svg>
                    Sign in with Microsoft
                  </button>

                  <button
                    type="button"
                    onClick={handleSSOLogin}
                    disabled={loading}
                    className="lp-sso-google"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                      <path
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        fill="#4285F4"
                      />
                      <path
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        fill="#34A853"
                      />
                      <path
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                        fill="#FBBC05"
                      />
                      <path
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        fill="#EA4335"
                      />
                    </svg>
                    Sign in with Google
                  </button>
                </div>

                <p className="lp-sso-note">
                  Enterprise SSO available · Contact IT for provisioning
                </p>
              </Step>

              <Step>
                {/* Step 2: Credentials */}
                <h2 className="lp-step-h2">
                  {role === "client" ? "Client sign in" : "Consultant sign in"}
                </h2>
                <p className="lp-step-p">
                  Enter your credentials to access your workspace.
                </p>

                <div className="mt-6 space-y-5">
                  <div>
                    <label className={GLASS_LABEL}>
                      {role === "client" ? "Company Email" : "Work Email"}
                    </label>
                    <div className="lp-input-wrap">
                      <span className={`material-symbols-outlined ${GLASS_ICON}`}>mail</span>
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder={
                          role === "admin" ? "consultant@company.com" : "john@acmecorp.com"
                        }
                        className={GLASS_INPUT}
                      />
                    </div>
                  </div>

                  <div>
                    <label className={GLASS_LABEL}>Password</label>
                    <div className="lp-input-wrap">
                      <span className={`material-symbols-outlined ${GLASS_ICON}`}>lock</span>
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !loading) handleSubmit();
                        }}
                        placeholder="••••••••"
                        className={GLASS_INPUT}
                      />
                    </div>
                  </div>

                  <div className="lp-remember-row">
                    <label className="lp-remember">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="lp-checkbox"
                      />
                      Remember me
                    </label>
                    <button
                      type="button"
                      onClick={onForgotPassword}
                      className="lp-forgot"
                    >
                      Forgot password?
                    </button>
                  </div>

                  {error && (
                    <div className={GLASS_ERROR}>
                      <span className="material-symbols-outlined text-[18px] text-red-300">
                        error
                      </span>
                      <span>{error}</span>
                    </div>
                  )}
                </div>

                <p className="lp-footer">
                  New to RequirementAI?{" "}
                  <button
                    type="button"
                    onClick={onShowSignup}
                    className="lp-forgot"
                  >
                    Create an account
                  </button>
                </p>
              </Step>
            </Stepper>
          </div>
        </div>
      </div>
    </div>
  );
}
