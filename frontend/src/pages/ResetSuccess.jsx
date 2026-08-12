import React from "react";
import AuthLayout from "../components/AuthLayout";
import "../styles/pages/ResetSuccess.css";

export default function ResetSuccess({ onBackToLogin }) {
  return (
    <AuthLayout>
      <div className="rsuccess-wrap">
        <div className="rsuccess-icon-circle">
          <span
            className="material-symbols-outlined rsuccess-icon"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            check_circle
          </span>
        </div>

        <h2 className="rsuccess-h2">
          Password Reset Successfully
        </h2>
        <p className="rsuccess-sub">
          Your password has been updated. You can now sign in to your workspace with your new
          password.
        </p>

        <button
          type="button"
          onClick={onBackToLogin}
          className="rsuccess-btn"
        >
          Back to Login
          <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
        </button>
      </div>
    </AuthLayout>
  );
}
