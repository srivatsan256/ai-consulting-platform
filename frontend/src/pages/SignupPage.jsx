import React, { useState } from "react";

export default function SignupPage({ onRegister, onShowLogin }) {
  const [accountType, setAccountType] = useState("client");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});

  const extractFieldErrors = (err) => {
    const detail =
      err?.response?.data?.detail ||
      err?.response?.data?.message ||
      err?.response?.data?.non_field_errors;
    const fields = err?.response?.data || {};
    const fieldMap = {};
    Object.entries(fields).forEach(([key, value]) => {
      if (key === "detail" || key === "message" || key === "non_field_errors") return;
      fieldMap[key] = Array.isArray(value) ? value[0] : value;
    });
    return { detail, fieldMap };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    if (!acceptedTerms) {
      setError("Please accept the terms and conditions to continue.");
      return;
    }

    setLoading(true);
    try {
      await onRegister({
        first_name: firstName,
        last_name: lastName,
        email,
        company_name: companyName,
        password,
        confirm_password: confirmPassword,
        account_type: accountType,
      });
    } catch (err) {
      const { detail, fieldMap } = extractFieldErrors(err);
      setFieldErrors(fieldMap);
      setError(
        detail ||
          fieldMap.company_name ||
          fieldMap.email ||
          fieldMap.confirm_password ||
          "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const inputClass = (hasError) =>
    `w-full pl-10 pr-4 py-3 rounded-xl border bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all ${
      hasError ? "border-error/60" : "border-outline-variant/40"
    }`;

  const fullName = [firstName, lastName].filter(Boolean).join(" ") || "there";

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

      {/* Signup form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8">
            <h1 className="font-display-lg text-2xl font-bold text-on-surface">RequirementAI</h1>
            <p className="text-outline-variant text-xs uppercase tracking-widest mt-1">Consulting Delivery OS</p>
          </div>

          <div className="bg-white p-8 rounded-2xl soft-shadow border border-outline-variant/20">
            <h2 className="font-headline-lg text-2xl font-bold text-on-surface">Create your account</h2>
            <p className="text-on-surface-variant text-sm mt-1">
              Welcome, {fullName}. Let's get your workspace set up.
            </p>

            {/* Role Toggle */}
            <div className="mt-6 bg-surface-container-low rounded-xl p-1 flex gap-1">
              <button
                type="button"
                onClick={() => setAccountType("client")}
                className={`flex-1 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                  accountType === "client"
                    ? "bg-primary text-on-primary shadow-md"
                    : "text-on-surface-variant hover:bg-surface-container"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">business</span>
                Client
              </button>
              <button
                type="button"
                onClick={() => setAccountType("consultant")}
                className={`flex-1 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                  accountType === "consultant"
                    ? "bg-primary text-on-primary shadow-md"
                    : "text-on-surface-variant hover:bg-surface-container"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">admin_panel_settings</span>
                Consulting Team
              </button>
            </div>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                    First Name
                  </label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                      person
                    </span>
                    <input
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="John"
                      required
                      className={inputClass(false)}
                    />
                  </div>
                </div>
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                    Last Name
                  </label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                      person
                    </span>
                    <input
                      type="text"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      placeholder="Smith"
                      required
                      className={inputClass(false)}
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                  {accountType === "client" ? "Company Email" : "Work Email"}
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                    mail
                  </span>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={accountType === "client" ? "john@acmecorp.com" : "you@company.com"}
                    required
                    className={inputClass(!!fieldErrors.email)}
                  />
                </div>
                {fieldErrors.email && (
                  <p className="mt-1 text-xs text-error">{fieldErrors.email}</p>
                )}
              </div>

              {accountType === "client" && (
                <div>
                  <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                    Company Name
                  </label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                      business
                    </span>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="Acme Corp"
                      required
                      className={inputClass(!!fieldErrors.company_name)}
                    />
                  </div>
                  {fieldErrors.company_name && (
                    <p className="mt-1 text-xs text-error">{fieldErrors.company_name}</p>
                  )}
                </div>
              )}

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
                    placeholder="At least 8 characters"
                    required
                    minLength={8}
                    className={inputClass(!!fieldErrors.password)}
                  />
                </div>
                {fieldErrors.password && (
                  <p className="mt-1 text-xs text-error">{fieldErrors.password}</p>
                )}
              </div>

              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                    lock
                  </span>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter your password"
                    required
                    className={inputClass(!!fieldErrors.confirm_password)}
                  />
                </div>
                {fieldErrors.confirm_password && (
                  <p className="mt-1 text-xs text-error">{fieldErrors.confirm_password}</p>
                )}
              </div>

              <label className="flex items-start gap-2 text-sm text-on-surface-variant cursor-pointer">
                <input
                  type="checkbox"
                  checked={acceptedTerms}
                  onChange={(e) => setAcceptedTerms(e.target.checked)}
                  className="mt-0.5 rounded border-outline-variant text-primary focus:ring-primary"
                />
                <span>
                  I agree to the{" "}
                  <button type="button" className="text-primary font-medium hover:underline">
                    Terms of Service
                  </button>{" "}
                  and{" "}
                  <button type="button" className="text-primary font-medium hover:underline">
                    Privacy Policy
                  </button>
                </span>
              </label>

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
                    Creating account...
                  </>
                ) : (
                  <>
                    {accountType === "client" ? "Create Client Account" : "Create Consultant Account"}
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>
            </form>

            <p className="text-center text-xs text-on-surface-variant mt-6">
              Already have an account?{" "}
              <button
                type="button"
                onClick={onShowLogin}
                className="text-primary font-medium hover:underline"
              >
                Sign in
              </button>
            </p>
          </div>

          <p className="text-center text-xs text-on-surface-variant mt-6">
            Enterprise SSO available · Contact IT for provisioning
          </p>
        </div>
      </div>
    </div>
  );
}
