import React, { useEffect, useMemo, useRef, useState } from "react";
import AuthLayout from "../components/AuthLayout";
import { authService } from "../services/api";
import { GLASS_INPUT, GLASS_LABEL, GLASS_ICON, GLASS_BUTTON, GLASS_ERROR } from "../constants/auth";
import "../styles/pages/VerifyOTP.css";

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
      <button
        type="button"
        onClick={onBackToLogin}
        className="otp-back"
      >
        <span className="material-symbols-outlined otp-back-icon">arrow_back</span>
        Back to sign in
      </button>

      <h2 className="otp-h2">Verify your email</h2>
      <p className="otp-sub">
        We've sent a 6-digit OTP to{" "}
        <button
          type="button"
          onClick={onBackToEmail}
          className="otp-email-link"
        >
          {maskedEmail}
        </button>
        . Enter the code below to reset your password.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        <div>
          <label className={GLASS_LABEL}>Enter OTP</label>
          <div className="relative">
            <span className={`material-symbols-outlined ${GLASS_ICON}`}>pin</span>
            <input
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              pattern="[0-9]*"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
              placeholder="••••••"
              className={`${GLASS_INPUT} otp-input`}
            />
          </div>
        </div>

        {error && (
          <div className={GLASS_ERROR}>
            <span className="material-symbols-outlined text-[18px] text-red-300">error</span>
            <span>{error}</span>
          </div>
        )}

        {resentMessage && (
          <div className="otp-success">
            <span
              className="material-symbols-outlined otp-success-icon"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              check_circle
            </span>
            <span className="otp-success-text">{resentMessage}</span>
          </div>
        )}

        <button type="submit" disabled={loading || otp.length !== 6} className={GLASS_BUTTON}>
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Verifying...
            </>
          ) : (
            <>
              Verify OTP
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </>
          )}
        </button>

        <div className="otp-footer">
          Didn't receive the code?{" "}
          {resendCountdown > 0 ? (
            <span className="otp-countdown">Resend in {resendCountdown}s</span>
          ) : (
            <button
              type="button"
              onClick={handleResend}
              disabled={resending}
              className="otp-resend"
            >
              {resending ? "Sending..." : "Resend OTP"}
            </button>
          )}
        </div>
      </form>
    </AuthLayout>
  );
}
