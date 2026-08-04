import React, { useState } from "react";
import AuthLayout from "../components/AuthLayout";
import { authService } from "../services/api";

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
      <div className="bg-white p-8 rounded-2xl soft-shadow border border-outline-variant/20">
        <button
          type="button"
          onClick={onBackToLogin}
          className="flex items-center gap-1 text-on-surface-variant text-xs font-medium hover:text-primary transition-all"
        >
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>
          Back to sign in
        </button>

        <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-6">Forgot password?</h2>
        <p className="text-on-surface-variant text-sm mt-1">
          No worries. Enter your work email and we'll send you a one-time password (OTP).
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          <div>
            <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
              Work Email
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                mail
              </span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="consultant@company.com"
                required
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
      </div>
    </AuthLayout>
  );
}
