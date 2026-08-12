import React, { useState } from "react";
import AuthLayout from "../components/AuthLayout";
import { authService } from "../services/api";
import { GLASS_INPUT, GLASS_LABEL, GLASS_ICON, GLASS_BUTTON, GLASS_ERROR } from "../constants/auth";
import "../styles/pages/ResetPassword.css";

export default function ResetPassword({ uid, token, onBackToLogin, onSuccess }) {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const invalidLink = !uid || !token;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await authService.resetPassword(uid, token, newPassword, confirmPassword);
      onSuccess();
    } catch (err) {
      const data = err?.response?.data || {};
      const message =
        data.message ||
        data.detail ||
        (data.confirm_password && data.confirm_password[0]) ||
        (data.new_password && data.new_password[0]) ||
        "Unable to reset your password. The link may be invalid or expired.";
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
        className="resetpw-back"
      >
        <span className="material-symbols-outlined resetpw-back-icon">arrow_back</span>
        Back to sign in
      </button>

      {invalidLink ? (
        <div className="mt-6">
          <div className="resetpw-icon-circle">
            <span className="material-symbols-outlined resetpw-invalid-icon">link_off</span>
          </div>
          <h2 className="resetpw-h2">
            Invalid or expired link
          </h2>
          <p className="resetpw-sub leading-relaxed">
            This password reset link is invalid or has already been used. Please request a new
            password reset link to continue.
          </p>
          <button
            type="button"
            onClick={onBackToLogin}
            className="resetpw-primary-btn"
          >
            Back to Login
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      ) : (
        <>
          <h2 className="resetpw-h2">
            Create new password
          </h2>
          <p className="resetpw-sub">
            Your new password must be different from previously used passwords.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div>
              <label className={GLASS_LABEL}>New Password</label>
              <div className="relative">
                <span className={`material-symbols-outlined ${GLASS_ICON}`}>lock</span>
                <input
                  type={showPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  required
                  minLength={8}
                  className={`${GLASS_INPUT} pr-10`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="resetpw-eye-btn"
                >
                  <span className="material-symbols-outlined resetpw-eye-icon">
                    {showPassword ? "visibility_off" : "visibility"}
                  </span>
                </button>
              </div>
            </div>

            <div>
              <label className={GLASS_LABEL}>Confirm Password</label>
              <div className="relative">
                <span className={`material-symbols-outlined ${GLASS_ICON}`}>lock</span>
                <input
                  type={showPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  required
                  minLength={8}
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
                  Resetting...
                </>
              ) : (
                <>
                  Reset Password
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </>
              )}
            </button>
          </form>
        </>
      )}
    </AuthLayout>
  );
}
