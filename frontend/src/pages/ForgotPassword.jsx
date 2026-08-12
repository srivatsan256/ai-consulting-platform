import React, { useState } from "react";
import AuthLayout from "../components/AuthLayout";
import { authService } from "../services/api";
import { GLASS_INPUT, GLASS_LABEL, GLASS_ICON, GLASS_BUTTON, GLASS_ERROR } from "../constants/auth";
import "../styles/pages/ForgotPassword.css";

export default function ForgotPassword({ onBackToLogin, onSent }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await authService.requestPasswordReset(email);
      onSent(email.trim());
    } catch (err) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <button
        type="button"
        onClick={onBackToLogin}
        className="forgot-back"
      >
        <span className="material-symbols-outlined forgot-back-icon">arrow_back</span>
        Back to sign in
      </button>

      <h2 className="forgot-h2">Forgot password?</h2>
      <p className="forgot-sub">
        No worries. Enter your work email and we'll send you a one-time password (OTP).
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        <div>
          <label className={GLASS_LABEL}>Work Email</label>
          <div className="relative">
            <span className={`material-symbols-outlined ${GLASS_ICON}`}>mail</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="consultant@company.com"
              required
              className={GLASS_INPUT}
            />
          </div>
        </div>

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
              Sending OTP...
            </>
          ) : (
            <>
              Send OTP
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </>
          )}
        </button>
      </form>
    </AuthLayout>
  );
}
