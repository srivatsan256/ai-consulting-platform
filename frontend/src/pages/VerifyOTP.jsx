import React, { useEffect, useMemo, useRef, useState } from "react";
import AuthLayout from "../components/AuthLayout";
import { authService } from "../services/api";

function maskEmail(email) {
  const [local, domain] = email.split("@");
  if (!domain) return email;
  const head = local.slice(0, 2);
  return `${head}${"*".repeat(Math.max(local.length - 2, 0))}@${domain}`;
}

export default function VerifyOTP({ email, onVerified, onBackToLogin, onBackToEmail }) {
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resendCountdown, setResendCountdown] = useState(30);
  const [resending, setResending] = useState(false);
  const [resentMessage, setResentMessage] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (resendCountdown <= 0) return;
    timerRef.current = setInterval(() => {
      setResendCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [resendCountdown]);

  const maskedEmail = useMemo(() => maskEmail(email || ""), [email]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await authService.verifyOtp(email, otp);
      onVerified(res.data.data);
    } catch (err) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        "Invalid OTP. Please check the code and try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setError(null);
    setResentMessage(null);
    try {
      await authService.requestPasswordReset(email);
      setResentMessage("A new OTP has been sent to your email.");
      setOtp("");
      setResendCountdown(30);
    } catch (err) {
      const message =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        "Unable to resend the OTP. Please try again.";
      setError(message);
    } finally {
      setResending(false);
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

        <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-6">Verify your email</h2>
        <p className="text-on-surface-variant text-sm mt-1 leading-relaxed">
          We've sent a 6-digit OTP to{" "}
          <button
            type="button"
            onClick={onBackToEmail}
            className="text-primary font-semibold hover:underline"
          >
            {maskedEmail}
          </button>
          . Enter the code below to reset your password.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          <div>
            <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
              Enter OTP
            </label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">
                pin
              </span>
              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                pattern="[0-9]*"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder="••••••"
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm tracking-[0.5em] font-bold focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all"
              />
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
              <span className="material-symbols-outlined text-[18px] text-error">error</span>
              <span>{error}</span>
            </div>
          )}

          {resentMessage && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-sm">
              <span className="material-symbols-outlined text-[18px] text-emerald-600" style={{ fontVariationSettings: "'FILL' 1" }}>
                check_circle
              </span>
              <span className="text-emerald-800">{resentMessage}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || otp.length !== 6}
            className="w-full py-3.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                Verify OTP
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </>
            )}
          </button>

          <div className="text-center text-xs text-on-surface-variant">
            Didn't receive the code?{" "}
            {resendCountdown > 0 ? (
              <span className="text-on-surface-variant">Resend in {resendCountdown}s</span>
            ) : (
              <button
                type="button"
                onClick={handleResend}
                disabled={resending}
                className="text-primary font-medium hover:underline disabled:opacity-60"
              >
                {resending ? "Sending..." : "Resend OTP"}
              </button>
            )}
          </div>
        </form>
      </div>
    </AuthLayout>
  );
}
