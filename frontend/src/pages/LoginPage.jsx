import React, { useState } from "react";

export default function LoginPage({ onLogin, onShowSignup, onForgotPassword }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("admin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
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
    // Simulate SSO login using a seeded account
    const ssoEmail = role === "client" ? "client_admin@acmecorp.com" : "companyadmin@requirementai.com";
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

      {/* Login form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8">
            <h1 className="font-display-lg text-2xl font-bold text-on-surface">RequirementAI</h1>
            <p className="text-outline-variant text-xs uppercase tracking-widest mt-1">Consulting Delivery OS</p>
          </div>

          <div className="bg-white p-8 rounded-2xl soft-shadow border border-outline-variant/20">
            <h2 className="font-headline-lg text-2xl font-bold text-on-surface">Welcome back</h2>
            <p className="text-on-surface-variant text-sm mt-1">Sign in to your workspace</p>

            {/* Role Toggle */}
            <div className="mt-6 bg-surface-container-low rounded-xl p-1 flex gap-1">
              <button
                type="button"
                onClick={() => setRole("admin")}
                className={`flex-1 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                  role === "admin"
                    ? "bg-primary text-on-primary shadow-md"
                    : "text-on-surface-variant hover:bg-surface-container"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">admin_panel_settings</span>
                Consulting Team
              </button>
              <button
                type="button"
                onClick={() => setRole("client")}
                className={`flex-1 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                  role === "client"
                    ? "bg-primary text-on-primary shadow-md"
                    : "text-on-surface-variant hover:bg-surface-container"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">business</span>
                Client
              </button>
            </div>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                  {role === "client" ? "Company Email" : "Work Email"}
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                    mail
                  </span>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={role === "admin" ? "consultant@company.com" : "john@acmecorp.com"}
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                  Password
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                    lock
                  </span>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-on-surface-variant cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-outline-variant text-primary focus:ring-primary" />
                  Remember me
                </label>
                <button type="button" onClick={onForgotPassword} className="text-primary font-medium hover:underline">
                  Forgot password?
                </button>
              </div>

              {error && (
                <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
                  <span className="material-symbols-outlined text-[18px] text-error">error</span>
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
                    Signing in...
                  </>
                ) : (
                  role === "admin"
                    ? "Sign In as Consultant"
                    : "Sign In as Client"
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-4 my-6">
              <div className="flex-1 h-px bg-outline-variant/40"></div>
              <span className="text-xs text-on-surface-variant">or continue with</span>
              <div className="flex-1 h-px bg-outline-variant/40"></div>
            </div>

            {/* SSO Buttons */}
            <div className="space-y-3">
              <button
                type="button"
                onClick={handleSSOLogin}
                disabled={loading}
                className="w-full py-3 bg-[#2F2F2F] text-white rounded-xl font-bold text-sm hover:bg-[#1a1a1a] transition-all flex items-center justify-center gap-3 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" viewBox="0 0 23 23" fill="none">
                  <rect x="1" y="1" width="10" height="10" fill="#F25022"/>
                  <rect x="12" y="1" width="10" height="10" fill="#7FBA00"/>
                  <rect x="1" y="12" width="10" height="10" fill="#00A4EF"/>
                  <rect x="12" y="12" width="10" height="10" fill="#FFB900"/>
                </svg>
                Sign in with Microsoft
              </button>
              <button
                type="button"
                onClick={handleSSOLogin}
                disabled={loading}
                className="w-full py-3 bg-white border border-outline-variant/40 text-on-surface rounded-xl font-bold text-sm hover:bg-surface-container-low transition-all flex items-center justify-center gap-3 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Sign in with Google
              </button>
            </div>

            <p className="text-center text-xs text-on-surface-variant mt-6">
              Enterprise SSO available · Contact IT for provisioning
            </p>
            <p className="text-center text-xs text-on-surface-variant mt-6">
              New to RequirementAI?{" "}
              <button
                type="button"
                onClick={onShowSignup}
                className="text-primary font-medium hover:underline"
              >
                Create an account
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
