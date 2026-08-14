import React, { useState } from "react";
import OnboardingOne from "../components/OnboardingOne";

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

  const handleToggleAccountType = (type) => {
    setAccountType(type);
    if (type === "client") setRole("");
  };

  const handleFieldChange = (field, value) => {
    switch (field) {
      case "firstName":
        setFirstName(value);
        break;
      case "lastName":
        setLastName(value);
        break;
      case "email":
        setEmail(value);
        break;
      case "companyName":
        setCompanyName(value);
        break;
      case "role":
        setRole(value);
        break;
      case "password":
        setPassword(value);
        break;
      case "confirmPassword":
        setConfirmPassword(value);
        break;
      case "acceptedTerms":
        setAcceptedTerms(value);
        break;
      default:
        break;
    }
  };

  return (
    <OnboardingOne
      accountType={accountType}
      onToggleAccountType={handleToggleAccountType}
      values={{
        firstName,
        lastName,
        email,
        companyName,
        role,
        password,
        confirmPassword,
        acceptedTerms,
      }}
      onChange={handleFieldChange}
      roles={EMPLOYEE_ROLES}
      loading={loading}
      error={error}
      fieldErrors={fieldErrors}
      onSubmit={handleSubmit}
      onShowLogin={onShowLogin}
    />
  );
}
