import React, { useState } from "react";
import AuthLayout from "../components/AuthLayout";
import { authService } from "../services/api";

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
      <div className="bg-white p-8 rounded-2xl soft-shadow border border-outline-variant/20">
        <button
          type="button"
          onClick={onBackToLogin}
          className="flex items-center gap-1 text-on-surface-variant text-xs font-medium hover:text-primary transition-all"
        >
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>
          Back to sign in
        </button>

        {invalidLink ? (
          <div className="mt-6">
            <div className="w-14 h-14 rounded-full bg-error/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-error text-[28px]">link_off</span>
            </div>
            <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-6">
              Invalid or expired link
            </h2>
            <p className="text-on-surface-variant text-sm mt-1 leading-relaxed">
              This password reset link is invalid or has already been used. Please request a new
              password reset link to continue.
            </p>
            <button
              type="button"
              onClick={onBackToLogin}
              className="mt-6 w-full py-3.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2"
            >
              Back to Login
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        ) : (
          <>
            <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-6">
              Create new password
            </h2>
            <p className="text-on-surface-variant text-sm mt-1">
              Your new password must be different from previously used passwords.
            </p>

            <form onSubmit={handleSubmit} className="mt-6 space-y-5">
              <div>
                <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
                  New Password
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                    lock
                  </span>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    required
                    minLength={8}
                    className="w-full pl-10 pr-10 py-3 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-outline hover:text-primary transition-all"
                  >
                    <span className="material-symbols-outlined text-[20px]">
                      {showPassword ? "visibility_off" : "visibility"}
                    </span>
                  </button>
                </div>
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
                    type={showPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter your password"
                    required
                    minLength={8}
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>
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
      </div>
    </AuthLayout>
  );
}
