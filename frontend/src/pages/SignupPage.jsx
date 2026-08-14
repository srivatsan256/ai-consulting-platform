import React, { useState } from "react";
import { Link } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { GLASS_INPUT, GLASS_INPUT_ERROR, GLASS_LABEL, GLASS_ICON, GLASS_BUTTON, GLASS_ERROR } from "../constants/auth";
import "../styles/pages/SignupPage.css";

const EMPLOYEE_ROLES = [
  { key: "project_manager", label: "Project Manager" },
  { key: "business_analyst", label: "Business Analyst" },
  { key: "solution_architect", label: "Solution Architect" },
  { key: "ai_ml_engineer", label: "AI/ML Engineer" },
  { key: "backend_developer", label: "Backend Developer" },
  { key: "frontend_developer", label: "Frontend Developer" },
  { key: "qa_test_engineer", label: "QA/Test Engineer" },
  { key: "security_consultant", label: "Security Consultant" },
  { key: "devops_engineer", label: "DevOps Engineer" },
  { key: "document_reviewer", label: "Document Reviewer" },
];

export default function SignupPage({ onRegister, onShowLogin }) {
  const [accountType, setAccountType] = useState("client");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [role, setRole] = useState("");
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
        role,
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

  const inputClass = (hasError) => (hasError ? GLASS_INPUT_ERROR : GLASS_INPUT);

  const fullName = [firstName, lastName].filter(Boolean).join(" ") || "there";

  return (
    <AuthLayout>
      <h2 className="signup-h2">Create your account</h2>
      <p className="signup-sub">
        Welcome, {fullName}. Let's get your workspace set up.
      </p>

      {/* Role Toggle */}
      <div className="signup-toggle">
        <button
          type="button"
          onClick={() => { setAccountType("client"); setRole(""); }}
          className={`signup-toggle-btn ${
            accountType === "client"
              ? "signup-toggle-btn-active"
              : "signup-toggle-btn-inactive"
          }`}
        >
          <span className="material-symbols-outlined signup-toggle-icon">business</span>
          Client
        </button>
        <button
          type="button"
          onClick={() => setAccountType("consultant")}
          className={`signup-toggle-btn ${
            accountType === "consultant"
              ? "signup-toggle-btn-active"
              : "signup-toggle-btn-inactive"
          }`}
        >
          <span className="material-symbols-outlined signup-toggle-icon">admin_panel_settings</span>
          Consulting Team
        </button>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        <div className="signup-grid">
          <div>
            <label className={GLASS_LABEL}>First Name</label>
            <div className="relative">
              <span className={`material-symbols-outlined ${GLASS_ICON}`}>person</span>
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
            <label className={GLASS_LABEL}>Last Name</label>
            <div className="relative">
              <span className={`material-symbols-outlined ${GLASS_ICON}`}>person</span>
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
          <label className={GLASS_LABEL}>
            {accountType === "client" ? "Company Email" : "Work Email"}
          </label>
          <div className="relative">
            <span className={`material-symbols-outlined ${GLASS_ICON}`}>mail</span>
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
            <p className="signup-field-error">{fieldErrors.email}</p>
          )}
        </div>

        {accountType === "client" && (
          <div>
            <label className={GLASS_LABEL}>Company Name</label>
            <div className="relative">
              <span className={`material-symbols-outlined ${GLASS_ICON}`}>business</span>
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
              <p className="signup-field-error">{fieldErrors.company_name}</p>
            )}
          </div>
        )}

        {accountType === "consultant" && (
          <div>
            <label className={GLASS_LABEL}>Your Role</label>
            <div className="relative">
              <span className={`material-symbols-outlined ${GLASS_ICON}`}>badge</span>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                required
                className={`${inputClass(!!fieldErrors.role)} ${role ? "" : "text-white/40"}`}
              >
                <option value="" disabled>
                  Select your role
                </option>
                {EMPLOYEE_ROLES.map((r) => (
                  <option key={r.key} value={r.key}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
            {fieldErrors.role && (
              <p className="signup-field-error">{fieldErrors.role}</p>
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
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              required
              minLength={8}
              className={inputClass(!!fieldErrors.password)}
            />
          </div>
          {fieldErrors.password && (
            <p className="signup-field-error">{fieldErrors.password}</p>
          )}
        </div>

        <div>
          <label className={GLASS_LABEL}>Confirm Password</label>
          <div className="relative">
            <span className={`material-symbols-outlined ${GLASS_ICON}`}>lock</span>
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
            <p className="signup-field-error">{fieldErrors.confirm_password}</p>
          )}
        </div>

        <label className="signup-terms">
          <input
            type="checkbox"
            checked={acceptedTerms}
            onChange={(e) => setAcceptedTerms(e.target.checked)}
            className="signup-checkbox"
          />
          <span>
            I agree to the{" "}
            <Link
              to="/terms-of-service"
              className="signup-link"
            >
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link
              to="/privacy-policy"
              className="signup-link"
            >
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
              {accountType === "client" ? "Create Client Account" : "Create Consultant Account"}
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </>
          )}
        </button>
      </form>

      <p className="signup-footer">
        Already have an account?{" "}
        <button
          type="button"
          onClick={onShowLogin}
          className="signup-link"
        >
          Sign in
        </button>
      </p>

      <p className="signup-footer-note">
        Enterprise SSO available · Contact IT for provisioning
      </p>
    </AuthLayout>
  );
}
