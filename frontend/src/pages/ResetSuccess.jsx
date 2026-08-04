import React from "react";
import AuthLayout from "../components/AuthLayout";

export default function ResetSuccess({ onBackToLogin }) {
  return (
    <AuthLayout>
      <div className="bg-white p-8 rounded-2xl soft-shadow border border-outline-variant/20">
        <div className="flex flex-col items-center text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-50 border-4 border-emerald-100 flex items-center justify-center">
            <span
              className="material-symbols-outlined text-emerald-600 text-[32px]"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              check_circle
            </span>
          </div>

          <h2 className="font-headline-lg text-2xl font-bold text-on-surface mt-6">
            Password Reset Successfully
          </h2>
          <p className="text-on-surface-variant text-sm mt-2 leading-relaxed">
            Your password has been updated. You can now sign in to your workspace with your new
            password.
          </p>

          <button
            type="button"
            onClick={onBackToLogin}
            className="mt-8 w-full py-3.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2"
          >
            Back to Login
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>
      </div>
    </AuthLayout>
  );
}
